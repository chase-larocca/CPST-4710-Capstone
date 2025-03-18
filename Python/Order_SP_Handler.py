import mysql.connector
from mysql.connector import Error
from flask import Blueprint, jsonify

# Connects to local MySQL database
def connect_to_mysql():

    try: 
        connection = mysql.connector.connect(

            host     = "localhost",
            user     = "root",
            password = "Dr3amC0ount3r$",
            database = "TTOps"
        )

        if connection.is_connected():
            print("Connect to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None
    
# Calls stored procedure to create an order
def create_order(connection, customer_id, total_price, order_status):
    try:
        cursor = connection.cursor()
        cursor.callproc('sp_createOrder', (customer_id, total_price, order_status))
        connection.commit()
        print("Order created successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls stored procedure to update an order
def update_order(connection, order_id, total_price, order_status):
    try:
        cursor = connection.cursor()
        cursor.callproc('sp_updateOrder', (order_id, total_price, order_status))
        connection.commit()
        print("Order updated successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls stored procedure to retrieve an order by ID

order_blueprint = Blueprint('order_routes', __name__)

@order_blueprint.route("/api/orders", methods=["GET"])
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# Calls stored procedure to cancel an order
def cancel_order(connection, order_id):
    try:
        cursor = connection.cursor()
        cursor.callproc('sp_cancelOrder', (order_id,))
        connection.commit()
        print("Order cancelled successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls stored procedure to archive an order
def archive_order(connection, order_id, reason):
    try:
        cursor = connection.cursor()
        cursor.callproc('sp_archiveOrder', (order_id, reason))
        connection.commit()
        print("Order archived successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

def main():
     # Create new connection
    connection = connect_to_mysql()

    # Test connection
    if connection:
        cursor=connection.cursor()
        cursor.execute("SELECT VERSION();")
        record = cursor.fetchone()
        print("MySQL Database Version:", record)

        # Test creating an order
        create_order(connection, 1, 99.99, "Pending")

        # Test retrieving an order
        order = get_order_by_id(connection, 1)
        print("Retrieved Order:", order)

        # Test updating an order
        update_order(connection, 1, 109.99, "Shipped")

        # Test cancelling an order
        cancel_order(connection, 1)

        # Test archiving an order
        archive_order(connection, 1, "Order is outdated")

        # Close connection
        cursor.close()
        connection.close()
        print("Connection close.")

if __name__ == '__main__':
    main()
