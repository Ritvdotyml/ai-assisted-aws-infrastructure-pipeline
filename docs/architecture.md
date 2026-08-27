# Architecture

The pipeline uses S3 to receive infrastructure templates and Lambda to handle validation and deployment decisions.

## Components

| Component | Responsibility |
|---|---|
| S3 bucket | Receives uploaded templates and stores validation or deployment results. |
| Lambda processor | Reads uploaded templates, validates them, and optionally starts a deployment. |
| CloudFormation | Validates templates and provisions the deployed application. |
| Dedicated CloudFormation role | Is assumed by CloudFormation during stack creation. |
| API Gateway | Exposes the deployed `POST /items` endpoint. |
| Lambda application function | Handles API requests and writes items to DynamoDB. |
| DynamoDB table | Stores created items. |

## End-to-end flow

```text
1. A template is uploaded to S3 under templates/ or deploy/.
2. S3 event notifications invoke the template processor Lambda.
3. The Lambda reads the uploaded object.
4. CloudFormation validate_template checks the template syntax and structure.
5. The Lambda writes a JSON result object back to S3.
6. If the object key starts with deploy/, the Lambda calls create_stack.
7. CloudFormation assumes the dedicated deployment role.
8. The deployed stack creates an API Gateway -> Lambda -> DynamoDB application.
```

## Validation and deployment paths

The S3 prefixes separate validation from deployment:

- `templates/` validates a template without creating a stack.
- `deploy/` validates the template and then promotes it to deployment.

This keeps deployment explicit while allowing templates to be checked independently.

## Template processor

There are two handler variants in the repository:

- `lambda/index-validation-only.py` validates a template and writes a validation result to S3.
- `lambda/index.py` validates first, then creates a stack when the key is under `deploy/`.

Both handlers:

- read the uploaded object from S3,
- call `cloudformation.validate_template`,
- write a JSON result object back to S3,
- and log their progress.

## Deployed serverless application

The deployable template in `templates/ai-generated-serverless-api.yaml` defines:

- a DynamoDB table with a string partition key named `id`,
- a Lambda function that writes items to the table,
- an API Gateway REST API,
- a `POST /items` method using Lambda proxy integration,
- a Lambda permission that allows API Gateway to invoke the function,
- and an output containing the API endpoint.

The Lambda implementation returns HTTP `201` with a JSON body containing the new item identifier.

## IAM role separation

Responsibilities are split across separate IAM roles:

- the application Lambda execution role allows the deployed function to write logs and access DynamoDB,
- the template processor role allows the processor to read and write the S3 bucket and call the required CloudFormation APIs,
- the CloudFormation deployment role is assumed during stack creation,
- and the processor can pass only the dedicated CloudFormation role when it starts a deployment.

This prevents the template processor from using its own runtime role to create application infrastructure directly.

## Local configuration

Account-specific values are kept in `.local.json` files. The repository also ignores `*.local.json` and `project.env`, so local account wiring does not need to be committed with the reusable project files.

## Design rationale

The architecture is intentionally small. The main design choices are:

- templates are validated before deployment,
- deployment requires use of the explicit `deploy/` prefix,
- validation results are written back to S3 for later inspection,
- and the deployed API can be tested independently from the template-processing pipeline.
