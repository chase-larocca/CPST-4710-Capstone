CREATE VIEW vw_UserRoles AS
SELECT UserID, FirstName, LastName, Email, Role, CreatedAt, LastLogin
FROM Users;
