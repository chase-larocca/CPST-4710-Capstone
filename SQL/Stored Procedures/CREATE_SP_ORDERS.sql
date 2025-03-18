DELIMITER //

-- Create an Order (adds a new order to the table)
CREATE PROCEDURE sp_createOrder(
    IN p_CustomerID INT,
    IN p_TotalPrice DECIMAL(10,2),
    IN p_OrderStatus ENUM('Pending', 'Shipped', 'Delivered', 'Cancelled')
)
BEGIN
    INSERT INTO Orders (CustomerID, OrderDate, TotalPrice, OrderStatus)
    VALUES (p_CustomerID, NOW(), p_TotalPrice, p_OrderStatus);
END //

-- Update an Order (updates an existing orders details if needed)
CREATE PROCEDURE sp_updateOrder(
    IN p_OrderID INT,
    IN p_TotalPrice DECIMAL(10,2),
    IN p_OrderStatus ENUM('Pending', 'Shipped', 'Delivered', 'Cancelled')
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = p_OrderID) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order not found.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM Orders 
        WHERE OrderID = p_OrderID AND OrderStatus = 'Delivered'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot modify a delivered order.';
    END IF;

    UPDATE Orders 
    SET TotalPrice = p_TotalPrice, 
        OrderStatus = p_OrderStatus
    WHERE OrderID = p_OrderID;
END //

-- Retrieve an Order (retrieves details of an order based on the ID. Can be used for tracking, verification, or cancelling)
CREATE PROCEDURE sp_getOrderByID(IN p_OrderID INT)
BEGIN
    SELECT * FROM Orders WHERE OrderID = p_OrderID;
END //

-- Cancel an Order (marks orders as cancelled rather than deleting so that all placed orders can still be tracked and accounted for)
CREATE PROCEDURE sp_cancelOrder(IN p_OrderID INT)
BEGIN
    UPDATE Orders SET OrderStatus = 'Cancelled' WHERE OrderID = p_OrderID;
END //

DELIMITER //

CREATE PROCEDURE sp_GetOrderStatuses()
BEGIN
    SELECT 
        OrderNumber,
        ShippingDestination,
        NumberOfItems,
        OrderStatus
    FROM Orders
    ORDER BY OrderDate DESC;
END //


DELIMITER ;
