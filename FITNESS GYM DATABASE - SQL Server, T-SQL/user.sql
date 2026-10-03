CREATE LOGIN Owner WITH PASSWORD = 'owner';

USE Sali;

CREATE USER Owner FOR LOGIN Owner;

EXEC sp_addrolemember 'db_owner', 'Owner';





CREATE LOGIN ManagerSali WITH PASSWORD = 'manager';

USE Sali;

CREATE USER ManagerSala FOR LOGIN ManagerSali;

GRANT CREATE TABLE, ALTER TO Manager;

REVOKE SELECT, INSERT, UPDATE, DELETE, ALTER ON dbo.Sali FROM Manager;
REVOKE SELECT, INSERT, UPDATE, DELETE, ALTER ON dbo.Audit_modificari FROM Manager;
REVOKE SELECT, INSERT, UPDATE, DELETE, ALTER ON dbo.Istoric_Inscrieri FROM Manager;

EXEC sp_addrolemember 'Manager', 'ManagerSala';







CREATE LOGIN Antrenor WITH PASSWORD = 'antrenor';

USE Sali;

CREATE USER Antrenor1 FOR LOGIN Antrenor;

CREATE ROLE Antrenor;

GRANT SELECT, INSERT, UPDATE ON dbo.Cursuri TO Antrenor;
GRANT SELECT, INSERT, UPDATE ON dbo.Programari_Cursuri TO Antrenor;

EXEC sp_addrolemember 'Antrenor', 'Antrenor1';
