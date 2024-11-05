from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt

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

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
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

    # Check if admin with email already exists
    if Admin.query.filter_by(email=email).first() is not None:
        return abort(409, "Admin with email already exists")

    # Create new admin
    try:
        admin = Admin(name, email, phone, password)
        admin_role = AdminRole(admin.admin_id, customer_support, logs, product_management, order_management, customer_management, inventory_management, reports)

        db.session.add(admin)
        db.session.add(admin_role)
        db.session.commit()

        return jsonify(admin_schema.dump(admin)), 201

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
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    try:
        logs = Log.query.all()
        return jsonify({logs_schema.dump(logs)}), 200
    except:
        return abort(500, "Something went wrong")





