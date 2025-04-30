This file is designed to help deploy the South Balance ecommerce webpage. 
-----------------------------------------------------------------------------------------
The website uses several different systems in conjunction with each other. All of these systems are required to ensure the website's full functionality. 

Core Systems:
- MySQL
- Python (See "Libraries" section for specific Python libraries employed)
- JavaScript
- HTML
- CSS

Libraries:
- mysql (Database handling)
- Flask (Web server hosting)
- wekzeug (Password hashing library)
- re (Searching/text patterns)
-----------------------------------------------------------------------------------------
MySQL Configuration

The database is a core element that facilitates the population of many of the tables and is critical for user login. Within the MAIN branch, the team has created an SQL folder within the project files.
Inside the SQL folder, there are prewritten files to deploy the tables and databases required for the backend code to run. Please review each file individually and execute the code to create the tables and stored procedures. 

The team has attached a link to a basic MySQL installation and initial database creation tutorial. https://dev.mysql.com/doc/mysql-getting-started/en/

While this is already filled out in the startup.py file below, you can find the credentials the team has used for their root user login to facilitate the SQL connections within the backend Flask processes. This information can be changed, but does not need to be. 

host="localhost"
user="root"
password="Dr3amC0ount3r$"
database="TTOps"

No users will be created by default. The team recommends running the following command within SQL to create your initial admin profile. The password below is hashed, but in plaintext, it would be "yourpassword."

INSERT INTO Users (FirstName, LastName, Email, Username, PasswordHash, Role)
VALUES ('Admin', 'User', 'admin@sb.com', 'admin', 'pbkdf2:sha256:260000$jWHKCJnozAmkU2fT$c4547fb7360cc83d344e60e86130022a60f26cd631ed32a892e5632ad1de8aa5', 'Admin');
-----------------------------------------------------------------------------------------

Once the database has been created, the user can run the startup.py file to launch the Flask server and begin utilizing the website. The IP address associated with your Flask server will be visible in the terminal from which you executed the startup.py
