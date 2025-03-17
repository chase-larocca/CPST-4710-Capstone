from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

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

# Calls stored procedure to create or update an inventory item
def create_or_update_inventory(connection, sku, item_name, item_desc, price, quant, supplier, restock_threshold):
    try: 
        cursor = connection.cursor()
        cursor.callproc("sp_Inventory_CreateOrUpdate", (sku, item_name, item_desc, price, quant, supplier, restock_threshold))
        connection.commit()
        print(f"Inventory item {'updated' if sku else 'created'}: {item_name}")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls stored procedure to fetch all inventory items (console test)
def read_inventory(connection): 
    try:
        cursor = connection.cursor()
        cursor.callproc("sp_Inventory_Read")
        for result in cursor.stored_results():
            inventory_items = result.fetchall()
            for item in inventory_items:
                print(item)
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls stored procedure to delete an inventory item
def delete_inventory_item(connection, sku):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT ItemName FROM Inventory WHERE SKU = %s", (sku,))
        item = cursor.fetchone()

        if item:
            item_name = item[0]
            cursor.callproc("sp_Inventory_Delete", (sku,))
            connection.commit()
            print(f"Inventory item '{item_name}' (SKU: {sku}) deleted successfully.")
        else:
            print(f"No inventory item found with SKU: {sku}")

    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

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

# Calls SQL connection & runs function tests
def main():
    connection = connect_to_mysql()

    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION();")
        record = cursor.fetchone()
        print("MySQL Database Version:", record)

        # Test create inventory function

        # Test read inventory function
        read_inventory(connection)

        # Test delete inventory function
        delete_inventory_item(connection, 1)

        cursor.cl

if __name__ == "__main__":
    app.run(debug=True)

