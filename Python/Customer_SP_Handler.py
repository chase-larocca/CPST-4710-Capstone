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
    
# Calls stored procedure to create or update a customer
def create_or_update_customer(connection, customer_id, first_name, last_name, email, phone, shipping_address):
    try:
        cursor = connection.cursor()
        cursor.callproc('sp_createOrUpdateCustomer', (customer_id, first_name, last_name, email, phone, shipping_address))
        connection.commit()
        print("Customer created/updated successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls stored procedure to retrieve a customer by ID
def get_customer_by_id(connection, customer_id):
    try:
        cursor = connection.cursor()
        cursor.callproc('sp_getCustomerByID', (customer_id,))
        customer = None
        for result in cursor.stored_results():
            customer = result.fetchone()
        return customer
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls stored procedure to (soft) delete a customer
def delete_customer(connection, customer_id):
    try:
        cursor = connection.cursor()
        cursor.callproc('sp_deleteCustomer', (customer_id,))
        connection.commit()
        print("Customer deleted (soft delete) successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls SQL connection & runs function tests
def main():
    connection = connect_to_mysql()
    if connection:
        cursor=connection.cursor()
        cursor.execute("SELECT VERSION();")
        record = cursor.fetchone()
        print("MySQL Database Version:", record)
        
        # Close connection
        cursor.close()
        connection.close()
        print("Connection close.")

if __name__ == '__main__':
    main()
