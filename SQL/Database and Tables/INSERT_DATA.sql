-- DATA INSERTS FOR SITE DATA POPULATION
 SELECT * FROM ttops.inventory; 
 SELECT * FROM ttops.inventorycolors; 

-- INVENTORY DATA

INSERT INTO Inventory (SKU, ItemName, ItemDescription, Price, QuantityInStock, Supplier, RestockThreshold, CreatedAt, UpdatedAt)
VALUES
('GOFIT-DT-PURPLE', 'GoFit Double Thick Yoga Mat', 'Extra-thick mat for comfort and support', 39.99, 50, 'GoFit', 10, NOW(), NOW()),
('GOFIT-GREY', 'GoFit Yoga Mat', 'Standard durable GoFit yoga mat', 24.99, 50, 'GoFit', 10, NOW(), NOW()),
('GOFIT-PATTERN', 'GoFit Pattern Yoga Mat w/ Yoga Pose Chart', 'Patterned mat with wall chart', 21.49, 50, 'GoFit', 10, NOW(), NOW()),
('GOFIT-SUMMIT', 'GoFit Summit Yoga Mat', 'Premium yoga mat for professionals', 69.99, 50, 'GoFit', 10, NOW(), NOW()),
('GOFIT-KIT', 'GoFit Yoga Kit: Mat, Block, Strap, Chart', 'All-in-one yoga kit for beginners', 29.99, 50, 'GoFit', 10, NOW(), NOW()),
('GOFIT-DELUXE', 'GoFit Deluxe Pilates Foam Mat', 'Foam mat for yoga and pilates routines', 34.99, 50, 'GoFit', 10, NOW(), NOW());


-- INVENTORY COLOR DATA 

INSERT INTO Inventory (SKU, ItemName, ItemDescription, Price, QuantityInStock, Supplier, RestockThreshold, CreatedAt, UpdatedAt)
VALUES 
('BUB-40OZ-BLK', 'Bubba 40 oz. Radiant Stainless Steel Bottle', 'Rubberized stainless steel bottle with matte finish', 25.99, 100, 'Bubba Brands', 10, NOW(), NOW()),
('BUB-HERO-BLK', 'Bubba Hero Mug', 'Travel mug with handle and vacuum insulation', 17.99, 100, 'Bubba Brands', 10, NOW(), NOW()),
('BUB-32OZ-STRAW', 'Bubba 32 oz. Radiant Bottle w/ Straw', 'Rubberized stainless steel bottle with built-in straw', 22.99, 100, 'Bubba Brands', 10, NOW(), NOW()),
('BUB-FLO-16OZ', 'Bubba Flo Refresh 16oz Bottle', 'Crystal Ice bottle with Rock Candy and Kiwi color wash', 12.99, 100, 'Bubba Brands', 10, NOW(), NOW()),
('BUB-32OZ-LIC', 'Bubba 32 oz. Radiant Bottle - Licorice', 'Matte black stainless steel water bottle', 22.99, 100, 'Bubba Brands', 10, NOW(), NOW());

-- INVENTORY COLOR DATA

INSERT INTO InventoryColors (SKU, ColorName)
VALUES 
('BUB-40OZ-BLK', 'Black'),
('BUB-40OZ-BLK', 'Navy'),
('BUB-HERO-BLK', 'Black'),
('BUB-32OZ-STRAW', 'Blue'),
('BUB-FLO-16OZ', 'Green'),
('BUB-FLO-16OZ', 'Blue-Green'),
('BUB-32OZ-LIC', 'Licorice');



INSERT INTO InventoryColors (SKU, ColorName)
VALUES
('GOFIT-DT-PURPLE', 'Purple'),
('GOFIT-GREY', 'Grey'),
('GOFIT-PATTERN', 'Pink'),
('GOFIT-PATTERN', 'Green'),
('GOFIT-PATTERN', 'Blue'),
('GOFIT-SUMMIT', 'Purple'),
('GOFIT-KIT', 'Blue'),
('GOFIT-DELUXE', 'Blue');

INSERT INTO Orders (OrderNumber, CustomerID, ShippingDestination, NumberOfItems, TotalPrice, OrderStatus)
VALUES 
('SB000001', 1, '7 FRANKFORD AVE BLDG 219 ANNISTON AL 36201-0000', 1111, 27941.98, 'Pending'),
('SB000002', 2, '7 FRANKFORD AVE BLDG 219 ANNISTON AL 36201-0000', 200, 4599.00, 'Pending'),
('SB000003', 1, '7 FRANKFORD AVE BLDG 219 ANNISTON AL 36201-0000', 552, 6899.00, 'Shipped'),
('SB000004', 3, '7 FRANKFORD AVE BLDG 219 ANNISTON AL 36201-0000', 3, 99.99, 'Delivered'),
('SB000005', 2, '7 FRANKFORD AVE BLDG 219 ANNISTON AL 36201-0000', 15, 229.99, 'Cancelled');






