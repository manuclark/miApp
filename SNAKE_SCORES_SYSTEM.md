# Sistema de Puntuaciones - Juego de la Serpiente

## 📋 Descripción General

Sistema completo para guardar y visualizar las puntuaciones del juego de la serpiente (Snake Game) en miApp. Incluye backend con FastAPI, frontend con Angular/Ionic, y base de datos Azure SQL.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Angular/Ionic)                  │
│  - Juego de la Serpiente (Canvas HTML5)                     │
│  - Formulario de captura de nombre                          │
│  - Tabla de mejores puntuaciones                            │
│  - Servicio HTTP (SnakeScoreService)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP REST API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  - POST /api/snake-scores (Guardar score)                   │
│  - GET /api/snake-scores/top/:limit (Top scores)            │
│  - GET /api/snake-scores/player/:name (Scores por jugador)  │
└──────────────────────┬──────────────────────────────────────┘
                       │ pyodbc
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                Azure SQL Database                            │
│  - Tabla: SnakeScores                                        │
│    * Id (INT, PK, IDENTITY)                                  │
│    * PlayerName (NVARCHAR(100))                              │
│    * Score (INT)                                             │
│    * GameDate (DATETIME)                                     │
│    * CreatedAt (DATETIME)                                    │
└──────────────────────────────────────────────────────────────┘
```

## 📁 Estructura de Archivos

### Backend
```
app/
└── main.py                 # API FastAPI con endpoints de scores
```

### Frontend
```
src/
├── app/
│   ├── services/
│   │   └── snake-score.service.ts    # Servicio para llamadas HTTP
│   └── home/
│       ├── home.page.ts              # Lógica del juego + integración scores
│       ├── home.page.html            # UI del juego + tabla de scores
│       └── home.page.scss            # Estilos incluyendo leaderboard
└── main.ts                           # Configuración de HttpClient
```

### Base de Datos
```
test/
└── DB/
    └── create_snake_scores.sql       # Script de creación de tabla
```

## 🚀 Instalación y Configuración

### 1. Crear la Tabla en la Base de Datos

Ejecutar el script SQL para crear la tabla:

```bash
python test/db.py --file=create_snake_scores.sql
```

El script creará:
- Tabla `SnakeScores` con todos los campos necesarios
- Índices para optimizar consultas por Score y GameDate
- Datos de prueba iniciales

### 2. Configurar el Backend

El backend ya está configurado con:
- **CORS** habilitado para `localhost:8100` y `localhost:4200`
- **Endpoints REST** para manejar scores
- **Validación** con Pydantic models

No requiere configuración adicional si el archivo `.env` ya está configurado.

### 3. Ejecutar el Backend

```bash
# Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# Ejecutar FastAPI
python app/main.py
```

O con uvicorn directamente:

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

### 4. Ejecutar el Frontend

```bash
# Instalar dependencias (si es necesario)
npm install

# Ejecutar en modo desarrollo
ionic serve
```

O con Angular CLI:

```bash
ng serve
```

El frontend estará disponible en: `http://localhost:8100`

## 🎮 Flujo de Uso

### 1. Jugar
- El jugador inicia el juego presionando "Iniciar Juego"
- Controla la serpiente con las flechas del teclado o botones
- Acumula puntos comiendo la comida (10 puntos por cada una)

### 2. Game Over
- Al perder, si el score es mayor a 0, aparece un **alert modal**
- El modal solicita el nombre del jugador
- El nombre debe tener mínimo 2 caracteres

### 3. Guardar Score
- Al ingresar un nombre válido y presionar "Guardar"
- El sistema envía el score al backend
- El backend lo guarda en la base de datos
- Se muestra un mensaje de confirmación
- La tabla de mejores scores se actualiza automáticamente

### 4. Ver Mejores Scores
- Los **Top 10 scores** se muestran en una tabla en la misma página
- Los primeros 3 lugares tienen diseño especial (🥇 🥈 🥉)
- La tabla se actualiza cada vez que se guarda un nuevo score

## 🔌 API Endpoints

### POST `/api/snake-scores`
Guardar un nuevo score.

**Request Body:**
```json
{
  "PlayerName": "Juan",
  "Score": 150
}
```

**Response:**
```json
{
  "success": true,
  "message": "Score guardado exitosamente",
  "id": 42
}
```

### GET `/api/snake-scores/top/{limit}`
Obtener los mejores scores.

**Parámetros:**
- `limit`: Número de scores a retornar (default: 10)

**Response:**
```json
[
  {
    "Id": 1,
    "PlayerName": "Snake Master",
    "Score": 320,
    "GameDate": "2025-11-26 14:30:00",
    "CreatedAt": "2025-11-26 14:30:00"
  },
  ...
]
```

### GET `/api/snake-scores/player/{player_name}`
Obtener todos los scores de un jugador específico.

**Parámetros:**
- `player_name`: Nombre del jugador

**Response:**
```json
[
  {
    "Id": 5,
    "PlayerName": "Juan",
    "Score": 200,
    "GameDate": "2025-11-26 15:00:00",
    "CreatedAt": "2025-11-26 15:00:00"
  },
  ...
]
```

## 🗃️ Esquema de Base de Datos

### Tabla: `SnakeScores`

| Campo       | Tipo           | Descripción                           | Constraints        |
|-------------|----------------|---------------------------------------|--------------------|
| Id          | INT            | Identificador único                   | PK, IDENTITY(1,1)  |
| PlayerName  | NVARCHAR(100)  | Nombre del jugador                    | NOT NULL           |
| Score       | INT            | Puntuación obtenida                   | NOT NULL           |
| GameDate    | DATETIME       | Fecha y hora del juego                | NOT NULL, DEFAULT  |
| CreatedAt   | DATETIME       | Fecha de creación del registro        | NOT NULL, DEFAULT  |

**Índices:**
- `IX_SnakeScores_Score DESC`: Para consultas ordenadas por puntuación
- `IX_SnakeScores_GameDate`: Para consultas por fecha

## 🎨 Características del Frontend

### Componente Principal: `HomePage`

**Propiedades:**
- `score`: Puntuación actual del juego
- `gameOver`: Estado del juego (terminado/en curso)
- `gameStarted`: Si el juego ha iniciado
- `topScores`: Array con los mejores scores

**Métodos principales:**
- `startGame()`: Inicia un nuevo juego
- `endGame()`: Termina el juego y muestra el alert para guardar
- `showSaveScoreAlert()`: Muestra el modal para capturar el nombre
- `saveScore(playerName)`: Envía el score al backend
- `loadTopScores()`: Carga los mejores 10 scores

### Servicio: `SnakeScoreService`

**Métodos:**
- `saveScore(playerName, score)`: Guardar score
- `getTopScores(limit)`: Obtener top scores
- `getPlayerScores(playerName)`: Obtener scores de un jugador

### Diseño de la Tabla de Scores

- **Responsive**: Se adapta a dispositivos móviles
- **Top 3 destacado**: Colores especiales y medallas
- **Animaciones**: Efecto hover en las filas
- **Gradientes**: Diseño visual atractivo

## 🔧 Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **Pydantic**: Validación de datos
- **pyodbc**: Conexión a SQL Server
- **python-dotenv**: Manejo de variables de entorno

### Frontend
- **Angular 17+**: Framework de desarrollo
- **Ionic 8**: Componentes UI móviles
- **TypeScript**: Lenguaje de programación
- **RxJS**: Programación reactiva
- **Canvas API**: Renderizado del juego

### Base de Datos
- **Azure SQL Database**: Base de datos en la nube

## 🧪 Pruebas

### Probar el Backend (sin frontend)

Con curl:

```bash
# Guardar un score
curl -X POST http://localhost:8000/api/snake-scores \
  -H "Content-Type: application/json" \
  -d '{"PlayerName": "Test Player", "Score": 150}'

# Obtener top 10
curl http://localhost:8000/api/snake-scores/top/10

# Obtener scores de un jugador
curl http://localhost:8000/api/snake-scores/player/Test%20Player
```

### Probar Directamente en la Base de Datos

```sql
-- Ver todos los scores
SELECT * FROM dbo.SnakeScores ORDER BY Score DESC;

-- Ver estadísticas
SELECT 
    COUNT(*) as TotalGames,
    MAX(Score) as MaxScore,
    AVG(Score) as AvgScore,
    COUNT(DISTINCT PlayerName) as UniquePlayers
FROM dbo.SnakeScores;

-- Top 10 jugadores
SELECT TOP 10 
    PlayerName,
    Score,
    FORMAT(GameDate, 'dd/MM/yyyy HH:mm') as FechaJuego
FROM dbo.SnakeScores
ORDER BY Score DESC;
```

## 📱 Responsive Design

El diseño se adapta a diferentes tamaños de pantalla:

- **Desktop**: Canvas de 400x400px, controles grandes
- **Mobile**: Canvas adaptativo (max 350px), controles más pequeños
- **Tablets**: Tamaño intermedio optimizado

## 🐛 Solución de Problemas

### Error: CORS
Si aparecen errores de CORS en el navegador:
- Verificar que el backend esté corriendo en `localhost:8000`
- Confirmar que CORS está configurado en `main.py`

### Error: Conexión a base de datos
- Verificar el archivo `.env` con las credenciales correctas
- Probar la conexión con `python test/db.py --file=create_snake_scores.sql`

### Error: HttpClient not provided
Si aparece este error en Angular:
- Verificar que `provideHttpClient()` está en `main.ts`

### La tabla no se actualiza
- Verificar la consola del navegador para errores HTTP
- Confirmar que el backend está respondiendo correctamente
- Revisar que el score sea mayor a 0

## 🔐 Seguridad

- Las credenciales se manejan a través de variables de entorno
- Las conexiones usan encriptación (Encrypt=yes)
- Validación de entrada en el frontend (mínimo 2 caracteres)
- Validación en el backend con Pydantic
- SQL parametrizado para prevenir SQL injection

## 🚀 Mejoras Futuras

- [ ] Autenticación de usuarios
- [ ] Filtros por fecha en el leaderboard
- [ ] Gráficos de estadísticas
- [ ] Compartir scores en redes sociales
- [ ] Modos de dificultad (velocidades diferentes)
- [ ] Power-ups en el juego
- [ ] Torneos y competencias
- [ ] Sistema de logros/achievements

## 📄 Licencia

Este sistema es parte del proyecto miApp.

---

**Última actualización**: 26 de noviembre de 2025
