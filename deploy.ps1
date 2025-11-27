# Script de despliegue manual a Azure Web App
# Ejecutar desde la raíz del proyecto

Write-Host "🚀 Iniciando despliegue a Azure Web App..." -ForegroundColor Cyan

# 1. Compilar el frontend
Write-Host "`n📦 Compilando aplicación Angular..." -ForegroundColor Yellow
npm run build -- --configuration production

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al compilar la aplicación" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Aplicación compilada exitosamente" -ForegroundColor Green

# 2. Crear archivo .env temporal para despliegue
Write-Host "`n🔐 Creando archivo .env..." -ForegroundColor Yellow
@"
HOST_DB=serversqlmanuprueba.database.windows.net
ADMIN_DB=adminqr
PASSWORD_DB=4}k`$57Tf8Jn1
DATABASE_NAME=qr-database1
PORT_DB=1433
DRIVER={ODBC Driver 18 for SQL Server}
"@ | Out-File -FilePath "app\.env" -Encoding UTF8 -Force

Write-Host "✅ Archivo .env creado" -ForegroundColor Green

# 3. Crear archivo zip temporal
Write-Host "`n📦 Creando paquete de despliegue..." -ForegroundColor Yellow

# Excluir carpetas innecesarias
$excludePaths = @(
    "node_modules",
    ".git",
    ".github",
    ".vscode",
    ".angular",
    "test",
    ".env"
)

# Crear directorio temporal
$tempDir = ".\temp_deploy"
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copiar archivos necesarios
Write-Host "Copiando archivos..." -ForegroundColor Gray
Copy-Item -Path "www" -Destination "$tempDir\www" -Recurse -Force
Copy-Item -Path "app" -Destination "$tempDir\app" -Recurse -Force
Copy-Item -Path "requirements.txt" -Destination "$tempDir\requirements.txt" -Force

# Crear archivo startup para Azure
@"
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind=0.0.0.0:8000
"@ | Out-File -FilePath "$tempDir\startup.txt" -Encoding UTF8 -Force

# Crear zip
$zipPath = ".\deploy.zip"
if (Test-Path $zipPath) {
    Remove-Item -Path $zipPath -Force
}
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force

Write-Host "✅ Paquete creado: deploy.zip" -ForegroundColor Green

# 4. Desplegar a Azure
Write-Host "`n🌐 Desplegando a Azure Web App..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --resource-group RG-MANU `
    --name miapp-serpiente-game `
    --src $zipPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al desplegar a Azure" -ForegroundColor Red
    # Limpiar archivos temporales
    Remove-Item -Path $zipPath -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "app\.env" -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "✅ Aplicación desplegada exitosamente" -ForegroundColor Green

# 5. Limpiar archivos temporales
Write-Host "`n🧹 Limpiando archivos temporales..." -ForegroundColor Yellow
Remove-Item -Path $zipPath -Force -ErrorAction SilentlyContinue
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "app\.env" -Force -ErrorAction SilentlyContinue

Write-Host "✅ Limpieza completada" -ForegroundColor Green

Write-Host "`n🎉 ¡Despliegue completado!" -ForegroundColor Cyan
Write-Host "🌐 URL: https://miapp-serpiente-game.azurewebsites.net" -ForegroundColor Cyan
Write-Host "`nPuedes verificar el estado del deployment en el portal de Azure." -ForegroundColor Gray
