from werkzeug.security import generate_password_hash

password = "admin"
hashed_password = generate_password_hash(password)
print("Hashed password:", hashed_password)
