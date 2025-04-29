DELIMITER %%

CREATE PROCEDURE sp_InventoryArchive_Insert(
    IN p_SKU INT, IN p_ItemName VARCHAR(255), IN p_ItemDescription TEXT, 
    IN p_ItemPrice DECIMAL(10,2), IN p_ItemQuantity INT, IN p_Supplier VARCHAR(255),
    IN p_CreatedAt TIMESTAMP, IN p_FinalUpdateAt TIMESTAMP
)
BEGIN
    INSERT INTO InventoryArchive (SKU, ItemName, ItemDescription, ItemPrice, ItemQuantity, Supplier, CreatedAt, FinalUpdateAt)
    VALUES (p_SKU, p_ItemName, p_ItemDescription, p_ItemPrice, p_ItemQuantity, p_Supplier, p_CreatedAt, p_FinalUpdateAt);
END %%

CREATE PROCEDURE sp_InventoryArchive_Read()
BEGIN
    SELECT * FROM InventoryArchive;
END %%

CREATE PROCEDURE sp_InventoryArchive_Delete(IN p_ArchiveID INT)
BEGIN
    DELETE FROM InventoryArchive WHERE ArchiveID = p_ArchiveID;
END %%