#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ejecutar archivos SQL contra Azure SQL Database.
Uso: python db.py --file=test.sql
Los archivos .sql deben estar en la carpeta DB/
"""

import sys
import os
import argparse
import pyodbc
from pathlib import Path
from dotenv import load_dotenv

# Activar entorno virtual automáticamente
def activate_venv():
    """Activa el entorno virtual si existe"""
    # Obtener la ruta base del proyecto (dos niveles arriba desde test/)
    base_dir = Path(__file__).resolve().parent.parent
    venv_path = base_dir / "venv"
    
    if venv_path.exists():
        # Agregar el entorno virtual al path de Python
        if sys.platform == "win32":
            site_packages = venv_path / "Lib" / "site-packages"
            scripts_dir = venv_path / "Scripts"
        else:
            site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
            scripts_dir = venv_path / "bin"
        
        # Agregar al path si no está ya
        if str(site_packages) not in sys.path:
            sys.path.insert(0, str(site_packages))
        
        # Actualizar PATH para incluir Scripts/bin
        os.environ["PATH"] = f"{scripts_dir}{os.pathsep}{os.environ.get('PATH', '')}"
        
        print(f"✓ Entorno virtual activado: {venv_path}")
    else:
        print(f"⚠ Advertencia: No se encontró el entorno virtual en {venv_path}")


# Activar el entorno virtual al inicio
activate_venv()

# Cargar variables de entorno desde .env
def load_environment():
    """Carga las variables de entorno desde el archivo .env"""
    base_dir = Path(__file__).resolve().parent.parent
    env_file = base_dir / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✓ Variables de entorno cargadas desde: {env_file}")
    else:
        print(f"⚠ Advertencia: No se encontró el archivo .env en {env_file}")
        sys.exit(1)


# Cargar entorno
load_environment()


def get_db_connection():
    """Crea y retorna una conexión a la base de datos"""
    try:
        # Obtener configuración desde variables de entorno
        host = os.getenv("HOST_DB")
        admin = os.getenv("ADMIN_DB")
        password = os.getenv("PASSWORD_DB")
        database = os.getenv("DATABASE_NAME", "master")
        port = os.getenv("PORT_DB", "1433")
        driver = os.getenv("DRIVER", "{ODBC Driver 18 for SQL Server}")
        
        # Validar que todas las variables estén configuradas
        if not all([host, admin, password, database]):
            print("✗ Error: Faltan variables de entorno requeridas en .env")
            print("  Requeridas: HOST_DB, ADMIN_DB, PASSWORD_DB, DATABASE_NAME")
            sys.exit(1)
        
        # Construir cadena de conexión
        conn_string = (
            f"DRIVER={driver};"
            f"SERVER={host},{port};"
            f"DATABASE={database};"
            f"UID={admin};"
            f"PWD={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
        
        print(f"Conectando a: {host}/{database}...")
        conn = pyodbc.connect(conn_string)
        print("✓ Conexión establecida exitosamente")
        return conn
    
    except Exception as e:
        print(f"✗ Error al conectar a la base de datos: {e}")
        sys.exit(1)


def read_sql_file(filename):
    """Lee el contenido de un archivo SQL desde la carpeta DB/"""
    # Ruta a la carpeta DB
    db_folder = Path(__file__).resolve().parent / "DB"
    sql_file = db_folder / filename
    
    # Verificar que el archivo existe
    if not sql_file.exists():
        print(f"✗ Error: El archivo '{filename}' no existe en {db_folder}")
        sys.exit(1)
    
    # Verificar que sea un archivo .sql
    if sql_file.suffix.lower() != '.sql':
        print(f"✗ Error: El archivo '{filename}' no es un archivo .sql")
        sys.exit(1)
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ Archivo SQL leído: {sql_file}")
        return content
    except Exception as e:
        print(f"✗ Error al leer el archivo: {e}")
        sys.exit(1)


def execute_sql(conn, sql_content, filename):
    """Ejecuta el contenido SQL y muestra los resultados"""
    try:
        cursor = conn.cursor()
        
        # Dividir el contenido en declaraciones individuales (separadas por GO)
        statements = [stmt.strip() for stmt in sql_content.split('GO') if stmt.strip()]
        
        print(f"\n{'='*60}")
        print(f"Ejecutando: {filename}")
        print(f"{'='*60}\n")
        
        total_statements = len(statements)
        for idx, statement in enumerate(statements, 1):
            if not statement:
                continue
            
            print(f"[{idx}/{total_statements}] Ejecutando declaración...")
            
            try:
                cursor.execute(statement)
                
                # Intentar obtener resultados si hay
                try:
                    columns = [column[0] for column in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                    
                    if rows:
                        # Mostrar resultados
                        print(f"\n✓ Resultados ({len(rows)} filas):")
                        
                        # Encabezados
                        if columns:
                            print("\n" + " | ".join(columns))
                            print("-" * (len(" | ".join(columns))))
                        
                        # Filas (limitar a 100 para no saturar la salida)
                        for row in rows[:100]:
                            print(" | ".join(str(value) for value in row))
                        
                        if len(rows) > 100:
                            print(f"\n... ({len(rows) - 100} filas más)")
                    else:
                        print("✓ Consulta ejecutada exitosamente (sin resultados)")
                
                except pyodbc.Error:
                    # No hay resultados (INSERT, UPDATE, DELETE, etc.)
                    if cursor.rowcount >= 0:
                        print(f"✓ Declaración ejecutada exitosamente ({cursor.rowcount} filas afectadas)")
                    else:
                        print("✓ Declaración ejecutada exitosamente")
                
                # Commit después de cada declaración exitosa
                conn.commit()
                
            except pyodbc.Error as e:
                print(f"✗ Error en la declaración {idx}: {e}")
                conn.rollback()
                raise
        
        print(f"\n{'='*60}")
        print(f"✓ Todas las declaraciones ejecutadas correctamente")
        print(f"{'='*60}\n")
        
        cursor.close()
        
    except Exception as e:
        print(f"\n✗ Error al ejecutar SQL: {e}")
        conn.rollback()
        sys.exit(1)


def main():
    """Función principal"""
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description='Ejecuta archivos SQL contra Azure SQL Database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python db.py --file=test.sql
  python db.py --file=create_tables.sql
  python db.py --file=seed_data.sql

Los archivos .sql deben estar ubicados en la carpeta DB/
        """
    )
    
    parser.add_argument(
        '--file',
        type=str,
        required=True,
        help='Nombre del archivo SQL a ejecutar (debe estar en la carpeta DB/)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  Ejecutor de Scripts SQL - Azure SQL Database")
    print("="*60 + "\n")
    
    # Leer archivo SQL
    sql_content = read_sql_file(args.file)
    
    # Conectar a la base de datos
    conn = get_db_connection()
    
    try:
        # Ejecutar SQL
        execute_sql(conn, sql_content, args.file)
    finally:
        # Cerrar conexión
        conn.close()
        print("✓ Conexión cerrada\n")


if __name__ == "__main__":
    main()
