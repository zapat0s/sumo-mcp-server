#!/usr/bin/env python3
"""
Simple tool listing script.

Lists all available MCP tools and their descriptions.
Connects to the MCP server via SSE (HTTP).

Prerequisites:
  1. Start the server first: python server.py --transport sse
  2. Then run this script: python tests/list_tools.py
"""
import asyncio
import sys
import argparse
from mcp import ClientSession
from mcp.client.sse import sse_client

DEFAULT_URL = "http://localhost:8000/sse"


async def list_all_tools(server_url: str):
    """List all available tools."""
    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools = await session.list_tools()
            
            print("🔧 Jumping Sumo MCP Server - Available Tools")
            print(f"📡 Connected to: {server_url}")
            print("=" * 70)
            print(f"\nTotal tools: {len(tools.tools)}\n")
            
            for i, tool in enumerate(tools.tools, 1):
                print(f"{i}. {tool.name}")
                print(f"   Description: {tool.description}")
                
                # Show parameters if any
                if tool.inputSchema and 'properties' in tool.inputSchema:
                    props = tool.inputSchema['properties']
                    if props:
                        print(f"   Parameters:")
                        for param_name, param_info in props.items():
                            param_type = param_info.get('type', 'unknown')
                            param_desc = param_info.get('description', 'No description')
                            default = param_info.get('default')
                            
                            param_str = f"      - {param_name} ({param_type}): {param_desc}"
                            if default:
                                param_str += f" [default: {default}]"
                            print(param_str)
                            
                            # Show enum values if available
                            if 'enum' in param_info:
                                print(f"        Options: {', '.join(param_info['enum'])}")
                print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List Jumping Sumo MCP Server Tools")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"SSE server URL (default: {DEFAULT_URL})")
    args = parser.parse_args()

    try:
        asyncio.run(list_all_tools(args.url))
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
