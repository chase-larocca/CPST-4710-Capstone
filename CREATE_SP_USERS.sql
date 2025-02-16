DELIMITER %%

CREATE PROCEDURE sp_Users_CreateOrUpdate(
    IN p_UserID INT,
    IN p_FirstName VARCHAR(255),
    IN p_LastName VARCHAR(255),
    IN p_Email VARCHAR(255),
    IN p_PasswordHash VARCHAR(255),
    IN p_Role ENUM('Admin', 'Employee', 'Manager', 'Customer')
)
BEGIN
    IF EXISTS (SELECT 1 FROM Users WHERE UserID = p_UserID) THEN
        UPDATE Users 
        SET FirstName = p_FirstName, LastName = p_LastName, Email = p_Email, PasswordHash = p_PasswordHash, Role = p_Role
        WHERE UserID = p_UserID;
    ELSE
        INSERT INTO Users (FirstName, LastName, Email, PasswordHash, Role)
        VALUES (p_FirstName, p_LastName, p_Email, p_PasswordHash, p_Role);
    END IF;
END %%

CREATE PROCEDURE sp_Users_Read()
BEGIN
    SELECT * FROM Users;
END %%

CREATE PROCEDURE sp_Users_Delete(IN p_UserID INT)
BEGIN
    DELETE FROM Users WHERE UserID = p_UserID;
END %%