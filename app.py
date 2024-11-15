from secret_key import SECRET_KEY

import jwt
import datetime

DB_PATH = "http://localhost:3000"
ADMIN_PATH = "http://localhost:5000"
INVENTORY_PATH = "http://localhost:5001"
ORDER_PATH = "http://localhost:5002"
CUSTOMER_PATH = "http://localhost:5003"
FRONTEND_PATH = "http://localhost:5004"

def extract_auth_token(authenticated_request):
    '''
    Extract Authentication Token.
    '''
    return authenticated_request.cookies.get('jwt')


def decode_token(token):
    '''
    Decode Authentication Token.
    '''
    payload = jwt.decode(token, SECRET_KEY, 'HS256')
    return payload['id']

def create_token(user_id):
    """
    Create a user token.

    Requires:
        user id (int)

    Returns:
        JWT Token
    """
    
    payload = {
        'iat': datetime.datetime.utcnow(),
        'id': user_id
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    )
