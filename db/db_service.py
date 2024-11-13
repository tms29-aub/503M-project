from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DB_FILE = 'ecommerce.db'

# Helper function to interact with the database
def execute_query(query, args=(), fetchone=False, fetchall=False, commit=False):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # To return results as dictionaries
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(query, args)
        if fetchone:
            result = dict(cursor.fetchone()) if cursor.fetchone() else None
        elif fetchall:
            result = [dict(row) for row in cursor.fetchall()]
        if commit:
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()
    return result


# Admin Routes
@app.route('/admin', methods=['GET', 'POST'])
def manage_admin():
    if request.method == 'GET':
        admins = execute_query("SELECT * FROM Admin", fetchall=True)
        return jsonify(admins)
    elif request.method == 'POST':
        data = request.json
        query = """
        INSERT INTO Admin (name, phone, email, hashed_password)
        VALUES (?, ?, ?, ?)
        """
        args = (data.get('name'), data.get('phone'), data.get('email'), data.get('hashed_password'))
        execute_query(query, args, commit=True)
        return jsonify({'message': 'Admin created successfully'}), 201


# Customer Routes
@app.route('/customers', methods=['GET', 'POST'])
def manage_customers():
    if request.method == 'GET':
        customers = execute_query("SELECT * FROM Customer", fetchall=True)
        return jsonify(customers)
    elif request.method == 'POST':
        data = request.json
        query = """
        INSERT INTO Customer (name, email, phone, address, tier)
        VALUES (?, ?, ?, ?, ?)
        """
        args = (data.get('name'), data.get('email'), data.get('phone'), data.get('address'), data.get('tier'))
        execute_query(query, args, commit=True)
        return jsonify({'message': 'Customer created successfully'}), 201


# Product Routes
@app.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'GET':
        products = execute_query("SELECT * FROM Product", fetchall=True)
        return jsonify(products)
    elif request.method == 'POST':
        data = request.json
        query = """
        INSERT INTO Product (category_id, name, description, subcategory, price, quantity_in_stock, reorder_level, image, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        args = (
            data.get('category_id'), data.get('name'), data.get('description'),
            data.get('subcategory'), data.get('price'), data.get('quantity_in_stock'),
            data.get('reorder_level'), data.get('image'), data.get('created_at'), data.get('updated_at')
        )
        execute_query(query, args, commit=True)
        return jsonify({'message': 'Product created successfully'}), 201


# Orders Routes
@app.route('/orders', methods=['GET', 'POST'])
def manage_orders():
    if request.method == 'GET':
        orders = execute_query("SELECT * FROM 'Order'", fetchall=True)
        return jsonify(orders)
    elif request.method == 'POST':
        data = request.json
        query = """
        INSERT INTO 'Order' (customer_id, status, total_amount, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """
        args = (
            data.get('customer_id'), data.get('status'), data.get('total_amount'),
            data.get('created_at'), data.get('updated_at')
        )
        execute_query(query, args, commit=True)
        return jsonify({'message': 'Order created successfully'}), 201


# Logs Routes
@app.route('/logs', methods=['GET', 'POST'])
def manage_logs():
    if request.method == 'GET':
        logs = execute_query("SELECT * FROM Log", fetchall=True)
        return jsonify(logs)
    elif request.method == 'POST':
        data = request.json
        query = """
        INSERT INTO Log (admin_id, details, action, timestamp)
        VALUES (?, ?, ?, ?)
        """
        args = (data.get('admin_id'), data.get('details'), data.get('action'), data.get('timestamp'))
        execute_query(query, args, commit=True)
        return jsonify({'message': 'Log created successfully'}), 201


# Support Ticket Routes
@app.route('/support', methods=['GET', 'POST'])
def manage_support_tickets():
    if request.method == 'GET':
        tickets = execute_query("SELECT * FROM Support", fetchall=True)
        return jsonify(tickets)
    elif request.method == 'POST':
        data = request.json
        query = """
        INSERT INTO Support (customer_id, issue_description, status, created_at, resolved_at)
        VALUES (?, ?, ?, ?, ?)
        """
        args = (
            data.get('customer_id'), data.get('issue_description'),
            data.get('status'), data.get('created_at'), data.get('resolved_at')
        )
        execute_query(query, args, commit=True)
        return jsonify({'message': 'Support ticket created successfully'}), 201


# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
