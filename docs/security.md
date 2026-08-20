# Security

This project uses separate trust and permission documents to keep the Lambda processor and CloudFormation deployment path distinct.

## Observed security model

The evidence shows three identities in play:

- the Lambda execution role for the template processor,
- the dedicated CloudFormation service role used for stack creation,
- and the Lambda execution role for the deployed application.

## Trust policies

- `infrastructure/lambda-trust-policy.json` allows `lambda.amazonaws.com` to assume the Lambda execution role.
- `infrastructure/cloudformation-trust-policy.json` allows `cloudformation.amazonaws.com` to assume the deployment role.

That separation matters because the Lambda processor should not create infrastructure with its own identity.

## Permission model

The repository shows two major permission sets:

- `infrastructure/lambda-permissions-policy.json` grants the template processor access to the S3 bucket, CloudFormation validation and stack APIs, and `iam:PassRole` for the dedicated CloudFormation role.
- `infrastructure/cloudformation-deployment-policy.json` grants CloudFormation the ability to create and manage Lambda, S3, DynamoDB, API Gateway, and IAM resources.

## Incident-driven permissions

The evidence also shows why the CloudFormation deployment role needed the following actions during debugging:

- `s3:CreateBucket` for the deployment-test stack,
- `s3:PutBucketTagging` for the deployment-test stack,
- `iam:AttachRolePolicy` when creating `LambdaExecutionRole`,
- and `iam:DetachRolePolicy` during rollback cleanup.

Those are exactly the kinds of generic IAM actions that are appropriate to document in a portfolio write-up.

## Why the dedicated CloudFormation role matters

The processor Lambda calls `create_stack` with `RoleARN`. That means CloudFormation, not Lambda, is the actor that performs resource creation.

This is the correct pattern for two reasons:

- it narrows the runtime identity of the Lambda function,
- and it keeps the deployment permissions in one place rather than embedding broad infrastructure access in the processor function.

## Architectural boundary

The `infrastructure/s3-notification.json` file shows prefix-based routing for `templates/` and `deploy/`. That is a functional boundary, but not an authorization boundary by itself.

The real security control comes from:

- who can upload objects into the bucket,
- which role the processor assumes,
- and what the deployment role is allowed to create.

## What should stay out of the public docs

Do not publish:

- account IDs,
- usernames,
- SSO URLs,
- access keys,
- session names,
- generated UUIDs,
- or account-specific ARNs.

The repository’s `.local.json` files are the right place for account-specific wiring, but they should stay out of the public narrative.
