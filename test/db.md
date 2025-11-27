# db.py - Ejecutor de Scripts SQL

Script de Python para ejecutar archivos SQL contra Azure SQL Database de forma automatizada.

## 📋 Descripción

`db.py` es una herramienta de línea de comandos que permite ejecutar scripts SQL almacenados en archivos `.sql` contra una base de datos Azure SQL. El script maneja automáticamente la configuración del entorno, la conexión a la base de datos y la ejecución de múltiples declaraciones SQL.

## 🚀 Características

- ✅ **Activación automática del entorno virtual**: Detecta y activa el entorno virtual `venv` automáticamente
- ✅ **Carga de variables de entorno**: Lee la configuración de conexión desde el archivo `.env`
- ✅ **Búsqueda automática**: Busca los archivos SQL en la carpeta `DB/`
- ✅ **Soporte para múltiples declaraciones**: Maneja scripts con múltiples comandos SQL separados por `GO`
- ✅ **Resultados formateados**: Muestra los resultados de las consultas en formato tabular
- ✅ **Manejo de transacciones**: Commit automático después de cada declaración exitosa
- ✅ **Manejo de errores**: Rollback automático en caso de error

## 📁 Estructura de Archivos

```
miApp/
├── .env                    # Variables de entorno (configuración de DB)
├── venv/                   # Entorno virtual de Python
└── test/
    ├── db.py              # Script ejecutor
    ├── db.md              # Esta documentación
    └── DB/                # Carpeta con scripts SQL
        ├── test.sql
        ├── create_tables.sql
        └── seed_data.sql
```

## ⚙️ Requisitos Previos

1. **Python 3.x** instalado
2. **Entorno virtual** creado en `venv/`
3. **Dependencias instaladas**:
   - `pyodbc`
   - `python-dotenv`
4. **ODBC Driver 18 for SQL Server** instalado
5. **Archivo .env** configurado con las credenciales de la base de datos

### Configuración del .env

El archivo `.env` debe estar en la raíz del proyecto con el siguiente formato:

```properties
HOST_DB=tu-servidor.database.windows.net
ADMIN_DB=tu-usuario
PASSWORD_DB=tu-contraseña
DATABASE_NAME=nombre-base-datos
PORT_DB=1433
DRIVER={ODBC Driver 18 for SQL Server}
```

## 🎯 Uso

### Sintaxis Básica

```bash
python db.py --file=nombre_archivo.sql
```

### Ejemplos

#### Ejecutar un archivo SQL específico

```bash
# Desde la carpeta test/
python db.py --file=test.sql
```

#### Ejecutar desde otra ubicación

```bash
# Desde la raíz del proyecto
python test/db.py --file=create_tables.sql
```

#### Ver ayuda

```bash
python db.py --help
```

## 📝 Formato de Archivos SQL

Los archivos SQL deben estar ubicados en la carpeta `test/DB/` y pueden contener:

### Declaración simple

```sql
SELECT * FROM Productos;
```

### Múltiples declaraciones con GO

```sql
-- Consulta 1
SELECT COUNT(*) FROM Productos;
GO

-- Consulta 2
SELECT * FROM Productos WHERE Precio > 100;
GO

-- Insertar datos
INSERT INTO Productos (Nombre, Precio) VALUES ('Producto A', 150);
GO
```

### Comandos DDL

```sql
-- Crear tabla
CREATE TABLE Usuarios (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100),
    Email NVARCHAR(100)
);
GO

-- Crear índice
CREATE INDEX IX_Usuarios_Email ON Usuarios(Email);
GO
```

## 📊 Salida del Script

El script proporciona retroalimentación detallada durante la ejecución:

```
============================================================
  Ejecutor de Scripts SQL - Azure SQL Database
============================================================

✓ Entorno virtual activado: C:\...\venv
✓ Variables de entorno cargadas desde: C:\...\.env
✓ Archivo SQL leído: C:\...\test\DB\test.sql
Conectando a: servidor.database.windows.net/base-datos...
✓ Conexión establecida exitosamente

============================================================
Ejecutando: test.sql
============================================================

[1/3] Ejecutando declaración...
✓ Resultados (5 filas):

Id | Nombre | Precio
-------------------
1  | Producto A | 100
2  | Producto B | 200
...

[2/3] Ejecutando declaración...
✓ Declaración ejecutada exitosamente (3 filas afectadas)

============================================================
✓ Todas las declaraciones ejecutadas correctamente
============================================================

✓ Conexión cerrada
```

## 🎨 Tipos de Resultados

### Consultas SELECT

Muestra los resultados en formato tabular con encabezados de columna (limitado a 100 filas en pantalla).

### Comandos INSERT/UPDATE/DELETE

Muestra el número de filas afectadas.

### Comandos DDL (CREATE/ALTER/DROP)

Confirma la ejecución exitosa del comando.

## ⚠️ Manejo de Errores

### Error: Archivo no encontrado

```
✗ Error: El archivo 'archivo.sql' no existe en C:\...\test\DB
```

**Solución**: Verificar que el archivo existe en la carpeta `DB/` con la extensión `.sql`

### Error: Conexión a base de datos

```
✗ Error al conectar a la base de datos: ...
```

**Solución**: Verificar las credenciales en el archivo `.env` y la conectividad a Azure

### Error: Variables de entorno faltantes

```
✗ Error: Faltan variables de entorno requeridas en .env
  Requeridas: HOST_DB, ADMIN_DB, PASSWORD_DB, DATABASE_NAME
```

**Solución**: Completar todas las variables requeridas en el archivo `.env`

### Error en declaración SQL

```
✗ Error en la declaración 2: Invalid object name 'TablaInexistente'
```

**Solución**: Revisar la sintaxis SQL y los nombres de objetos en el archivo `.sql`

## 💡 Casos de Uso

### 1. Crear tablas iniciales

```bash
python db.py --file=create_schema.sql
```

### 2. Insertar datos de prueba

```bash
python db.py --file=seed_data.sql
```

### 3. Ejecutar migraciones

```bash
python db.py --file=migration_v1.sql
```

### 4. Ejecutar consultas de análisis

```bash
python db.py --file=analytics_report.sql
```

### 5. Limpieza de datos

```bash
python db.py --file=cleanup.sql
```

## 🔒 Seguridad

- Las credenciales se almacenan en el archivo `.env` (no incluir en control de versiones)
- La conexión usa encriptación (Encrypt=yes)
- Validación de certificados habilitada (TrustServerCertificate=no)
- Timeout de conexión configurado a 30 segundos

## 🛠️ Solución de Problemas

### El entorno virtual no se activa

Verificar que existe la carpeta `venv/` en la raíz del proyecto:

```bash
# Crear entorno virtual si no existe
python -m venv venv
```

### El driver ODBC no está instalado

Instalar el driver ODBC 18:

```bash
winget install Microsoft.msodbcsql.18
```

### Permisos insuficientes en la base de datos

Verificar que el usuario tenga los permisos necesarios para ejecutar las operaciones SQL requeridas.

## 📚 Referencias

- [Documentación pyodbc](https://github.com/mkleehammer/pyodbc/wiki)
- [ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- [Azure SQL Database](https://learn.microsoft.com/en-us/azure/azure-sql/)

## 📄 Licencia

Este script es parte del proyecto miApp.

---

**Última actualización**: 26 de noviembre de 2025
