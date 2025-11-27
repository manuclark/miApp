-- Archivo SQL de prueba
-- Este es un ejemplo para probar el script db.py

-- Consulta simple: obtener la fecha actual del servidor
SELECT GETDATE() AS FechaActual;
GO

-- Consulta de información del servidor
SELECT 
    @@VERSION AS VersionSQL,
    DB_NAME() AS NombreBaseDatos,
    SYSTEM_USER AS Usuario;
GO

-- Consulta: listar todas las tablas en la base de datos
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE
FROM 
    INFORMATION_SCHEMA.TABLES
ORDER BY 
    TABLE_SCHEMA, 
    TABLE_NAME;
GO
