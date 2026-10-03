CREATE INDEX idx_ID_Membru ON Inscrieri(ID_Membru);

CREATE CLUSTERED INDEX idx_clustered_ID_Curs ON Programari_Cursuri(ID_Membru, ID_Curs);
