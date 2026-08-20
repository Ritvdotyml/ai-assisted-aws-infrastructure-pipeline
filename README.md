# AI-Assisted AWS Infrastructure Code Generation

This repository documents an AI-assisted AWS infrastructure-as-code pipeline that accepts template uploads in S3, validates them with CloudFormation, and promotes only explicitly designated artifacts into deployment.

The project solves a practical problem: generated infrastructure code is only useful if there is a controlled path to validate it, separate review-worthy templates from deployable ones, and keep the deployment path tied to a dedicated CloudFormation service role.

Observed in the evidence:

- invalid templates are rejected before deployment,
- valid templates are written back to S3 as validation artifacts,
- `deploy/` objects trigger stack creation,
- and the deployed application returns HTTP `201` from an API Gateway backed Lambda that writes to DynamoDB.

```text
S3 object created under templates/ or deploy/
  -> Lambda processor
  -> CloudFormation validate_template
  -> validation result written back to S3
  -> deploy/ objects also call CloudFormation create_stack
  -> deployed app exposes API Gateway POST /items
  -> Lambda writes to DynamoDB
```
##Project architecture diagram
<img width="549" height="1834" alt="image" src="https://github.com/user-attachments/assets/7664e88d-afd1-45af-a095-b2b818886ae4" />

## What This Repository Contains

- A template-driven pipeline for validating and deploying infrastructure.
- A deployed serverless application defined in CloudFormation.
- A strict `templates/` versus `deploy/` promotion gate.
- Separate IAM trust and permissions policies for Lambda and CloudFormation.

## Where Amazon Q Fits

The filename `templates/ai-generated-serverless-api.yaml` and the evidence trail suggest that Amazon Q Developer was part of the template-generation story. The repository then captures the engineering work needed to make that output operational:

- wiring S3 notifications,
- validating templates before deployment,
- restricting deployment to a dedicated prefix,
- adding a CloudFormation service role,
- and producing observable validation and deployment artifacts in S3.

## Repository Layout

- `templates/` contains the CloudFormation templates used for validation and promotion.
- `lambda/` contains the template-processing handlers.
- `infrastructure/` contains trust and permissions documents for the roles and S3 notifications.

## Core Outcome

The deployed application in `templates/ai-generated-serverless-api.yaml` is an API Gateway `POST /items` endpoint backed by Lambda and DynamoDB. The evidence records a successful HTTP `201` response and verification that the created item was written to DynamoDB.

## Documentation Map

- [Implementation](docs/implementation.md)
- [Security](docs/security.md)
- [Testing](docs/testing.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Cleanup](docs/cleanup.md)
- [Architecture](docs/architecture.md)
