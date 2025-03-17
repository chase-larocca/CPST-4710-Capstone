DELIMITER //

-- Create or Update a Customer (adds a new customer if they don’t exist or updates an existing customer if there’s new details)
CREATE PROCEDURE sp_createOrUpdateCustomer (
    IN p_CustomerID INT,
    IN p_FirstName VARCHAR(50),
    IN p_LastName VARCHAR(50),
    IN p_Email VARCHAR(100),
    IN p_PhoneNumber VARCHAR(20),
    IN p_ShippingAddress TEXT
)
BEGIN
    IF EXISTS (SELECT 1 FROM Customers WHERE CustomerID = p_CustomerID) THEN
        UPDATE Customers 
        SET FirstName = p_FirstName, 
            LastName = p_LastName, 
            Email = p_Email, 
            PhoneNumber = p_PhoneNumber, 
            ShippingAddress = p_ShippingAddress
        WHERE CustomerID = p_CustomerID;
    ELSE
        INSERT INTO Customers (FirstName, LastName, Email, PhoneNumber, ShippingAddress) 
        VALUES (p_FirstName, p_LastName, p_Email, p_PhoneNumber, p_ShippingAddress);
    END IF;
END //

-- Retrieve a Customer (grabs customer information using their ID in order to process an order, deal with a customer service request, or validate information)
CREATE PROCEDURE sp_getCustomerByID(IN p_CustomerID INT)
BEGIN
    SELECT * FROM Customers WHERE CustomerID = p_CustomerID;
END //

-- Delete a Customer soft delete to archive a customer rather than hard delete in case information on past orders involving a customer is needed. Ensures only a customer without an active order can be deleted (FK relationship )
CREATE PROCEDURE sp_deleteCustomer(IN p_CustomerID INT)
BEGIN
    IF EXISTS (SELECT 1 FROM Orders WHERE CustomerID = p_CustomerID AND OrderStatus != 'Cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot delete customer with active orders.';
    ELSE
        UPDATE Customers SET isDeleted = 1 WHERE CustomerID = p_CustomerID;
    END IF;
END //

DELIMITER ;
