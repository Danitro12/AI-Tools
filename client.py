import asyncio
import json
import nest_asyncio
import sys
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.core.workflow import Context
from llama_index.core.agent import ReActAgent
import os

nest_asyncio.apply()


# -----------------------------
# Configura tu LLM local (modelo por argumento)
# -----------------------------
def get_llm_from_args():
    if len(sys.argv) < 2:
        print("Uso: python client.py <nombre_modelo>")
        sys.exit(1)
    modelo = sys.argv[1]
    llm = Ollama(
        model=modelo,
        request_timeout=120.0,
        additional_kwargs={
            "num_ctx": 8192,      # Con 12GB puedes subir esto para manejar muchos archivos
            "num_gpu": -1,        # Fuerza a usar toda la GPU
            "temperature": 0.2,
        }
    )
    Settings.llm = llm
    return llm

# -----------------------------
# Conectar con el servidor MCP
# -----------------------------
mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
mcp_tool_spec = McpToolSpec(client=mcp_client)
# 2. Cliente para las herramientas oficiales (Filesystem TS vía Stdio)
shared_folder = os.path.abspath(r"C:\Users\Daniel\Downloads")
mcp_client_fs = BasicMCPClient(
    "npx", 
    args=["-y", "@modelcontextprotocol/server-filesystem", shared_folder]
)
mcp_spec_fs = McpToolSpec(client=mcp_client_fs)

# -----------------------------
# Prompt del sistema
# -----------------------------
SYSTEM_PROMPT = """Eres un agente avanzado que puede usar herramientas para interactuar con el sistema de archivos y realizar tareas complejas. Utiliza las herramientas disponibles de manera efectiva para cumplir con los objetivos del usuario, solo puedes utilizar estas herramientas, por lo que no intentes distintos comandos..
REGLA CRÍTICA DE PATHS: 
1. NUNCA escribas 'C:\\Users\\...' ni rutas absolutas. 
2. Considera que la carpeta de Descargas es el nivel raíz ('.').
3. Estas en windows, usa '\' para separar carpetas.
Si una herramienta devuelve un 'Error':
1. Analiza el mensaje de error detenidamente.
2. Si el error es de 'Permisos', intenta usar una ruta relativa en lugar de absoluta.
3. Si el error es 'Archivo no encontrado', usa primero 'ls' para verificar el nombre real.
4. NUNCA repitas la misma llamada que falló. Cambia los parámetros."
"""
# -----------------------------
# Función para crear el agente
# -----------------------------
async def get_agent(tools_spec: McpToolSpec, llm):
    custom_tools = await tools_spec.to_tool_list_async()
    fs_tools = await mcp_spec_fs.to_tool_list_async()
    all_tools = fs_tools + custom_tools
    agent = ReActAgent(
        name="SuperAgent",
        description="Agente con herramientas propias y de sistema de archivos.",
        tools=all_tools,
        llm=llm,  # usamos tu modelo local
        verbose=True,
        system_prompt=SYSTEM_PROMPT, # Esto obliga al modelo a entender que DEBE usar herramientas
        allow_parallel_tool_calls=True
    )
    return agent

# -----------------------------
# Función para manejar mensajes
# -----------------------------
async def handle_user_message(message_content: str, agent: FunctionAgent, agent_context: Context, verbose: bool = False):
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
      
        if verbose and isinstance(event, ToolCall):
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and isinstance(event, ToolCallResult):
            print(f"Tool {event.tool_name} returned an output")
    response = await handler
    return str(response)

# -----------------------------
# Función principal async
# -----------------------------

async def main():
    # Obtiene el modelo desde los argumentos
    llm = get_llm_from_args()
    # Crea el agente
    agent = await get_agent(mcp_tool_spec, llm)

    # Crea contexto del agente
    agent_context = Context(agent)

    # Loop de interacción con el usuario
    while True:
        user_input = input("Enter your message: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = await handle_user_message(user_input, agent, agent_context, verbose=True)
        print("Agent:", response)

# Ejecutar todo
asyncio.run(main())
