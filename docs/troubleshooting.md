# Troubleshooting

Failures in the pipeline are surfaced through Lambda logs, S3 result files, and CloudFormation stack events.

## Diagnosis workflow

When a failure occurs, check the components in this order:

1. inspect the template processor Lambda logs,
2. inspect the generated S3 error result,
3. inspect CloudFormation stack events if stack creation has started,
4. compare the failure with the relevant processor code and IAM policy.

## Incidents encountered

| Incident | Cause | Diagnosis | Resolution |
|---|---|---|---|
| Lambda Python syntax failure | `lambda/index.py` had inconsistent indentation in the deployment block, causing `Runtime.UserCodeSyntaxError`. | The Lambda error stream reported an indentation error at line 74. | The indentation was corrected and the file was checked locally with `python3 -m py_compile lambda/index.py`. |
| Deployment-test bucket creation denied | The CloudFormation deployment role did not have `s3:CreateBucket`. | The deployment stack entered rollback when bucket creation failed. | `s3:CreateBucket` was added to the CloudFormation deployment policy. |
| Deployment-test bucket tagging denied | The deployment role did not have `s3:PutBucketTagging`. | CloudFormation failed while applying tags to the test bucket. | `s3:PutBucketTagging` was added to the deployment policy. |
| Lambda execution role policy attachment denied | The deployment role did not have `iam:AttachRolePolicy`. | The stack failed while creating the Lambda execution role for the application. | `iam:AttachRolePolicy` was added to the deployment policy. |
| Rollback cleanup failed | The deployment role did not have `iam:DetachRolePolicy`. | The stack entered `ROLLBACK_FAILED` while cleaning up IAM resources. | `iam:DetachRolePolicy` was added and the failed stack was cleaned up. |

## Validation failures

The intentionally invalid template under `templates/invalid-template.yaml` is expected to fail validation because its YAML is malformed.

A validation failure is working as intended when:

- CloudFormation rejects the template,
- the processor handles the exception,
- and an error result is written back to S3.

## Deployment failures

If validation succeeds but stack creation fails, inspect the CloudFormation stack events first. In this project, the deployment failures encountered during testing were caused by missing permissions in the CloudFormation deployment role.

Common checks include:

- whether the deployment role can create the required resource,
- whether it can apply tags or policies during creation,
- and whether it also has the permissions needed to remove those resources during rollback.

## Prefix and trigger issues

The S3 notification configuration expects objects under the `templates/` and `deploy/` prefixes.

If the processor is not invoked, confirm that:

- the object was uploaded under the expected prefix,
- the S3 notification configuration is active,
- and the notification target points to the correct Lambda function.

## Useful debugging sources

The most useful places to check are:

- Lambda logs for processor errors,
- S3 result files for validation and deployment responses,
- and CloudFormation stack events for resource-level deployment failures.
