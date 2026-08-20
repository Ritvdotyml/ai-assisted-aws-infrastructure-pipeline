# Architecture

This project uses S3 as the intake point for infrastructure templates and Lambda as the control plane for validation and promotion.

## Components

| Component | Responsibility |
|---|---|
| S3 bucket | Receives uploaded templates and stores validation or deployment results. |
| Lambda processor | Reads the uploaded template, validates it, and optionally creates a stack. |
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
4. CloudFormation validate_template checks syntax and structure.
5. The Lambda writes a JSON result object back to S3.
6. If the object key starts with deploy/, the Lambda calls create_stack.
7. CloudFormation assumes the dedicated deployment role.
8. The deployed stack creates an API Gateway -> Lambda -> DynamoDB application.
```

## Pipeline split

The repository encodes two distinct paths:

- `templates/` is the validation path.
- `deploy/` is the promotion path.

That split is the core control mechanism. Validation can happen without stack creation. Deployment only happens when the object is placed in the explicit deployment prefix.

## Processing Lambda

There are two handler variants in the repository:

- `lambda/index-validation-only.py` validates a template and writes a validation artifact to S3.
- `lambda/index.py` validates first, then creates a stack when the key is under `deploy/`.

Both handlers:

- read the uploaded object from S3,
- call `cloudformation.validate_template`,
- write a JSON result object back to S3,
- and log their progress.

## Deployed serverless application

The deployable template in `templates/ai-generated-serverless-api.yaml` defines:

- a DynamoDB table with a string partition key named `id`,
- a Lambda function that writes items to that table,
- an API Gateway REST API,
- a `POST /items` method using Lambda proxy integration,
- a Lambda permission that allows API Gateway to invoke the function,
- and an output that exposes the API endpoint.

The Lambda implementation returns HTTP `201` and a JSON body containing the new item identifier.

## Role separation

The architecture separates responsibilities into distinct IAM identities:

- the Lambda execution role lets the function write to CloudWatch Logs and DynamoDB,
- the Lambda processor role lets the template processor read and write the S3 bucket and use CloudFormation validation and stack operations,
- the CloudFormation trust role lets CloudFormation create the deployed resources,
- and the Lambda processor passes only that dedicated CloudFormation role during stack creation.

## Local versus shared config

The repository also contains `.local.json` variants and `.gitignore` explicitly excludes `*.local.json` and `project.env`. That is a strong signal that account-specific wiring stays out of the committed documentation and should be treated as environment-local configuration.

## Why This Matters

The architecture is intentionally small, but the separation of concerns is the important part:

- templates are validated before they are trusted,
- deployment is only possible through an explicit prefix,
- and the deployed application remains a normal serverless API that can be tested independently from the template pipeline.
