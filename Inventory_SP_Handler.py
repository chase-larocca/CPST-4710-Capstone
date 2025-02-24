import mysql.connector
from mysql.connector import Error

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
    
# Calls stored procedure to create or update an inventory item
def create_or_update_inventory(connection, sku, item_name, item_desc, price, quant, supplier, restock_threshold):

    # Create or edit inventory item
    try: 
        cursor = connection.cursor()
        cursor.callproc("sp_Inventory_CreateOrUpdate", (sku, item_name, item_desc, price, quant, supplier, restock_threshold))
        connection.commit()
        print(f"Inventory item {'updated' if sku else 'created'}: {item_name}")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls stored procedure to fetch all inventory items
def read_inventory(connection): 

    # Get list of all inventory items
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

        # Access item name before deletion
        cursor.execute("SELECT ItemName FROM Inventory WHERE SKU = %s", (sku,))
        item = cursor.fetchone()

        # Delete inventory item
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

# Calls SQL connection & runs function tests
def main():

    # Create new connection
    connection = connect_to_mysql()

    # Test connection
    if connection:
        cursor=connection.cursor()
        cursor.execute("SELECT VERSION();")
        record = cursor.fetchone()
        print("MySQL Database Version:", record)

        # Test create inventory function
        create_or_update_inventory(connection, None, "Gaming Laptop", "High-end laptop", 1499.99, 5, "TechSupplier Inc.", 2)

        # Test read inventory function
        read_inventory(connection)
        
        # Test delete inventory function
        delete_inventory_item(connection, 1)

        # Close connection
        cursor.close()
        connection.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()