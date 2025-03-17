USE TTOps;

-- Inventory Table
-- USE TTOps;
CREATE TABLE IF NOT EXISTS Inventory (
    SKU INT AUTO_INCREMENT PRIMARY KEY,
    ItemName VARCHAR(255) NOT NULL,
    ItemDescription TEXT,
    Price DECIMAL(10,2) NOT NULL,
    QuantityInStock INT NOT NULL DEFAULT 0,
    Supplier VARCHAR(255),
    RestockThreshold INT DEFAULT 30,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Inventory Archive Table
-- USE TTOps;
CREATE TABLE InventoryArchive (
    ArchiveID INT AUTO_INCREMENT PRIMARY KEY,
    SKUINT INT NOT NULL,
    ItemName VARCHAR(255) NOT NULL,
    ItemDescription TEXT,
    ItemPrice DECIMAL(10,2) NOT NULL,
    ItemQuantity INT NOT NULL,
    Supplier VARCHAR(255),
    CreatedAt TIMESTAMP NOT NULL,
    FinalUpdateAt TIMESTAMP NOT NULL,
    ArchivedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Table
-- USE TTOps;
CREATE TABLE IF NOT EXISTS Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role ENUM('Admin', 'Employee', 'Manager', 'Customer') NOT NULL DEFAULT 'Customer',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    LastLogin TIMESTAMP NULL
);

-- Customers Table
-- USE TTOps;
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(20),
    ShippingAddress TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    isDeleted BOOLEAN DEFAULT FALSE
);

-- Orders Table
-- USE TTOps;
CREATE TABLE IF NOT EXISTS Orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    TotalPrice DECIMAL(10,2) NOT NULL,
    OrderStatus ENUM('Pending', 'Shipped', 'Delivered', 'Cancelled') NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
);

-- Orders Archive Table
-- USE TTOps; 
CREATE TABLE IF NOT EXISTS OrdersArchive (
    ArchiveID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL,
    CustomerID INT NOT NULL,
    OrderDate DATETIME NOT NULL,
    TotalPrice DECIMAL(10,2) NOT NULL,
    OrderStatus ENUM('Cancelled', 'Deleted', 'Completed') NOT NULL,
    ArchivedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ArchivedReason TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
);

-- Inventory Colors Table
USE TTOps;
CREATE TABLE InventoryColors (
    ColorID INT AUTO_INCREMENT PRIMARY KEY,
    SKU VARCHAR(50) NOT NULL,
    ColorName VARCHAR(50) NOT NULL,
    FOREIGN KEY (SKU) REFERENCES Inventory(SKU)
);




