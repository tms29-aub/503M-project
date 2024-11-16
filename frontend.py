from flask import Flask, render_template, request, abort, make_response, redirect, url_for
import requests
from app import extract_auth_token, decode_token, jwt, DB_PATH, ADMIN_PATH
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        response = requests.post(f"{ADMIN_PATH}/admin-login", json={"email": request.get('email'), "password": request.get('password')})
        if response.status_code == 200:
            token = jwt.encode({'id': response.json()['id'], 'exp': datetime.datetime.now()+datetime.timedelta(days=1)}, app.config['SECRET_KEY'])
            resp = make_response(redirect(url_for('logs_page')))
            resp.set_cookie('jwt', token)
            return resp
    return render_template('login.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('jwt', '', expires=0)
    return resp

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
