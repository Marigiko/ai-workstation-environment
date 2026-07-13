# Terax Fork — Guía de Modificaciones

> **Fork source**: Clonar `https://github.com/crynta/terax-ai` → `https://github.com/<user>/terax-ai-fork`
> **Licencia**: Apache-2.0 (permite fork y modificación)
> **Stack**: Tauri 2 + Rust + React 19 + TypeScript + Vercel AI SDK v6

## Arquitectura Actual de Terax

```
src-tauri/           ← Rust backend
  src/main.rs        ← Entry point, commands Tauri
  Cargo.toml         ← Dependencias Rust
  tauri.conf.json    ← Config Tauri
  capabilities/      ← Permisos IPC

src/                 ← React frontend (webview)
  ai/                ← AI providers, config
  ui/
    components/      ← Componentes UI
    settings/        ← Panel de configuración
  terminals/         ← xterm.js terminal management

src-tauri/src/
  commands/          ← Tauri command handlers
  pty/               ← PTY management (portable-pty)
  secrets/           ← OS keychain integration
```

## Modificaciones por Feature

---

### 1. Modo "AI Workstation Gateway" Provider

**Objetivo**: Terax se conecta al gateway (`localhost:8000`).

**Archivos a crear/modificar**:

| Acción | Archivo | Descripción |
|--------|---------|-------------|
| Crear | `src/ai/providers/ai-workstation.ts` | Nuevo provider que usa `POST /chat` del gateway |
| Modificar | `src/ai/providers/index.ts` | Registrar nuevo provider type |
| Modificar | `src/ai/config.ts` | Extender tipo `AIConfig` con `{ type: "ai-workstation", gatewayUrl: string, autoStart: boolean }` |
| Modificar | `src/ui/settings/Providers.tsx` | Agregar UI para configurar gateway URL y auto-start |

**Código ejemplo para el provider**:

```typescript
// src/ai/providers/ai-workstation.ts
import { generateText, streamText } from 'ai';

export interface AIWorkstationConfig {
  gatewayUrl: string;
  autoStart: boolean;
}

export async function chatWithGateway(
  messages: Message[],
  config: AIWorkstationConfig
): AsyncGenerator<string> {
  const response = await fetch(`${config.gatewayUrl}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: messages.map(m => ({ role: m.role, content: m.content })),
      stream: true,
    }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const text = decoder.decode(value);
    for (const line of text.split('\n')) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        if (data.content) yield data.content;
      }
    }
  }
}
```

---

### 2. Auto-Start del Gateway

**Objetivo**: Si el gateway no está corriendo, Terax lo inicia automáticamente.

**Archivos**:

| Acción | Archivo | Descripción |
|--------|---------|-------------|
| Crear | `src-tauri/src/commands/gateway.rs` | Command `start_gateway()` y `check_gateway_health()` |
| Modificar | `src-tauri/src/main.rs` | Registrar commands en `invoke_handler` |
| Modificar | `src-tauri/capabilities/default.json` | Agregar permisos para `spawn` de procesos |
| Crear | `src/ai/gateway.ts` | Módulo TypeScript que llama al command vía `invoke()` |

**Código Rust**:

```rust
// src-tauri/src/commands/gateway.rs
use std::process::Command;
use tauri::command;

#[command]
pub async fn check_gateway_health(url: String) -> Result<bool, String> {
    let resp = reqwest::get(format!("{}/health", url)).await;
    match resp {
        Ok(r) => Ok(r.status().is_success()),
        Err(_) => Ok(false),
    }
}

#[command]
pub async fn start_gateway() -> Result<(), String> {
    Command::new("docker")
        .args([
            "compose",
            "-f",
            "infrastructure/compose/docker-compose.prod.yml",
            "up",
            "-d",
        ])
        .spawn()
        .map_err(|e| format!("Failed to start gateway: {}", e))?;
    Ok(())
}
```

**Código TypeScript**:

```typescript
// src/ai/gateway.ts
import { invoke } from '@tauri-apps/api/core';

export async function ensureGatewayRunning(
  gatewayUrl: string = 'http://localhost:8000'
): Promise<boolean> {
  let healthy = await invoke<boolean>('check_gateway_health', { url: gatewayUrl });

  if (!healthy) {
    console.log('Gateway not running, starting...');
    await invoke('start_gateway');

    // Wait for health (poll up to 120s)
    for (let i = 0; i < 60; i++) {
      await new Promise(r => setTimeout(r, 2000));
      healthy = await invoke<boolean>('check_gateway_health', { url: gatewayUrl });
      if (healthy) return true;
    }
    return false;
  }
  return true;
}
```

---

### 3. Status Bar del Gateway

**Objetivo**: Mostrar indicador visual del estado del gateway en la UI.

**Archivos**:

| Acción | Archivo | Descripción |
|--------|---------|-------------|
| Crear | `src/ui/components/GatewayStatus.tsx` | Componente indicador (verde/rojo) |
| Modificar | `src/ui/components/Statusbar.tsx` | Agregar `GatewayStatus` a la barra |
| Crear | `src/hooks/useGatewayStatus.ts` | Hook que polling `/health` cada 10s |

**Componente React**:

```tsx
// src/ui/components/GatewayStatus.tsx
import { useGatewayStatus } from '@/hooks/useGatewayStatus';

export function GatewayStatus({ url }: { url: string }) {
  const { healthy, latency } = useGatewayStatus(url);

  return (
    <div className="flex items-center gap-1 px-2 py-1 rounded" title={`Gateway: ${url}`}>
      <span
        className={`w-2 h-2 rounded-full ${healthy ? 'bg-green-500' : 'bg-red-500'}`}
      />
      <span className="text-xs text-muted-foreground">
        {healthy ? `${latency}ms` : 'offline'}
      </span>
    </div>
  );
}
```

---

### 4. Mejora de Memoria

**Objetivo**: Reemplazar TERAX.md plano por memoria persistente via gateway.

**Archivos**:

| Acción | Archivo | Descripción |
|--------|---------|-------------|
| Crear | `src/ai/memory.ts` | Módulo con `remember()` y `recall()` |
| Modificar | `src/ai/agents/base.ts` | Inyectar memorias en system prompt |

**Código**:

```typescript
// src/ai/memory.ts
export interface Memory {
  id: string;
  content: string;
  scope: 'global' | 'project' | 'session';
  timestamp: string;
}

export async function recall(
  query: string,
  scope: string = 'project',
  gatewayUrl: string = 'http://localhost:8000'
): Promise<Memory[]> {
  const resp = await fetch(`${gatewayUrl}/memory/recall`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, scope }),
  });
  return (await resp.json()).memories;
}

export async function remember(
  content: string,
  scope: string = 'project',
  gatewayUrl: string = 'http://localhost:8000'
): Promise<void> {
  await fetch(`${gatewayUrl}/memory/remember`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, scope }),
  });
}
```

---

### 5. Modo No-Bloqueante / Headless

**Objetivo**: Terax no bloquea la terminal cuando se lanza desde CLI.

**Archivos**:

| Acción | Archivo | Descripción |
|--------|---------|-------------|
| Modificar | `src-tauri/src/main.rs` | Flag `--no-block` que detach del proceso |
| Crear | `src-tauri/src/cli.rs` | Parser para `--no-block` y `--serve :8080` |

**Código Rust**:

```rust
// En main.rs
let args: Vec<String> = std::env::collect();
let no_block = args.contains(&"--no-block".to_string());

if no_block {
    #[cfg(unix)]
    {
        use std::process::Command;
        // Fork and detach
        let current = std::env::current_exe().unwrap();
        Command::new(current)
            .args(&args[1..])
            .stdin(std::process::Stdio::null())
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .spawn()
            .expect("Failed to detach");
        std::process::exit(0);
    }
}
```

---

### 6. Modo Servidor Web (v2)

**Objetivo**: `terax --serve :8080` expone la UI como web app.

**Nota**: Requiere que Terax tenga un modo "remote" donde el backend Rust expone HTTP. Esto es un feature más grande.

**Alternativa simple (v1)**: En vez de exponer Terax directamente, usar `src-tauri/src/server.rs` con `tiny_http` que sirva el builds estáticos de `dist/`.

---

### 7. Compilación Nativa Windows

**Configuración**:

```toml
# src-tauri/Cargo.toml - agregar dependencia
[dependencies]
reqwest = { version = "0.12", features = ["json"] }
```

```json
// src-tauri/tauri.conf.json
{
  "productName": "TeraxAI",
  "version": "0.9.0",
  "identifier": "app.ai-workstation.terax",
  "bundle": {
    "targets": ["msi", "nsis"],
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "externalBin": [],
    "resources": []
  }
}
```

**Build commands**:

```bash
# Add Windows target
rustup target add x86_64-pc-windows-gnu
sudo apt install mingw-w64

# Build
cd src-tauri
cargo tauri build --target x86_64-pc-windows-gnu

# Output: src-tauri/target/x86_64-pc-windows-gnu/release/bundle/msi/TeraxAI_0.9.0_x64_en-US.msi
```

---

### 8. Windows Code-Signing (post-v1)

Para que Windows no bloquee el instalador:
- Obtener certificado EV (~$300-500/año) o usar signtool con certificado estándar
- Alternativa: MSIX packaging via MS Store (sin costo de certificado)

---

## Orden Recomendado de Implementación

```
1. Configuración Windows build (tauri.conf.json, Cargo.toml)
2. Provider "AI Workstation Gateway"
3. Auto-start gateway (commands Rust + módulo TS)
4. Status bar gateway
5. Mejora de memoria (recall/remember via gateway API)
6. Modo no-bloqueante (--no-block)
7. Compilar .msi de prueba
8. Modo headless/serve (v2)
```

---

## Testing Checklist

- [ ] `terax` abre normalmente en Linux
- [ ] `terax --no-block` se detach de terminal
- [ ] Provider "AI Workstation" aparece en settings
- [ ] Gateway offline → Terax auto-lo-espera
- [ ] Status bar muestra verde/rojo según gateway
- [ ] Memoria: recuerdos persisten entre sesiones
- [ ] `cargo tauri build --target x86_64-pc-windows-gnu` exitoso
- [ ] .msi instalador funciona en Windows 11 limpio
