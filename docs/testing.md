# Testing

The following tests were run against the implemented pipeline and deployed application.

## Test matrix

| Test | Result |
|---|---|
| Valid template validation | Validation succeeded and a JSON result file was written to S3. |
| Invalid template validation | CloudFormation rejected the malformed YAML as expected. |
| Deployment gate | Objects under `deploy/` triggered validation followed by stack creation. |
| Deployment smoke test | The test stack reached `CREATE_COMPLETE` after the required role permissions were added. |
| API Gateway test | A request to the deployed API returned HTTP `201`, and the new item was stored in DynamoDB. |

## Validation path

The validation-only path was tested with both valid and invalid templates.

For valid templates:

- `validate_template` completed successfully,
- the processor wrote a validation result to S3,
- and no deployment was started.

For the intentionally invalid template:

- CloudFormation rejected the malformed YAML,
- the processor caught the validation failure,
- and an error result was written back to S3.

## Deployment path

Objects uploaded under `deploy/` were processed through validation first and then passed to CloudFormation for stack creation.

The initial deployment tests exposed missing IAM permissions in the CloudFormation service role. After those permissions were added, the deployment smoke-test stack completed successfully.

## Application test

The deployed API was tested through its API Gateway endpoint.

A `POST /items` request:

- reached the application Lambda,
- returned HTTP `201`,
- and created the corresponding item in DynamoDB.

This confirmed the complete API Gateway -> Lambda -> DynamoDB path.
