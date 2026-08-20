# Cleanup

Use this order to tear down the environment safely.

## Recommended order

1. Stop new uploads to the S3 bucket used for the pipeline.
2. Delete or disable the S3 event notification configuration.
3. Delete any deployed CloudFormation stacks created by the promotion path.
4. Confirm the API Gateway stage and Lambda function are removed with the stack.
5. Empty any S3 buckets that hold uploaded templates, validation results, or deployment results.
6. Remove any manually created Lambda, IAM, or CloudFormation roles that are not stack-managed.
7. Delete any standalone IAM policies that were created for the demo environment.
8. Remove local account-specific files or keep them untracked if they are still useful for future runs.

## What to verify

- No CloudFormation stacks remain from the deployment test.
- No active API Gateway endpoint remains.
- No Lambda function or execution role remains if it was created outside a stack.
- The S3 bucket is empty before deletion.
- The account-specific `.local.json` wiring is not published with the docs.

## Notes

If the cleanup process is driven by a stack, prefer deleting the stack before manually removing its member resources. That avoids leaving behind dependencies that can make teardown harder than deployment.

