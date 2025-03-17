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

from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_url_path='', static_folder='.')

# Serve the ProductPage.html
@app.route('/')
def serve_product_page():
    return send_from_directory('.', 'ProductPage.html')

# Flask route to return inventory as JSON
@app.route("/api/products", methods=["GET"])
def get_inventory_items():
    connection = connect_to_mysql()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.callproc("sp_InventoryWithColors")

        rows = []
        for result in cursor.stored_results():
            rows = result.fetchall()

        # Group rows by SKU and collect colors
        products = {}
        for row in rows:
            sku = row["SKU"]
            if sku not in products:
                products[sku] = {
                    "SKU": sku,
                    "ItemName": row["ItemName"],
                    "ItemDescription": row["ItemDescription"],
                    "Price": float(row["Price"]),
                    "QuantityInStock": row["QuantityInStock"],
                    "Supplier": row["Supplier"],
                    "RestockThreshold": row["RestockThreshold"],
                    "CreatedAt": row["CreatedAt"].isoformat() if row["CreatedAt"] else None,
                    "UpdatedAt": row["UpdatedAt"].isoformat() if row["UpdatedAt"] else None,
                    "Colors": []
                }
            if row["ColorName"]:
                products[sku]["Colors"].append(row["ColorName"])

        return jsonify(list(products.values()))
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to read inventory"}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    app.run(debug=True)