from flask import Flask, request, jsonify, abort
import requests

from app import extract_auth_token, decode_token, jwt, DB_PATH

app = Flask(__name__)

@app.route('/customers', methods=['GET'])
def get_customers():
    '''
    Get customers.
    Must be an Admin with customer_management role.

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
    response = requests.get(f"{DB_PATH}/admin/{admin_id}")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['customer_management'] == False:
        return abort(401, "Unauthorized")

    response = requests.get(f'{DB_PATH}/get_customers')
    customers = response.json()

    if response.status_code != 200:
        return abort(500, "Internal server error")

    response = requests.get(f'{DB_PATH}/get_supports')
    support = response.json()

    if response.status_code != 200:
        return abort(500, "Internal server error")

    response = requests.get(f'{DB_PATH}/get_wishlists')
    wishlist = response.json()

    if response.status_code != 200:
        return abort(500, "Internal server error")

    return jsonify({'customers': customers, 'support': support, 'wishlist': wishlist}), 200

if __name__ == "__main__":
    app.run(port=5003)