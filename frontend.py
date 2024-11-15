from flask import Flask, render_template

app = Flask(__name__)

@app.route('/create-admin', methods=['GET'])
def admin_dashboard():
    return render_template('create_admin.html')

@app.route('/get-logs', methods=['GET'])
def get_logs():
    return render_template('get_logs.html')

@app.route('/get-customers', methods=['GET'])
def get_customers():
    return render_template('get_customers.html')


if __name__ == "__main__":
    app.run(port=5004)