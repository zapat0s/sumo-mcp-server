# Raspberry Pi Deployment Guide

This guide explains how to deploy the Jumping Sumo MCP Server on a Raspberry Pi to control your robot over the network.

## Prerequisites

- **Raspberry Pi** (3B+, 4, or 5 recommended) running Raspberry Pi OS (Bullseye or later)
- **Python 3.9+** (Installed by default on Raspbian)
- **WiFi connection** on the Pi (to connect to the robot)
- **Ethernet connection** (optional but recommended for the Pi to connect to your network)

> **Note**: The Raspberry Pi needs to connect to the Jumping Sumo's WiFi network (`JumpingSumo-XXXXXX`). This means it will lose internet access via WiFi. Ideally, connect the Pi to your home network via **Ethernet** so you can access it while it controls the robot.

## Step 1: System Setup

Update your system and install system dependencies for OpenCV and Python:

```bash
sudo apt update
sudo apt install -y git python3-pip python3-venv libgl1-mesa-glx libglib2.0-0
```

## Step 2: Clone the Repository

Clone the project to your Raspberry Pi:

```bash
cd ~
git clone <your-repo-url> jumping-sumo-mcp
cd jumping-sumo-mcp
```

## Step 3: Set Up Python Environment

Create a virtual environment to keep dependencies isolated:

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r sumo-mcp-server/requirements.txt
```

> **Note**: If you encounter issues installing `opencv-python` on Raspberry Pi, you might need to use `apt` instead:
> `sudo apt install python3-opencv`
> And then remove `opencv-python` from requirements.txt.

## Step 4: install python-sumo Fork

You need the `python-sumo` library. Since we're using a specific fork with Python 3 fixes:

```bash
# Clone the fork
git clone https://github.com/zapat0s/python-sumo.git

# Install in editable mode
pip install -e python-sumo
```

## Step 5: Network Configuration

1. **Connect Pi to Robot WiFi**:
   - On the Pi desktop, select the `JumpingSumo-XXXXXX` network.
   - Or use command line:
     ```bash
     sudo nmcli dev wifi connect "JumpingSumo-XXXXXX"
     ```

2. **Verify Connection**:
   ```bash
   ping 192.168.2.1
   ```

3. **Check Pi's IP Address**:
   Find the IP address of your Pi regarding your home network (Ethernet interface `eth0` usually):
   ```bash
   ip addr show eth0
   ```
   *Example: 192.168.1.50*

## Step 6: Run the Server

Start the server in **SSE mode**:

```bash
cd sumo-mcp-server
python server.py --transport sse --host 0.0.0.0 --port 8000
```

- `--host 0.0.0.0` allows connections from other devices on the network.
- `--port 8000` specifies the port (default).

You should see:
```
🚀 Starting Jumping Sumo MCP Server (SSE)
📡 Listening on http://0.0.0.0:8000
🔗 SSE Endpoint: http://0.0.0.0:8000/sse
```

## Step 7: Connect from Claude Desktop

On your main computer (where Claude Desktop is running):

1. Edit your `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac).

2. Add the SSE configuration:

```json
{
  "mcpServers": {
    "sumo-pi": {
      "endpoint": "http://192.168.1.50:8000/sse",
      "transport": "sse"
    }
  }
}
```
*(Replace `192.168.1.50` with your Pi's actual IP address)*

3. Restart Claude Desktop.

4. You should now be able to control the robot through Claude!

## Troubleshooting

**"Connection Refused"**
- Check if the Pi firewall is blocking port 8000.
- Ensure you used `--host 0.0.0.0`.

**Robot Connection Fails**
- Ensure the Pi is connected to the `JumpingSumo-XXXXXX` WiFi.
- The Pi cannot be connected to your home WiFi to reach the robot (unless you have a dual WiFi setup). Recommendation: Use Ethernet for home network, WiFi for robot.

**Latency Issues**
- Video streaming over two network hops (Robot->Pi->PC) can have latency.
- Reduce usage of `get_camera_frame` if it's too slow.
