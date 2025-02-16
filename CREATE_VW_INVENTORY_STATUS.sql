CREATE VIEW vw_InventoryStatus AS
SELECT SKU, ItemName, QuantityInStock, RestockThreshold,
       CASE 
           WHEN QuantityInStock <= RestockThreshold THEN 'Restock Needed'
           ELSE 'Sufficient Stock'
       END AS StockStatus
FROM Inventory;
