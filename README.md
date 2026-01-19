# MCP Demo - Agente con LLM y Servidor de Archivos

Este proyecto permite interactuar con un agente inteligente que utiliza un modelo LLM local (Ollama) y puede manipular archivos en una carpeta segura a través de un servidor MCP personalizado.

## Requisitos

- Python 3.9+
- Node.js (para herramientas de sistema de archivos)
- [Ollama](https://ollama.com/) instalado y corriendo localmente
- Dependencias Python:
  - llama_index
  - nest_asyncio
  - mcp (y sus dependencias)
  - httpx
  - argparse
  - shutil (incluido en la librería estándar)

Instala las dependencias necesarias con:

```
pip install llama_index nest_asyncio httpx mcp
```

## Estructura

- `client.py`: Cliente interactivo que conecta con el servidor MCP y permite usar un modelo LLM local.
- `filesystem_server.py`: Servidor MCP con herramientas para manipular archivos en la carpeta de Descargas.

## Uso

### 1. Inicia el servidor MCP

Abre una terminal y ejecuta:

```
python filesystem_server.py --server_type sse
```

Esto levantará el servidor MCP con acceso seguro a la carpeta de Descargas.

### 2. Ejecuta el cliente

En otra terminal, ejecuta el cliente indicando el modelo de Ollama que quieres usar (por ejemplo, `qwen2.5-coder:7b`):

```
python client.py modelo
```

### 3. Interactúa con el agente

El cliente te pedirá mensajes. Escribe tus instrucciones y el agente usará las herramientas disponibles para cumplirlas. Para salir, escribe `exit` o `quit`.

#### Ejemplo de comandos:

- `ls` — Lista archivos en la carpeta raíz (Descargas)
- `mover_archivo_local archivo.txt carpeta_destino` — Mueve un archivo a una subcarpeta

### Notas importantes

- El agente solo puede ver y manipular archivos dentro de la carpeta de Descargas.
- Los paths deben ser relativos (no uses rutas absolutas de Windows).
- El modelo LLM se elige al lanzar el cliente.

## Personalización

Puedes agregar más herramientas al servidor MCP editando `filesystem_server.py` y decorando funciones con `@mcp.tool()`.

---
