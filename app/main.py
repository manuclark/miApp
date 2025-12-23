from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import pyodbc
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Cargar variables de entorno
load_dotenv()

# Versión del protocolo MCP
MCP_PROTOCOL_VERSION = "2025-06-18"

# Versiones compatibles del protocolo
COMPATIBLE_MCP_VERSIONS = ["2024-11-05", "2025-06-18"]

# Obtener configuración de base de datos desde .env
HOST_DB = os.getenv("HOST_DB")
ADMIN_DB = os.getenv("ADMIN_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
DATABASE_NAME = os.getenv("DATABASE_NAME", "master")
PORT_DB = os.getenv("PORT_DB", "1433")
DRIVER = os.getenv("DRIVER", "{ODBC Driver 18 for SQL Server}")

# Configurar rutas
BASE_DIR = Path(__file__).resolve().parent.parent
WWW_DIR = BASE_DIR / "www"


def get_db_connection_string():
    """Construir la cadena de conexión a la base de datos"""
    return (
        f"DRIVER={DRIVER};"
        f"SERVER={HOST_DB},{PORT_DB};"
        f"DATABASE={DATABASE_NAME};"
        f"UID={ADMIN_DB};"
        f"PWD={PASSWORD_DB};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )


def test_database_connection():
    """Probar la conexión a la base de datos"""
    try:
        conn_string = get_db_connection_string()
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True, "Database connection successful"
    except Exception as e:
        return False, str(e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar el ciclo de vida de la aplicación"""
    # Startup
    print("Starting up FastAPI application...")
    success, message = test_database_connection()
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ Database connection failed: {message}")
    
    yield
    
    # Shutdown
    print("Shutting down FastAPI application...")


# Crear la aplicación FastAPI
app = FastAPI(
    title="miApp API",
    description="API con FastAPI y conexión a Azure SQL Database",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos del frontend Angular
if WWW_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(WWW_DIR / "assets")), name="assets")


# ============================================================
# Modelos Pydantic para Snake Scores
# ============================================================

class SnakeScoreCreate(BaseModel):
    PlayerName: str
    Score: int

class SnakeScoreResponse(BaseModel):
    Id: int
    PlayerName: str
    Score: int
    GameDate: str
    CreatedAt: str


# ============================================================
# Modelos Pydantic para MCP Tools (JSON-RPC 2.0)
# ============================================================

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None
    id: Optional[Union[str, int]] = None


class MCPToolCall(BaseModel):
    tool_name: str
    arguments: Optional[Dict[str, Any]] = None


class MCPToolResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None


@app.get("/api")
async def api_root():
    """Endpoint raíz de la API"""
    return {
        "message": "Bienvenido a miApp API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "api": "/api",
            "mcp": {
                "list_tools": "/api/mcp/tools",
                "call_tool": "/api/mcp/call-tool"
            }
        }
    }


# ============================================================
# Endpoints para MCP Tools (JSON-RPC 2.0)
# ============================================================

@app.post("/mcp")
async def mcp_jsonrpc_handler(request: JSONRPCRequest):
    """
    Manejador principal de JSON-RPC 2.0 para MCP.
    Soporta los métodos estándar de MCP.
    """
    try:
        method = request.method
        params = request.params or {}
        request_id = request.id
        
        # Método: initialize
        if method == "initialize":
            return JSONRPCResponse(
                result={
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "serverInfo": {
                        "name": "miApp MCP Server",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    }
                },
                id=request_id
            )
        
        # Método: tools/list
        elif method == "tools/list":
            tools = [
                {
                    "name": "get_user_demo",
                    "description": "Obtiene datos de demostración de un usuario. Retorna información de perfil con email benito@gmail.com, nombre, estadísticas y preferencias.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "include_details": {
                                "type": "boolean",
                                "description": "Si es true, incluye detalles adicionales del usuario como estadísticas, preferencias y fechas",
                                "default": True
                            }
                        }
                    }
                }
            ]
            
            return JSONRPCResponse(
                result={"tools": tools},
                id=request_id
            )
        
        # Método: tools/call
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "get_user_demo":
                include_details = arguments.get("include_details", True)
                
                user_data = {
                    "email": "benito@gmail.com",
                    "name": "Benito Martínez",
                    "username": "benito_m",
                    "id": "usr_12345",
                    "status": "active"
                }
                
                if include_details:
                    user_data.update({
                        "created_at": "2024-01-15T10:30:00Z",
                        "last_login": "2025-12-23T08:15:30Z",
                        "role": "premium_user",
                        "preferences": {
                            "language": "es",
                            "notifications": True,
                            "theme": "dark"
                        },
                        "stats": {
                            "total_games": 42,
                            "high_score": 1250,
                            "achievements": 15
                        }
                    })
                
                return JSONRPCResponse(
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(user_data, indent=2, ensure_ascii=False)
                            }
                        ]
                    },
                    id=request_id
                )
            else:
                return JSONRPCResponse(
                    error=JSONRPCError(
                        code=-32602,
                        message=f"Herramienta desconocida: {tool_name}"
                    ),
                    id=request_id
                )
        
        # Método desconocido
        else:
            return JSONRPCResponse(
                error=JSONRPCError(
                    code=-32601,
                    message=f"Método no encontrado: {method}"
                ),
                id=request_id
            )
            
    except Exception as e:
        return JSONRPCResponse(
            error=JSONRPCError(
                code=-32603,
                message="Error interno del servidor",
                data=str(e)
            ),
            id=request.id
        )


@app.get("/")
async def serve_spa():
    """Servir el frontend Angular"""
    index_file = WWW_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Frontend no encontrado. Asegúrate de compilar la aplicación Angular."}


@app.get("/health")
async def health_check():
    """
    Endpoint de health check que verifica:
    - Estado de la aplicación
    - Conexión a la base de datos
    """
    # Verificar conexión a la base de datos
    db_success, db_message = test_database_connection()
    
    health_status = {
        "status": "healthy" if db_success else "unhealthy",
        "timestamp": None,
        "checks": {
            "application": {
                "status": "up",
                "message": "Application is running"
            },
            "database": {
                "status": "up" if db_success else "down",
                "message": db_message,
                "server": HOST_DB,
                "database": DATABASE_NAME
            }
        }
    }
    
    # Agregar timestamp
    from datetime import datetime
    health_status["timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    if not db_success:
        return JSONResponse(
            status_code=503,
            content=health_status
        )
    
    return health_status


# ============================================================
# Endpoints para Snake Scores
# ============================================================

@app.post("/api/snake-scores", response_model=dict)
async def create_snake_score(score_data: SnakeScoreCreate):
    """
    Guardar un nuevo score del juego de la serpiente
    """
    try:
        conn_string = get_db_connection_string()
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        
        # Insertar el score en la base de datos y obtener el ID
        query = """
            INSERT INTO dbo.SnakeScores (PlayerName, Score, GameDate)
            OUTPUT INSERTED.Id
            VALUES (?, ?, GETDATE());
        """
        
        cursor.execute(query, score_data.PlayerName, score_data.Score)
        result = cursor.fetchone()
        new_id = result[0] if result else None
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Score guardado exitosamente",
            "id": int(new_id) if new_id else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el score: {str(e)}")


@app.get("/api/snake-scores/top/{limit}", response_model=List[SnakeScoreResponse])
async def get_top_scores(limit: int = 10):
    """
    Obtener los mejores scores (top N)
    """
    try:
        conn_string = get_db_connection_string()
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        
        # Obtener los mejores scores
        query = """
            SELECT TOP (?) 
                Id,
                PlayerName,
                Score,
                FORMAT(GameDate, 'yyyy-MM-dd HH:mm:ss') as GameDate,
                FORMAT(CreatedAt, 'yyyy-MM-dd HH:mm:ss') as CreatedAt
            FROM dbo.SnakeScores
            ORDER BY Score DESC, GameDate DESC
        """
        
        cursor.execute(query, limit)
        rows = cursor.fetchall()
        
        scores = []
        for row in rows:
            scores.append({
                "Id": row.Id,
                "PlayerName": row.PlayerName,
                "Score": row.Score,
                "GameDate": row.GameDate,
                "CreatedAt": row.CreatedAt
            })
        
        cursor.close()
        conn.close()
        
        return scores
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los scores: {str(e)}")


@app.get("/api/snake-scores/player/{player_name}", response_model=List[SnakeScoreResponse])
async def get_player_scores(player_name: str):
    """
    Obtener todos los scores de un jugador específico
    """
    try:
        conn_string = get_db_connection_string()
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        
        # Obtener los scores del jugador
        query = """
            SELECT 
                Id,
                PlayerName,
                Score,
                FORMAT(GameDate, 'yyyy-MM-dd HH:mm:ss') as GameDate,
                FORMAT(CreatedAt, 'yyyy-MM-dd HH:mm:ss') as CreatedAt
            FROM dbo.SnakeScores
            WHERE PlayerName = ?
            ORDER BY Score DESC, GameDate DESC
        """
        
        cursor.execute(query, player_name)
        rows = cursor.fetchall()
        
        scores = []
        for row in rows:
            scores.append({
                "Id": row.Id,
                "PlayerName": row.PlayerName,
                "Score": row.Score,
                "GameDate": row.GameDate,
                "CreatedAt": row.CreatedAt
            })
        
        cursor.close()
        conn.close()
        
        return scores
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los scores del jugador: {str(e)}")


@app.get("/{full_path:path}")
async def serve_static_or_spa(full_path: str):
    """
    Servir archivos estáticos o el SPA para rutas no encontradas.
    Esto permite que Angular maneje las rutas del frontend.
    """
    # Intentar servir archivo estático
    file_path = WWW_DIR / full_path
    if file_path.is_file():
        return FileResponse(str(file_path))
    
    # Si no es un archivo, servir index.html para que Angular maneje la ruta
    index_file = WWW_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    raise HTTPException(status_code=404, detail="Archivo no encontrado")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
