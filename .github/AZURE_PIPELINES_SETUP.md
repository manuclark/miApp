# Configuración de Azure Pipelines

Ya que GitHub Actions está deshabilitado en tu repositorio, puedes usar Azure Pipelines como alternativa.

## ¿Qué es Azure Pipelines?

Azure Pipelines es el servicio de CI/CD de Azure DevOps que se integra perfectamente con Azure y GitHub.

## Pasos para configurar Azure Pipelines

### 1. Crear un proyecto en Azure DevOps

1. Ve a: https://dev.azure.com
2. Haz clic en **New Project**
3. Nombre: `miApp`
4. Visibilidad: Private
5. Haz clic en **Create**

### 2. Conectar tu repositorio de GitHub

1. En tu proyecto de Azure DevOps, ve a **Pipelines**
2. Haz clic en **Create Pipeline**
3. Selecciona **GitHub** como fuente del código
4. Autoriza la conexión entre Azure DevOps y GitHub
5. Selecciona tu repositorio: `gmendoza_ITQS/miApp`
6. Azure DevOps detectará el archivo `azure-pipelines.yml`

### 3. Crear Service Connection para Azure

1. En tu proyecto, ve a **Project Settings** (esquina inferior izquierda)
2. Ve a **Service connections**
3. Haz clic en **New service connection**
4. Selecciona **Azure Resource Manager**
5. Selecciona **Service principal (automatic)**
6. Configura:
   - Subscription: Tu suscripción de Azure
   - Resource group: `RG-MANU`
   - Service connection name: `Azure-miApp-Connection`
7. Marca **Grant access permission to all pipelines**
8. Haz clic en **Save**

### 4. Configurar Variables Secretas

1. Ve a **Pipelines** → Selecciona tu pipeline → **Edit**
2. Haz clic en **Variables** (esquina superior derecha)
3. Agrega estas variables y marca cada una como **Secret** (candado):

| Variable | Valor | Secret |
|----------|-------|--------|
| `HOST_DB` | `serversqlmanuprueba.database.windows.net` | ✅ |
| `ADMIN_DB` | `adminqr` | ✅ |
| `PASSWORD_DB` | `4}k$57Tf8Jn1` | ✅ |
| `DATABASE_NAME` | `qr-database1` | ✅ |
| `PORT_DB` | `1433` | ❌ |
| `DRIVER` | `{ODBC Driver 18 for SQL Server}` | ❌ |

4. Haz clic en **Save**

### 5. Actualizar el archivo azure-pipelines.yml

En la variable `azureSubscription`, reemplaza `YOUR_AZURE_SERVICE_CONNECTION` con el nombre de tu service connection (ejemplo: `Azure-miApp-Connection`)

### 6. Ejecutar el Pipeline

1. Haz clic en **Run** para ejecutar el pipeline manualmente
2. O haz un commit a la rama `master` para que se ejecute automáticamente

## Ventajas de Azure Pipelines

- ✅ Se integra nativamente con Azure
- ✅ No requiere permisos de GitHub Actions
- ✅ Incluye minutos gratuitos para builds
- ✅ Soporte completo para despliegues a Azure Web Apps
- ✅ Interfaz visual para ver el progreso de los pipelines

## Alternativa Rápida: Despliegue directo con Azure CLI

Si prefieres algo más simple, puedes desplegar directamente desde tu máquina:

\`\`\`bash
# Compilar el frontend
npm run build -- --configuration production

# Crear archivo .env (solo para deployment)
echo "HOST_DB=serversqlmanuprueba.database.windows.net" > app/.env
echo "ADMIN_DB=adminqr" >> app/.env
echo "PASSWORD_DB=4}k$57Tf8Jn1" >> app/.env
echo "DATABASE_NAME=qr-database1" >> app/.env
echo "PORT_DB=1433" >> app/.env
echo "DRIVER={ODBC Driver 18 for SQL Server}" >> app/.env

# Crear archivo zip con todo el contenido
Compress-Archive -Path * -DestinationPath deploy.zip -Force

# Desplegar a Azure
az webapp deployment source config-zip --resource-group RG-MANU --name miapp-serpiente-game --src deploy.zip

# Limpiar
Remove-Item deploy.zip
Remove-Item app/.env
\`\`\`

## ¿Necesitas ayuda?

- Para habilitar GitHub Actions: Contacta al administrador de tu GitHub Enterprise
- Para Azure Pipelines: Sigue los pasos anteriores
- Para despliegue manual: Usa el script de Azure CLI

