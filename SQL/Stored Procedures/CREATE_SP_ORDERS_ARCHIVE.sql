DELIMITER //

-- Archive an Order  (archives an order thats very old or not needed anymore. doesn’t fully delete it for record purposes.)
CREATE PROCEDURE sp_archiveOrder(IN p_OrderID INT, IN p_Reason TEXT)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = p_OrderID) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order not found.';
    END IF;

    INSERT INTO OrdersArchive (OrderID, CustomerID, OrderDate, TotalPrice, OrderStatus, ArchivedReason)
    SELECT OrderID, CustomerID, OrderDate, TotalPrice, OrderStatus, p_Reason 
    FROM Orders 
    WHERE OrderID = p_OrderID;

    DELETE FROM Orders WHERE OrderID = p_OrderID;
END //

DELIMITER ;
