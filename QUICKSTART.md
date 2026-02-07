# Quick Setup Guide - Parrot Jumping Sumo MCP Server

Follow these steps to get your robot control MCP server running:

## 1. Install Dependencies

```powershell
cd c:\Users\zer0z\.gemini\antigravity\playground\orbital-singularity\sumo-mcp-server
pip install -r requirements.txt
```

## 2. Connect to Robot WiFi

1. Turn on your Parrot Jumping Sumo robot
2. Connect your computer to the robot's WiFi network (JumpingSumo-XXXXXX)
3. Verify: `ping 192.168.2.1`

## 3. Configure Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "sumo-robot": {
      "command": "python",
      "args": [
        "c:\\Users\\zer0z\\.gemini\\antigravity\\playground\\orbital-singularity\\sumo-mcp-server\\server.py"
      ]
    }
  }
}
```

## 4. Restart Claude Desktop

Close and restart Claude Desktop to load the new MCP server.

## 5. Test the Connection

In Claude, try:
- "Connect to my Sumo robot"
- "Show me what the robot's camera sees"
- "Move the robot forward slowly for 2 seconds"
- "Make the robot dance" (plays ondulation animation)
- "Do a high jump"
- "Change to kicker posture"

**13 tools now available**:
- Connection (connect, disconnect, status)
- Movement (move_robot)
- Jumping (jump_robot, load_jump, cancel_jump, stop_jump)
- Postures (change_posture - standing/jumper/kicker)
- Animations (play_animation - 10 different animations)
- Camera (get_camera_frame, capture_photo)

## Safety Tips

- ⚠️ Test in a clear, open area
- ⚠️ Start with low speeds (20-30%)
- ⚠️ Keep robot on flat surfaces only
- ⚠️ Supervise all movement

See [README.md](README.md) for complete documentation.
