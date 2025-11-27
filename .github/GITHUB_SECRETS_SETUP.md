# Configuración de GitHub Secrets

Para que el CI/CD funcione correctamente, debes configurar los siguientes secrets en tu repositorio de GitHub.

## ¿Dónde configurar los secrets?

1. Ve a tu repositorio: `https://github.com/gmendoza_ITQS/miApp`
2. Haz clic en **Settings** (Configuración)
3. En el menú lateral, ve a **Secrets and variables** → **Actions**
4. Haz clic en **New repository secret** para cada uno de los secrets a continuación

## Secrets requeridos

### 1. AZURE_WEBAPP_PUBLISH_PROFILE
**Descripción:** Perfil de publicación de tu Azure Web App  
**Valor:** El contenido XML completo del publish profile (ya proporcionado anteriormente)

### 2. HOST_DB
**Descripción:** Host del servidor de Azure SQL Database  
**Valor:** `serversqlmanuprueba.database.windows.net`

### 3. ADMIN_DB
**Descripción:** Usuario administrador de la base de datos  
**Valor:** `adminqr`

### 4. PASSWORD_DB
**Descripción:** Contraseña del usuario administrador  
**Valor:** `4}k$57Tf8Jn1`

### 5. DATABASE_NAME
**Descripción:** Nombre de la base de datos  
**Valor:** `qr-database1`

### 6. PORT_DB
**Descripción:** Puerto del servidor SQL  
**Valor:** `1433`

### 7. DRIVER
**Descripción:** Driver ODBC para SQL Server  
**Valor:** `{ODBC Driver 18 for SQL Server}`

## Verificación

Una vez configurados todos los secrets:

1. Verifica que todos aparezcan en la lista de secrets (Settings → Secrets and variables → Actions)
2. Los valores de los secrets estarán ocultos (solo verás asteriscos)
3. Haz un commit y push a la rama `master` para activar el workflow
4. Ve a la pestaña **Actions** en GitHub para ver el progreso del deployment

## Seguridad

⚠️ **IMPORTANTE:**
- Nunca subas el archivo `.env` al repositorio (ya está en `.gitignore`)
- Los secrets solo son accesibles durante la ejecución del workflow
- No compartas los valores de los secrets públicamente
- Cambia las contraseñas periódicamente

## Solución de problemas

Si el deployment falla:
1. Verifica que todos los secrets estén configurados correctamente
2. Revisa los logs en la pestaña **Actions** de GitHub
3. Asegúrate de que la Azure Web App esté corriendo
4. Verifica la conectividad con la base de datos desde Azure

