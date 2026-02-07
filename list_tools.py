#!/usr/bin/env python3
"""
Simple tool listing script.

Lists all available MCP tools and their descriptions.
"""
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def list_all_tools():
    """List all available tools."""
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools = await session.list_tools()
            
            print("🔧 Jumping Sumo MCP Server - Available Tools")
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
    try:
        asyncio.run(list_all_tools())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
