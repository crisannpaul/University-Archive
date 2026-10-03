CREATE TRIGGER InregistrareSchimbariTablouri
ON DATABASE 
FOR CREATE_TABLE, ALTER_TABLE, DROP_TABLE
AS
BEGIN
    DECLARE @TipSchimbare NVARCHAR(100), @NumeObiect NVARCHAR(100);

    SET @TipSchimbare = EVENTDATA().value('(/EVENT_INSTANCE/EventType)[1]', 'NVARCHAR(100)');
    SET @NumeObiect = EVENTDATA().value('(/EVENT_INSTANCE/ObjectName)[1]', 'NVARCHAR(100)');

    INSERT INTO AuditareSchimbareTabele (TipSchimbare, NumeObiect)
    VALUES (@TipSchimbare, @NumeObiect);
END;
