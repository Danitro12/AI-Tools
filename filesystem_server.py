from mcp.server import Server
from pathlib import Path
import os
from mcp.server.fastmcp import FastMCP
import httpx
import argparse
import shutil
# Create an MCP server
mcp = FastMCP("Demo")
# Carpeta segura para que la IA pueda ver
BASE_DIR = Path(r"C:\Users\Daniel\Downloads").resolve()

# ls simple
@mcp.tool()
def ls(path: str = ".") -> str:
    target = (BASE_DIR / path).resolve()
    if not str(target).startswith(str(BASE_DIR)):
        return "Acceso denegado"
    if not target.exists() or not target.is_dir():
        return "No es un directorio válido"
    return "\n".join(p.name for p in target.iterdir())

@mcp.tool()
def mover_archivo_local(nombre_archivo: str, carpeta_destino: str) -> str:
    """Mueve un archivo dentro de la carpeta de descargas."""
    # BASE_DIR ya lo definiste como la ruta de descargas
    origen = BASE_DIR / nombre_archivo
    destino_dir = BASE_DIR / carpeta_destino
    
    # Crear carpeta si no existe
    destino_dir.mkdir(exist_ok=True)
    
    destino_final = destino_dir / nombre_archivo
    
    try:
        shutil.move(str(origen), str(destino_final))
        return f"Éxito: {nombre_archivo} movido a {carpeta_destino}"
    except Exception as e:
        return f"Error de sistema: {str(e)}"


if __name__ == "__main__":
        # Start the server
    print("Starting server... ")

    # Debug Mode
    #  uv run mcp dev server.py

    # Production Mode
    # uv run server.py --server_type=sse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()
    mcp.run(args.server_type)