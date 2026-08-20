# Troubleshooting

This repository is built to surface failures through logs and S3 result objects rather than through silent exits.

The curated evidence is enough to document the real incident history without quoting raw CloudWatch output.

## Diagnosis path

When something failed, the workflow was:

1. inspect the Lambda logs,
2. inspect the generated S3 error JSON,
3. inspect CloudFormation stack events if deployment had already started,
4. and then compare the observed failure with the repo source and the curated incident notes.

## Real incidents

| Incident | Cause | Diagnosis | Resolution |
|---|---|---|---|
| Lambda Python syntax failure | `lambda/index.py` had inconsistent indentation in the deployment block, which caused a `Runtime.UserCodeSyntaxError`. | The Lambda error stream showed an indentation syntax error at line 74. The fix was validated locally with `python3 -m py_compile lambda/index.py`. | The indentation was corrected and the Lambda package was rebuilt. |
| Deployment-test bucket creation denied | The CloudFormation deployment role did not have `s3:CreateBucket`. | The deployment stack entered rollback after the bucket creation step failed. | `s3:CreateBucket` was added to the CloudFormation deployment policy. |
| Deployment-test bucket tagging denied | The CloudFormation deployment role did not have `s3:PutBucketTagging`. | CloudFormation failed while creating or tagging the test S3 bucket. | `s3:PutBucketTagging` was added to the CloudFormation deployment policy. |
| LambdaExecutionRole attachment denied | The deployment role did not have `iam:AttachRolePolicy` while creating the Lambda execution role for the generated application stack. | The stack failed during IAM role creation. | `iam:AttachRolePolicy` was added to the CloudFormation deployment policy. |
| Rollback failed | The deployment role did not have `iam:DetachRolePolicy` during CloudFormation rollback cleanup. | The stack entered `ROLLBACK_FAILED`, which showed that cleanup permissions were also required. | `iam:DetachRolePolicy` was added and the failed stack was allowed to clean up. |

## Validation failure

The deliberately invalid template under `templates/invalid-template.yaml` was rejected by CloudFormation with a YAML format error. That is a useful sanity check for the validation path, not a deployment failure.

## What this means for the public docs

- The validation path is working when invalid YAML is rejected and valid templates produce S3 result files.
- The deployment path is working when the CloudFormation role has the resource-management permissions it needs to create the stack.
- The application path is working when the deployed API returns HTTP `201` and the item appears in DynamoDB.

## Sanitized takeaways

- Prefix mismatches are handled by the S3 trigger design, so `templates/` and `deploy/` need to match the intended path.
- CloudFormation failures were permission-driven, not template-generation failures.
- The most important debugging tool was the combination of Lambda logs, S3 result artifacts, and CloudFormation stack state.
