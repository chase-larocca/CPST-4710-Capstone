DELIMITER %%


-- CREATE INVENTORY CREATE OR UPDATE PROCEDURE
CREATE PROCEDURE sp_Inventory_CreateOrUpdate(
    IN p_SKU INT,
    IN p_ItemName VARCHAR(255),
    IN p_ItemDescription TEXT,
    IN p_Price DECIMAL(10,2),
    IN p_QuantityInStock INT,
    IN p_Supplier VARCHAR(255),
    IN p_RestockThreshold INT
)
BEGIN
    IF EXISTS (SELECT 1 FROM Inventory WHERE SKU = p_SKU) THEN
        UPDATE Inventory 
        SET ItemName = p_ItemName, ItemDescription = p_ItemDescription, Price = p_Price, 
            QuantityInStock = p_QuantityInStock, Supplier = p_Supplier, RestockThreshold = p_RestockThreshold
        WHERE SKU = p_SKU;
    ELSE
        INSERT INTO Inventory (ItemName, ItemDescription, Price, QuantityInStock, Supplier, RestockThreshold)
        VALUES (p_ItemName, p_ItemDescription, p_Price, p_QuantityInStock, p_Supplier, p_RestockThreshold);
    END IF;
END %%


-- CREATE INVENTORY READ PROCEDURE
USE TTOps;

DELIMITER %%

CREATE PROCEDURE sp_Inventory_Read()
BEGIN
    SELECT * FROM Inventory;
END %%

-- CREATE INVENTORY DELETE PROCEDURE
USE TTOps;

DELIMITER %%

CREATE PROCEDURE sp_Inventory_Delete(IN p_SKU INT)
BEGIN
    DELETE FROM Inventory WHERE SKU = p_SKU;
END %%

-- CREATE INVENTORY GRAB ITEM PROCEDURE (WITH COLORS)
USE TTOps;

DELIMITER %%
CREATE PROCEDURE sp_InventoryWithColors()
BEGIN
  SELECT 
    i.SKU,
    i.ItemName,
    i.ItemDescription,
    i.Price,
    i.QuantityInStock,
    i.Supplier,
    i.RestockThreshold,
    i.CreatedAt,
    i.UpdatedAt,
    c.ColorName
  FROM Inventory i
  LEFT JOIN InventoryColors c ON i.SKU = c.SKU;
END %%

DELIMITER ;
