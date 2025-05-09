This file is designed to help deploy the South Balance e-commerce webpage. 
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
- tqdm
-----------------------------------------------------------------------------------------
MySQL Configuration, Python, and setup.py:

The database is a core element that facilitates the population of many tables and is critical for user login and product population. The team wanted to ensure that when the system is installed and set up for the first time, it is done in a very organized and repeatable manner. To this end, we have created a file called "setup.py" designed to develop all of the tables, stored procedures, and additional schemas required for the website to run. 

PRE-REQUISITES

PYTHON PIP COMMANDS:
pip install mysql
pip install mysql.connector
pip install mysql-connector-python
pip install tqdm
pip install flask
pip install werkzeug

PREPARE FOR SETUP.PY
Before running the setup.py file, the host machine must install an updated version of MySQL. The team tested with version 8.0.42. When installing MySQL, it is recommended to be configured with the default settings and the FULL MySQL package, including Workbench and Server. This link will direct the user to a MySQL install page. By default, you will be recommended port 3306. The team recommends this default. Remember your root username and password, which will be important later (SEE BELOW NOTES ON ROOT PASSWORD CHOICES). 

In testing, the team used the following password as their root SQL login: "Dr3amC0ount3r$." If your root login differs from the team's, you must change the root credentials stored in the startup.py file. These properties can be found in the function "connect_to_mysql" in the connection properties starting on line 26. Update this section with your credentials if you want to change.

RUNNING SETUP.PY

Once your MySQL instance is installed, the user can run setup.py. Upon running setup.py, the user will be asked to enter their hostname, which is by default "localhost," their port, 3306 by default, their root username, and their password. The script will use this information to generate the procedures and schemas the application requires. 

Upon completion of the script, the user can now run the startup.py. This will start the Flask server and present the user with a local IP address in the terminal. Navigating to this link in a browser will display the website's home page. 

KNOWN BUGS: Some MySQL installations might have a mismatch in authentication plugins. If upon running the setup.py file, you receive a message like "FAILURE ERROR: Authentication plugin 'caching_sha2_password' is not supported," follow these steps:

  1) In the terminal, run cd "C:\Program Files\MySQL\MySQL Server 8.0\bin" unless your MySQL is in a different location.
  2) Run the command .\mysql -u root -p and enter your root password
  3) Within SQL run the following commands in order:
     - ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Dr3amC0ount3r$'; (REPLACE WITH YOUR ROOT PASSWORD)
     - FLUSH PRIVILEGES;
     - EXIT;
  4) In a separate terminal session open as admin run the commands:
     - net stop mysql80
     - net start mysql80

If users utilize the setup.py script, they will already be granted an admin account. The default credentials should immediately be changed. These credentials are admin@sb.com with an admin password. 

From this point, the user can utilize the site as needed. 

