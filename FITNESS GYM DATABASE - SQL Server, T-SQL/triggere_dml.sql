CREATE TRIGGER trg_CheckInscriere
ON Inscrieri
INSTEAD OF INSERT
AS
BEGIN
    DECLARE @ID_Membru INT, @Tip_Abonament NVARCHAR(100), @NumeMembru NVARCHAR(200), @NumeSala NVARCHAR(100);

    -- Extragerea informațiilor despre membru și abonamentul inserat
    SELECT @ID_Membru = ins.ID_Membru, @Tip_Abonament = a.Tip_Abonament, @NumeMembru = m.Nume + ' ' + m.Prenume
    FROM inserted ins
    JOIN Abonamente a ON ins.ID_Abonament = a.ID_Abonament
    JOIN Membri m ON ins.ID_Membru = m.ID_Membru;

    -- Verifică dacă membrul are deja un abonament și obținerea sălii
    IF EXISTS (SELECT 1 FROM Inscrieri i JOIN Sali s ON i.ID_Sala = s.ID_Sala WHERE i.ID_Membru = @ID_Membru)
    BEGIN
        SELECT @NumeSala = s.Nume
        FROM Inscrieri i
        JOIN Sali s ON i.ID_Sala = s.ID_Sala
        WHERE i.ID_Membru = @ID_Membru;

        RAISERROR ('Membrul %s are deja un abonament activ (%s) la sala %s. Inserarea a fost anulată.', 16, 1, @NumeMembru, @Tip_Abonament, @NumeSala);
    END
    ELSE
    BEGIN
        -- Dacă membrul nu are un abonament activ, permite inserarea
        INSERT INTO Inscrieri (ID_Membru, ID_Abonament, ID_Sala, Data_Inceput, Data_Sfarsit)
        SELECT ID_Membru, ID_Abonament, ID_Sala, Data_Inceput, Data_Sfarsit FROM inserted;
    END
END;



CREATE TRIGGER trg_VerificaProgramareCurs
ON Programari_Cursuri
INSTEAD OF INSERT
AS
BEGIN
    DECLARE @ID_Membru INT, @ID_Curs INT, @ID_SalaCurs INT, @NumeMembru NVARCHAR(50);

    -- Extragerea informațiilor despre membru și cursul inserat
    SELECT @ID_Membru = ins.ID_Membru, @ID_Curs = ins.ID_Curs
    FROM inserted ins;

    -- Obținerea ID-ului sălii unde se ține cursul
    SELECT @ID_SalaCurs = a.ID_Sala
    FROM Cursuri c
    JOIN Antrenori a ON c.ID_Antrenor = a.ID_Antrenor
    WHERE c.ID_Curs = @ID_Curs;

    -- Verifică dacă membrul este înscriș la sala unde se ține cursul
    IF NOT EXISTS (SELECT 1 FROM Inscrieri WHERE ID_Membru = @ID_Membru AND ID_Sala = @ID_SalaCurs)
    BEGIN
		SELECT @NumeMembru =  m.Nume + ' ' + m.Prenume
		FROM Membri m
		WHERE m.ID_Membru = @ID_Membru

        RAISERROR ('Membrul %s nu este inscris la sala unde se tine cursul.', 16, 1, @NumeMembru);
    END
    ELSE
    BEGIN
        -- Dacă membrul este înscriș la sala respectivă, permite inserarea
        INSERT INTO Programari_Cursuri (ID_Membru, ID_Curs, Data_Programare)
        SELECT ID_Membru, ID_Curs, Data_Programare FROM inserted;
    END
END;



CREATE TRIGGER trg_MarireSalariuAntrenor
ON Cursuri
AFTER INSERT
AS
BEGIN
    -- Actualizarea salariului antrenorilor pentru fiecare curs nou adăugat
    UPDATE Antrenori
    SET Salar = Salar + 150
    FROM Antrenori
    JOIN inserted ON Antrenori.ID_Antrenor = inserted.ID_Antrenor;
END;

