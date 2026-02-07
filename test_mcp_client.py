#!/usr/bin/env python3
"""
Basic MCP test client for Jumping Sumo robot.

This script allows you to test the MCP server without Claude Desktop.
It connects to the MCP server and sends tool calls directly.
"""
import asyncio
import json
import sys
from typing import Any, Dict

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_tool(session: ClientSession, tool_name: str, arguments: Dict[str, Any] = None):
    """Call a tool on the MCP server."""
    if arguments is None:
        arguments = {}
    
    print(f"\n🔧 Calling tool: {tool_name}")
    if arguments:
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")
    
    result = await session.call_tool(tool_name, arguments=arguments)
    
    print(f"\n✅ Response:")
    for content in result.content:
        if hasattr(content, 'text'):
            print(content.text)
        elif hasattr(content, 'data'):
            print(f"   [Image data: {len(content.data)} bytes]")
    
    return result


async def list_tools(session: ClientSession):
    """List all available tools."""
    tools = await session.list_tools()
    print("\n📋 Available Tools:")
    for i, tool in enumerate(tools.tools, 1):
        print(f"{i}. {tool.name}")
        print(f"   {tool.description}")
    return tools


async def main():
    """Main test function."""
    print("🤖 Jumping Sumo MCP Test Client")
    print("=" * 50)
    
    # Server parameters - adjust path if needed
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            await list_tools(session)
            
            print("\n" + "=" * 50)
            print("🧪 Running Test Sequence")
            print("=" * 50)
            
            # Test 1: Get connection status
            await call_tool(session, "get_connection_status")
            
            # Test 2: Connect to robot
            print("\n⚠️  Make sure your robot is on and you're connected to its WiFi!")
            input("Press Enter when ready to connect...")
            
            await call_tool(session, "connect_robot", {"sumo_ip": "192.168.2.1"})
            
            # Wait a moment for connection to stabilize
            await asyncio.sleep(2)
            
            # Test 3: Check status again
            await call_tool(session, "get_connection_status")
            
            # Test 4: Move robot
            print("\n⚠️  Robot will move forward!")
            input("Press Enter to make robot move forward...")
            
            await call_tool(session, "move_robot", {
                "speed": 30,
                "turn": 0,
                "duration": 1.0
            })
            
            # Test 5: Play animation
            print("\n🎭 Robot will perform a spin animation!")
            input("Press Enter to play animation...")
            
            await call_tool(session, "play_animation", {"animation": "spin"})
            
            # Test 6: Get camera frame
            print("\n📷 Retrieving camera frame...")
            await call_tool(session, "get_camera_frame")
            
            # Optional: Jump test
            print("\n🦘 Jump test (optional)")
            jump = input("Do you want to test jumping? (y/n): ")
            if jump.lower() == 'y':
                await call_tool(session, "jump_robot", {"jump_type": "high"})
            
            # Disconnect
            print("\n👋 Disconnecting from robot...")
            await call_tool(session, "disconnect_robot")
            
            print("\n✅ Test sequence complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
