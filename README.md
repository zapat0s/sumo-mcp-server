# Parrot Jumping Sumo MCP Server

Control your Parrot Jumping Sumo robot through the Model Context Protocol! This MCP server enables AI assistants like Claude to drive your robot and see through its onboard camera.

## 🤖 Features

- **Robot Movement Control** - Drive forward/backward, turn left/right with precise speed and duration control
- **Advanced Jumping** - Complete jump control including spring loading, long/high jumps, and cancellation
- **Kicking** - Enable kicker mode and perform kicks with the front accessory
- **Posture Changes** - Switch between standing, jumper, and kicker stances
- **10 Built-in Animations** - Spin, tap, dance, spinjump, spiral, slalom, and more for personality
- **Live Camera Streaming** - View what your robot sees in real-time
- **Photo Capture** - Take photos and save them to the robot's internal storage
- **Connection Management** - Easy connect/disconnect with status monitoring
- **Safety Features** - Emergency stop, parameter validation, automatic shutdown

## 📋 Prerequisites

### Hardware
- **Parrot Jumping Sumo** robot (fully charged)
- Computer with WiFi capability

### Software
- **Python 3.8 - 3.11** (Python 3.12+ may have compatibility issues with opencv-python)
- **pip** package manager
- **Git** (for cloning repositories)

## 🚀 Installation

### Step 1: Clone the Required Repositories

The MCP server needs both this repository and the python-sumo library:

```powershell
# Navigate to your working directory
# The python-sumo repository should already be cloned
# If not, clone it:
git clone https://github.com/faturita/python-sumo.git

# Navigate to the MCP server directory
cd sumo-mcp-server
```

### Step 2: Install Python Dependencies

Install the required Python packages:

```powershell
# Install the MCP server and its dependencies
pip install -r requirements.txt

# Install the MCP server in editable mode (for development)
pip install -e .
```

> **Note**: If you encounter issues with opencv-python on Windows, you may need to install Visual C++ redistributables.

### Step 3: Connect to Your Robot

1. **Power on** your Parrot Jumping Sumo robot
2. Wait for the robot to boot up (lights will stabilize)
3. On your computer, open WiFi settings
4. Look for a network named **"JumpingSumo-XXXXXX"** (XXXXXX is a unique identifier)
5. Connect to this network (default password: none, it's an open network)
6. Verify connection by opening PowerShell and running:
   ```powershell
   ping 192.168.2.1
   ```
   You should see successful ping responses.

## 🎮 Usage

### Starting the MCP Server

There are two ways to run the server:

#### Option 1: Direct Execution
```powershell
python server.py
```

#### Option 2: Using the Installed Command
```powershell
sumo-mcp-server
```

The server will start and wait for MCP client connections via stdio.

### Configuring Your MCP Client

To use this server with Claude Desktop or another MCP client, add it to your MCP configuration file.

Add this configuration:

```json
{
  "mcpServers": {
    "sumo-robot": {
      "command": "python",
      "args": [
        "~/sumo-mcp-server/server.py"
      ]
    }
  }
}
```

Restart Claude Desktop after making changes.

### Available Tools

Once connected, the following **12 tools** will be available to your AI assistant:

#### Connection & Status

**1. `connect_robot`**
Establish connection to the robot.
- **Parameters**: 
  - `sumo_ip` (optional): Robot IP address (default: "192.168.2.1")
- **Usage**: "Connect to my Sumo robot"

**2. `disconnect_robot`**
Safely disconnect from the robot.
- **Parameters**: None
- **Usage**: "Disconnect from the robot"

**3. `get_connection_status`**
Check robot connection status.
- **Parameters**: None
- **Returns**: Connection status and IP address
- **Usage**: "Is the robot still connected?"

#### Movement

**4. `move_robot`**
Control robot movement.
- **Parameters**:
  - `speed` (required): -100 to 100 (negative = backward, positive = forward)
  - `turn` (optional): -100 to 100 (negative = left, positive = right)
  - `duration` (optional): Time in seconds (default: 1.0)
- **Usage Examples**:
  - "Move forward at 50% speed for 2 seconds"
  - "Turn left in place"
  - "Drive backward and turn right"

#### Jumping & Kicking

**5. `jump_robot`**
Execute a jump (simple one-step command).
- **Parameters**:
  - `jump_type` (optional): "long" or "high" (default: "long")
- **Usage**: "Make the robot jump" or "Do a high jump"

**6. `load_jump`**
Load/compress the spring (advanced control).
- **Parameters**: None
- **Usage**: "Load the jump spring"
- **Note**: Allows manual control of jump timing

**7. `cancel_jump`**
Cancel a loaded jump.
- **Parameters**: None
- **Usage**: "Cancel the jump"

**8. `stop_jump`**
Emergency stop for jump motor.
- **Parameters**: None
- **Usage**: "Stop the jump motor immediately"
- **Safety**: High priority emergency command

#### Postures

**9. `change_posture`**
Change robot's physical stance.
- **Parameters**:
  - `posture_type` (optional): "standing", "jumper", or "kicker"
- **Postures**:
  - **standing**: Normal driving mode
  - **jumper**: Jump-ready position
  - **kicker**: Enables kicking with front accessory
- **Usage**: "Change to kicker posture"

#### Animations

**10. `play_animation`**
Play built-in animations.
- **Parameters**:
  - `animation` (optional): Animation name
- **Available Animations**:
  - `stop` - Stop ongoing animation
  - `spin` - Spinning in place  
  - `tap` - Tapping motion
  - `slowshake` - Slow shaking
  - `metronome` - Back and forth like a metronome
  - `ondulation` - Standing dance
  - `spinjump` - Spin combined with jump
  - `spintoposture` - Spin ending in different posture
  - `spiral` - Spiral movement
  - `slalom` - Slalom-style zigzag
- **Usage**: "Do a spin animation" or "Make the robot dance"

#### Camera

**11. `get_camera_frame`**
Retrieve current camera view.
- **Parameters**: None
- **Returns**: JPEG image of what the robot sees
- **Usage**: "Show me what the robot's camera sees"

**12. `capture_photo`**
Take a photo to robot's storage.
- **Parameters**: None
- **Note**: Photo stored on robot, requires FTP to retrieve
- **Usage**: "Capture a photo"

## 💡 Example Usage Scenarios

### Basic Movement Test
```
You: "Connect to my robot and make it move forward slowly"
AI: *connects and moves robot at 30% speed for 1 second*
```

### Camera Exploration
```
You: "Show me what the robot sees, then turn right and show me again"
AI: *captures frame, rotates robot, captures another frame*
```

### Controlled Navigation
```
You: "Move the robot forward for 3 seconds, then rotate 90 degrees to the left"
AI: *executes forward movement, then executes turn command*
```

### Jumping Action
```
You: "Make the robot do a high jump"
AI: *executes high jump command*

You: "Do a long jump to clear that obstacle"
AI: *executes long jump for maximum distance*
```

### Advanced Jump Control (Manual Timing)
```
You: "Load the jump spring and wait for my signal"
AI: *compresses spring, robot ready*

You: "Now jump high!"
AI: *executes high jump from loaded state*
```

### Kicking Sequence
```
You: "Switch to kicker mode"
AI: *changes posture to kicker stance*

You: "Load the kicker and kick that ball"
AI: *loads mechanism, executes kick*

You: "Return to normal driving mode"
AI: *changes posture back to standing*
```

### Fun Animations
```
You: "Make the robot dance"
AI: *plays ondulation (dance) animation*

You: "Do a spin jump!"
AI: *plays spinjump animation*

You: "Make it do a slalom pattern"
AI: *plays slalom zigzag animation*

You: "Make it tap"
AI: *plays tap animation*
```

### Complex Sequence (Combining Features)
```
You: "Move forward, do a spin, then jump high"
AI: *drives forward, spins 360 degrees, performs high jump*
```

## 🌐 Network Deployment (Raspberry Pi)

You can deploy this server on a Raspberry Pi and control the robot remotely over your network!

See [DEPLOYMENT.md](DEPLOYMENT.md) for a complete setup guide.

Key features of network mode:
- **SSE Transport**: Uses Server-Sent Events standard for MCP
- **Remote Access**: Drive the robot from any computer on your network
- **Dual Connection**: Pi connects to Robot (WiFi) + Your Network (Ethernet)

Basic command:
```bash
python server.py --transport sse --host 0.0.0.0
```

## ⚠️ Safety Guidelines

1. **Clear Space**: Ensure the robot has adequate space to move (at least 2m x 2m)
2. **Jump Clearance**: When jumping, ensure at least 50cm clearance above robot
3. **Supervision**: Never leave the robot operating unattended
4. **Speed Limits**: Start with low speeds (20-30%) when testing
5. **Emergency Stop**: Use `stop_jump` command or power off if needed
6. **Surface**: Use on flat, smooth surfaces only
7. **Obstacles**: Keep the area clear of obstacles, stairs, and edges
8. **Kicking**: When in kicker mode, keep hands and objects clear of front accessory

## 🔧 Troubleshooting

### "Failed to connect to Sumo robot"

**Possible causes:**
- Robot is off or not fully booted → Wait 30 seconds after power on
- Not connected to robot's WiFi → Check WiFi connection
- Another device is connected → Only one connection allowed at a time
- Windows Firewall blocking → Allow Python through firewall

**Solution:**
```powershell
# Test network connectivity
ping 192.168.2.1

# If ping fails, reconnect to robot's WiFi
```

### "No camera frame available yet"

**Cause:** Video stream still initializing

**Solution:** Wait 2-3 seconds after connecting, then try again

### "Robot not connected" error

**Cause:** Connection was lost or never established

**Solution:** 
1. Check `get_connection_status`
2. If disconnected, use `connect_robot` again
3. Verify robot is still powered on

### Python/OpenCV Issues

**ImportError for cv2:**
```powershell
# Reinstall opencv-python
pip uninstall opencv-python
pip install opencv-python
```

**Python version issues:**
- Use Python 3.8-3.11 for best compatibility
- Python 3.12+ may require opencv-python from source

## 📁 Project Structure

```
sumo-mcp-server/
├── server.py              # Main MCP server implementation
├── sumopy_wrapper.py      # Wrapper for python-sumo library
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Package configuration
└── README.md             # This file

python-sumo/              # Separate repository
├── sumopy/
│   ├── interface.py      # SumoController class
│   └── commands.py       # Command definitions
└── ...
```

## 🛠️ Development

### Running in Development Mode

```powershell
# Install in editable mode with dependencies
pip install -e .

# Run the server with logging
python server.py
```

### Modifying the Server

- **Add new tools**: Add a new `@app.tool(...)` function in `server.py`
- **Change robot behavior**: Modify `sumopy_wrapper.py`
- **Adjust connection settings**: Edit default parameters in `SumoWrapper.__init__()`

## 📝 Technical Details

### Communication Protocol

- **Connection**: WiFi, TCP/UDP sockets
- **Default IP**: 192.168.2.1
- **Ports**: 44444 (init), 54321 (device-to-controller), dynamic (controller-to-device)
- **Command Frequency**: 40 Hz for maintaining connection
- **Video Format**: JPEG frames via UDP

### Camera Stream

The robot streams JPEG-encoded frames over UDP. The MCP server:
1. Automatically starts video streaming on connect
2. Buffers the latest frame
3. Returns JPEG data when `get_camera_frame` is called
4. Saves frames to the artifacts directory for persistence

### Movement Control

Movement commands specify:
- **Speed**: -100 (full reverse) to +100 (full forward)
- **Turn**: -100 (hard left) to +100 (hard right)  
- **Duration**: Minimum 0.025s (1 frame at 40Hz)

Commands are sent at 40Hz. Between explicit commands, the server sends "stop" commands to maintain the connection.

## 📚 References

- [python-sumo GitHub Repository](https://github.com/faturita/python-sumo)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Parrot Jumping Sumo Hacking Resources](https://ka010.com/post/108890023092/hacking-the-parrot-jumping-sumo)

## 📄 License

This MCP server wrapper is provided as-is for educational and personal use. The underlying python-sumo library has its own license (check the repository).

## 🤝 Contributing

Feel free to submit issues, suggestions, or improvements!

---

**Happy robot driving! 🚗🤖**
