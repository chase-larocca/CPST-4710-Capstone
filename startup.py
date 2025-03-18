import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Blueprint
from Python.Order_SP_Handler import order_blueprint  

app = Flask(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')

app.register_blueprint(order_blueprint)

# Connects to local MySQL database
def connect_to_mysql():
    try: 
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Dr3amC0ount3r$",
            database="TTOps"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None


# Home Page (starting page)
@app.route('/')
def home():
    return render_template('HomePage.html')

# Sign-In Page (Shows login form, clicking "Sign In" redirects to product page)
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for('product_page')) 
    
    return render_template('SignIn_Page.html')  

# Signup Page
'''@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Users WHERE username=%s OR email=%s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username or email already exists!", "error")
            else:
                cursor.execute("INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
                connection.commit()
                flash("Account created successfully!", "success")

            connection.close()

    return render_template('Account_Signup_Page.html')'''

# Product Page
@app.route('/product')
def product_page():
    return render_template('ProductPage.html')

# Cart Page
@app.route("/cart")
def cart():
    return render_template("Checkout_Cart_Page.html")

# Order Status Page
@app.route("/order-status")
def order_status():
    return render_template("OrderStatusPage.html")

@app.route('/account', methods=["GET", "POST"])
def account():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        new_password = request.form.get("new-password")
        confirm_password = request.form.get("confirm-password")

        if new_password and new_password != confirm_password:
            flash("The entered passwords do not match. Please try again.", "error")
            return redirect(url_for('account'))

        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()

            # Ensure username and email are unique (except for the current user)
            cursor.execute("SELECT * FROM Users WHERE (username=%s OR email=%s) AND id!=%s", 
                           (username, email, 1))  # Replace `1` with the session user ID
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username or email is already in use.", "error")
            else:
                update_query = "UPDATE Users SET username=%s, email=%s, password=%s WHERE id=%s"
                cursor.execute(update_query, (username, email, new_password, 1))  # Replace `1` with session user ID
                connection.commit()
                flash("Account updated successfully!", "success")

            connection.close()

    return render_template('Account_Change_Information_Page.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        print(request.form)  # Debugging: See what data is being received
        
        if "first_name" not in request.form:
            flash("First Name is missing!", "error")
            return redirect(url_for('signup'))

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT * FROM Users WHERE Email=%s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Email already exists!", "error")
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                cursor.execute("INSERT INTO Users (FirstName, LastName, Email, PasswordHash) VALUES (%s, %s, %s, %s)",
                               (first_name, last_name, email, hashed_password))
                connection.commit()
                flash("Account created successfully!", "success")
                return redirect(url_for('login'))

            connection.close()

    return render_template('Account_Signup_Page.html')


# Flask route to return inventory as JSON
@app.route("/api/products", methods=["GET"])
def get_inventory_items():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.callproc("sp_InventoryWithColors")
        results = []
        for result in cursor.stored_results():
            for row in result.fetchall():
                row['Colors'] = [row['ColorName']] if row['ColorName'] else []
                del row['ColorName']
                results.append(row)
        return jsonify(results)
    except Error as e:
        return jsonify({"error": "Failed to read inventory"}), 500
    finally:
        cursor.close()
        connection.close()

def get_orders():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.callproc("sp_GetOrderStatuses")
        orders = []
        for result in cursor.stored_results():
            orders = result.fetchall()
        return jsonify(orders)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)

