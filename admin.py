from flask import Flask, request, abort
from flask_cors import CORS
import requests

from secret_key import SECRET_KEY
from app import create_token, extract_auth_token, decode_token, jwt, DB_PATH 

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/admin-login', methods=['POST'])
def admin_login():
    email = request.json['email']
    password = request.json['password']
    response = requests.post(f"{DB_PATH}/admin/authenticate", json={'email': email, 'password': password})

    if response.status_code != 200:
        return abort(401, "Unauthorized")
    return response


@app.route('/create-admin', methods=['POST'])
def create_admin():
    '''
    Create new admin.
    Must be Admin with admin_management role

    Requires:
        token (jwt)
        name (str)
        email (str)
        phone (int)
        password (str)
        inventory_management (bool)
        order_management (bool)
        product_management (bool)
        customer_management (bool)
        customer_support (bool)
        logs (bool)
        reports (bool)

    Returns:
        201: Admin created successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        409: Admin with email already exists
        500: Internal server error
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")
        
    response = requests.get(f"{DB_PATH}/admin/{admin_id}")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['admin_management'] == False:
        return abort(401, "Unauthorized")

    required_fields = ['name', 'email', 'phone', 'password', 'inventory_management', 'order_management', 'product_management', 'customer_management', 'customer_support', 'logs', 'reports']
    # Check if all required fields are present
    if not all(field in request.json for field in required_fields):
        return abort(400, "Bad request")

    # Required Fields
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    password = request.json['password']
    inventory_management = request.json['inventory_management']
    order_management = request.json['order_management']
    product_management = request.json['product_management']
    customer_management = request.json['customer_management']
    customer_support = request.json['customer_support']
    logs = request.json['logs']
    reports = request.json['reports']

    if type(name) != str or type(email) != str or type(phone) != int or type(password) != str:
        return abort(400, "Bad request")
    
    if type(inventory_management) != bool or type(order_management) != bool or type(product_management) != bool or type(customer_management) != bool or type(customer_support) != bool or type(logs) != bool or type(reports) != bool:
        return abort(400, "Bad request")

    # Check if admin with email already exists
    response = requests.get(f"{DB_PATH}/admin/email/{email}")
    if response.status_code == 200:
        return abort(409, "Admin with email already exists")

    # Create new admin
    try:
        response = requests.post(f'{DB_PATH}/add/admin', json={'name': name, 'email': email, 'phone': phone, 'password': password})

        if response.status_code != 201:
            return abort(500, "Something went wrong")
        
        admin_id = response.get('id')
        response = requests.post(f'{DB_PATH}/add-admin-role', json={
            "admin_id": admin_id,
            "customer_support": customer_support,
            "logs": logs,
            "product_management": product_management,
            "order_management": order_management,
            "customer_management": customer_management,
            "inventory_management": inventory_management,
            "reports": reports
        })
        
        if response.status_code != 201:
            return abort(500, "Something went wrong")

        return {'message': "Admin created successfully"}, 201

    except Exception as e:
        return abort(500, "Something went wrong")


@app.route('/logs', methods=['POST'])
def get_logs():
    '''
    Get logs.
    Must be Admin with logs role

    Requires:
        token (jwt)

    Returns:
        200: Logs retrieved successfully
        401: Unauthorized
        403: Invalid or expired token
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code != 200:
        return abort(500, "Something went wrong")

    if response.json()['logs'] == False:
        return abort(401, "Unauthorized")
    
    response = requests.get(f'{DB_PATH}/get_logs')
    if response.status_code != 200:
        return abort(500, "Something went wrong")
    
    return response.json(), 200
    

@app.route('/login', methods=['POST'])
def login():
    '''
    Login as Admin.

    Requires:
        email (str)
        password (str)

    Returns:
        200: JWT Token
        401: Unauthorized
        500: Internal server error
    '''
    required_fields = ['email', 'password']
    # Check if all required fields are present
    if not all(field in request.json for field in required_fields):
        return abort(400, "Bad request")

    email = request.json['email']
    password = request.json['password']

    if type(email) != str or type(password) != str:
        return abort(400, "Bad request")

    response = requests.get(f"{DB_PATH}/admin/email/{email}")
    if response.status_code != 200:
        return abort(401, "Unauthorized")

    response = requests.post(f"{DB_PATH}/admin/authenticate", json={"email": email, "password": password})
    if response.status_code != 200:
        return abort(401, "Unauthorized")

    admin = response.json()
    token = create_token(admin['admin_id'])

    return {'token': token}, 200

if __name__ == "__main__":
    app.run(port=5000)