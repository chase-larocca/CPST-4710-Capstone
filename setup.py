
import mysql.connector
from mysql.connector import Error
from tqdm import tqdm
import time

print("=== South Balance MySQL Setup Utility ===")

host = "localhost"
port = "3306"
user = "root"
password = "Dr3amC0ount3r$"
db_name = "ttops"

schema_commands = [
    f"CREATE DATABASE IF NOT EXISTS {db_name};",
    f"USE {db_name};",
    """
    CREATE TABLE IF NOT EXISTS Users (
        UserID INT AUTO_INCREMENT PRIMARY KEY,
        FirstName VARCHAR(50),
        LastName VARCHAR(50),
        Email VARCHAR(100) UNIQUE,
        Username VARCHAR(50) UNIQUE,
        PasswordHash VARCHAR(255),
        Role ENUM('Admin', 'Employee', 'Customer') DEFAULT 'Customer'
    );
    """,
    """
    INSERT INTO Users (FirstName, LastName, Email, Username, PasswordHash, Role)
    VALUES ('Admin', 'User', 'admin@sb.com', 'admin',
    'scrypt:32768:8:1$E0pXMHc9JLpYpDUZ$5e5707db9367b0728f1f5b209beedbfd33eac9ef10a404ecbf1c7fc9dc21a68cc4e40625bcfc7b3c0044b26e3ec26cce61569610c3d8e955636eda1f12417998',
    'Admin')
    ON DUPLICATE KEY UPDATE Email = Email;
    """,
    """
    CREATE TABLE IF NOT EXISTS Customers (
        CustomerID INT PRIMARY KEY,
        FirstName VARCHAR(100),
        LastName VARCHAR(100),
        Email VARCHAR(100),
        FOREIGN KEY (CustomerID) REFERENCES Users(UserID) ON DELETE CASCADE
    );
    """,
    # INSERT Admin into Customers table
    """
    INSERT IGNORE INTO Customers (CustomerID, FirstName, LastName, Email)
    SELECT UserID, 'Admin', 'User', Email FROM Users WHERE Email = 'admin@sb.com';
    """,
    """
    CREATE TABLE IF NOT EXISTS Colors (
        ColorID INT AUTO_INCREMENT PRIMARY KEY,
        ColorName VARCHAR(50) UNIQUE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Inventory (
        SKU VARCHAR(50) PRIMARY KEY,
        ItemName VARCHAR(100),
        ItemDescription TEXT,
        Supplier VARCHAR(100),
        Price DECIMAL(10, 2),
        QuantityInStock INT,
        RestockThreshold INT,
        ColorID INT,
        FOREIGN KEY (ColorID) REFERENCES Colors(ColorID)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS InventoryColors (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        SKU VARCHAR(50),
        ColorName VARCHAR(50),
        FOREIGN KEY (SKU) REFERENCES Inventory(SKU) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Orders (
        OrderID INT AUTO_INCREMENT PRIMARY KEY,
        CustomerID INT,
        ShippingDestination VARCHAR(255),
        NumberOfItems INT,
        TotalPrice DECIMAL(10, 2),
        OrderStatus VARCHAR(50),
        OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS OrderItems (
        OrderItemID INT AUTO_INCREMENT PRIMARY KEY,
        OrderID INT,
        SKU VARCHAR(50),
        ProductName VARCHAR(100),
        Quantity INT,
        Price DECIMAL(10, 2),
        Color VARCHAR(50),
        Customization VARCHAR(255),
        FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
        FOREIGN KEY (SKU) REFERENCES Inventory(SKU)
    );
    """,
    """
    INSERT IGNORE INTO Colors (ColorName) VALUES
    ('Black'), ('Blue'), ('Grey'), ('Purple'), 
    ('Pattern'), ('Straw'), ('Summit'), ('Licorice');
    """,
    """
    INSERT IGNORE INTO Inventory (SKU, ItemName, ItemDescription, Supplier, Price, QuantityInStock, RestockThreshold) VALUES
    ('BUB-32OZ-LIC', 'Bubba 32oz Licorice', 'Durable water bottle in licorice color', 'Bubba', 14.99, 100, 25),
    ('BUB-32OZ-STRAW', 'Bubba 32oz Straw', 'Easy-sip straw water bottle', 'Bubba', 14.99, 100, 25),
    ('BUB-40OZ-BLK', 'Bubba 40oz Black', 'Extra large water bottle in black', 'Bubba', 16.99, 100, 25),
    ('BUB-FLO-16OZ', 'Bubba Flo 16oz', 'Compact 16oz bottle with flow control', 'Bubba', 9.99, 100, 25),
    ('BUB-HERO-BLK', 'Bubba Hero Black', 'Premium black insulated bottle', 'Bubba', 19.99, 100, 25),
    ('GOFIT-DELUXE', 'GoFit Deluxe', 'Deluxe fitness bottle with grip', 'GoFit', 18.99, 100, 25),
    ('GOFIT-DT-PURPLE', 'GoFit DT Purple', 'Dual-tone purple fitness bottle', 'GoFit', 17.49, 100, 25),
    ('GOFIT-GREY', 'GoFit Grey', 'Sleek grey hydration bottle', 'GoFit', 15.99, 100, 25),
    ('GOFIT-KIT', 'GoFit Kit', 'Hydration kit with accessories', 'GoFit', 24.99, 100, 25),
    ('GOFIT-PATTERN', 'GoFit Pattern', 'Patterned fitness bottle', 'GoFit', 16.49, 100, 25),
    ('GOFIT-SUMMIT', 'GoFit Summit', 'Summit series adventure bottle', 'GoFit', 21.99, 100, 25);
    """,
    """
    INSERT IGNORE INTO InventoryColors (SKU, ColorName) VALUES
    ('BUB-32OZ-LIC', 'Licorice'),
    ('BUB-32OZ-STRAW', 'Straw'),
    ('BUB-40OZ-BLK', 'Black'),
    ('BUB-FLO-16OZ', 'Blue'),
    ('BUB-HERO-BLK', 'Black'),
    ('GOFIT-DELUXE', 'Blue'),
    ('GOFIT-DT-PURPLE', 'Purple'),
    ('GOFIT-GREY', 'Grey'),
    ('GOFIT-KIT', 'Black'),
    ('GOFIT-PATTERN', 'Pattern'),
    ('GOFIT-SUMMIT', 'Summit');
    """
]

stored_procedures = [
    """
    DROP PROCEDURE IF EXISTS sp_Inventory_CreateOrUpdate;
    CREATE PROCEDURE sp_Inventory_CreateOrUpdate (
        IN p_SKU VARCHAR(50),
        IN p_ItemName VARCHAR(100),
        IN p_ItemDescription TEXT,
        IN p_Price DECIMAL(10,2),
        IN p_QuantityInStock INT,
        IN p_Supplier VARCHAR(100),
        IN p_RestockThreshold INT
    )
    BEGIN
        INSERT INTO Inventory (SKU, ItemName, ItemDescription, Price, QuantityInStock, Supplier, RestockThreshold)
        VALUES (p_SKU, p_ItemName, p_ItemDescription, p_Price, p_QuantityInStock, p_Supplier, p_RestockThreshold)
        ON DUPLICATE KEY UPDATE
            ItemName = VALUES(ItemName),
            ItemDescription = VALUES(ItemDescription),
            Price = VALUES(Price),
            QuantityInStock = VALUES(QuantityInStock),
            Supplier = VALUES(Supplier),
            RestockThreshold = VALUES(RestockThreshold);
    END;
    """,
    """
    DROP PROCEDURE IF EXISTS sp_AddInventoryItem;
    CREATE PROCEDURE sp_AddInventoryItem (
        IN p_SKU VARCHAR(50),
        IN p_ItemName VARCHAR(100),
        IN p_ItemDescription TEXT,
        IN p_Supplier VARCHAR(100),
        IN p_Price DECIMAL(10,2),
        IN p_QuantityInStock INT,
        IN p_RestockThreshold INT
    )
    BEGIN
        INSERT INTO Inventory (SKU, ItemName, ItemDescription, Supplier, Price, QuantityInStock, RestockThreshold)
        VALUES (p_SKU, p_ItemName, p_ItemDescription, p_Supplier, p_Price, p_QuantityInStock, p_RestockThreshold);
    END;
    """,
    """
    DROP PROCEDURE IF EXISTS sp_Users_CreateOrUpdate;
    CREATE PROCEDURE sp_Users_CreateOrUpdate (
        IN p_UserID INT,
        IN p_FirstName VARCHAR(50),
        IN p_LastName VARCHAR(50),
        IN p_Email VARCHAR(100),
        IN p_PasswordPlain VARCHAR(255),
        IN p_Role ENUM('Admin', 'Employee', 'Customer')
    )
    BEGIN
        IF p_UserID IS NULL THEN
            INSERT INTO Users (FirstName, LastName, Email, Username, PasswordHash, Role)
            VALUES (
                p_FirstName,
                p_LastName,
                p_Email,
                LOWER(SUBSTRING_INDEX(p_Email, '@', 1)),
                SHA2(p_PasswordPlain, 256),
                p_Role
            );
        ELSE
            UPDATE Users
            SET FirstName = p_FirstName,
                LastName = p_LastName,
                Email = p_Email,
                PasswordHash = SHA2(p_PasswordPlain, 256),
                Role = p_Role
            WHERE UserID = p_UserID;
        END IF;
    END;
    """,
    """
    DROP PROCEDURE IF EXISTS sp_InventoryWithColors;
    CREATE PROCEDURE sp_InventoryWithColors()
    BEGIN
        SELECT 
            i.SKU,
            i.ItemName,
            i.ItemDescription,
            i.Supplier,
            i.Price,
            i.QuantityInStock,
            i.RestockThreshold,
            GROUP_CONCAT(ic.ColorName) AS AvailableColors
        FROM Inventory i
        LEFT JOIN InventoryColors ic ON i.SKU = ic.SKU
        GROUP BY i.SKU;
    END;
    """,
    """
    DROP PROCEDURE IF EXISTS sp_SignupUser;
    CREATE PROCEDURE sp_SignupUser (
        IN p_FirstName VARCHAR(50),
        IN p_LastName VARCHAR(50),
        IN p_Email VARCHAR(100),
        IN p_Username VARCHAR(50),
        IN p_PasswordHash VARCHAR(255)
    )
    BEGIN
        INSERT INTO Users (FirstName, LastName, Email, Username, PasswordHash, Role)
        VALUES (p_FirstName, p_LastName, p_Email, p_Username, p_PasswordHash, 'Customer');
        
        INSERT INTO Customers (CustomerID, FirstName, LastName, Email)
        VALUES (LAST_INSERT_ID(), p_FirstName, p_LastName, p_Email);
    END;    
    """
]

try:
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password
    )

    if connection.is_connected():
        print("\nIN PROGRESS: Connected to MySQL Server. Executing schema setup...\n")
        cursor = connection.cursor()

        for command in tqdm(schema_commands, desc="Creating Tables", unit="step"):
            if command.strip():
                cursor.execute(command)
                time.sleep(0.1)

        cursor.execute(f"USE {db_name}")
        print("\nCreating stored procedures...")
        for proc in stored_procedures:
            for statement in cursor.execut(proc, multi=True):
                cursor.execute(proc)
                time.sleep(0.1)
                pass

        connection.commit()
        print(f"\nSUCCESS: Database '{db_name}' setup complete with all stored procedures.")

except Error as e:
    print(f"\nFAILURE ERROR: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()

