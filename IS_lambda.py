import boto3
import logging
import json
from customEncoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamoName = "IS-3150"
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamoName)

getMethod = "GET"
postMethod = "POST"

healthPath = "/health"
productPath = "/product"
productsPath = "/products"

#main handler
def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']

    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event['body']))
    elif httpMethod == getMethod and path == productsPath:
        response = getProducts()
    else:
        response = buildResponse(404, 'Not Found')
    
    return response


# Gets all items from the product table in DynamoDB
def getProducts():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey = response['LastEvaluatedKey'])
            result.extend(response['Items'])

        body = {
            'products': result
        }

        return buildResponse(200, body)
    except:
        logger.exception("Exception logged.")

# posts a product into dynamoDB
def saveProduct(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)
    except:
        logger.exception("Exception logged.")

# Response builder.
def buildResponse(statusCode, body = None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls = CustomEncoder)
    return response


