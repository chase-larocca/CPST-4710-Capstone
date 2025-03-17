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
    
# Calls stored procedure to create or update a user   
def create_or_update_user(connection, user_id, first_name, last_name, email, password_hash, role):

    # Create or edit user
    try:
        cursor = connection.cursor()
        cursor.callproc("sp_Users_CreateOrUpdate", (user_id, first_name, last_name, email, password_hash, role))
        connection.commit()
        print("User created/updated successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally: 
        cursor.close()

# Calls stored procedure to fetch all users
def read_users(connection):

    # Get list of all users
    try: 
        cursor = connection.cursor()
        cursor.callproc("sp_Users_Read")
        for result in cursor.stored_results():
            users = result.fetchall()
            for user in users:
                print(users)
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Calls stored procedure to delete a user
def delete_user(connection, user_id):
    
    try:
        cursor = connection.cursor()

        # Access user's name before deletion
        cursor.execute("SELECT FirstName, LastName FROM Users WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()

        # Delete user
        if user:
            first_name, last_name = user
            cursor.callproc("sp_Users_Delete", (user_id,))
            connection.commit()
            print(f"User '{first_name} {last_name}' (UserID: {user_id}) deleted successfully.")
        else:
            print(f"No user found with UserID: {user_id}")

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

        # Test create user function
        create_or_update_user(connection, None, "Jimmy", "Doe", "jimmy.doe@example.com", "hash_pass2", "Customer")

        # Test read user function
        read_users(connection)
        
        # Test delete user function
        delete_user(connection, 2)

        # Close connection
        cursor.close()
        connection.close()
        print("Connection close.")

if __name__ == "__main__":
    main()