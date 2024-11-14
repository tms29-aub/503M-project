from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import requests

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
    response = requests.get(f"http://127.0.0.1:5001/admin/{admin_id}")
    if response.code == 404:
        return abort(404, "Admin not found")
    # admin = Admin.query.filter_by(admin_id=admin_id).first()
    # if admin is None:
    #     return abort(401, "Unauthorized")
    
    # Check admin role
    response = requests.get(f"http://127.0.0.1:5001/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['customer_management'] == False:
        return abort(401, "Unauthorized")
    # admin_role = AdminRole.query.filter_by(admin_id=admin_id).first()
    # if admin_role.customer_management == False:
    #     return abort(401, "Unauthorized")

    try:
        response = requests.get('http://127.0.0.1:5001/get_customers')
        customers = response.json()
        # customers = Customer.query.all()
        response = requests.get('http://127.0.0.1:5001/get_supports')
        support = response.json()
        # support = Support.query.all()
        response = requests.get('http://127.0.0.1:5001/get_wishlists')
        wishlist = response.json()
        # wishlist = Wishlist.query.all()
        return jsonify({'customers': customers, 'support': support, 'wishlist': wishlist}), 200
    except:
        return abort(500, "Something went wrong")
