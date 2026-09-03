# Implementation

This document describes how the pipeline is implemented and how the main pieces work together.

## Repository structure

- `templates/valid-template.yaml` is a minimal valid CloudFormation template.
- `templates/invalid-template.yaml` is intentionally invalid and is used to test validation failures.
- `templates/deployment-test.yaml` is a small S3 bucket template used to test deployment permissions.
- `templates/ai-generated-serverless-api.yaml` defines the deployable serverless application.
- `lambda/index-validation-only.py` handles validation-only processing.
- `lambda/index.py` handles validation and deployment promotion.
- `infrastructure/s3-notification.json` defines prefix-based S3 event routing.
- `infrastructure/lambda-trust-policy.json` and `infrastructure/cloudformation-trust-policy.json` define IAM trust relationships.
- `infrastructure/lambda-permissions-policy.json` and `infrastructure/cloudformation-deployment-policy.json` define the required permissions.

## Template processing

The pipeline supports two paths:

1. objects uploaded under `templates/` are validated only,
2. objects uploaded under `deploy/` are validated and then submitted to CloudFormation for stack creation.

`lambda/index-validation-only.py` implements the first path. It validates the uploaded template and writes either a success result or an error result back to S3.

`lambda/index.py` implements the deployment path. It:

- validates every template before deployment,
- only creates a stack when the object key starts with `deploy/`,
- passes the dedicated CloudFormation deployment role through `RoleARN`,
- and writes deployment metadata back to S3.

## Stack naming

The processor derives the CloudFormation stack name from the uploaded object key. It:

- removes the file extension,
- replaces non-alphanumeric characters with `-`,
- adds the `stack-` prefix if the resulting name does not begin with a letter,
- and limits the final name to 128 characters.

This keeps arbitrary uploaded filenames compatible with CloudFormation stack naming rules.

## Serverless application

The application template in `templates/ai-generated-serverless-api.yaml` creates:

- a DynamoDB table with a string `id` partition key,
- a Lambda function that writes items to the table,
- an API Gateway REST API,
- a `POST /items` route using Lambda proxy integration,
- permission for API Gateway to invoke the function,
- and an output containing the deployed API endpoint.

A successful request returns HTTP `201` with a JSON response containing the new item identifier.

## Design choices

A few implementation details were kept deliberately simple:

- S3 prefixes act as the promotion mechanism between validation and deployment.
- Validation and deployment results are written back to S3 instead of requiring a separate state database.
- CloudFormation uses its own deployment role rather than relying on broad permissions in the processor Lambda role.
- The deployed application can be tested independently from the template-processing pipeline.
- 
## Future improvements

- Add a CI step that validates CloudFormation templates before they are uploaded to S3.
- Include timestamps and stack event summaries in result files.
- Poll deployment status so result files can be updated from `CREATE_IN_PROGRESS` to a terminal stack state.
- Reduce broad IAM permissions further where resource-level restrictions are practical.
