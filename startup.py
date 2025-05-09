import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Blueprint
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.exceptions import NotFound, HTTPException
#from Python.Order_SP_Handler import order_blueprint  
import re

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'a4f3e86de5f241f6b9112f882eecf1a3'

#app.register_blueprint(order_blueprint)

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
            print("Connection to TTOps initiated -- Success")
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

                if user and check_password_hash(user['PasswordHash'], password):
                    session['user_id'] = user['UserID']
                    session['role'] = user['Role']
                    role = user['Role']

                    # Only insert into Customers if user is a Customer or Employee
                    if role in ["Customer", "Employee"]:
                        customer_conn = connect_to_mysql()
                        customer_cursor = customer_conn.cursor()

                        # Check if customer already exists
                        customer_cursor.execute(
                            "SELECT CustomerID FROM Customers WHERE CustomerID = %s", (user['UserID'],)
                        )
                        existing_customer = customer_cursor.fetchone()

                        if not existing_customer:
                            # Parse First and Last name from email
                            email_parts = user['Email'].split('@')[0].split('.')
                            first_name = email_parts[0].capitalize() if len(email_parts) > 0 else "First"
                            last_name = email_parts[1].capitalize() if len(email_parts) > 1 else "Last"

                            # Insert into Customers table
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

                    # Redirect based on role and login type
                    if login_type == "customer" and role in ["Customer", "Employee", "Admin"]:
                        return redirect(url_for('product_page'))
                    elif login_type == "inventory" and role in ["Employee", "Admin"]:
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


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user_admin(user_id):
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Users WHERE UserID = %s", (user_id,))
        connection.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Delete user error:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# Signup Page
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        username = request.form.get("username")
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
            cursor.execute("SELECT * FROM Users WHERE Email=%s OR Username=%s", (email, username))
            if cursor.fetchone():
                return render_template("Account_Signup_Page.html", error="Email or username already registered.")

            # Hash password
            password_hash = generate_password_hash(password)

            cursor.callproc("sp_SignupUser", (first_name, last_name, email, username, password_hash))
            connection.commit()

            return redirect(url_for("login"))
        
        except Error as e:
            import traceback
            traceback.print_exec()
            return render_template("Account_Signup_Page.html", error=f"Signup failed: {str(e)}")
        
        finally:
            cursor.close()
            connection.close()

    return render_template("Account_Signup_page.html")
            

@app.route('/inventory')
def inventory():
    if 'user_id' not in session or session.get('role') not in ['Employee', 'Admin']:
        flash("Access Denied.", "error")
        return redirect(url_for('login'))

    return render_template(
        'InventoryManagementPage.html',
        nav_context='admin',  
        role=session.get('role')
    )


@app.route('/api/inventory/delete/<string:sku>', methods=['DELETE'])
def delete_inventory_item(sku):
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Inventory WHERE SKU = %s", (sku,))
        connection.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Delete inventory error:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# Product Page
@app.route('/product')
def product_page():
    return render_template('ProductPage.html', nav_context="customer")

# Cart Page
@app.route("/cart")
def cart():
    return render_template("Checkout_Cart_Page.html", nav_context="customer")



# Order Status Page
@app.route("/order-status")
def order_status():
    if 'user_id' not in session:
        flash("You must be logged in to view orders.", "error")
        return redirect(url_for('login'))
    
    return render_template('OrderStatusPage.html', nav_context="customer")

@app.route("/api/submit-order", methods=["POST"])
def submit_order():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 403

    data = request.get_json()
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        user_id = session['user_id']
        total_price = data.get("total", 0.00)
        order_items = data.get('items', [])
        shipping_address = data.get('shippingAddress', 'None')
        number_of_items = data.get('NumberOfItems', 0)

        # Get real CustomerID
        cursor.execute("SELECT CustomerID FROM Customers WHERE CustomerID = %s", (user_id,))
        customer = cursor.fetchone()

        if not customer:
            print(f"No customer record found for user_id {user_id}")
            return jsonify({"success": False, "error": "Customer record not found"}), 400

        customer_id = customer['CustomerID']

        # Check inventory levels for each item
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

        # Insert into Orders
        insert_query = """
            INSERT INTO Orders (CustomerID, ShippingDestination, NumberOfItems, TotalPrice, OrderStatus)
            VALUES (%s, %s, %s, %s, 'Pending')
        """
        cursor.execute(insert_query, (customer_id, shipping_address, number_of_items, total_price))
        connection.commit()

        order_id = cursor.lastrowid

        # Insert each item into OrderItems and update Inventory
        for item in order_items:
            sku = item.get('sku')
            name = item.get('name')
            quantity = item.get('quantity', 1)
            price = item.get('price')
            color = item.get('color', None)
            customization = item.get('customization', None)

            # Insert order item
            cursor.execute("""
                INSERT INTO OrderItems (OrderID, SKU, ProductName, Quantity, Price, Color, Customization)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (order_id, sku, name, quantity, price, color, customization))

            # Update inventory
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
        return jsonify({"success": True})
    except Error as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Load the order management page
@app.route('/order-management')
def order_management():
    if 'user_id' not in session or session.get('role') not in ['Employee', 'Admin']:
        flash("Access Denied.", "error")
        return redirect(url_for('login'))

    return render_template(
        'OrderManagementPage.html',
        nav_context='admin',  
        role=session.get('role')
    )

# Load orders data
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

# Update the order information
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

# Load user management table
@app.route('/user-management')
def user_management():
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash("Access Denied.", "error")
        return redirect(url_for('login'))

    return render_template(
        'UserManagementPage.html',
        nav_context='admin',
        role=session.get('role')
    )



# Get users to populate page
@app.route('/api/admin/users', methods=['GET'])
def get_all_users_admin():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT UserID, Username, FirstName, LastName, Email, Role
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

# Update user information
@app.route('/api/admin/users/update', methods=['POST'])
def update_user_admin():
    data = request.get_json()
    connection = connect_to_mysql()

    print("Incoming update payload:", data)

    if not connection:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

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

        return jsonify({"success": True})

    except Error as e:
        print("Error updating user:", e)
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()

# Function to add users to the users table
@app.route('/api/admin/users/add', methods=['POST'])
def add_user_admin():
    data = request.get_json()
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()

        # Hash the password securely
        password_hash = generate_password_hash(data['Password'])

        # Insert into Users table
        insert_query = """
            INSERT INTO Users (FirstName, LastName, Email, Username, PasswordHash, Role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            data['FirstName'],
            data['LastName'],
            data['Email'],
            data['Username'],
            password_hash,
            data['Role']
        ))
        connection.commit()

        # Get the new UserID
        cursor.execute("SELECT LAST_INSERT_ID()")
        new_user_id = cursor.fetchone()[0]

        # If user is a Customer or Employee, insert into Customers table
        if data['Role'] in ['Customer', 'Employee']:
            cursor.execute("""
                INSERT INTO Customers (CustomerID, FirstName, LastName, Email)
                VALUES (%s, %s, %s, %s)
            """, (
                new_user_id,
                data['FirstName'],
                data['LastName'],
                data['Email']
            ))
            connection.commit()

        return jsonify({"success": True})
    
    except Exception as e:
        print("Add user error:", e)
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# Changing Account Information
@app.route('/account', methods=["GET", "POST"])
def account():
    nav_context = request.args.get("context", "customer")

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        new_password = request.form.get("new-password")
        confirm_password = request.form.get("confirm-password")

        if new_password and new_password != confirm_password:
            flash("The entered passwords do not match. Please try again.", "error")
            return redirect(url_for('account', context=nav_context))  # preserve context in redirect

        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()

            user_id = session.get('user_id')
            if not user_id:
                flash("You must be logged in to update your account.", "error")
                return redirect(url_for('login'))

            # Check for duplicate username/email (excluding current logged user)
            cursor.execute("""
                SELECT * FROM Users
                WHERE (Username=%s OR Email=%s) AND UserID != %s
            """, (username, email, user_id))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username or email is already in use.", "error")
            else:
                if new_password:
                    password_hash = generate_password_hash(new_password)
                    cursor.execute("""
                        UPDATE Users SET Username=%s, Email=%s, PasswordHash=%s
                        WHERE UserID=%s
                    """, (username, email, password_hash, user_id))
                else:
                    cursor.execute("""
                        UPDATE Users SET Username=%s, Email=%s
                        WHERE UserID=%s
                    """, (username, email, user_id))

                connection.commit()
                flash("Account updated successfully!", "success")

            cursor.close()
            connection.close()

        # Always re-render with nav_context after POST
        return render_template('Account_Change_Information_Page.html',
                               username=username,
                               email=email,
                               role=session.get('role'),
                               nav_context=nav_context)

    else:
        user_id = session.get('user_id')
        if not user_id:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('login'))

        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT Username, Email FROM Users WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                return render_template('Account_Change_Information_Page.html',
                                       username=user['Username'],
                                       email=user['Email'],
                                       role=session.get('role'),
                                       nav_context=nav_context)

        flash("Failed to load account information.", "error")
        return redirect(url_for('home'))
    
@app.context_processor
def inject_user_role():
    return dict(role=session.get('role'))

# Get product data for table population
@app.route("/api/products", methods=["GET"])
def get_inventory_items():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                i.SKU,
                i.ItemName,
                i.ItemDescription,
                i.Supplier,
                i.Price,
                i.QuantityInStock,
                i.RestockThreshold,
                GROUP_CONCAT(ic.ColorName) AS AvailableColors
            FROM Inventory i
            LEFT JOIN InventoryColors ic ON i.SKU = ic.SKU
            GROUP BY i.SKU
        """)

        rows = cursor.fetchall()
        products = {}

        for row in rows:
            sku = row['SKU']
            if sku not in products:
                products[sku] = {
                    'SKU': sku,
                    'ItemName': row.get('ItemName'),
                    'ItemDescription': row.get('ItemDescription'),
                    'Price': row.get('Price'),
                    'QuantityInStock': row.get('QuantityInStock'),
                    'Supplier': row.get('Supplier'),
                    'RestockThreshold': row.get('RestockThreshold'),
                    'Colors': []
                }

            if 'AvailableColors' in row and row['AvailableColors']:
                if not products[sku]['Colors']:
                    products[sku]['Colors'] = row['AvailableColors'].split(',')

        return jsonify(list(products.values()))


    except Error as e:
        import traceback
        traceback.print_exc()
        print(f"Returning {len(products)} products", flush=True)

        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Get colors with current SKU prevent duplication
@app.route('/api/colors-for-sku/<string:sku>', methods=['GET'])
def get_colors_for_sku(sku):
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT ColorName FROM inventorycolors
            WHERE SKU = %s
        """, (sku,))
        colors = cursor.fetchall()
        return jsonify(colors)
    except Error as e:
        print("Error fetching colors for SKU:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Get colors from colors table
@app.route('/api/colors', methods=['GET'])
def get_colors():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT ColorName FROM inventorycolors")
        colors = cursor.fetchall()
        return jsonify(colors)
    except Error as e:
        print("Error fetching colors:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Get customer's associated orders
@app.route('/api/orders')
def get_orders():
    if 'user_id' not in session:
        print("!!! ERROR: No user_id in session", flush=True)
        return jsonify({"error": "User not logged in"}), 403

    connection = connect_to_mysql()
    if not connection:
        print("!!!! ERROR: Failed DB connection", flush=True)
        return jsonify({"error": "Database connection failed"}), 500

    try:
        user_id = session.get('user_id')
        if not user_id:
            print("!!! ERROR: Session does not contain 'user_id'", flush=True)
            return jsonify({"error": "User not logged in"}), 403


        cursor = connection.cursor(dictionary=True)

        # Find customer record
        cursor.execute("SELECT CustomerID FROM Customers WHERE CustomerID = %s", (user_id,))
        customer = cursor.fetchone()
        print(f"--- INFORMATION: Customer fetch: {customer}", flush=True)

        if not customer:
            print("--- INFORMATION: No customer record found for user_id", flush=True)
            return jsonify([])  # Don't crash

        customer_id = customer['CustomerID']
        print(f"--- INFORMATION: Using customer_id: {customer_id}", flush=True)

        # Fetch orders for customer
        cursor.execute("""
            SELECT o.OrderID, o.ShippingDestination, o.NumberOfItems, o.TotalPrice, o.OrderStatus
            FROM Orders o
            WHERE o.CustomerID = %s
            ORDER BY o.OrderDate DESC
        """, (customer_id,))

        orders = cursor.fetchall()
        print(f"--- SUCCESS: Retrieved {len(orders)} orders.", flush=True)
        return jsonify(orders)

    except Exception as e:
        import traceback
        print("ERROR: EXCEPTION IN /api/orders", flush=True)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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
    
# Debug commands for testing routes and functionality
@app.route('/debug-alive')
def debug_alive():
    return "This is the correct startup.py"

@app.route("/debug/confirm-orders-route")
def debug_confirm_orders_route():
    print("CONFIRM: /api/orders route is reachable", flush=True)
    return "Route is active"

@app.route("/debug/session")
def debug_session():
    print("Debugging session:", dict(session), flush=True)
    return jsonify({
        "user_id": session.get("user_id"),
        "role": session.get("role")
})

# Error handling for common flask server errrors
@app.errorhandler(Exception)
def handle_exception(e):
    # Flask handle 404s normally 
    if isinstance(e, NotFound):
        return e
    
    # Return standard HTTP with JSON response
    if isinstance(e, HTTPException):
        
        return jsonify({"error": e.description}), e.code

    # Log and return server errors (non-HTTP)
    import traceback
    print("Global Flask Exception Caught", flush=True)
    traceback.print_exc()
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5055)

