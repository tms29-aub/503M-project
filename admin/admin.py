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


@app.route('/', methods=['GET'])
def get_admin_dashboard():
    pass


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
        return jsonify({
            'message': 'Unauthorized'
        }), 401

    required_fields = ['name', 'email', 'phone', 'password', 'inventory_management', 'order_management', 'product_management', 'customer_management', 'customer_support', 'logs', 'reports']
    # Check if all required fields are present
    if not all(field in request.json for field in required_fields):
        return jsonify({
            'message': 'Missing required fields'
        }), 400

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
        return jsonify({
            'message': 'Admin with email already exists'
        }), 409

    # Create new admin
    try:
        admin = Admin(name, email, phone, password)
        admin_role = AdminRole(admin.admin_id, customer_support, logs, product_management, order_management, customer_management, inventory_management, reports)

        db.session.add(admin)
        db.session.add(admin_role)
        db.session.commit()

        return jsonify({
            'message': 'Admin created successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'message': 'Internal server error'
        }), 500

