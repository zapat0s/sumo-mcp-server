"""
Parrot Jumping Sumo MCP Server

This MCP server provides tools to control a Parrot Jumping Sumo robot
and access its onboard camera through the Model Context Protocol.
"""
import asyncio
import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

# Import the wrapper module
from sumopy_wrapper import SumoWrapper

# Initialize the MCP server
app = Server("sumo-robot-controller")

# Global robot wrapper instance
robot: Optional[SumoWrapper] = None

# Define the tools
TOOLS = [
    Tool(
        name="connect_robot",
        description="Connect to the Parrot Jumping Sumo robot via WiFi. The robot must be powered on and your computer must be connected to its WiFi network (default IP: 192.168.2.1).",
        inputSchema={
            "type": "object",
            "properties": {
                "sumo_ip": {
                    "type": "string",
                    "description": "IP address of the Sumo robot (default: 192.168.2.1)",
                    "default": "192.168.2.1"
                }
            }
        }
    ),
    Tool(
        name="disconnect_robot",
        description="Safely disconnect from the Sumo robot and clean up resources.",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="move_robot",
        description="Control the robot's movement. Speed controls forward/backward motion (-100 to 100), turn controls rotation (-100 to 100 for -360 to 360 degrees), and duration is in seconds. The robot will execute the command for the specified duration then stop.",
        inputSchema={
            "type": "object",
            "properties": {
                "speed": {
                    "type": "integer",
                    "description": "Movement speed from -100 (full backward) to 100 (full forward), 0 = stop",
                    "minimum": -100,
                    "maximum": 100
                },
                "turn": {
                    "type": "integer",
                    "description": "Turn rate from -100 (full left) to 100 (full right), 0 = straight",
                    "minimum": -100,
                    "maximum": 100,
                    "default": 0
                },
                "duration": {
                    "type": "number",
                    "description": "Duration of movement in seconds (minimum 0.025s)",
                    "minimum": 0.025,
                    "default": 1.0
                }
            },
            "required": ["speed"]
        }
    ),
    Tool(
        name="get_camera_frame",
        description="Retrieve the current frame from the robot's onboard camera. Returns a base64-encoded JPEG image and saves it to the artifacts directory for viewing. The video stream must be active (automatically started on connect).",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="capture_photo",
        description="Capture a photo to the robot's internal storage. Note: The photo is stored on the robot itself and requires FTP access to retrieve. Use get_camera_frame instead if you want immediate access to images.",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="jump_robot",
        description="Make the robot jump! The Jumping Sumo can perform two types of jumps: 'long' for distance and 'high' for height. Note: Ensure adequate clearance above and around the robot before jumping.",
        inputSchema={
            "type": "object",
            "properties": {
                "jump_type": {
                    "type": "string",
                    "enum": ["long", "high"],
                    "description": "Type of jump: 'long' for maximum distance or 'high' for maximum height",
                    "default": "long"
                }
            }
        }
    ),
    Tool(
        name="load_jump",
        description="Load/compress the spring for jumping or kicking. This prepares the robot without executing the action immediately. After loading, you can execute a jump or kick.",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="cancel_jump",
        description="Cancel a loaded jump and return the robot to its previous state. Use this to abort a jump after calling load_jump.",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="stop_jump",
        description="Emergency stop for the jump motor. Immediately stops any jump-related motion. Use for safety.",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="change_posture",
        description="Change the robot's physical posture. Options: 'standing' (normal driving), 'jumper' (jump-ready), or 'kicker' (enables kicking with front accessory).",
        inputSchema={
            "type": "object",
            "properties": {
                "posture_type": {
                    "type": "string",
                    "enum": ["standing", "jumper", "kicker"],
                    "description": "The posture to assume",
                    "default": "standing"
                }
            }
        }
    ),
    Tool(
        name="play_animation",
        description="Play one of the robot's built-in animations for fun and personality. Options include spin, tap, slowshake, metronome, ondulation (dance), spinjump, spintoposture, spiral, slalom, and stop.",
        inputSchema={
            "type": "object",
            "properties": {
                "animation": {
                    "type": "string",
                    "enum": ["stop", "spin", "tap", "slowshake", "metronome", "ondulation", "spinjump", "spintoposture", "spiral", "slalom"],
                    "description": "The animation to play",
                    "default": "spin"
                }
            }
        }
    ),
    Tool(
        name="get_connection_status",
        description="Check if the robot is currently connected and responding. Returns connection status and details.",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available robot control tools."""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for robot control."""
    global robot
    
    try:
        if name == "connect_robot":
            sumo_ip = arguments.get("sumo_ip", "192.168.2.1")
            
            # Disconnect existing connection if any
            if robot is not None:
                robot.disconnect()
            
            # Create new robot connection
            robot = SumoWrapper(sumo_ip=sumo_ip)
            
            if robot.is_connected():
                return [
                    TextContent(
                        type="text",
                        text=f"✅ Successfully connected to Sumo robot at {sumo_ip}\n"
                             f"Video streaming is active. You can now control the robot!\n\n"
                             f"Available commands:\n"
                             f"- move_robot: Control movement\n"
                             f"- get_camera_frame: View camera\n"
                             f"- capture_photo: Take a photo\n"
                             f"- get_connection_status: Check status"
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Failed to connect to Sumo robot at {sumo_ip}\n\n"
                             f"Troubleshooting:\n"
                             f"1. Ensure the robot is powered on\n"
                             f"2. Connect to the robot's WiFi network (JumpingSumo-XXXXXX)\n"
                             f"3. Verify you can ping {sumo_ip}\n"
                             f"4. Check that no other device is connected to the robot"
                    )
                ]
        
        elif name == "disconnect_robot":
            if robot is None:
                return [TextContent(type="text", text="ℹ️ No robot connection active.")]
            
            robot.disconnect()
            robot = None
            return [TextContent(type="text", text="✅ Successfully disconnected from robot.")]
        
        elif name == "get_connection_status":
            if robot is None:
                return [
                    TextContent(
                        type="text",
                        text="❌ Not connected to robot.\nUse connect_robot to establish a connection."
                    )
                ]
            
            connected = robot.is_connected()
            status_emoji = "✅" if connected else "❌"
            status_text = "Connected" if connected else "Disconnected"
            
            return [
                TextContent(
                    type="text",
                    text=f"{status_emoji} Robot Status: {status_text}\n"
                         f"IP Address: {robot.sumo_ip}"
                )
            ]
        
        # All other commands require an active connection
        if robot is None:
            return [
                TextContent(
                    type="text",
                    text="❌ Error: Not connected to robot.\n"
                         "Please use connect_robot first to establish a connection."
                )
            ]
        
        if not robot.is_connected():
            return [
                TextContent(
                    type="text",
                    text="❌ Error: Robot connection lost.\n"
                         "Please reconnect using connect_robot."
                )
            ]
        
        if name == "move_robot":
            speed = arguments["speed"]
            turn = arguments.get("turn", 0)
            duration = arguments.get("duration", 1.0)
            
            # Execute movement
            robot.move(speed, turn, duration)
            
            # Build description
            direction = "forward" if speed > 0 else "backward" if speed < 0 else "no movement"
            turn_desc = ""
            if turn > 0:
                turn_desc = f", turning right ({abs(turn)}%)"
            elif turn < 0:
                turn_desc = f", turning left ({abs(turn)}%)"
            
            return [
                TextContent(
                    type="text",
                    text=f"🤖 Robot moving {direction} at {abs(speed)}% speed{turn_desc} for {duration}s"
                )
            ]
        
        elif name == "get_camera_frame":
            # Get the latest frame
            frame_data = robot.get_camera_frame()
            
            if frame_data is None:
                return [
                    TextContent(
                        type="text",
                        text="⚠️ No camera frame available yet.\n"
                             "The video stream may still be initializing. Please try again in a moment."
                    )
                ]
            
            # Save to artifacts directory
            artifacts_dir = Path(os.environ.get("APPDATA_DIR", ".")) / "brain" / os.environ.get("CONVERSATION_ID", "default") / "camera_frames"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            frame_path = artifacts_dir / f"sumo_frame_{timestamp}.jpg"
            
            with open(frame_path, "wb") as f:
                f.write(frame_data)
            
            # Encode as base64 for return
            frame_base64 = base64.b64encode(frame_data).decode('utf-8')
            
            return [
                TextContent(
                    type="text",
                    text=f"📷 Camera frame captured and saved to:\n{frame_path}\n\n"
                         f"Image size: {len(frame_data)} bytes"
                ),
                ImageContent(
                    type="image",
                    data=frame_base64,
                    mimeType="image/jpeg"
                )
            ]
        
        elif name == "capture_photo":
            robot.capture_photo()
            
            return [
                TextContent(
                    type="text",
                    text="📸 Photo captured to robot's internal storage.\n\n"
                         "Note: The photo is stored on the robot itself.\n"
                         "To retrieve it, you'll need to access the robot via FTP.\n"
                         "For immediate viewing, use get_camera_frame instead."
                )
            ]
        
        elif name == "jump_robot":
            jump_type = arguments.get("jump_type", "long")
            
            # Execute jump
            robot.jump(jump_type)
            
            jump_emoji = "🦘" if jump_type == "long" else "⬆️"
            jump_desc = "long jump (for distance)" if jump_type == "long" else "high jump (for height)"
            
            return [
                TextContent(
                    type="text",
                    text=f"{jump_emoji} Robot performing {jump_desc}!\n\n"
                         "⚠️ Make sure there's adequate clearance around the robot."
                )
            ]
        
        elif name == "load_jump":
            robot.load_jump()
            
            return [
                TextContent(
                    type="text",
                    text="🔧 Spring loaded! Robot ready to jump or kick.\n\n"
                         "Next steps:\n"
                         "- Call jump_robot to execute the jump\n"
                         "- Or change_posture to kicker, then jump_robot to kick\n"
                         "- Or cancel_jump to abort"
                )
            ]
        
        elif name == "cancel_jump":
            robot.cancel_jump()
            
            return [
                TextContent(
                    type="text",
                    text="↩️ Jump cancelled. Robot returning to previous state."
                )
            ]
        
        elif name == "stop_jump":
            robot.stop_jump()
            
            return [
                TextContent(
                    type="text",
                    text="🛑 Jump motor stopped immediately (emergency stop)."
                )
            ]
        
        elif name == "change_posture":
            posture_type = arguments.get("posture_type", "standing")
            
            robot.change_posture(posture_type)
            
            posture_emojis = {
                "standing": "🚗",
                "jumper": "🦘",
                "kicker": "⚽"
            }
            
            posture_descriptions = {
                "standing": "normal driving mode",
                "jumper": "jump-ready position",
                "kicker": "kicking stance (front accessory active)"
            }
            
            emoji = posture_emojis.get(posture_type, "🤖")
            desc = posture_descriptions.get(posture_type, posture_type)
            
            return [
                TextContent(
                    type="text",
                    text=f"{emoji} Posture changed to {posture_type} ({desc})."
                )
            ]
        
        elif name == "play_animation":
            animation = arguments.get("animation", "spin")
            
            robot.play_animation(animation)
            
            animation_emojis = {
                "stop": "⏹️",
                "spin": "🌀",
                "tap": "👆",
                "slowshake": "🤝",
                "metronome": "⏱️",
                "ondulation": "💃",
                "spinjump": "🌪️",
                "spintoposture": "🔄",
                "spiral": "🌀",
                "slalom": "⛷️"
            }
            
            emoji = animation_emojis.get(animation, "✨")
            
            return [
                TextContent(
                    type="text",
                    text=f"{emoji} Playing '{animation}' animation!"
                )
            ]
        
        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]
    
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"❌ Error executing {name}: {str(e)}\n\n"
                     f"If this is a connection error, try reconnecting with connect_robot."
            )
        ]


async def main():
    """Run the MCP server."""
    # Use stdio transport for MCP communication
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
