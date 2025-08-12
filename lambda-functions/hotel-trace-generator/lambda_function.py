import json
import boto3
import os
import random
import uuid
import datetime
import re
import hashlib
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch all supported libraries for X-Ray
patch_all()

# Input validation patterns
VALID_MODE_PATTERN = re.compile(r'^(search|booking|both)$')

def sanitize_string(value, max_length=100):
    """Sanitize string input to prevent injection attacks"""
    if not isinstance(value, str):
        return str(value)[:max_length]
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', value)
    return sanitized[:max_length]

def generate_synthetic_id(prefix=""):
    """Generate clearly synthetic identifiers"""
    return f"SYNTHETIC_{prefix}_{uuid.uuid4().hex[:8].upper()}"

def hash_sensitive_data(data):
    """Hash sensitive data for tracing without exposing real values"""
    return hashlib.sha256(str(data).encode()).hexdigest()[:16]

# Configuration
NUM_ACCOUNTS = 5
NUM_USERS = 100
NUM_HOTELS = 50
NUM_CITIES = 20

# Generate AWS account IDs
AWS_ACCOUNTS = [f"{random.randint(100000000000, 999999999999)}" for _ in range(NUM_ACCOUNTS)]

# Generate AWS regions
AWS_REGIONS = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "eu-west-1", 
               "eu-central-1", "ap-northeast-1", "ap-southeast-1", "ap-southeast-2"]

# Generate marketing channels
MARKETING_CHANNELS = [
    "direct", "google_search", "google_ads", "bing_ads", "facebook", 
    "instagram", "twitter", "email_campaign", "affiliate", "booking.com"
]

# Generate payment methods
PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Apple Pay", "Google Pay"]

# Generate error types
ERROR_TYPES = ["ConnectionError", "TimeoutError", "AuthenticationError", "ValidationError", 
              "ServiceUnavailable", "ResourceNotFound", "ThrottlingError", "PermissionDenied"]

# Generate cities
CITIES = [fake.city() for _ in range(NUM_CITIES)]

# Generate synthetic users (clearly marked as test data)
def generate_users(num_users):
    loyalty_levels = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]
    users = []
    
    for i in range(num_users):
        user_id = generate_synthetic_id("USER")
        # Use clearly synthetic data
        name = f"TestUser_{i:06d}"
        email = f"testuser{i:06d}@example-synthetic.com"
        loyalty_level = random.choice(loyalty_levels)
        
        users.append({
            "id": user_id,
            "name": name,
            "email": email,
            "loyalty_level": loyalty_level,
            "registration_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "last_login": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return users

# Generate synthetic hotels (clearly marked as test data)
def generate_hotels(num_hotels, cities):
    hotel_types = ["Resort", "Hotel", "Motel", "Inn", "B&B"]
    
    hotels = []
    
    for i in range(num_hotels):
        hotel_id = generate_synthetic_id("HOTEL")
        city = random.choice(cities)
        hotel_type = random.choice(hotel_types)
        stars = random.randint(1, 5)
        price = stars * random.uniform(30, 60)
        
        # Use clearly synthetic names
        name = f"TestHotel_{hotel_type}_{i:06d}"
        
        hotels.append({
            "id": hotel_id,
            "name": name,
            "stars": stars,
            "price": price,
            "location": city,
            "chain": "SYNTHETIC_CHAIN"
        })
    
    return hotels

# Generate users and hotels
USERS = generate_users(NUM_USERS)
HOTELS = generate_hotels(NUM_HOTELS, CITIES)

def simulate_search_flow(user, city):
    """Simulate a hotel search flow using X-Ray subsegments."""
    # Create search date and check-in/check-out dates
    search_date = datetime.datetime.now()
    check_in = (search_date + datetime.timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
    check_out = (search_date + datetime.timedelta(days=random.randint(31, 60))).strftime("%Y-%m-%d")
    
    guests = random.randint(1, 6)
    rooms = random.randint(1, 3)
    
    # Add marketing channel data
    marketing_channel = random.choice(MARKETING_CHANNELS)
    device_type = random.choice(["desktop", "mobile", "tablet"])
    campaign_id = f"camp-{uuid.uuid4().hex[:8]}"
    
    # Begin API Gateway subsegment - instead of creating a segment
    api_gateway_subsegment = xray_recorder.begin_subsegment('API Gateway - Hotel Search')
    
    # Add annotations to API Gateway subsegment
    xray_recorder.put_annotation('user_id', user["id"])
    xray_recorder.put_annotation('city', city)
    xray_recorder.put_annotation('check_in', check_in)
    xray_recorder.put_annotation('check_out', check_out)
    xray_recorder.put_annotation('guests', guests)
    xray_recorder.put_annotation('rooms', rooms)
    xray_recorder.put_annotation('marketing_channel', marketing_channel)
    xray_recorder.put_annotation('device_type', device_type)
    
    # Add metadata to API Gateway subsegment
    xray_recorder.put_metadata('request', {
        'url': f"https://api.hotelbooking.example.com/search",
        'method': 'GET',
        'user_agent': fake.user_agent(),
        'client_ip': fake.ipv4()
    })
    
    try:
        # Begin Lambda subsegment
        lambda_subsegment = xray_recorder.begin_subsegment('Lambda - Search Service')
        xray_recorder.put_annotation('function_name', 'hotel-search-service')
        
        # Processing time simulation removed for production
        
        # Begin user authentication subsegment
        auth_subsegment = xray_recorder.begin_subsegment('UserAuthentication')
        xray_recorder.put_annotation('user_id', user["id"])
        xray_recorder.put_annotation('loyalty_level', user["loyalty_level"])
        xray_recorder.put_metadata('user', {
            'id': user["id"],
            'name': user["name"],
            'email': user["email"],
            'loyalty_level': user["loyalty_level"]
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # Begin DynamoDB user profile query subsegment
        dynamo_user_subsegment = xray_recorder.begin_subsegment('DynamoDB - User Profiles')
        xray_recorder.put_annotation('table', 'user-profiles')
        xray_recorder.put_metadata('dynamodb', {
            'table_name': 'user-profiles',
            'operation': 'GetItem',
            'request_items': {
                'user-profiles': {
                    'Keys': [{"user_id": user["id"]}]
                }
            }
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # Begin DynamoDB hotel inventory query subsegment
        dynamo_hotel_subsegment = xray_recorder.begin_subsegment('DynamoDB - Hotel Inventory')
        xray_recorder.put_annotation('table', 'hotel-inventory')
        xray_recorder.put_annotation('city', city)
        xray_recorder.put_metadata('dynamodb', {
            'table_name': 'hotel-inventory',
            'operation': 'Query',
            'request_items': {
                'hotel-inventory': {
                    'KeyConditionExpression': 'city = :city',
                    'ExpressionAttributeValues': {
                        ':city': city
                    }
                }
            }
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # Filter results subsegment
        filter_subsegment = xray_recorder.begin_subsegment('FilterResults')
        
        # Get random hotels for this city
        city_hotels = [h for h in HOTELS if h["location"] == city]
        if not city_hotels:  # Fallback if no hotels match the city
            city_hotels = random.sample(HOTELS, min(5, len(HOTELS)))
        
        available_hotels = random.sample(city_hotels, min(random.randint(1, 5), len(city_hotels)))
        xray_recorder.put_annotation('results_count', len(available_hotels))
        xray_recorder.put_metadata('search', {
            'criteria': {
                'city': city,
                'check_in': check_in,
                'check_out': check_out,
                'guests': guests,
                'rooms': rooms
            },
            'results_count': len(available_hotels)
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # S3 image retrieval subsegment
        s3_subsegment = xray_recorder.begin_subsegment('S3 - Hotel Images')
        xray_recorder.put_annotation('operation', 'GetObject')
        xray_recorder.put_metadata('s3', {
            'operation': 'GetObject',
            'bucket_name': 'hotel-images',
            'key_count': len(available_hotels)
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # Randomly add errors (10% chance)
        if random.random() < 0.1:
            error_type = random.choice(ERROR_TYPES)
            error_message = f"An error occurred: {error_type}"
            
            # Create an exception
            exception = Exception(error_message)
            
            # Record the exception in the current subsegment
            xray_recorder.add_exception(
                exception,
                remote=False,
                stack=None,
                skip_frames=0
            )
            
            # End the Lambda subsegment with error
            xray_recorder.end_subsegment()
            
            # End the API Gateway subsegment with error
            xray_recorder.end_subsegment()
            
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': error_message,
                    'success': False
                })
            }
        
        # End Lambda subsegment
        xray_recorder.end_subsegment()
        
        # Add result metadata to API Gateway subsegment
        xray_recorder.put_metadata('search_results', {
            'city': city,
            'check_in': check_in,
            'check_out': check_out,
            'guests': guests,
            'rooms': rooms,
            'hotels_found': len(available_hotels),
            'marketing_channel': marketing_channel,
            'device_type': device_type,
            'campaign_id': campaign_id
        })
        
        # End the API Gateway subsegment
        xray_recorder.end_subsegment()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'hotels': [h["name"] for h in available_hotels],
                'count': len(available_hotels),
                'success': True
            })
        }
        
    except Exception as e:
        # Handle any unexpected exceptions
        xray_recorder.add_exception(e)
        
        # Make sure to end all subsegments
        if xray_recorder.current_subsegment():
            xray_recorder.end_subsegment()
            
        # End the API Gateway subsegment if still active
        if xray_recorder.current_subsegment():
            xray_recorder.end_subsegment()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'success': False
            })
        }

def simulate_booking_flow(user, hotel):
    """Simulate a hotel booking flow using X-Ray subsegments."""
    # Create booking date and check-in/check-out dates
    booking_date = datetime.datetime.now()
    check_in = (booking_date + datetime.timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
    check_out = (booking_date + datetime.timedelta(days=random.randint(31, 60))).strftime("%Y-%m-%d")
    
    guests = random.randint(1, 6)
    rooms = random.randint(1, 3)
    
    # Add marketing channel data
    marketing_channel = random.choice(MARKETING_CHANNELS)
    device_type = random.choice(["desktop", "mobile", "tablet"])
    campaign_id = f"camp-{uuid.uuid4().hex[:8]}"
    
    # Begin API Gateway subsegment - instead of creating a segment
    api_gateway_subsegment = xray_recorder.begin_subsegment('API Gateway - Hotel Booking')
    
    # Add annotations to API Gateway subsegment
    xray_recorder.put_annotation('user_id', user["id"])
    xray_recorder.put_annotation('hotel_id', hotel["id"])
    xray_recorder.put_annotation('hotel_name', hotel["name"])
    xray_recorder.put_annotation('check_in', check_in)
    xray_recorder.put_annotation('check_out', check_out)
    xray_recorder.put_annotation('guests', guests)
    xray_recorder.put_annotation('rooms', rooms)
    xray_recorder.put_annotation('marketing_channel', marketing_channel)
    xray_recorder.put_annotation('device_type', device_type)
    
    # Add metadata to API Gateway subsegment
    xray_recorder.put_metadata('request', {
        'url': f"https://api.hotelbooking.example.com/booking",
        'method': 'POST',
        'user_agent': fake.user_agent(),
        'client_ip': fake.ipv4()
    })
    
    try:
        # Begin Lambda Reservation subsegment
        reservation_subsegment = xray_recorder.begin_subsegment('Lambda - Reservation Service')
        xray_recorder.put_annotation('function_name', 'hotel-reservation-service')
        
        # Processing time simulation removed for production
        
        # Check room availability subsegment
        room_check_subsegment = xray_recorder.begin_subsegment('CheckRoomAvailability')
        xray_recorder.put_annotation('hotel_id', hotel["id"])
        xray_recorder.put_annotation('hotel_name', hotel["name"])
        xray_recorder.put_annotation('check_in', check_in)
        xray_recorder.put_annotation('check_out', check_out)
        xray_recorder.put_annotation('rooms', rooms)
        xray_recorder.put_metadata('availability', {
            'hotel': hotel,
            'available': True,
            'room_types': ["Standard", "Deluxe", "Suite"]
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # DynamoDB query for room availability
        dynamo_room_subsegment = xray_recorder.begin_subsegment('DynamoDB - Hotel Inventory')
        xray_recorder.put_annotation('table', 'hotel-inventory')
        xray_recorder.put_annotation('operation', 'Query')
        xray_recorder.put_metadata('dynamodb', {
            'table_name': 'hotel-inventory',
            'operation': 'Query',
            'request_items': {
                'hotel-inventory': {
                    'KeyConditionExpression': 'hotel_id = :hotel_id',
                    'ExpressionAttributeValues': {
                        ':hotel_id': hotel["id"]
                    }
                }
            }
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # Process payment subsegment
        payment_subsegment = xray_recorder.begin_subsegment('ProcessPayment')
        payment_method = random.choice(PAYMENT_METHODS)
        
        # Calculate price
        stay_duration = (datetime.datetime.strptime(check_out, "%Y-%m-%d") - 
                         datetime.datetime.strptime(check_in, "%Y-%m-%d")).days
        total_price = hotel["price"] * rooms * stay_duration
        
        xray_recorder.put_annotation('payment_method', payment_method)
        xray_recorder.put_annotation('amount', total_price)
        xray_recorder.put_annotation('currency', 'USD')
        xray_recorder.put_metadata('payment', {
            'method': payment_method,
            'amount': total_price,
            'currency': 'USD',
            'success': True,
            'transaction_id': f"TXN-{uuid.uuid4()}"
        })
        # Processing delay removed
        
        # Lambda payment processor subsegment
        lambda_payment_subsegment = xray_recorder.begin_subsegment('Lambda - Payment Service')
        xray_recorder.put_annotation('function', 'payment-processing-service')
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        xray_recorder.end_subsegment()  # End payment subsegment
        
        # Create reservation subsegment
        reserve_create_subsegment = xray_recorder.begin_subsegment('CreateReservation')
        confirmation_number = f"RES-{uuid.uuid4().hex[:8].upper()}"
        xray_recorder.put_annotation('confirmation_number', confirmation_number)
        xray_recorder.put_annotation('hotel_id', hotel["id"])
        xray_recorder.put_annotation('user_id', user["id"])
        xray_recorder.put_metadata('reservation', {
            'confirmation_number': confirmation_number,
            'hotel': hotel,
            'user': user,
            'check_in': check_in,
            'check_out': check_out,
            'guests': guests,
            'rooms': rooms,
            'total_price': total_price,
            'marketing_data': {
                'channel': marketing_channel,
                'campaign_id': campaign_id,
                'device_type': device_type
            }
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # DynamoDB put reservation
        dynamo_res_subsegment = xray_recorder.begin_subsegment('DynamoDB - Reservations')
        xray_recorder.put_annotation('table', 'reservations')
        xray_recorder.put_annotation('operation', 'PutItem')
        xray_recorder.put_metadata('dynamodb', {
            'table_name': 'reservations',
            'operation': 'PutItem',
            'item': {
                'reservation_id': confirmation_number,
                'user_id': user["id"],
                'hotel_id': hotel["id"],
                'check_in': check_in,
                'check_out': check_out,
                'status': 'CONFIRMED',
                'marketing_channel': marketing_channel
            }
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # SNS notification subsegment
        sns_subsegment = xray_recorder.begin_subsegment('SNS - Notification')
        xray_recorder.put_annotation('topic', 'reservation-events')
        xray_recorder.put_metadata('sns', {
            'topic_name': 'reservation-events',
            'message': {
                'event_type': 'RESERVATION_CREATED',
                'reservation_id': confirmation_number,
                'user_id': user["id"],
                'hotel_id': hotel["id"]
            }
        })
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        # Send confirmation email subsegment
        email_subsegment = xray_recorder.begin_subsegment('SendEmail')
        xray_recorder.put_annotation('email_type', 'booking_confirmation')
        xray_recorder.put_annotation('recipient', user["email"])
        xray_recorder.put_metadata('email', {
            'type': 'booking_confirmation',
            'recipient': user["email"],
            'subject': f"Your Booking Confirmation #{confirmation_number}",
            'sent': True
        })
        # Processing delay removed
        
        # Lambda notification service subsegment
        lambda_notify_subsegment = xray_recorder.begin_subsegment('Lambda - Notification Service')
        xray_recorder.put_annotation('function', 'notification-service')
        # Processing delay removed
        xray_recorder.end_subsegment()
        
        xray_recorder.end_subsegment()  # End email subsegment
        
        # Randomly add errors (5% chance)
        if random.random() < 0.05:
            error_type = random.choice(ERROR_TYPES)
            error_message = f"An error occurred: {error_type}"
            
            # Create an exception
            exception = Exception(error_message)
            
            # Record the exception in the current subsegment
            xray_recorder.add_exception(
                exception,
                remote=False,
                stack=None,
                skip_frames=0
            )
            
            # End the Lambda subsegment with error
            xray_recorder.end_subsegment()
            
            # End the API Gateway subsegment with error
            xray_recorder.end_subsegment()
            
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': error_message,
                    'success': False
                })
            }
        
        # End Lambda subsegment
        xray_recorder.end_subsegment()
        
        # Add result metadata to API Gateway subsegment
        xray_recorder.put_metadata('booking_result', {
            'success': True,
            'confirmation_number': confirmation_number,
            'hotel': hotel["name"],
            'check_in': check_in,
            'check_out': check_out,
            'total_price': total_price,
            'marketing_channel': marketing_channel
        })
        
        # End the API Gateway subsegment
        xray_recorder.end_subsegment()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'confirmation_number': confirmation_number,
                'hotel_name': hotel["name"],
                'check_in': check_in,
                'check_out': check_out,
                'total_price': total_price,
                'success': True
            })
        }
        
    except Exception as e:
        # Handle any unexpected exceptions
        xray_recorder.add_exception(e)
        
        # Make sure to end all subsegments
        if xray_recorder.current_subsegment():
            xray_recorder.end_subsegment()
            
        # End the API Gateway subsegment if still active
        if xray_recorder.current_subsegment():
            xray_recorder.end_subsegment()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'success': False
            })
        }

def lambda_handler(event, context):
    """
    Secure Lambda handler function to generate X-Ray traces for hotel search and booking.
    
    Parameters:
    - event: Can contain 'mode' parameter ('search', 'booking', or 'both')
    - context: Lambda context
    
    Returns:
    - Response with status code and trace information
    """
    try:
        # Input validation
        if not isinstance(event, dict):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid request format',
                    'success': False
                })
            }
        
        # Get and validate the mode parameter
        mode = event.get('mode', 'both')
        mode = sanitize_string(mode, 20)
        
        if not VALID_MODE_PATTERN.match(mode):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid mode parameter. Must be: search, booking, or both',
                    'success': False
                })
            }
        
        # Select a random user and city
        user = random.choice(USERS)
        city = random.choice(CITIES)
        
        # Select a random hotel (for booking)
        hotel = random.choice(HOTELS)
        
        results = {}
        
        if mode == 'search' or mode == 'both':
            # Simulate search flow
            search_result = simulate_search_flow(user, city)
            results['search'] = search_result
        
        if mode == 'booking' or mode == 'both':
            # Simulate booking flow
            booking_result = simulate_booking_flow(user, hotel)
            results['booking'] = booking_result
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            },
            'body': json.dumps(results)
        }
        
    except ValueError as e:
        # Handle validation errors
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid input data',
                'success': False
            })
        }
    except Exception as e:
        # Log error for monitoring (without exposing details to client)
        print(f"Internal error: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'success': False
            })
        }