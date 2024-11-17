from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import requests
from secret_key import SECRET_KEY
from app import extract_auth_token, decode_token, jwt, datetime, DB_PATH

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/orders', methods=['GET'])
def get_orders():
    '''
    Gets all orders in database.
    Must be an admin with order_management role 

    Requires:
        token (jwt)

    Returns:
        200: Orders retrieved successfully
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
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
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['order_management'] == False:
        return abort(401, "Unauthorized")

    response = requests.get(f"{DB_PATH}/orders")
    if response.status_code == 500:
        return abort(500, "Internal server error")

    return response.json(), 200

@app.route('/order-items', methods=['GET'])
def get_order_items():
    '''
    Get all items of an order. 
    Must be an Admin with order_management role

    Requires:
        token (jwt)
        order_id (int)

    Returns:
        200: Order items retrieved successfully
        401: Unauthorized
        403: Invalid or expired token
        404: Order not found
        500: Internal server error
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
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['order_management'] == False:
        return abort(401, "Unauthorized")
    
    response = requests.get(f"{DB_PATH}/order-items")
    if response.status_code == 500:
        return abort(500, "Internal server error")

    return response.json(), 200
    
    

@app.route('/returns', methods=['GET'])
def get_returns():
    '''
    Get all returns. 
    Must be an Admin with order_management or inventory_management role

    Requires:
        token (jwt)

    Returns:
        200: Returns retrieved successfully
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
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
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['order_management'] == False or admin_role['inventory_management'] == False:
        return abort(401, "Unauthorized")
    
    response = requests.get(f"{DB_PATH}/returns")
    if response.status_code == 500:
        return abort(500, "Internal server error")

    return response.json(), 200
    

@app.route('/invoice', methods=['POST'])
def create_invoice():
    '''
    Create an invoice. Must be an Admin.

    Requires:
        token (jwt)

    Returns:
        200: Invoice created successfully
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
    '''
    pass


@app.route('/refund/<int:order_id>', methods=['POST'])
def refund(order_id):
    '''
    Refund an order. 
    Must be an Admin with order_management or inventory_management role

    Requires:
        token (jwt)
        order_id (int)

    Returns:
        200: Refund created successfully
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
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
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['order_management'] == False or admin_role['inventory_management'] == False:
        return abort(401, "Unauthorized")

    if type(order_id) != int:
        return abort(400, "Invalid order_id")
    
    response = requests.post(f"{DB_PATH}/refund/{order_id}")

    if response.status_code == 500:
        return abort(500, "Internal server error")
    elif response.status_code == 404:
        return abort(404, "Order not found")
    
    return response.json(), 200

@app.route('/cancel/<int:order_id>', methods=['POST'])
def cancel(order_id):
    '''
    Cancel an order. 
    Must be an Admin with order_management role

    Requires:
        token (jwt)
        order_id (int)

    Returns:
        200: Order canceled successfully
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
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
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['order_management'] == False:
        return abort(401, "Unauthorized")

    if type(order_id) != int:
        return abort(400, "Invalid order_id")
    
    response = requests.post(f"{DB_PATH}/cancel-order/{order_id}")
    if response.status_code == 500:
        return abort(500, "Internal server error")
    elif response.status_code == 404:
        return abort(404, "Order not found")
    
    return response.json(), 200
    
@app.route('/replace/<int:order_id>', methods=['POST'])
def replace(order_id):
    '''
    Replace an order. 
    Must be an Admin with order_management role

    Requires:
        token (jwt)
        order_id (int)

    Returns:
        200: Order replaced successfully
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
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
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['order_management'] == False:
        return abort(401, "Unauthorized")

    if type(order_id) != int:
        return abort(400, "Invalid order_id")

    response = requests.post(f"{DB_PATH}/replace-order/{order_id}")
    if response.status_code == 500:
        return abort(500, "Internal server error")
    elif response.status_code == 404:
        return abort(404, "Order not found")
    
    return response.json(), 200
    

if __name__ == "__main__":
    app.run(port=5002, debug=True)
