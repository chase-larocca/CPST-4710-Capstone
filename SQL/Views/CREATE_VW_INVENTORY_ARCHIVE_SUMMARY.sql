CREATE VIEW vw_InventoryArchiveSummary AS
SELECT ArchiveID, SKU, ItemName, ItemPrice, ItemQuantity, Supplier, FinalUpdateAt, ArchivedDate
FROM InventoryArchive;
