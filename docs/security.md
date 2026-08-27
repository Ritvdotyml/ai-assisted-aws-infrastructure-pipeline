# Security

The project keeps the template processor and the CloudFormation deployment path under separate IAM roles.

## IAM roles

Three identities are involved:

- the Lambda execution role used by the template processor,
- the dedicated CloudFormation service role used during stack creation,
- and the Lambda execution role used by the deployed application.

Separating these roles keeps deployment permissions out of the processor's normal runtime identity.

## Trust policies

- `infrastructure/lambda-trust-policy.json` allows `lambda.amazonaws.com` to assume the template processor role.
- `infrastructure/cloudformation-trust-policy.json` allows `cloudformation.amazonaws.com` to assume the deployment role.

## Permissions

The two main permission policies are:

- `infrastructure/lambda-permissions-policy.json`, which gives the processor access to the S3 bucket, CloudFormation validation and stack operations, and `iam:PassRole` for the dedicated deployment role.
- `infrastructure/cloudformation-deployment-policy.json`, which gives CloudFormation the permissions required to create and manage Lambda, S3, DynamoDB, API Gateway, and IAM resources used by the deployed stack.

## Permissions added during testing

Several permissions were added as deployment failures exposed missing actions:

- `s3:CreateBucket` was required for the deployment smoke-test stack.
- `s3:PutBucketTagging` was required when CloudFormation tagged the test bucket.
- `iam:AttachRolePolicy` was required while creating `LambdaExecutionRole`.
- `iam:DetachRolePolicy` was required during rollback cleanup.

These failures helped narrow the deployment role to the actions the stack actually needed.

## Why CloudFormation uses a dedicated role

The processor calls `create_stack` with `RoleARN`, so CloudFormation performs resource creation using the deployment role rather than the Lambda processor role.

This has two benefits:

- the processor keeps a smaller runtime permission set,
- and infrastructure deployment permissions remain isolated in a role dedicated to CloudFormation.

## S3 prefix boundary

The `infrastructure/s3-notification.json` file routes objects based on the `templates/` and `deploy/` prefixes. This separates validation and deployment behavior, but the prefixes themselves are not an authorization mechanism.

Access control still depends on:

- who can upload objects to the bucket,
- what the processor role is allowed to do,
- and what resources the CloudFormation role is allowed to create.

## Sensitive configuration

Account-specific values should not be committed to the repository. This includes:

- account IDs,
- usernames,
- SSO URLs,
- access keys,
- session names,
- generated UUIDs,
- and account-specific ARNs.

Local account wiring is kept in `.local.json` files, which are excluded from version control.
