# Testing Scripts for Jumping Sumo MCP Server

This directory contains several test scripts that allow you to test the MCP server directly without needing Claude Desktop.

## Prerequisites

Make sure you have the MCP Python client library installed:

```powershell
pip install mcp
```

## Test Scripts

### 1. `list_tools.py` - Tool Discovery
Lists all available MCP tools and their parameters.

```powershell
python list_tools.py
```

**Use this first** to see what tools are available.

### 2. `test_mcp_client.py` - Full Integration Test
Interactive test client that walks through:
- Connecting to robot
- Moving the robot
- Playing animations
- Getting camera frames
- Optional jump test

```powershell
python test_mcp_client.py
```

**Best for initial testing** - covers all basic functionality with prompts.

### 3. `test_animations.py` - Animation Suite
Tests all 10 built-in animations sequentially.

```powershell
python test_animations.py
```

Animations tested:
- spin, tap, slowshake, metronome, ondulation
- spinjump, spintoposture, spiral, slalom

### 4. `test_jump_kick.py` - Jump & Kick Testing
Comprehensive jumping and kicking test including:
- Simple high/long jumps
- Manual jump loading
- Posture changes (standing, jumper, kicker)
- Kicking sequence

```powershell
python test_jump_kick.py
```

**Use with caution** - ensure adequate clearance around robot!

## Usage Tips

1. **Always connect to robot WiFi first**
   - Robot network: JumpingSumo-XXXXXX
   - Verify: `ping 192.168.2.1`

2. **Run from the sumo-mcp-server directory**
   ```powershell
   cd c:\Users\zer0z\Projects\JumpingSumoMCPServer\sumo-mcp-server
   python test_mcp_client.py
   ```

3. **Start simple**
   - First run: `list_tools.py`
   - Second run: `test_mcp_client.py`
   - Then try specialized tests

4. **Interrupting tests**
   - Press `Ctrl+C` to interrupt any test
   - Robot will remain connected - use `disconnect_robot` call if needed

## Creating Custom Tests

You can create your own test scripts using this template:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def my_test():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Your test code here
            result = await session.call_tool("connect_robot", arguments={})
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(my_test())
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'mcp'"**
- Install: `pip install mcp`

**"Robot not connected" errors**
- Ensure you're connected to robot WiFi
- Check robot is powered on
- Verify network: `ping 192.168.2.1`

**"Server not responding"**
- Make sure `server.py` is in the same directory
- Check Python path in server_params if needed

## Safety Reminders

- ⚠️ Clear 2m x 2m space for movement tests
- ⚠️ 50cm clearance above for jump tests
- ⚠️ Keep hands clear during kicking tests
- ⚠️ Use `stop_jump` tool for emergency stop
