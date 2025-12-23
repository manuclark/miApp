"""
Bot de chat interactivo con GPT 5.2 y herramientas MCP
Consola interactiva para chatear con el modelo y usar las herramientas disponibles
"""

import os
import json
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional, Union, Any

# Cargar variables de entorno
load_dotenv()

# Configuración
FASTAPI_BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("KEY_API_AZURE")
API_ENDPOINT = os.getenv("URL_API_AZURE")
API_VERSION = os.getenv("API_VERSION", "2024-12-01-preview")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gpt-5.2")

# Versión del protocolo MCP
MCP_PROTOCOL_VERSION = "2025-06-18"

# Versiones compatibles del protocolo
COMPATIBLE_MCP_VERSIONS = ["2024-11-05", "2025-06-18"]

# Usar JSON-RPC 2.0 (True) o formato legacy (False)
USE_JSONRPC = True


class MCPChatBot:
    """Bot de chat con GPT 5.2 y herramientas MCP"""
    
    def __init__(self, use_jsonrpc: bool = USE_JSONRPC):
        """Inicializar el bot"""
        self.client = AzureOpenAI(
            api_key=API_KEY,
            api_version=API_VERSION,
            azure_endpoint=API_ENDPOINT
        )
        self.messages: List[Dict] = []
        self.tools = []
        self.conversation_active = True
        self.use_jsonrpc = use_jsonrpc
        self.jsonrpc_id = 0
        
        # Inicializar sistema
        self._setup_system()
        
        # Inicializar servidor MCP con JSON-RPC si está habilitado
        if self.use_jsonrpc:
            self._initialize_mcp_server()
        
        self._load_mcp_tools()
    
    def _setup_system(self):
        """Configurar el mensaje del sistema"""
        system_message = {
            "role": "system",
            "content": (
                "Eres un asistente útil y amigable. Tienes acceso a herramientas para "
                "obtener información de usuarios y otros datos. Cuando el usuario te pida "
                "información que puedes obtener con tus herramientas, úsalas automáticamente. "
                "Responde de manera clara, concisa y en español."
            )
        }
        self.messages.append(system_message)
    
    def _get_next_jsonrpc_id(self) -> int:
        """Obtener el siguiente ID para JSON-RPC"""
        self.jsonrpc_id += 1
        return self.jsonrpc_id
    
    def _jsonrpc_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """Crear una petición JSON-RPC 2.0"""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._get_next_jsonrpc_id()
        }
        if params:
            request["params"] = params
        return request
    
    def _initialize_mcp_server(self):
        """Inicializar el servidor MCP usando JSON-RPC"""
        try:
            request = self._jsonrpc_request("initialize", {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "clientInfo": {
                    "name": "MCPChatBot",
                    "version": "1.0.0"
                }
            })
            
            response = requests.post(
                f"{FASTAPI_BASE_URL}/mcp",
                json=request,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    server_info = data["result"]
                    print(f"✅ Servidor MCP inicializado: {server_info.get('serverInfo', {}).get('name', 'Unknown')}")
                    print(f"   Versión del protocolo: {server_info.get('protocolVersion', 'Unknown')}")
                else:
                    print(f"⚠️  Error en initialize: {data.get('error', {}).get('message', 'Unknown')}")
            else:
                print(f"⚠️  No se pudo inicializar MCP: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Error al inicializar servidor MCP: {e}")
    
    def _load_mcp_tools(self):
        """Cargar herramientas MCP desde el servidor"""
        try:
            if self.use_jsonrpc:
                # Usar JSON-RPC 2.0
                request = self._jsonrpc_request("tools/list")
                response = requests.post(
                    f"{FASTAPI_BASE_URL}/mcp",
                    json=request,
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data and "tools" in data["result"]:
                        # Convertir formato MCP a formato OpenAI
                        mcp_tools = data["result"]["tools"]
                        self.tools = []
                        for tool in mcp_tools:
                            self.tools.append({
                                "type": "function",
                                "function": {
                                    "name": tool["name"],
                                    "description": tool["description"],
                                    "parameters": tool.get("inputSchema", {})
                                }
                            })
                        print(f"✅ {len(self.tools)} herramientas MCP cargadas (JSON-RPC)")
                        for tool in mcp_tools:
                            print(f"   📌 {tool['name']}")
                    else:
                        print(f"⚠️  Error en tools/list: {data.get('error', {}).get('message', 'Unknown')}")
                else:
                    print(f"⚠️  No se pudieron cargar las herramientas MCP: {response.status_code}")
            else:
                # Usar formato legacy
                response = requests.get(f"{FASTAPI_BASE_URL}/api/mcp/tools", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.tools = data["tools"]
                    print(f"✅ {len(self.tools)} herramientas MCP cargadas (legacy)")
                    for tool in self.tools:
                        print(f"   📌 {tool['function']['name']}")
                else:
                    print(f"⚠️  No se pudieron cargar las herramientas MCP: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Error al conectar con el servidor MCP: {e}")
            print("   El bot funcionará sin herramientas MCP")
    
    def _call_mcp_tool(self, tool_name: str, arguments: dict) -> dict:
        """Llamar a una herramienta MCP"""
        try:
            if self.use_jsonrpc:
                # Usar JSON-RPC 2.0
                request = self._jsonrpc_request("tools/call", {
                    "name": tool_name,
                    "arguments": arguments
                })
                
                response = requests.post(
                    f"{FASTAPI_BASE_URL}/mcp",
                    json=request,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data:
                        # Extraer el contenido del resultado MCP
                        result = data["result"]
                        if "content" in result and len(result["content"]) > 0:
                            # Parsear el JSON del contenido de texto
                            content_text = result["content"][0].get("text", "{}")
                            parsed_result = json.loads(content_text)
                            return {
                                "success": True,
                                "result": parsed_result
                            }
                        return {
                            "success": True,
                            "result": result
                        }
                    else:
                        error = data.get("error", {})
                        return {
                            "success": False,
                            "error": error.get("message", "Unknown error")
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Error HTTP {response.status_code}"
                    }
            else:
                # Usar formato legacy
                response = requests.post(
                    f"{FASTAPI_BASE_URL}/api/mcp/call-tool",
                    json={
                        "tool_name": tool_name,
                        "arguments": arguments
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"Error HTTP {response.status_code}"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_tool_calls(self, tool_calls):
        """Procesar llamadas a herramientas del modelo"""
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            print(f"\n🔧 Usando herramienta: {tool_name}")
            if tool_args:
                print(f"   Parámetros: {json.dumps(tool_args, ensure_ascii=False)}")
            
            # Llamar al tool MCP
            result = self._call_mcp_tool(tool_name, tool_args)
            
            if result.get("success"):
                print(f"   ✅ Resultado obtenido")
            else:
                print(f"   ❌ Error: {result.get('error')}")
            
            # Agregar tool call a los mensajes
            self.messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(tool_args)
                        }
                    }
                ]
            })
            
            # Agregar resultado del tool
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result.get("result", {}))
            })
    
    def chat(self, user_message: str) -> str:
        """Enviar un mensaje y obtener respuesta"""
        # Agregar mensaje del usuario
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Llamar al modelo
            response = self.client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=self.messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                max_completion_tokens=2000
            )
            
            assistant_message = response.choices[0].message
            
            # Procesar tool calls si existen
            if assistant_message.tool_calls:
                self._process_tool_calls(assistant_message.tool_calls)
                
                # Obtener respuesta final después de usar las herramientas
                final_response = self.client.chat.completions.create(
                    model=DEPLOYMENT_NAME,
                    messages=self.messages,
                    max_completion_tokens=2000
                )
                
                final_message = final_response.choices[0].message.content
                self.messages.append({
                    "role": "assistant",
                    "content": final_message
                })
                return final_message
            else:
                # Respuesta directa sin herramientas
                content = assistant_message.content
                self.messages.append({
                    "role": "assistant",
                    "content": content
                })
                return content
                
        except Exception as e:
            error_msg = f"Error al comunicarse con GPT: {e}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def run(self):
        """Ejecutar el bot en modo interactivo"""
        self._print_welcome()
        
        while self.conversation_active:
            try:
                # Leer entrada del usuario
                user_input = input("\n💬 Tú: ").strip()
                
                # Comandos especiales
                if user_input.lower() in ['/salir', '/exit', '/quit']:
                    print("\n👋 ¡Hasta luego!")
                    break
                
                if user_input.lower() == '/limpiar':
                    self._clear_history()
                    continue
                
                if user_input.lower() == '/historial':
                    self._show_history()
                    continue
                
                if user_input.lower() == '/ayuda':
                    self._show_help()
                    continue
                
                if not user_input:
                    continue
                
                # Obtener respuesta del bot
                print("\n🤖 Asistente: ", end="", flush=True)
                response = self.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _print_welcome(self):
        """Imprimir mensaje de bienvenida"""
        print("\n" + "=" * 70)
        print("🤖 BOT CHAT INTERACTIVO - GPT 5.2 + MCP")
        print("=" * 70)
        print(f"\n✅ Conectado a: {DEPLOYMENT_NAME}")
        print(f"✅ Servidor MCP: {FASTAPI_BASE_URL}")
        print("\n📝 Comandos disponibles:")
        print("   /salir     - Terminar la conversación")
        print("   /limpiar   - Limpiar historial de conversación")
        print(f"✅ Protocolo: {'JSON-RPC 2.0' if self.use_jsonrpc else 'Legacy'}")
        if self.use_jsonrpc:
            print(f"✅ Versión MCP: {MCP_PROTOCOL_VERSION}")
        print("   /historial - Ver historial de mensajes")
        print("   /ayuda     - Mostrar esta ayuda")
        print("\n💡 Puedes preguntarme lo que quieras. Tengo acceso a herramientas MCP.")
        print("=" * 70)
    
    def _clear_history(self):
        """Limpiar el historial de conversación"""
        self.messages = []
        self._setup_system()
        print("✅ Historial limpiado")
    
    def _show_history(self):
        """Mostrar el historial de mensajes"""
        print("\n📜 Historial de conversación:")
        print("-" * 70)
        for i, msg in enumerate(self.messages):
            if msg["role"] == "system":
                continue
            elif msg["role"] == "user":
                print(f"\n{i}. 💬 Usuario:")
                print(f"   {msg['content']}")
            elif msg["role"] == "assistant" and msg.get("content"):
                print(f"\n{i}. 🤖 Asistente:")
                print(f"   {msg['content']}")
            elif msg["role"] == "tool":
                print(f"\n{i}. 🔧 Resultado de herramienta")
        print("-" * 70)
    
    def _show_help(self):
        """Mostrar ayuda"""
        print("\n📚 Ayuda del Bot Chat")
        print("-" * 70)
        print("Comandos disponibles:")
        print("  /salir, /exit, /quit  - Terminar la conversación")
        print("  /limpiar              - Limpiar historial de conversación")
        print("  /historial            - Ver todos los mensajes")
        print("  /ayuda                - Mostrar esta ayuda")
        print("\nHerramientas MCP disponibles:")
        for tool in self.tools:
            func = tool['function']
            print(f"  • {func['name']}: {func['description']}")
        print("-" * 70)


def main():
    """Función principal"""
    # Verificar que el servidor MCP esté corriendo
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/health", timeout=3)
        if response.status_code != 200:
            print("⚠️  El servidor FastAPI no está respondiendo correctamente")
            print(f"   Asegúrate de que esté corriendo en {FASTAPI_BASE_URL}")
            return
    except Exception as e:
        print("❌ No se pudo conectar al servidor FastAPI")
        print(f"   Error: {e}")
        print(f"\n💡 Inicia el servidor con:")
        print("   python -m uvicorn app.main:app --reload")
        return
    
    # Iniciar el bot
    bot = MCPChatBot()
    bot.run()


if __name__ == "__main__":
    main()
