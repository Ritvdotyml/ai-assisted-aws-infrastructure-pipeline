import json
import boto3
import logging
import re
import os
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
cloudformation = boto3.client("cloudformation")


def make_stack_name(key):
    filename = key.rsplit("/", 1)[-1]
    name = filename.rsplit(".", 1)[0]

    name = re.sub(r"[^a-zA-Z0-9-]", "-", name)

    if not name[0].isalpha():
        name = "stack-" + name

    return name[:128]


def lambda_handler(event, context):

    logger.info("Received event: %s", json.dumps(event))

    for record in event["Records"]:

        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        logger.info("Processing s3://%s/%s", bucket, key)

        try:
            response = s3.get_object(
                Bucket=bucket,
                Key=key
            )

            template_body = response["Body"].read().decode("utf-8")

            # Always validate first
            validation = cloudformation.validate_template(
                TemplateBody=template_body
            )

            logger.info("Template validation successful")

            result = {
                "template_file": key,
                "validation_status": "VALID",
                "description": validation.get("Description", ""),
                "parameters": validation.get("Parameters", []),
                "capabilities": validation.get("Capabilities", [])
            }

            filename = key.rsplit("/", 1)[-1]
            result_name = filename.rsplit(".", 1)[0]

            # Deploy only files explicitly placed under deploy/
            if key.startswith("deploy/"):

                stack_name = make_stack_name(key)

                logger.info(
                    "Deployment authorized for stack: %s",
                    stack_name
                )

                stack = cloudformation.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    RoleARN=os.environ["CFN_ROLE_ARN"],
                    Capabilities=[
                        "CAPABILITY_IAM",
                        "CAPABILITY_NAMED_IAM"
                    ],
                    Tags=[
                        {
                            "Key": "Project",
                            "Value": "AIInfrastructureCodeGeneration"
                        }
                    ]
                )
                result["deployment_status"] = "CREATE_IN_PROGRESS"
                result["stack_name"] = stack_name
                result["stack_id"] = stack["StackId"]

                result_key = (
                    f"deployment-results/"
                    f"{result_name}-deployment.json"
                )

            else:

                result["deployment_status"] = "NOT_REQUESTED"

                result_key = (
                    f"validation-results/"
                    f"{result_name}-validation.json"
                )

            s3.put_object(
                Bucket=bucket,
                Key=result_key,
                Body=json.dumps(result, indent=2, default=str),
                ContentType="application/json"
            )

            logger.info(
                "Result written to s3://%s/%s",
                bucket,
                result_key
            )

        except Exception as error:

            logger.exception("Processing failed")

            filename = key.rsplit("/", 1)[-1]
            result_name = filename.rsplit(".", 1)[0]

            if key.startswith("deploy/"):
                result_key = (
                    f"deployment-results/"
                    f"{result_name}-error.json"
                )
            else:
                result_key = (
                    f"validation-results/"
                    f"{result_name}-error.json"
                )

            error_result = {
                "template_file": key,
                "status": "FAILED",
                "error": str(error)
            }

            s3.put_object(
                Bucket=bucket,
                Key=result_key,
                Body=json.dumps(error_result, indent=2),
                ContentType="application/json"
            )

    return {
        "statusCode": 200,
        "body": "Template processing complete"
    }
