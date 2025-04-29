import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Blueprint
from Python.Order_SP_Handler import order_blueprint  
import re

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'a4f3e86de5f241f6b9112f882eecf1a3'

app.register_blueprint(order_blueprint)

# Function for passwordc validation 
def is_valid_password(password):
    return (
        len(password) >= 7 and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password) and
        re.search(r"\d", password)
    )

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

# Sign-In Page 
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('username')
        password = request.form.get('password')
        login_type = request.form.get('login_type')

        connection = connect_to_mysql()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Users WHERE Email=%s", (email,))
                user = cursor.fetchone()

                if user and user['PasswordHash'] == password:
                    session['user_id'] = user['UserID']
                    role = user['Role']

                    # Check if customer exists
                    customer_conn = connect_to_mysql()
                    if customer_conn:
                        customer_cursor = customer_conn.cursor()
                        customer_cursor.execute(
                            "SELECT CustomerID FROM Customers WHERE CustomerID = %s", (user['UserID'],)
                        )
                        existing_customer = customer_cursor.fetchone()

                        if not existing_customer:
                            # Insert new customer into Customers table
                            # Assuming Email like: john.doe@example.com -> FirstName = John, LastName = Doe
                            email_parts = user['Email'].split('@')[0].split('.')
                            first_name = email_parts[0].capitalize() if len(email_parts) > 0 else "First"
                            last_name = email_parts[1].capitalize() if len(email_parts) > 1 else "Last"

                            customer_cursor.execute(
                                """
                                INSERT INTO Customers (CustomerID, FirstName, LastName, Email)
                                VALUES (%s, %s, %s, %s)
                                """,
                                (user['UserID'], first_name, last_name, user['Email'])
                            )
                            customer_conn.commit()

                        customer_cursor.close()
                        customer_conn.close()

                    if login_type == "customer" and role in ["Customer", "Employee"]:
                        return redirect(url_for('product_page'))
                    elif login_type == "inventory" and role == "Employee":
                        return redirect(url_for('inventory'))
                    else:
                        flash("Access Denied: incorrect role", "error")
                else:
                    flash("Invalid login credentials", "error")

            except Error as e:
                print("Login error:", e)
                flash("Login failed.", "error")
            finally:
                cursor.close()
                connection.close()
    return render_template('SignIn_Page.html')

# Signup Page
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not all([first_name, last_name, email, password, confirm_password]):
            return render_template("Account_Signup_Page.html", error="Please fill out all fields.")

        if password != confirm_password:
            return render_template("Account_Signup_Page.html", error="Passwords do not match.")
        if not is_valid_password(password):
            return render_template("Account_Signup_Page.html", error="Password must be at least 7 characters long, include a number and a special character.")
        connection = connect_to_mysql()
        if not connection:
            return render_template("Account_Signup_Page.html", error="Database connection failed.")

        try:
            cursor = connection.cursor()
            # Check if email is already taken
            cursor.execute("SELECT * FROM Users WHERE Email=%s", (email,))
            if cursor.fetchone():
                return render_template("Account_Signup_Page.html", error="Email already registered.")

            # Insert new user
            cursor.callproc("sp_Users_CreateOrUpdate", (
                None,  
                first_name,
                last_name,
                email,
                password,  
                "Customer"
            ))
            connection.commit()
            return redirect(url_for("login"))
        except Error as e:
            import traceback
            traceback.print_exc()
            return render_template("Account_Signup_Page.html", error=f"Signup failed: {str(e)}")
        finally:
            cursor.close()
            connection.close()
    else:
        return render_template("Account_Signup_Page.html")

@app.route('/inventory')
def inventory():
    return render_template('InventoryManagementPage.html')

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
    if 'user_id' not in session:
        flash("You must be logged in to view orders.", "error")
        return redirect(url_for('login'))
    
    return render_template('OrderStatusPage.html')

@app.route("/api/submit-order", methods=["POST"])
def submit_order():
    data = request.get_json()
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        customer_id = session.get('user_id')
        total_price = data.get("total", 0.00)
        order_items = data.get('items', [])
        shipping_address = data.get('shippingAddress', 'None')
        number_of_items = data.get('NumberOfItems', 0)

        # ✅ Step 1: Check inventory levels
        for item in order_items:
            sku = item.get('sku')
            quantity_ordered = item.get('quantity', 0)

            cursor.execute("SELECT QuantityInStock FROM Inventory WHERE SKU = %s", (sku,))
            result = cursor.fetchone()

            if not result or result["QuantityInStock"] < quantity_ordered:
                return jsonify({
                    "success": False,
                    "error": f"Not enough stock for SKU: {sku}. Available: {result['QuantityInStock'] if result else 0}"
                }), 400

        # ✅ Step 2: Insert into Orders
        insert_query = """
            INSERT INTO Orders (CustomerID, ShippingDestination, NumberOfItems, TotalPrice, OrderStatus)
            VALUES (%s, %s, %s, %s, 'Pending')
        """
        cursor.execute(insert_query, (customer_id, shipping_address, number_of_items, total_price))
        connection.commit()

        order_id = cursor.lastrowid

        # ✅ Step 3: Insert each item into OrderItems
        for item in order_items:
            sku = item.get('sku')
            name = item.get('name')
            quantity = item.get('quantity', 1)
            price = item.get('price')

            cursor.execute("""
                INSERT INTO OrderItems (OrderID, SKU, ProductName, Quantity, Price)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, sku, name, quantity, price))

            # ✅ Step 4: Reduce inventory
            cursor.execute("""
                UPDATE Inventory
                SET QuantityInStock = QuantityInStock - %s
                WHERE SKU = %s
            """, (quantity, sku))

        connection.commit()

        return jsonify({"success": True, "orderNumber": order_id})

    except Exception as e:
        print("Order submission error:", e)
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()

@app.route("/api/order/<int:order_id>/items", methods=["GET"])
def get_order_items(order_id):
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT ProductName, Quantity, Price
            FROM OrderItems
            WHERE OrderID = %s
        """
        cursor.execute(query, (order_id,))
        items = cursor.fetchall()
        return jsonify(items)
    except Error as e:
        print("Order items retrieval error:", e)
        return jsonify({"error": "Failed to fetch order items"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route("/api/inventory/add", methods=["POST"])
def add_inventory_item():
    data = request.get_json()
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "DB connection failed"}), 500

    try:
        cursor = connection.cursor()
        cursor.callproc("sp_AddInventoryItem", [
            data["SKU"],
            data["ItemName"],
            data["ItemDescription"],
            data["Supplier"],
            data["Price"],
            data["QuantityInStock"],
            data["RestockThreshold"]
        ])
        connection.commit()
        return jsonify({"message": "Item added successfully!"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route("/api/inventory/update", methods=["POST"])
def update_inventory():
    data = request.get_json()
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "DB connection failed"}), 500
    try:
        cursor = connection.cursor()
        cursor.callproc("sp_Inventory_CreateOrUpdate", (
            data["SKU"], data["ItemName"], data["ItemDescription"],
            data["Price"], data["QuantityInStock"],
            data["Supplier"], data["RestockThreshold"]
        ))
        connection.commit()
        return jsonify({"message": "Update successful"})
    except Error as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/order-management')
def order_management():
    return render_template('OrderManagementPage.html')

@app.route('/api/admin/orders')
def get_all_orders_for_admin():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT o.OrderID, o.ShippingDestination, o.NumberOfItems, o.TotalPrice, o.OrderStatus,
                   c.FirstName, c.LastName
            FROM Orders o
            JOIN Customers c ON o.CustomerID = c.CustomerID
            ORDER BY o.OrderDate DESC
        """
        cursor.execute(query)
        orders = cursor.fetchall()
        return jsonify(orders)
    except Error as e:
        print("Admin Order retrieval error:", e)
        return jsonify({"error": "Failed to fetch orders"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/admin/orders/update', methods=["POST"])
def update_order_admin():
    data = request.get_json()
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "DB connection failed"}), 500

    try:
        cursor = connection.cursor()
        query = """
            UPDATE Orders
            SET ShippingDestination = %s,
                NumberOfItems = %s,
                OrderStatus = %s
            WHERE OrderID = %s
        """
        cursor.execute(query, (
            data["ShippingDestination"],
            data["NumberOfItems"],
            data["OrderStatus"],
            data["OrderID"]
        ))
        connection.commit()
        return jsonify({"message": "Order updated"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/user-management')
def user_management():
    return render_template('UserManagementPage.html')


@app.route('/api/admin/users', methods=['GET'])
def get_all_users_admin():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT UserID, FirstName, LastName, Email, Role
            FROM Users
            ORDER BY LastName ASC
        """
        cursor.execute(query)
        users = cursor.fetchall()
        return jsonify(users)
    except Error as e:
        print("Error fetching users:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/admin/users/update', methods=['POST'])
def update_user_admin():
    
    data = request.get_json()
    connection = connect_to_mysql()

    print("Incoming update payload:", data)

    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()
        update_query = """
            UPDATE Users
            SET FirstName = %s,
                LastName = %s,
                Email = %s,
                Role = %s
            WHERE UserID = %s
        """
        cursor.execute(update_query, (
            data["FirstName"],
            data["LastName"],
            data["Email"],
            data["Role"],
            data["UserID"]
        ))
        connection.commit()
        return jsonify({"message": "User updated successfully."})
    except Error as e:
        print("Error updating user:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()



# Changing Account Information
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

# Flask route to return inventory as JSON
@app.route("/api/products", methods=["GET"])
def get_inventory_items():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.callproc("sp_InventoryWithColors")

        products = {}

        for result in cursor.stored_results():
            for row in result.fetchall():
                sku = row['SKU']
                if sku not in products:
                    products[sku] = {
                        'SKU': sku,
                        'ItemName': row['ItemName'],
                        'ItemDescription': row['ItemDescription'],
                        'Price': row['Price'],
                        'QuantityInStock': row['QuantityInStock'],
                        'Supplier': row['Supplier'],
                        'RestockThreshold': row['RestockThreshold'],
                        'Colors': []  
                    }
                if row['ColorName']:
                    products[sku]['Colors'].append(row['ColorName'])

        return jsonify(list(products.values()))
    
    except Error as e:
        import traceback
        traceback.print_exc()  
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/orders')
def get_orders():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        customer_id = session.get('user_id')

        if not customer_id:
            return jsonify({"error": "User not logged in"}), 403

        query = "SELECT OrderID, ShippingDestination, NumberOfItems, OrderStatus FROM Orders WHERE CustomerID = %s"
        cursor.execute(query, (customer_id,))
        orders = cursor.fetchall()

        return jsonify(orders)

    except Error as e:
        print("Order retrieval error:", e)
        return jsonify({"error": "Failed to fetch orders"}), 500
    finally:
        cursor.close()
        connection.close()


# To deal with forget password button on sign up page
@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"success": False, "error": "Email is required"}), 400

    connection = connect_to_mysql()
    if not connection:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE Email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": True})  

        # Generate a temporary password (You could send an email instead)
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Store the temporary password in the database 
        cursor.execute("UPDATE Users SET PasswordHash=%s WHERE Email=%s", (temp_password, email))
        connection.commit()

        return jsonify({"success": True, "message": f"A reset link has been sent to {email}"})

    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    app.run(debug=True, port=5055)

