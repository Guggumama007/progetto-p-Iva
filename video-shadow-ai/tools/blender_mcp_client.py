"""Client MCP per 'MCP for Blender' (ahujasid): avvia il server MCP via stdio,
che parla con l'add-on dentro Blender (porta 9876). Uso:
  python blender_mcp_client.py tools
  python blender_mcp_client.py call <tool> '<json args>'
  python blender_mcp_client.py code <file.py>     # esegue codice nella scena viva
"""
import asyncio, json, sys, os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="/opt/venv/tools/bin/mcp-for-blender", args=[], env={"BLENDER_HOST": "localhost", "BLENDER_PORT": "9876", "DISABLE_TELEMETRY": "true", "PATH": "/usr/bin:/bin"})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            mode = sys.argv[1]
            if mode == "tools":
                for t in (await s.list_tools()).tools: print("-", t.name, json.dumps(t.inputSchema.get("properties", {}))[:300])
                return
            if mode == "code":
                name, args = "execute_blender_code", {"code": open(sys.argv[2]).read()}
            else:
                name, args = sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
            res = await s.call_tool(name, args)
            for i, c in enumerate(res.content):
                if c.type == "image":
                    import base64; out = os.environ.get("MCP_IMG", "/tmp/mcp_look.png").replace(".png", f"_{i}.png")
                    open(out, "wb").write(base64.b64decode(c.data)); print("immagine salvata:", out)
                else: print(getattr(c, "text", f"[{c.type}]")[:3000])
asyncio.run(main())
