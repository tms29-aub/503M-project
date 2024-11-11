from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow

from secret_key import SECRET_KEY
from order.db_config import DB_CONFIG
from app import extract_auth_token, decode_token, jwt, datetime

from admin.models.admin import Admin
from models.order import Order, order_schema, orders_schema
from models.order_items import OrderItem, order_item_schema, order_items_schema
from models.returns import Return, return_schema, returns_schema

app = Flask(__name__)
ma = Marshmallow(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/orders', methods=['GET'])
def get_orders():
    '''
    Gets all orders in database. Must be an Admin

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

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")

    try:
        orders = Order.query.all()
        return jsonify({orders_schema.dump(orders)}), 200
    except:
        return abort(500, "Internal server error")
    
@app.route('/order-items', methods=['GET'])
def get_order_items():
    '''
    Get all items of an order. Must be an Admin.

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

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")  
    
    order_id = request.json['order_id']

    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            abort(404, 'Order not found')

        order_items = OrderItem.query.filter_by(order_id).all()

        return jsonify(order_items_schema.dump(order_items)), 200

    except:
        return abort(500, "Internal server error")
    

@app.route('/returns', methods=['GET'])
def get_returns():
    '''
    Get all returns. Must be an Admin.

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

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")  
    
    try:
        returns = Return.query.all()
        return jsonify({returns_schema.dump(returns)}), 200
    except:
        return abort(500, "Internal server error")
    

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


@app.route('/refund', methods=['POST'])
def refund():
    '''
    Refund an order. Must be an Admin.

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

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    order_id = request.json['order_id']

    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if order is None:
            return abort(404, "Order not found")
        
        order.status = "refunded"
        
        db.session.commit()
        
        return jsonify({order_schema.dump(order)}), 200
    except:
        return abort(500, "Internal server error")

@app.route('/cancel', methods=['POST'])
def cancel():
    '''
    Cancel an order. Must be an Admin.

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

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    order_id = request.json['order_id']

    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if order is None:
            return abort(404, "Order not found")
        
        order.status = "canceled"
        
        db.session.commit()
        
        return jsonify({order_schema.dump(order)}), 200
    except:
        return abort(500, "Internal server error")
    
@app.route('/replace', methods=['POST'])
def replace():
    '''
    Replace an order. Must be an Admin.

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

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    order_id = request.json['order_id']

    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if order is None:
            return abort(404, "Order not found")
        
        order.status = "replaced"

        ## PLACE NEW ORDER HERE
        
        db.session.commit()
        
        return jsonify({order_schema.dump(order)}), 200
    except:
        return abort(500, "Internal server error")
    


