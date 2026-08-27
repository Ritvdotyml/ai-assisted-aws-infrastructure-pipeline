# Cleanup

Use the following order to tear down the environment without leaving dependent resources behind.

## Recommended order

1. Stop uploading new templates to the pipeline S3 bucket.
2. Disable or remove the S3 event notification configuration.
3. Delete any CloudFormation stacks created through the deployment path.
4. Confirm that stack-managed resources such as the API Gateway stage and application Lambda have been removed.
5. Empty S3 buckets that contain uploaded templates, validation results, or deployment results.
6. Remove manually created Lambda functions, IAM roles, or CloudFormation roles that are not managed by a stack.
7. Delete standalone IAM policies created for the environment.
8. Remove local account-specific files if they are no longer needed, or keep them untracked for future runs.

## Verification

Before considering cleanup complete, confirm that:

- no deployment-test CloudFormation stacks remain,
- no API Gateway endpoint from the project is still active,
- no manually created Lambda function or execution role remains,
- the S3 bucket is empty before deletion,
- and account-specific `.local.json` files remain outside version control.

## Notes

When resources were created by CloudFormation, delete the stack before removing its individual resources manually. CloudFormation can then remove dependencies in the correct order and is less likely to leave the environment in a partially deleted state.
