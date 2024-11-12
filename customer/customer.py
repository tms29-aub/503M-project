from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow

from admin.models.admin_role import AdminRole
from secret_key import SECRET_KEY
from customer.db_config import DB_CONFIG
from app import extract_auth_token, decode_token, jwt, datetime

app = Flask(__name__)
ma = Marshmallow(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from models.customer import Customer, customer_schema, customers_schema
from models.support import Support, support_schema, supports_schema
from models.wishlist import Wishlist, wishlist_schema, wishlists_schema
from admin.models.admin import Admin

@app.route('/customers', methods=['GET'])
def get_customers():
    '''
    Get customers.

    Requires:
        token (jwt)

    Returns:
        200: Customers retrieved successfully
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
    
    # Check admin role
    admin_role = AdminRole.query.filter_by(admin_id=admin_id).first()
    if admin_role.customer_management == False:
        return abort(401, "Unauthorized")

    try:
        customers = Customer.query.all()
        support = Support.query.all()
        wishlist = Wishlist.query.all()
        return jsonify({'customers': customers_schema.dump(customers), 'support': supports_schema.dump(support), 'wishlist': wishlists_schema.dump(wishlist)}), 200
    except:
        return abort(500, "Something went wrong")
