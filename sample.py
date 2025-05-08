import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dr3amC0ount3r$"
)

if connection.is_connected():
    print("✅ Connected successfully!")
    connection.close()
