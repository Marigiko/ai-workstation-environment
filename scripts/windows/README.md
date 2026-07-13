# Windows Installation Scripts

Scripts para instalar AI Workstation en Windows via WSL2.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `install.ps1` | Instalador principal PowerShell (requiere admin) |
| `launch-terax.vbs` | Launcher invisible (sin ventana negra de terminal) |
| `create-shortcut.ps1` | Crea acceso directo en Desktop y Start Menu |
| `icon.ico` | Icono de Terax (copiar/agregar manualmente) |

## Uso

### Instalación completa

1. Abrir PowerShell como Administrador
2. Ejecutar:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass
   .\install.ps1
   ```
3. Seguir las instrucciones (reinicio puede ser necesario para WSL)

### Solo crear acceso directo (si ya instaló)

```powershell
.\create-shortcut.ps1
```

### Variables de entorno opcionales

| Variable | Descripción |
|----------|-------------|
| `AIWSL_GITHUB_TOKEN` | GitHub personal access token para git credential helper |
| `WSL_DISTRO` | Nombre de distribución WSL (default: Ubuntu-24.04) |

Ejemplo:

```powershell
$env:AIWSL_GITHUB_TOKEN = "ghp_xxxx"
$env:WSL_DISTRO = "Ubuntu-22.04"
.\install.ps1
```

## Flujo del acceso directo

```
Usuario doble-click "Terax AI Workstation.lnk"
  │
  ▼
launch-terax.vbs (invisible)
  │
  ├─ 1. Verifica WSL corriendo
  ├─ 2. Verifica gateway /health → si no responde:
  │     └─ docker compose up -d dentro de WSL
  │     └─ Espera /health (hasta 60s)
  └─ 3. Ejecuta `terax` → WSLg abre ventana GUI
```

## Requisitos

- Windows 11 (recomendado) o Windows 10 v2004+ con WSLg
- WSL2 instalado
- Docker Desktop con WSL2 backend o Docker Engine en WSL
