from flask import Flask, render_template, request, abort
import requests
from app import extract_auth_token, decode_token, jwt, DB_PATH

app = Flask(__name__)

@app.route('/')
def home():
    '''
    Render the homepage or redirect to the logs page.
    '''
    return render_template('login.html')

@app.route('/logs', methods=['GET'])
def logs_page():
    '''
    Render the logs page.
    Requires:
        token (JWT)
    Returns:
        200: Logs page rendered
        403: Invalid or expired token
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Token missing or invalid")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Invalid or expired token")
    
    # Verify role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code != 200:
        abort(403, "Unauthorized")
    
    admin_role = response.json()
    if not admin_role.get('logs', False):
        abort(403, "Unauthorized")
    
    return render_template('logs.html')

@app.route('/orders', methods=['GET'])
def orders_page():
    '''
    Render the orders management page.
    Requires:
        token (JWT)
    Returns:
        200: Orders page rendered
        403: Invalid or expired token
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Token missing or invalid")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Invalid or expired token")
    
    # Verify role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code != 200:
        abort(403, "Unauthorized")
    
    admin_role = response.json()
    if not admin_role.get('order_management', False):
        abort(403, "Unauthorized")
    
    return render_template('orders.html')

@app.route('/products', methods=['GET'])
def products_page():
    '''
    Render the products management page.
    Requires:
        token (JWT)
    Returns:
        200: Products page rendered
        403: Invalid or expired token
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Token missing or invalid")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Invalid or expired token")
    
    # Verify role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code != 200:
        abort(403, "Unauthorized")
    
    admin_role = response.json()
    if not admin_role.get('product_management', False):
        abort(403, "Unauthorized")
    
    return render_template('products.html')

@app.route('/reports', methods=['GET'])
def reports_page():
    '''
    Render the reports management page.
    Requires:
        token (JWT)
    Returns:
        200: Reports page rendered
        403: Invalid or expired token
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Token missing or invalid")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Invalid or expired token")
    
    # Verify role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code != 200:
        abort(403, "Unauthorized")
    
    admin_role = response.json()
    if not admin_role.get('reports', False):
        abort(403, "Unauthorized")
    
    return render_template('reports.html')

@app.route('/create_admin', methods=['GET'])
def create_admin_page():
    '''
    Render the create admin page.
    Requires:
        token (JWT)
    Returns:
        200: Create Admin page rendered
        403: Invalid or expired token
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Token missing or invalid")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Invalid or expired token")
    
    # Verify role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code != 200:
        abort(403, "Unauthorized")
    
    admin_role = response.json()
    if not admin_role.get('admin_management', False):
        abort(403, "Unauthorized")
    
    return render_template('create_admin.html')

@app.route('/get_customer', methods=['GET'])
def get_customer_page():
    '''
    Render the get customer page.
    Requires:
        token (JWT)
    Returns:
        200: Get Customer page rendered
        403: Invalid or expired token
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Token missing or invalid")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Invalid or expired token")
    
    # Verify role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code != 200:
        abort(403, "Unauthorized")
    
    admin_role = response.json()
    if not admin_role.get('customer_management', False):
        abort(403, "Unauthorized")
    
    return render_template('get_customer.html')

if __name__ == '__main__':
    app.run(debug=True, port=5004)
