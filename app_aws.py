import boto3
from botocore.exceptions import ClientError
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
import os

# ===============================
# AWS Configuration
# ===============================
AWS_REGION = "us-east-1"
USERS_TABLE = "quickfix_users"
SERVICES_TABLE = "quickfix_services"

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

users_table = dynamodb.Table(USERS_TABLE)
services_table = dynamodb.Table(SERVICES_TABLE)

# ===============================
# Utility
# ===============================
def deserialize_item(item):
    if not item:
        return None
    return {
        k: float(v) if isinstance(v, Decimal) else v
        for k, v in item.items()
    }

# ===============================
# USER FUNCTIONS
# ===============================
def get_user_by_username(username):
    """
    MOCK user for offline testing
    """
    if username == "test":
        return {
            "username": "test",
            "password": generate_password_hash("123456"),
            "role": "customer"
        }

    try:
        response = users_table.get_item(
            Key={"username": username}
        )
        return deserialize_item(response.get("Item"))

    except ClientError as e:
        print("DynamoDB Error:", e.response["Error"]["Message"])
        return None


def create_user(username, password, role):
    try:
        users_table.put_item(
            Item={
                "username": username,
                "password": generate_password_hash(password),
                "role": role
            }
        )
        return True
    except ClientError as e:
        print(e)
        return False


def validate_login(username, password):
    user = get_user_by_username(username)
    if not user:
        return False

    return check_password_hash(user["password"], password)

# ===============================
# SERVICE FUNCTIONS
# ===============================
def get_all_services():
    try:
        response = services_table.scan()
        return [deserialize_item(item) for item in response.get("Items", [])]
    except ClientError as e:
        print(e)
        return []


def get_services_by_category(category):
    try:
        response = services_table.scan(
            FilterExpression="category = :c",
            ExpressionAttributeValues={":c": category}
        )
        return [deserialize_item(i) for i in response.get("Items", [])]
    except ClientError as e:
        print(e)
        return []


def add_service(service_id, name, category, price, provider):
    try:
        services_table.put_item(
            Item={
                "service_id": service_id,
                "name": name,
                "category": category,
                "price": Decimal(str(price)),
                "provider": provider
            }
        )
        return True
    except ClientError as e:
        print(e)
        return False
