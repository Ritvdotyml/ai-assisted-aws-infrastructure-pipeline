import json
import boto3
import logging
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
cloudformation = boto3.client("cloudformation")


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

            validation = cloudformation.validate_template(
                TemplateBody=template_body
            )

            result = {
                "template_file": key,
                "validation_status": "VALID",
                "description": validation.get("Description", ""),
                "parameters": validation.get("Parameters", []),
                "capabilities": validation.get("Capabilities", [])
            }

            result_name = key.rsplit("/", 1)[-1]
            result_name = result_name.rsplit(".", 1)[0]

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
                "Template validated successfully. Result: s3://%s/%s",
                bucket,
                result_key
            )

        except Exception as error:

            logger.exception("Template validation failed")

            result_name = key.rsplit("/", 1)[-1]
            result_name = result_name.rsplit(".", 1)[0]

            result_key = (
                f"validation-results/"
                f"{result_name}-error.json"
            )

            error_result = {
                "template_file": key,
                "validation_status": "INVALID",
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