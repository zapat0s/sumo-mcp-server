#!/usr/bin/env python3
"""
Jump and posture test script.

Tests the complete jump workflow including loading, postures, and kicking.
Connects to the MCP server via SSE (HTTP).

Prerequisites:
  1. Start the server first: python server.py --transport sse
  2. Then run this script: python tests/test_jump_kick.py
"""
import asyncio
import sys
import argparse
from mcp import ClientSession
from mcp.client.sse import sse_client

DEFAULT_URL = "http://localhost:8000/sse"


async def test_jumping(server_url: str):
    """Test jump and kicking functionality."""
    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("🦘 Jump & Kick Test Suite")
            print(f"📡 Connected to: {server_url}")
            print("=" * 50)
            
            # Connect
            print("\n1. Connecting to robot...")
            result = await session.call_tool("connect_robot", arguments={})
            print(result.content[0].text)
            await asyncio.sleep(2)
            
            # Test simple jump
            print("\n2. Simple high jump test")
            input("   Press Enter to execute high jump...")
            result = await session.call_tool("jump_robot", arguments={"jump_type": "high"})
            print(f"   {result.content[0].text}")
            await asyncio.sleep(3)
            
            # Test simple long jump
            print("\n3. Simple long jump test")
            input("   Press Enter to execute long jump...")
            result = await session.call_tool("jump_robot", arguments={"jump_type": "long"})
            print(f"   {result.content[0].text}")
            await asyncio.sleep(3)
            
            # Test manual jump loading
            print("\n4. Manual jump control test")
            input("   Press Enter to load jump spring...")
            result = await session.call_tool("load_jump", arguments={})
            print(f"   {result.content[0].text}")
            await asyncio.sleep(2)
            
            print("\n   Spring loaded! Now execute jump...")
            input("   Press Enter to jump...")
            result = await session.call_tool("jump_robot", arguments={"jump_type": "high"})
            print(f"   {result.content[0].text}")
            await asyncio.sleep(3)
            
            # Test posture changes
            print("\n5. Posture test - Jumper mode")
            input("   Press Enter to change to jumper posture...")
            result = await session.call_tool("change_posture", arguments={"posture_type": "jumper"})
            print(f"   {result.content[0].text}")
            await asyncio.sleep(2)
            
            # Back to standing
            print("\n6. Return to standing posture")
            result = await session.call_tool("change_posture", arguments={"posture_type": "standing"})
            print(f"   {result.content[0].text}")
            await asyncio.sleep(2)
            
            # Test kicker mode (if user wants)
            print("\n7. Kicker mode test")
            kick = input("   Test kicker mode? (y/n): ")
            if kick.lower() == 'y':
                print("\n   Changing to kicker posture...")
                result = await session.call_tool("change_posture", arguments={"posture_type": "kicker"})
                print(f"   {result.content[0].text}")
                await asyncio.sleep(2)
                
                input("   Press Enter to load kicker...")
                result = await session.call_tool("load_jump", arguments={})
                print(f"   {result.content[0].text}")
                await asyncio.sleep(1)
                
                input("   Press Enter to KICK...")
                result = await session.call_tool("jump_robot", arguments={"jump_type": "long"})
                print(f"   {result.content[0].text}")
                await asyncio.sleep(2)
                
                # Return to standing
                result = await session.call_tool("change_posture", arguments={"posture_type": "standing"})
                print(f"   {result.content[0].text}")
            
            # Disconnect
            print("\n👋 Disconnecting...")
            await session.call_tool("disconnect_robot", arguments={})
            
            print("\n✅ Jump test complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jumping Sumo Jump & Kick Test")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"SSE server URL (default: {DEFAULT_URL})")
    args = parser.parse_args()

    try:
        asyncio.run(test_jumping(args.url))
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
