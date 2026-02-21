#!/usr/bin/env python3
"""
Quick animation test script for Jumping Sumo.

Tests all the robot's built-in animations.
Connects to the MCP server via SSE (HTTP).

Prerequisites:
  1. Start the server first: python server.py --transport sse
  2. Then run this script: python tests/test_animations.py
"""
import asyncio
import sys
import argparse
from mcp import ClientSession
from mcp.client.sse import sse_client

DEFAULT_URL = "http://localhost:8000/sse"


async def test_animations(server_url: str):
    """Test all animations sequentially."""
    animations = [
        "spin",
        "tap", 
        "slowshake",
        "metronome",
        "ondulation",
        "spinjump",
        "spintoposture",
        "spiral",
        "slalom"
    ]
    
    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("🎭 Animation Test Suite")
            print(f"📡 Connected to: {server_url}")
            print("=" * 50)
            
            # Connect to robot
            print("\n1. Connecting to robot...")
            result = await session.call_tool("connect_robot", arguments={})
            print(result.content[0].text)
            
            await asyncio.sleep(2)
            
            # Test each animation
            for i, anim in enumerate(animations, 2):
                print(f"\n{i}. Testing '{anim}' animation")
                print(f"   Press Enter to play (or Ctrl+C to skip)...")
                try:
                    input()
                    result = await session.call_tool("play_animation", arguments={"animation": anim})
                    print(f"   {result.content[0].text}")
                    await asyncio.sleep(3)  # Wait for animation to complete
                except KeyboardInterrupt:
                    print("   Skipped")
                    continue
            
            # Test stop animation
            print(f"\n{len(animations) + 2}. Testing 'stop' animation")
            result = await session.call_tool("play_animation", arguments={"animation": "stop"})
            print(f"   {result.content[0].text}")
            
            # Disconnect
            print("\n👋 Disconnecting...")
            await session.call_tool("disconnect_robot", arguments={})
            
            print("\n✅ Animation test complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jumping Sumo Animation Test")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"SSE server URL (default: {DEFAULT_URL})")
    args = parser.parse_args()

    try:
        asyncio.run(test_animations(args.url))
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
