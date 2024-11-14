from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
import requests

from secret_key import SECRET_KEY
from admin.db_config import DB_CONFIG
from app import extract_auth_token, decode_token, jwt, datetime

from admin.models.admin import Admin
from admin.models.admin_role import AdminRole

app = Flask(__name__)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models.log import Log, log_schema, logs_schema
from admin import Admin, admin_schema, admins_schema


@app.route('/create-admin', methods=['POST'])
def create_admin():
    '''
    Create new admin. Only admins can create other admins.

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
        
    response = requests.get(f"http://127.0.0.1:5001/admin/{admin_id}")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    response = requests.get(f"http://127.0.0.1:5001/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['admin_management'] == False:
        return abort(401, "Unauthorized")
    
    

    # # Check if admin exists
    # admin = Admin.query.filter_by(admin_id=admin_id).first()
    # if admin is None:
    #     return abort(401, "Unauthorized")
    
    # # Check admin role
    # admin_role = AdminRole.query.filter_by(admin_id=admin_id).first()
    # if admin_role.admin_management == False:
    #     return abort(401, "Unauthorized")

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

    # Check if admin with email already exists
    response = requests.get(f"127.0.0.1:5001/admin/email/{email}")
    if response.status_code == 200:
        return abort(409, "Admin with email already exists")
    
    # if Admin.query.filter_by(email=email).first() is not None:
    #     return abort(409, "Admin with email already exists")

    # Create new admin
    try:
        response = requests.post('http://127.0.0.1:5001/add/admin', json={'name': name, 'email': email, 'phone': phone, 'password': password})
        # admin = Admin(name, email, phone, password)
        if response.status_code != 201:
            return abort(500, "Something went wrong")
        
        admin_id = response.get('id')
        response = requests.post('http://127.0.0.1:5001/add-admin-role', json={
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

        # admin_role = AdminRole(admin_id, customer_support, logs, product_management, order_management, customer_management, inventory_management, reports)

        # db.session.add(admin)
        # db.session.add(admin_role)
        # db.session.commit()

        return {'message': "Admin created successfully"}, 201

    except Exception as e:
        return abort(500, "Something went wrong")

@app.route('/logs', methods=['GET'])
def get_logs():
    '''
    Get logs.

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

    # Check if admin exists
    response = requests.get(f"http://127.0.0.1:5001/admin/{admin_id}")
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if response.status_code != 200:
        return abort(401, "Unauthorized")
    
    # Check admin role
    response = requests.get(f"http://127.0.0.1:5001/admin/{admin_id}/role")
    if response.status_code != 200:
        return abort(500, "Something went wrong")
    # admin_role = AdminRole.query.filter_by(admin_id=admin_id).first()
    if response.json()['logs'] == False:
        return abort(401, "Unauthorized")
    
    response = request.get('http://127.0.0.1:5001/get_logs')
    if response.status_code != 200:
        return abort(500, "Something went wrong")
    return response.json()
    
    # try:
    #     logs = Log.query.all()
    #     return jsonify({logs_schema.dump(logs)}), 200
    # except:
    #     return abort(500, "Something went wrong")





