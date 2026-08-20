# Testing

This section is based on evidence from the actual implementation, not on synthetic examples.

## Test matrix

| Test | Evidence used | Observed result |
|---|---|---|
| Valid template validation | `incident-history.md`, `template-processor-lambda-logs.txt` | Validation succeeded and a validation JSON artifact was written to S3. |
| Invalid template validation | `invalid-template-validation-error.json`, `template-processor-errors.json` | CloudFormation rejected the template because the YAML was not well formed. |
| Deployment gate | `incident-history.md`, `template-processor-lambda-logs.txt` | `deploy/` objects triggered validation and stack creation authorization. |
| Deployment smoke test | `incident-history.md`, `template-processor-lambda-logs.txt` | The deployment test stack reached `CREATE_COMPLETE` after permissions were corrected. |
| API Gateway test | `incident-history.md` | A request to the deployed API returned HTTP `201`, and the created item was verified in DynamoDB. |

## What the evidence proves

The validation path is confirmed by the Lambda logs and the invalid-template result file:

- valid templates were accepted,
- malformed YAML was rejected by `validate_template`,
- and the Lambda wrote the outcome back to S3.

The deployment path is confirmed by the incident history and the processor logs:

- objects under `deploy/` were treated as deployment candidates,
- CloudFormation stack creation was attempted from the processor,
- and deployment permissions had to be expanded before the stack completed successfully.

The application path is confirmed by the curated incident history:

- API Gateway fronted the Lambda function,
- the Lambda wrote to DynamoDB,
- and the successful request returned HTTP `201`.

## Public write-up guidance

When you describe the test results in public documentation, keep the framing factual:

- state what was tested,
- state the observed result,
- and avoid reproducing raw AWS logs or unique identifiers.

If you want this section to read like a fully documented case study, add the exact API request and a sanitized response snippet to your private notes, not to the public repo.
