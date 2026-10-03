1.
CREATE PROCEDURE InserareInscriere
    @ID_Membru INT,
	@ID_Sala INT, 
    @Tip_Abonament NVARCHAR(100)
AS
BEGIN
    DECLARE @ID_Abonament INT;
    DECLARE @Durata INT;
    DECLARE @Data_Inceput DATE = GETDATE();
    DECLARE @Data_Sfarsit DATE;

    SELECT @ID_Abonament = ID_Abonament, @Durata = Durata
    FROM Abonamente
    WHERE Tip_Abonament = @Tip_Abonament;

    SET @Data_Sfarsit = DATEADD(DAY, @Durata, @Data_Inceput);

    INSERT INTO Inscrieri (ID_Membru, ID_Abonament, ID_Sala, Data_Inceput, Data_Sfarsit)
    VALUES (@ID_Membru, @ID_Abonament, @ID_Sala, @Data_Inceput, @Data_Sfarsit);
END;


2.
CREATE PROCEDURE AnuleazaAbonament
    @ID_Membru INT
AS
BEGIN
    IF EXISTS (SELECT 1 FROM Inscrieri WHERE ID_Membru = @ID_Membru)
    BEGIN
        DELETE FROM Inscrieri WHERE ID_Membru = @ID_Membru;
    END
END;


3. 
CREATE PROCEDURE ProgramareCurs
    @ID_Membru INT,
    @Nume_Curs NVARCHAR(100)
AS
BEGIN
    DECLARE @ID_Curs INT;
    DECLARE @Ziua_Saptamanii NVARCHAR(20);
    DECLARE @Data_Programare DATE;

    -- Selectarea ID-ului cursului și a zilei săptămânii pe baza numelui cursului
    SELECT @ID_Curs = ID_Curs, @Ziua_Saptamanii = Ziua_Saptamanii
    FROM Cursuri
    WHERE Nume_Curs = @Nume_Curs;

    -- Maparea zilei săptămânii în limba engleză
    DECLARE @Ziua_Saptamanii_Eng NVARCHAR(20);
    SET @Ziua_Saptamanii_Eng = CASE @Ziua_Saptamanii
		WHEN 'Luni' THEN 'Monday'
		WHEN 'Marti' THEN 'Tuesday'
		WHEN 'Miercuri' THEN 'Wednesday'
		WHEN 'Joi' THEN 'Thursday'
		WHEN 'Vineri' THEN 'Friday'
		WHEN 'Sambata' THEN 'Saturday'
		WHEN 'Duminica' THEN 'Sunday'
		ELSE @Ziua_Saptamanii
	END;

    -- Calcularea următoarei date pentru ziua specificată a săptămânii
    SET @Data_Programare = (SELECT TOP 1 [Date]
                            FROM (SELECT DISTINCT TOP 7
                                  DATEADD(DAY, number, CONVERT(DATE, GETDATE())) AS [Date]
                                  FROM master..spt_values
                                  WHERE [type] = 'P' AND number BETWEEN 1 AND 14) AS NextDates
                            WHERE DATENAME(WEEKDAY, [Date]) = @Ziua_Saptamanii_Eng
                            ORDER BY [Date]);

    -- Inserarea în tabelul Programari_Cursuri
    INSERT INTO Programari_Cursuri (ID_Membru, ID_Curs, Data_Programare)
    VALUES (@ID_Membru, @ID_Curs, @Data_Programare);
END;


4.
CREATE PROCEDURE ActualizeazaSalariiAntrenori
AS
BEGIN
    -- Declararea variabilelor pentru cursor
    DECLARE @ID_Antrenor INT, @NumarCursuri INT, @NouSalariu DECIMAL(10, 2);

    -- Crearea cursorului pentru a itera prin antrenori
    DECLARE cursorAntrenori CURSOR FOR
    SELECT a.ID_Antrenor, COUNT(c.ID_Curs) AS NumarCursuri
    FROM Antrenori a
    LEFT JOIN Cursuri c ON a.ID_Antrenor = c.ID_Antrenor
    GROUP BY a.ID_Antrenor;

    -- Deschiderea cursorului și preluarea primului rând
    OPEN cursorAntrenori;
    FETCH NEXT FROM cursorAntrenori INTO @ID_Antrenor, @NumarCursuri;

    -- Parcurgerea fiecărui antrenor și actualizarea salariului
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Calculul noului salariu
        SET @NouSalariu = 2000 + 150 * @NumarCursuri;

        -- Actualizarea salariului în baza de date pentru antrenorul curent
        UPDATE Antrenori
        SET Salar = @NouSalariu
        WHERE ID_Antrenor = @ID_Antrenor;

        -- Preia următorul rând
        FETCH NEXT FROM cursorAntrenori INTO @ID_Antrenor, @NumarCursuri;
    END

    -- Închiderea cursorului și eliberarea resurselor
    CLOSE cursorAntrenori;
    DEALLOCATE cursorAntrenori;
END;
GO


