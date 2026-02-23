"""
Parrot Jumping Sumo MCP Server.

This MCP server provides tools to control a Parrot Jumping Sumo robot
and access its onboard camera through the Model Context Protocol.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal, Optional

from mcp.server.fastmcp import FastMCP, Image
from pydantic import Field

from sumopy_wrapper import SumoWrapper


robot: Optional[SumoWrapper] = None
CAMERA_FRAMES_DIR = Path(__file__).resolve().parent / "artifacts" / "camera_frames"


def create_app(host: str = "0.0.0.0", port: int = 8000) -> FastMCP:
    """Build and configure the FastMCP app."""
    app = FastMCP(
        name="sumo-robot-controller",
        host=host,
        port=port,
        sse_path="/sse",
        message_path="/messages",
        log_level="INFO",
    )

    @app.tool(
        name="connect_robot",
        description=(
            "Connect to the Parrot Jumping Sumo robot via WiFi. The robot must be "
            "powered on and your computer must be connected to its WiFi network "
            "(default IP: 192.168.2.1)."
        ),
        structured_output=False,
    )
    def connect_robot(sumo_ip: str = "192.168.2.1") -> str:
        global robot
        try:
            if robot is not None:
                robot.disconnect()

            robot = SumoWrapper(sumo_ip=sumo_ip)
            if robot.is_connected():
                return (
                    f"Connected to Sumo robot at {sumo_ip}\n"
                    "Video streaming is active. You can now control the robot.\n\n"
                    "Available commands:\n"
                    "- move_robot: Control movement\n"
                    "- get_camera_frame: View camera\n"
                    "- capture_photo: Take a photo\n"
                    "- get_connection_status: Check status"
                )

            return (
                f"Failed to connect to Sumo robot at {sumo_ip}\n\n"
                "Troubleshooting:\n"
                "1. Ensure the robot is powered on\n"
                "2. Connect to the robot's WiFi network (JumpingSumo-XXXXXX)\n"
                f"3. Verify you can ping {sumo_ip}\n"
                "4. Check that no other device is connected to the robot"
            )
        except Exception as exc:
            return (
                f"Error executing connect_robot: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    @app.tool(
        name="disconnect_robot",
        description="Safely disconnect from the Sumo robot and clean up resources.",
        structured_output=False,
    )
    def disconnect_robot() -> str:
        global robot
        try:
            if robot is None:
                return "No robot connection active."
            robot.disconnect()
            robot = None
            return "Disconnected from robot."
        except Exception as exc:
            return (
                f"Error executing disconnect_robot: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    @app.tool(
        name="get_connection_status",
        description="Check if the robot is currently connected and responding. Returns connection status and details.",
        structured_output=False,
    )
    def get_connection_status() -> str:
        global robot
        try:
            if robot is None:
                return "Not connected to robot.\nUse connect_robot to establish a connection."

            connected = robot.is_connected()
            status_text = "Connected" if connected else "Disconnected"
            return f"Robot Status: {status_text}\nIP Address: {robot.sumo_ip}"
        except Exception as exc:
            return (
                f"Error executing get_connection_status: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    def ensure_connected() -> Optional[str]:
        if robot is None:
            return (
                "Error: Not connected to robot.\n"
                "Please use connect_robot first to establish a connection."
            )
        if not robot.is_connected():
            return "Error: Robot connection lost.\nPlease reconnect using connect_robot."
        return None

    @app.tool(
        name="move_robot",
        description=(
            "Control the robot's movement. Speed controls forward/backward motion "
            "(-100 to 100), turn controls rotation (-100 to 100 for -360 to 360 degrees), "
            "and duration is in seconds. The robot will execute the command for the "
            "specified duration then stop."
        ),
        structured_output=False,
    )
    def move_robot(
        speed: Annotated[
            int,
            Field(
                ge=-100,
                le=100,
                description="Movement speed from -100 (full backward) to 100 (full forward), 0 = stop",
            ),
        ],
        turn: Annotated[
            int,
            Field(
                ge=-100,
                le=100,
                description="Turn rate from -100 (full left) to 100 (full right), 0 = straight",
            ),
        ] = 0,
        duration: Annotated[
            float,
            Field(ge=0.025, description="Duration of movement in seconds (minimum 0.025s)"),
        ] = 1.0,
    ) -> str:
        global robot
        try:
            error = ensure_connected()
            if error is not None:
                return error

            assert robot is not None
            robot.move(speed, turn, duration)

            direction = "forward" if speed > 0 else "backward" if speed < 0 else "no movement"
            turn_desc = ""
            if turn > 0:
                turn_desc = f", turning right ({abs(turn)}%)"
            elif turn < 0:
                turn_desc = f", turning left ({abs(turn)}%)"

            return f"Robot moving {direction} at {abs(speed)}% speed{turn_desc} for {duration}s"
        except Exception as exc:
            return (
                f"Error executing move_robot: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    @app.tool(
        name="get_camera_frame",
        description=(
            "Retrieve the current frame from the robot's onboard camera. Returns a "
            "JPEG image and saves it to the artifacts directory for "
            "viewing. The video stream must be active (automatically started on connect)."
        ),
        structured_output=False,
    )
    def get_camera_frame() -> list[str | Image]:
        global robot
        try:
            error = ensure_connected()
            if error is not None:
                return [error]

            assert robot is not None
            frame_data = robot.get_camera_frame()
            if frame_data is None:
                return [
                    (
                        "No camera frame available yet.\n"
                        "The video stream may still be initializing. Please try again in a moment."
                    )
                ]

            CAMERA_FRAMES_DIR.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            frame_path = CAMERA_FRAMES_DIR / f"sumo_frame_{timestamp}.jpg"
            with open(frame_path, "wb") as file_obj:
                file_obj.write(frame_data)

            return [
                f"Camera frame captured and saved to:\n{frame_path}\n\nImage size: {len(frame_data)} bytes",
                Image(data=frame_data, format="jpeg"),
            ]
        except Exception as exc:
            return [
                (
                    f"Error executing get_camera_frame: {exc}\n\n"
                    "If this is a connection error, try reconnecting with connect_robot."
                )
            ]

    @app.tool(
        name="capture_photo",
        description=(
            "Capture a photo to the robot's internal storage. Note: The photo is stored "
            "on the robot itself and requires FTP access to retrieve. Use get_camera_frame "
            "instead if you want immediate access to images."
        ),
        structured_output=False,
    )
    def capture_photo() -> str:
        global robot
        try:
            error = ensure_connected()
            if error is not None:
                return error

            assert robot is not None
            robot.capture_photo()
            return (
                "Photo captured to robot's internal storage.\n\n"
                "Note: The photo is stored on the robot itself.\n"
                "To retrieve it, you'll need to access the robot via FTP.\n"
                "For immediate viewing, use get_camera_frame instead."
            )
        except Exception as exc:
            return (
                f"Error executing capture_photo: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    @app.tool(
        name="jump_robot",
        description=(
            "Make the robot jump! The Jumping Sumo can perform two types of jumps: "
            "'long' for distance and 'high' for height. Note: Ensure adequate "
            "clearance above and around the robot before jumping."
        ),
        structured_output=False,
    )
    def jump_robot(jump_type: Literal["long", "high"] = "long") -> str:
        global robot
        try:
            error = ensure_connected()
            if error is not None:
                return error

            assert robot is not None
            robot.jump(jump_type)
            jump_desc = "long jump (for distance)" if jump_type == "long" else "high jump (for height)"
            return (
                f"Robot performing {jump_desc}.\n\n"
                "Make sure there is adequate clearance around the robot."
            )
        except Exception as exc:
            return (
                f"Error executing jump_robot: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    @app.tool(
        name="load_jump",
        description=(
            "Load/compress the spring for jumping or kicking. This prepares the robot "
            "without executing the action immediately. After loading, you can execute "
            "a jump or kick."
        ),
        structured_output=False,
    )
    def load_jump() -> str:
        global robot
        try:
            error = ensure_connected()
            if error is not None:
                return error

            assert robot is not None
            robot.load_jump()
            return (
                "Spring loaded. Robot ready to jump or kick.\n\n"
                "Next steps:\n"
                "- Call jump_robot to execute the jump\n"
                "- Or change_posture to kicker, then jump_robot to kick\n"
                "- Or cancel_jump to abort"
            )
        except Exception as exc:
            return (
                f"Error executing load_jump: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    @app.tool(
        name="cancel_jump",
        description=(
            "Cancel a loaded jump and return the robot to its previous state. "
            "Use this to abort a jump after calling load_jump."
        ),
        structured_output=False,
    )
    def cancel_jump() -> str:
        global robot
        try:
            error = ensure_connected()
            if error is not None:
                return error

            assert robot is not None
            robot.cancel_jump()
            return "Jump cancelled. Robot returning to previous state."
        except Exception as exc:
            return (
                f"Error executing cancel_jump: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    @app.tool(
        name="stop_jump",
        description="Emergency stop for the jump motor. Immediately stops any jump-related motion. Use for safety.",
        structured_output=False,
    )
    def stop_jump() -> str:
        global robot
        try:
            error = ensure_connected()
            if error is not None:
                return error

            assert robot is not None
            robot.stop_jump()
            return "Jump motor stopped immediately (emergency stop)."
        except Exception as exc:
            return (
                f"Error executing stop_jump: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    @app.tool(
        name="change_posture",
        description=(
            "Change the robot's physical posture. Options: 'standing' (normal driving), "
            "'jumper' (jump-ready), or 'kicker' (enables kicking with front accessory)."
        ),
        structured_output=False,
    )
    def change_posture(posture_type: Literal["standing", "jumper", "kicker"] = "standing") -> str:
        global robot
        try:
            error = ensure_connected()
            if error is not None:
                return error

            assert robot is not None
            robot.change_posture(posture_type)
            posture_descriptions = {
                "standing": "normal driving mode",
                "jumper": "jump-ready position",
                "kicker": "kicking stance (front accessory active)",
            }
            desc = posture_descriptions.get(posture_type, posture_type)
            return f"Posture changed to {posture_type} ({desc})."
        except Exception as exc:
            return (
                f"Error executing change_posture: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    @app.tool(
        name="play_animation",
        description=(
            "Play one of the robot's built-in animations for fun and personality. "
            "Options include spin, tap, slowshake, metronome, ondulation (dance), "
            "spinjump, spintoposture, spiral, slalom, and stop."
        ),
        structured_output=False,
    )
    def play_animation(
        animation: Literal[
            "stop",
            "spin",
            "tap",
            "slowshake",
            "metronome",
            "ondulation",
            "spinjump",
            "spintoposture",
            "spiral",
            "slalom",
        ] = "spin",
    ) -> str:
        global robot
        try:
            error = ensure_connected()
            if error is not None:
                return error

            assert robot is not None
            robot.play_animation(animation)
            return f"Playing '{animation}' animation."
        except Exception as exc:
            return (
                f"Error executing play_animation: {exc}\n\n"
                "If this is a connection error, try reconnecting with connect_robot."
            )

    return app


def main() -> None:
    """Run the MCP server."""
    parser = argparse.ArgumentParser(description="Parrot Jumping Sumo MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol to use",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for SSE server")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE server")
    args = parser.parse_args()

    app = create_app(host=args.host, port=args.port)
    if args.transport == "sse":
        print("Starting Jumping Sumo MCP Server (SSE)")
        print(f"Listening on http://{args.host}:{args.port}")
        print(f"SSE Endpoint: http://{args.host}:{args.port}/sse")
        app.run(transport="sse")
    else:
        app.run(transport="stdio")


if __name__ == "__main__":
    main()
