## THIS FILE IS NOT CRITICAL TO THE RUNNING OF THE APPLICATION. THIS FILE IS DESIGNED TO BE USE TO GENERATE A 
# TEMPORARY HASHED PASSWORD FOR MANUAL USER CREATION VIA INSERT STATEMENTS.

from werkzeug.security import generate_password_hash

password = "admin"
hashed_password = generate_password_hash(password)
print("Hashed password:", hashed_password)
