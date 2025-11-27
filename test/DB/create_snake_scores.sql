-- ============================================================
-- Tabla para guardar los scores del juego de la serpiente
-- ============================================================

-- Eliminar tabla si existe (para desarrollo)
IF OBJECT_ID('dbo.SnakeScores', 'U') IS NOT NULL
    DROP TABLE dbo.SnakeScores;
GO

-- Crear la tabla SnakeScores
CREATE TABLE dbo.SnakeScores (
    Id INT PRIMARY KEY IDENTITY(1,1),
    PlayerName NVARCHAR(100) NOT NULL,
    Score INT NOT NULL,
    GameDate DATETIME NOT NULL DEFAULT GETDATE(),
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- Crear índices para optimizar las consultas
CREATE INDEX IX_SnakeScores_Score ON dbo.SnakeScores(Score DESC);
GO

CREATE INDEX IX_SnakeScores_GameDate ON dbo.SnakeScores(GameDate);
GO

-- Insertar algunos datos de prueba
INSERT INTO dbo.SnakeScores (PlayerName, Score, GameDate)
VALUES 
    ('Jugador Demo', 150, GETDATE()),
    ('Pro Player', 280, GETDATE()),
    ('Snake Master', 320, GETDATE()),
    ('Novato', 50, GETDATE()),
    ('Experto', 200, GETDATE());
GO

-- Verificar la creación
SELECT TOP 10 
    Id,
    PlayerName,
    Score,
    FORMAT(GameDate, 'dd/MM/yyyy HH:mm') as FechaJuego
FROM dbo.SnakeScores
ORDER BY Score DESC;
GO
