# Testing Scripts for Jumping Sumo MCP Server

This directory contains several test scripts in the `tests/` folder that allow you to test the MCP server directly without needing Claude Desktop. Tests connect to the server via SSE (HTTP).

## Prerequisites

1. Install dependencies:
   ```powershell
   pip install mcp
   ```

2. **Start the server in SSE mode** (required before running any test):
   ```powershell
   cd c:\Users\zer0z\Projects\JumpingSumoMCPServer\sumo-mcp-server
   python server.py --transport sse
   ```
   The server will listen on `http://localhost:8000`.

## Test Scripts

All test scripts are in the `tests/` directory and should be run from the `sumo-mcp-server` directory.

### 1. `tests/list_tools.py` - Tool Discovery
Lists all available MCP tools and their parameters.

```powershell
python tests/list_tools.py
```

**Use this first** to see what tools are available.

### 2. `tests/test_mcp_client.py` - Full Integration Test
Interactive test client that walks through:
- Connecting to robot
- Moving the robot
- Playing animations
- Getting camera frames
- Optional jump test

```powershell
python tests/test_mcp_client.py
```

**Best for initial testing** - covers all basic functionality with prompts.

### 3. `tests/test_animations.py` - Animation Suite
Tests all 10 built-in animations sequentially.

```powershell
python tests/test_animations.py
```

Animations tested:
- spin, tap, slowshake, metronome, ondulation
- spinjump, spintoposture, spiral, slalom

### 4. `tests/test_jump_kick.py` - Jump & Kick Testing
Comprehensive jumping and kicking test including:
- Simple high/long jumps
- Manual jump loading
- Posture changes (standing, jumper, kicker)
- Kicking sequence

```powershell
python tests/test_jump_kick.py
```

**Use with caution** - ensure adequate clearance around robot!

## Custom Server URL

All test scripts accept a `--url` argument to connect to a different server:

```powershell
python tests/list_tools.py --url http://192.168.1.100:8000/sse
```

## Usage Tips

1. **Start the server first** in a separate terminal:
   ```powershell
   python server.py --transport sse
   ```

2. **Connect to robot WiFi**
   - Robot network: JumpingSumo-XXXXXX
   - Verify: `ping 192.168.2.1`

3. **Run from the sumo-mcp-server directory**
   ```powershell
   python tests/test_mcp_client.py
   ```

4. **Start simple**
   - First run: `tests/list_tools.py`
   - Second run: `tests/test_mcp_client.py`
   - Then try specialized tests

5. **Interrupting tests**
   - Press `Ctrl+C` to interrupt any test
   - Robot will remain connected - use `disconnect_robot` call if needed

## Creating Custom Tests

You can create your own test scripts using this template:

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def my_test():
    async with sse_client("http://localhost:8000/sse") as (read, write):
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

**"Connection refused" or "Cannot connect"**
- Make sure the server is running: `python server.py --transport sse`
- Verify the server URL matches (default: `http://localhost:8000/sse`)

**"Robot not connected" errors**
- Ensure you're connected to robot WiFi
- Check robot is powered on
- Verify network: `ping 192.168.2.1`

## Safety Reminders

- ⚠️ Clear 2m x 2m space for movement tests
- ⚠️ 50cm clearance above for jump tests
- ⚠️ Keep hands clear during kicking tests
- ⚠️ Use `stop_jump` tool for emergency stop
