import key_config as keys
import boto3
from boto3.dynamodb.conditions import Key


# DynamoDB client object - client API
dynamodb_client = boto3.client(
    'dynamodb',
    aws_access_key_id=keys.ACCESS_KEY_ID,
    aws_secret_access_key=keys.ACCESS_SECRET_KEY,
    region_name=keys.REGION_NAME
)

# Get the service resource - DynamoDB resrouce object
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id = keys.ACCESS_KEY_ID,
    aws_secret_access_key = keys.ACCESS_SECRET_KEY,
    region_name = keys.REGION_NAME
)


# Create the DynamoDB table
def create_table_student():
    table = dynamodb.create_table(
        TableName='students',
        KeySchema=[
            {
                'AttributeName': 'registration_number',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'email',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'registration_number',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'email',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table


# Getting the dynamodb table
table_students = dynamodb.Table('students')


# Update student account details
def update_student_account_details(regno, email, firstname, lastname, degprogramme, password, contactno, gpa, gender, intro, skills):
    
    print(f'Updating student account details for regno: {regno}')
    
    try:
        response = table_students.update_item(
            Key={
                'registration_number': regno,
                'email': email
            },
            UpdateExpression="set first_name=:fn, last_name=:ln, degree_programme=:dp, password=:pw, contact_number=:cn, gpa=:gpa, gender=:gender, introduction=:intro, skills=:skills",
            ExpressionAttributeValues={
                ':fn': firstname,
                ':ln': lastname,
                ':dp': degprogramme,
                ':pw': password,
                ':cn': contactno,
                ':gpa': gpa,
                ':gender': gender,
                ':intro': intro,
                ':skills': skills
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f'Update response: {response}')
    except Exception as e:
        print(f'Error updating student account details: {e}')
    return response



