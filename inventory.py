from flask import Flask, jsonify, request, abort, flash, redirect, url_for
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename
import pandas as pd
import magic
import os
import re

from secret_key import SECRET_KEY
from app import extract_auth_token, decode_token, jwt, DB_PATH

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
ALLOWED_EXTENSIONS = {'csv'}


@app.route('/reports', methods=['GET'])
def get_reports():
    '''
    Get reports.
    Must be an Admin with reports role

    Requires:
        token (jwt)

    Returns:
        200: Reports retrieved successfully
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
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['reports'] == False:
        return abort(401, "Unauthorized")
    
    response = requests.get(f'{DB_PATH}/reports')
    reports = response.json()

    if response.status_code != 200:
        return abort(500, "Something went wrong")
    
    return reports, 200
    

@app.route('/update-inventory', methods=['POST'])
def update_inventory():
    '''
    Update inventory.
    Must be an admin with inventory_management role

    Requires:
        token (jwt)
        product_id (int)
        quantity (int)

    Returns:
        200: Inventory updated successfully
        401: Unauthorized
        403: Invalid or expired token
        404: Product not found
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
    if admin_role['inventory_management'] == False:
        return abort(401, "Unauthorized")
    
    required_fields = ['product_id', 'quantity']
    # Check if all required fields are present
    if not all(field in request.json for field in required_fields):
        return abort(400, "Bad request")
    
    product_id = request.json['product_id']
    quantity = request.json['quantity']

    if type(product_id) != int or type(quantity) != int:
        return abort(400, "Bad request")

    response = requests.get(f"{DB_PATH}/product/{product_id}")
    if response.status_code == 404:
        return abort(404, "Product not found")
    
    product = response.json()
    product['quantity'] += quantity

    response = requests.post(f"{DB_PATH}/product/{product_id}", json=product)
    if response.status_code == 500:
        return abort(500, "Something went wrong")
    
    return response.json(), 200


@app.before_request
def log_request():
    print(f"Request: {request.method} {request.path}")

@app.route('/update-product/<int:product_id>', methods=['POST', 'OPTIONS'])
def update_product(product_id):
    '''
    Update product.
    Must be an admin with product_management role

    Requires:
        token (jwt)
        product_id (int)
        name (str) - optional
        quantity (int) - optional
        price (float) - optional
        description (str) - optional
        category_id (int) - optional
        promotion_id (int) - optional
        image (str) - optional
        subcategory (str) - optional

    Returns:
        200: Inventory updated successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
    '''
    if request.method == 'OPTIONS':
        # Dynamically set CORS headers
        origin = request.headers.get('Origin')
        response = jsonify({'message': 'Preflight OK'})
        if origin == "http://localhost:5004":
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    # Extract token
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
    if not admin_role.get('product_management', False):
        return abort(401, "Unauthorized")

    # Optional fields
    data = {"request":request.json, "admin_id":admin_id}

    # Validate fields
    if not isinstance(product_id, int):
        return abort(400, "Bad request")

    response = requests.post(f"{DB_PATH}/product/{product_id}", json=data)
    if response.status_code == 500:
        return abort(500, "Something went wrong")

    return response.json(), 200


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    '''
    Delete product by product_id.
    Must be an admin with product_management role

    Requires:
        token (jwt)
        product_id (int)

    Returns:
        200: Product deleted successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        404: Product not found
        500: Internal server error
    '''
    print(request.headers)
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
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")

    if type(product_id) != int:
        return abort(400, "Bad request")

    # Check if product exists
    response = requests.get(f"{DB_PATH}/product/{product_id}")
    if response.status_code == 404:
        return abort(404, "Product not found")

    # Delete product
    response = requests.delete(f"{DB_PATH}/product/{product_id}", json={'admin_id': admin_id})
    if response.status_code == 500:
        return abort(500, "Something went wrong")
    
    return response.json(), 200
    

@app.route('/promote', methods=['POST'])
def promote_product():
    '''
    Promote product.
    Must be an admin with product_management role

    Requires:
        token (jwt)
        product_id (int)
        promotion_type (str)
        promotion_value (float)
        user_tier (str)
        name (str)

    Returns:
        200: Product promoted successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        404: Product not found
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
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['product_id', 'promotion_type', 'promotion_value', 'user_tier', 'name']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    product_id = request.json['product_id']
    promotion_type = request.json['promotion_type']
    promotion_value = request.json['promotion_value']
    user_tier = request.json['user_tier']
    name = request.json['name']

    if type(product_id) != int or type(promotion_type) != str or type(promotion_value) != float or type(user_tier) != str or type(name) != str:
        return abort(400, "Invalid data type")
    
    response = requests.post(f"{DB_PATH}/promote/{product_id}", json=request.json)
    if response.status_code == 500:
        return abort(500, "Something went wrong")
    elif response.status_code == 404:
        return abort(404, "Product not found")
    
    return response.json(), 200


@app.route('/add-product', methods=['POST'])
def add_product():
    '''
    Add product.
    Must be an admin with product_management role

    Requires:
        token (jwt)
        name (str)
        quantity (int)
        price (float)
        description (str)
        category_id (int)
        image (str)
        subcategory (str)


    Returns:
        200: Product added successfully
        400: Bad request
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
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['name', 'quantity', 'price', 'description', 'category_id']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    # Add product
    response = requests.post(f"{DB_PATH}/add-product", json={"request": request.json, "admin_id": admin_id})
    if response.status_code == 500:
        return abort(500, "Something went wrong")
    
    return response.json(), 200


@app.route('/add-category', methods=['POST'])
def add_category():
    '''
    Add category.
    Must be an admin with product_management role

    Requires:
        token (jwt)
        name (str)
        description (str)

    Returns:
        200: Category added successfully
        400: Bad request
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
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    name = request.json['name']
    description = request.json['description']

    if type(name) != str or type(description) != str:
        return abort(400, "Invalid data type")
        
    # Add category
    response = requests.post(f"{DB_PATH}/add-category", json=request.json)
    if response.status_code == 500:
        return abort(500, "Something went wrong")
    
    elif response.status_code == 400:
        return abort(400, "Category already exists")
    
    return response.json(), 200
    

@app.route('/delete-category', methods=['POST'])
def delete_category():
    '''
    Delete category.
    Must be an admin with product_management role

    Requires:
        token (jwt)
        category_id (int)

    Returns:
        200: Category deleted successfully
        400: Bad request
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
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['category_id']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    category_id = request.json['category_id']

    if type(category_id) != int:
        return abort(400, "Invalid data type")
        
    response = requests.post(f"{DB_PATH}/delete-category", json=request.json)
    if response.status_code == 500:
        return abort(500, "Something went wrong")
    
    elif response.status_code == 404:
        return abort(404, "Category not found")
    
    return response.json(), 200


@app.route('/delete-promotion', methods=['POST'])
def delete_promotion():
    '''
    Delete promotion.

    Requires:
        token (jwt)
        promotion_id (int)

    Returns:
        200: Promotion deleted successfully
        400: Bad request
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
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    promotion_id = request.json['promotion_id']

    if type(promotion_id) != int:
        return abort(400, "Invalid promotion_id")
    
    response = requests.delete(f"{DB_PATH}/promote/{promotion_id}", json=request.json)
    if response.status_code == 500:
        return abort(500, "Something went wrong")
    elif response.status_code == 404:
        return abort(404, "Promotion not found")
    
    return response.json(), 200


def allowed_file_type(file_path):
    # Use magic to determine the file type
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_file(file_path)
    return file_mime_type in ['text/csv', 'application/vnd.ms-excel']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_csv(filepath):
    '''
    Process a CSV file and return a list of Product instances.
    '''
    # Load the CSV file into a DataFrame
    df = pd.read_csv(filepath)
    
    # Convert 'created_at' and 'updated_at' to datetime objects
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    
    # Create a list to store Product objects
    products = []
    
    # Iterate over the DataFrame rows and create Product instances
    for _, row in df.iterrows():
        product = {
            "product_id": row["product_id"],
            "category_id": row["category_id"],
            "name": row["name"],
            "description": row["description"],
            "subcategory": row["subcategory"],
            "price": row["price"],
            "quantity_in_stock": row["quantity_in_stock"],
            "reorder_level": row["reorder_level"],
            "image": row["image"] if pd.notna(row["image"]) else None,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
        products.append(product)
    
    return products


@app.route('/add-products-csv', methods=["POST"])
def add_products_csv():
    '''
    Add products from CSV.

    Requires:
        token (jwt)
        file (csv)

    Returns:
        200: Products added successfully
        400: Bad request
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
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    # admin_role = AdminRole.query.filter_by(admin_id=admin_id).first()
    # if admin_role.product_management == False:
    #     return abort(401, "Unauthorized")
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    #Save the file if extention is allowed
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print("entered secure file name\n")
        print(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filename)  # Save the file
            print('File successfully saved')
        except Exception as e:
            flash(f'Error saving file: {e}')
            print(f'Error: {e}')
        
        
        
        # Check the file type using magic
        if not allowed_file_type(filename):
            os.remove(filename)
            print('Invalid file type.')
            return redirect(request.url)
        
        # Process the CSV file
        products = process_csv(file_path)
        for p in products:
            response = requests.post(f'{DB_PATH}/add-product', json=p)
            if response.status_code != 200:
                return abort(500, "Something went wrong")
        flash('Products added successfully.')
        return redirect(url_for('get_products'))
    else:
        flash('Invalid file extension.')
        return redirect(request.url)
    

def is_valid_url(url):
    allowed_domains = ["example.com", "trusted.com"]
    pattern = re.compile(r"^(http|https)://")
    
    # Check URL starts with HTTP/HTTPS
    if not pattern.match(url):
        return False

    # Check domain is in whitelist
    domain = url.split('/')[2]
    return any(domain.endswith(allowed_domain) for allowed_domain in allowed_domains)

    
@app.route('/add-products-thirdparty', methods=['POST'])
def add_products_thirdparty():
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    response = requests.get(f"{DB_PATH}/admin/{admin_id}")
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    try:
        # Parse the incoming JSON payload
        data = request.json
        link = data.get('link')
        
        if not link:
            return {'message': 'No link provided'}, 400

        if not is_valid_url(link) or "localhost" in link or "127.0.0.1" in link:
            return {'message': 'No hacking today'}, 400
        
        # Fetch the product data from the link
        response = requests.get(link)

        if response.status_code != 200:
            return {'message': f'Failed to fetch data from the link. Status code: {response.status_code}'}, 400
        
        # Parse the fetched data
        products = response.json()
        
        # Check if products is a list
        if not isinstance(products, list):
            return {'message': 'Invalid data format. Expected a list of products.'}, 400


        # Loop through each product and add to inventory
        for product_data in products:
            product = {
                "product_id": product_data["product_id"],
                "category_id": product_data["category_id"],
                "name": product_data["name"],
                "description": product_data["description"],
                "subcategory": product_data["subcategory"],
                "price": product_data["price"],
                "quantity_in_stock": product_data["quantity_in_stock"],
                "reorder_level": product_data["reorder_level"],
                "image": product_data["image"] if pd.notna(product_data["image"]) else None,
                "created_at": product_data["created_at"],
                "updated_at": product_data["updated_at"]
            }
            response = requests.post(f'{DB_PATH}/add-product', json=product)
            if response.status_code != 200:
                return abort(500, "Something went wrong")

        # Commit all changes to the database

        return {'message': 'Products added successfully'}, 201

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500

@app.route('/generate-inventory-reports', methods=['POST'])
def generate_inventory_reports():
    '''
    Generate inventory reports for turnover rate, most popular products, and demand forecast.
    Requires admin with reports role.

    Returns:
        200: Inventory report generated successfully.
        401: Unauthorized
        403: Invalid Token
        500: Internal server error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Invalid token")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Invalid or expired token")
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.status_code != 200 or not response.json():
        return abort(403, "Unauthorized")
    
    admin_role = response.json()
    if not admin_role.get('reports', False):
        return abort(401, "Unauthorized")
    
    response = requests.post(f"{DB_PATH}/generate-inventory-reports")
    if response.status_code != 200:
        return abort(500, "Something went wrong")
    
    return response.json(), 200


if __name__ == "__main__":
    app.run(port=5001, debug=True)