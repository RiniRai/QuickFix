import boto3
from botocore.exceptions import ClientError
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal

# ===============================
# AWS MODE DETECTION
# ===============================
AWS_ENABLED = False

try:
    boto3.client("sts").get_caller_identity()
    AWS_ENABLED = True
    print("✅ AWS credentials detected — running in AWS MODE")
except Exception:
    print("⚠️ AWS credentials not found — running in LOCAL MODE")

# ===============================
# CONFIG
# ===============================
AWS_REGION = "us-east-1"
USERS_TABLE = "quickfix_users"
SERVICES_TABLE = "quickfix_services"
BOOKINGS_TABLE = "quickfix_bookings"

# ===============================
# AWS RESOURCES (ONLY IF ENABLED)
# ===============================
if AWS_ENABLED:
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    users_table = dynamodb.Table(USERS_TABLE)
    services_table = dynamodb.Table(SERVICES_TABLE)
    bookings_table = dynamodb.Table(BOOKINGS_TABLE)

# ===============================
# LOCAL MOCK DATABASE
# ===============================
LOCAL_USERS = {}
LOCAL_SERVICES = []
LOCAL_BOOKINGS = []

# ===============================
# USER FUNCTIONS
# ===============================
def get_user_by_username(username):
    """Fetch user (AWS or LOCAL)"""
    if not AWS_ENABLED:
        return LOCAL_USERS.get(username)

    try:
        response = users_table.get_item(Key={"username": username})
        return response.get("Item")
    except ClientError as e:
        print("DynamoDB Error:", e)
        return None


def create_user(username, password, user_type):
    """Create user (AWS or LOCAL)"""
    if not AWS_ENABLED:
        LOCAL_USERS[username] = {
            "username": username,
            "password": generate_password_hash(password),
            "user_type": user_type
        }
        print(f"LOCAL MODE: User created → {username}, {user_type}")
        return True

    try:
        users_table.put_item(
            Item={
                "username": username,
                "password": generate_password_hash(password),
                "user_type": user_type
            },
            ConditionExpression="attribute_not_exists(username)"
        )
        return True
    except ClientError as e:
        print("AWS ERROR:", e)
        return False


def validate_login(username, password):
    """Validate login credentials"""
    user = get_user_by_username(username)
    if not user:
        return False
    return check_password_hash(user["password"], password)

# ===============================
# SERVICE FUNCTIONS
# ===============================
def get_all_services():
    """Fetch all services"""
    if not AWS_ENABLED:
        return LOCAL_SERVICES

    try:
        response = services_table.scan()
        return response.get("Items", [])
    except ClientError as e:
        print("AWS ERROR:", e)
        return []


def add_service(service_id, name, category, price, provider):
    """Add a service"""
    if not AWS_ENABLED:
        LOCAL_SERVICES.append({
            "service_id": service_id,
            "name": name,
            "category": category,
            "price": price,
            "provider": provider
        })
        print("LOCAL MODE: Service added")
        return True

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
        print("AWS ERROR:", e)
        return False

def create_booking(username, provider_id, date, time, notes):
    if not AWS_ENABLED:
        LOCAL_BOOKINGS.append({...})
        return True
    try:
        bookings_table.put_item(
            Item={
                "booking_id": f"{username}_{provider_id}_{date}_{time}",
                "username": username,
                "provider_id": provider_id,
                "date": date,
                "time": time,
                "notes": notes
            }
        )
        return True
    except ClientError as e:
        print("BOOKING ERROR:", e)
        return False





def get_bookings_by_user(username):
    if not AWS_ENABLED:
        return [b for b in LOCAL_BOOKINGS if b["username"] == username]
    try:
        response = bookings_table.scan()
        return [b for b in response.get("Items", []) if b["username"] == username]
    except ClientError as e:
        print("BOOKING FETCH ERROR:", e)
        return []




# ===============================
# NOTIFICATION FUNCTION
# ===============================
def send_notification(message):
    """
    Send notification via AWS SNS (if enabled)
    Otherwise print locally
    """
    if not AWS_ENABLED:
        print(f"📢 LOCAL NOTIFICATION: {message}")
        return True

    try:
        sns = boto3.client("sns", region_name=AWS_REGION)

        response = sns.publish(
            TopicArn="arn:aws:sns:us-east-1:123456789012:QuickFixNotifications",
            Message=message,
            Subject="QuickFix Alert"
        )

        return True

    except ClientError as e:
        print("SNS ERROR:", e)
        return False
