# Implementation

This file describes the implementation present in the repository and the evidence that confirms how it behaved.

## Evidence-backed source map

- `source-reference.txt` identifies `lambda/index.py` as the final template processor.
- `incident-history.md` records the real failures and their fixes.
- `template-processor-lambda-logs.txt` confirms the runtime behavior of validation, deployment authorization, and error handling.

## Files and responsibilities

- `templates/valid-template.yaml` is a minimal valid CloudFormation template.
- `templates/invalid-template.yaml` is intentionally invalid and exists to exercise validation failure handling.
- `templates/deployment-test.yaml` is a minimal S3 bucket template used to smoke-test deployment permissions.
- `templates/ai-generated-serverless-api.yaml` is the deployable serverless application.
- `lambda/index-validation-only.py` handles validation-only workflows.
- `lambda/index.py` handles validation plus promotion to deployment.
- `infrastructure/s3-notification.json` defines the S3 prefix-based event routing.
- `infrastructure/lambda-trust-policy.json` and `infrastructure/cloudformation-trust-policy.json` define trust relationships.
- `infrastructure/lambda-permissions-policy.json` and `infrastructure/cloudformation-deployment-policy.json` define permissions.

## Observed behavior

The evidence shows two distinct Lambda behaviors:

1. validation-only processing for objects under `templates/`,
2. validation followed by stack creation for objects under `deploy/`.

`lambda/index-validation-only.py` implements the first behavior. It validates the uploaded template and writes either a validation result or an error result back to S3.

`lambda/index.py` implements the final behavior:

- it validates every template first,
- it only creates a stack when the key begins with `deploy/`,
- it passes the dedicated CloudFormation role through `RoleARN`,
- and it records deployment metadata in an S3 result file.

## Architectural explanation

The promotion gate is storage-based rather than manual inside the code:

- `templates/` means validate only,
- `deploy/` means validate and deploy.

The Lambda derives a stack name from the S3 object key by:

- taking the filename without extension,
- replacing non-alphanumeric characters with `-`,
- prefixing `stack-` if the name does not start with a letter,
- and trimming the result to 128 characters.

That naming logic reduces avoidable CloudFormation failures when arbitrary filenames are promoted.

## Final serverless application

The final application template defines:

- a DynamoDB table with a string `id` partition key,
- a Lambda function that writes items to that table,
- an API Gateway REST API,
- a `POST /items` method using Lambda proxy integration,
- a Lambda permission that allows API Gateway to invoke the function,
- and an output that exposes the API endpoint.

That application behavior is verified separately in the testing evidence.

## Implementation lessons from the evidence

- Generated templates are only a starting point; they still need validation, gating, and least-privilege access.
- Prefix-based routing is a simple but effective promotion control.
- Returning validation artifacts to S3 makes the pipeline auditable without needing a separate state store.
- A dedicated CloudFormation role is cleaner than letting the Lambda processor create resources directly with broad privileges.
- The deployment package had to be validated locally after an indentation bug caused a Python syntax error in `lambda/index.py`.

## Future improvements

- Add an explicit CI step that validates templates before S3 promotion.
- Add richer result records with timestamps and stack event summaries.
- Capture deployment status polling so the deployment result can progress from `CREATE_IN_PROGRESS` to a terminal state.
- Replace broad permissions with tighter resource-level scoping where practical.
