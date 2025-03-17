import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify

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

app = Flask(__name__)

from flask import Flask, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def home():
    return render_template('ProductPage.html')  

@app.route('/product')
def product_page():
    return render_template('ProductPage.html')

@app.route("/cart")
def cart():
    return render_template("Checkout_Cart_Page.html")

@app.route("/order-status")
def order_status():
    return render_template("OrderStatusPage.html")


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



if __name__ == "__main__":
    app.run(debug=True)