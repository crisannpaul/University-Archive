CREATE TABLE Sali (
    ID_Sala INT PRIMARY KEY,
    Nume NVARCHAR(100),
    Oras NVARCHAR(100),
    Adresa NVARCHAR(255)
);

CREATE TABLE Membri (
    ID_Membru INT PRIMARY KEY,
    Nume NVARCHAR(100),
    Prenume NVARCHAR(100),
    Email NVARCHAR(100),
    Telefon NVARCHAR(15)
);

CREATE TABLE Abonamente (
    ID_Abonament INT PRIMARY KEY,
    Tip_Abonament NVARCHAR(100),
    Durata INT,
    Pret INT
);

CREATE TABLE Inscrieri (
    ID_Membru INT FOREIGN KEY REFERENCES Membri(ID_Membru),
    ID_Abonament INT FOREIGN KEY REFERENCES Abonamente(ID_Abonament),
    ID_Sala INT FOREIGN KEY REFERENCES Sali(ID_Sala),
    Data_Inceput DATE,
    Data_Sfarsit DATE
);

CREATE TABLE Antrenori (
    ID_Antrenor INT PRIMARY KEY,
    Nume NVARCHAR(100),
    Prenume NVARCHAR(100),
    Specializare NVARCHAR(100),
    ID_Sala INT FOREIGN KEY REFERENCES Sali(ID_Sala),
    Salar INT
);

CREATE TABLE Cursuri (
    ID_Curs INT PRIMARY KEY,
    Nume_Curs NVARCHAR(100),
    ID_Antrenor INT FOREIGN KEY REFERENCES Antrenori(ID_Antrenor),
    Ziua_Saptamanii NVARCHAR(20),
    Ora_Start TIME
);

CREATE TABLE Programari_Cursuri (
    ID_Membru INT FOREIGN KEY REFERENCES Membri(ID_Membru),
    ID_Curs INT FOREIGN KEY REFERENCES Cursuri(ID_Curs),
    Data_Programare DATE
);

CREATE TABLE Echipamente (
    ID_Echipament INT PRIMARY KEY,
    Tip_Echipament NVARCHAR(100),
    Stare NVARCHAR(50),
    Data_Achizitiei DATE,
    ID_Sala INT FOREIGN KEY REFERENCES Sali(ID_Sala)
);

CREATE TABLE Angajati (
    ID_Angajat INT PRIMARY KEY,
    Nume NVARCHAR(100),
    Prenume NVARCHAR(100),
    Functie NVARCHAR(100),
    ID_Sala INT FOREIGN KEY REFERENCES Sali(ID_Sala),
    Salar INT
);

CREATE TABLE Audit_Modificari (
    ID_Schimbare INT PRIMARY KEY IDENTITY(1,1),
    TipSchimbare NVARCHAR(100),
    NumeObiect NVARCHAR(100),
    DataSchimbare DATETIME DEFAULT GETDATE()
);

CREATE TABLE Istoric_Inscrieri (
    ID_Istoric INT PRIMARY KEY IDENTITY(1,1),
    ID_Membru INT FOREIGN KEY REFERENCES Membri(ID_Membru),
    ID_Abonament INT FOREIGN KEY REFERENCES Abonamente(ID_Abonament),
    ID_Sala INT FOREIGN KEY REFERENCES Sali(ID_Sala),
    Data_Inceput DATE,
    Data_Sfarsit DATE,
    Data_Expirare DATE DEFAULT GETDATE()
);


