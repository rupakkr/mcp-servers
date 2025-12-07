import os
import sys
import asyncio
import json
from typing import Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cline_rules")

RULES_DIR = "rules"

def read_markdown_file(filename: str) -> str:
    filepath = os.path.join(RULES_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return f"Error: Missing file {filename} in {RULES_DIR}/"

@mcp.tool()
async def get_global_rules() -> str:
    return read_markdown_file("global_rules.md")

@mcp.tool()
async def get_local_rules() -> str:
    return read_markdown_file("local_rules.md")

# ---------------- MCP JSON-RPC structures ----------------

class JsonRpcRequest(BaseModel):
    jsonrpc: str
    id: Any
    method: str
    params: dict = Field(default_factory=dict)

# ---------------- MCP Handlers (HTTP Mode) ----------------

def mcp_handle(req: dict):
    method = req.get("method")

    # -------- 1. initialize handshake --------
    if method == "initialize":
        return {
            "protocolVersion": "2024-10-07",
            "serverInfo": {"name": "cline_rules", "version": "1.0.0"},
            "capabilities": { "tools": {}, "resources": {} }
        }

    # -------- 2. list tools --------
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "get_global_rules",
                    "description": "Get global rules",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "get_local_rules",
                    "description": "Get local rules",
                    "inputSchema": {"type": "object", "properties": {}}
                }
            ]
        }

    # -------- 3. resources/list --------
    if method == "resources/list":
        return {"resources": []}

    # -------- 4. tools/call --------
    if method == "tools/call":
        tool = req["params"]["name"]

        if tool == "get_global_rules":
            result = read_markdown_file("global_rules.md")
        elif tool == "get_local_rules":
            result = read_markdown_file("local_rules.md")
        else:
            raise Exception(f"Unknown tool: {tool}")

        return { "content": [ { "type": "text", "text": result } ] }

    raise Exception(f"Unknown MCP method: {method}")


# ---------------- SSE Server Setup ----------------

def main():
    # HTTP/SSE mode
    app = FastAPI(title="CLine Rules MCP (HTTP + SSE)")

    # GET /sse: persistent connection (keepalive)
    @app.get("/sse")
    async def sse_connect():
        async def stream():
            yield ": connected\n\n"
            while True:
                await asyncio.sleep(25)
                yield ": keepalive\n\n"

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )

    # POST /sse: one response event and CLOSE
    @app.post("/sse")
    async def sse_post(payload: dict):
        async def event():
            try:
                result = mcp_handle(payload)
                response = {
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "result": result
                }
            except Exception as e:
                response = {
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "error": { "code": -32601, "message": str(e) }
                }

            # Send exactly ONE event
            yield f"event: message\ndata: {json.dumps(response)}\n\n"

        return StreamingResponse(
            event(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
