"""
Wrapper module for the python-sumo SumoController class.

This module provides a cleaner interface with error handling,
state management, and helper functions for the MCP server.
"""
import sys
import os
from pathlib import Path

# Add python-sumo to path
sumo_path = Path(__file__).parent.parent / "python-sumo"
sys.path.insert(0, str(sumo_path))

try:
    from sumopy.interface import SumoController, InitTimeoutException
except ImportError as e:
    print(f"Error: Could not import python-sumo module: {e}")
    print(f"Make sure python-sumo is installed at: {sumo_path}")
    sys.exit(1)


class SumoWrapper:
    """Wrapper around SumoController with additional safety and error handling."""
    
    def __init__(self, sumo_ip='192.168.2.1', timeout=5):
        """
        Initialize connection to the Sumo robot.
        
        Args:
            sumo_ip: IP address of the robot (default: 192.168.2.1)
            timeout: Connection timeout in seconds
        """
        self.sumo_ip = sumo_ip
        self.controller = None
        self._connect(timeout)
    
    def _connect(self, timeout):
        """Establish connection to the robot."""
        try:
            print(f"Connecting to Sumo robot at {self.sumo_ip}...")
            self.controller = SumoController(
                sumo_ip=self.sumo_ip,
                start_video_stream=True,
                sock_timeout=timeout
            )
            print("Connection established!")
        except InitTimeoutException as e:
            print(f"Connection timeout: {e}")
            self.controller = None
        except Exception as e:
            print(f"Connection failed: {e}")
            self.controller = None
    
    def is_connected(self):
        """
        Check if the robot is connected and responding.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if self.controller is None:
            return False
        
        try:
            return self.controller.connected
        except Exception:
            return False
    
    def move(self, speed, turn=0, duration=1.0):
        """
        Move the robot.
        
        Args:
            speed: Speed from -100 (backward) to 100 (forward)
            turn: Turn rate from -100 (left) to 100 (right)
            duration: Duration in seconds
        
        Raises:
            ValueError: If not connected or parameters invalid
        """
        if not self.is_connected():
            raise ValueError("Robot not connected")
        
        # Validate parameters
        if not -100 <= speed <= 100:
            raise ValueError("Speed must be between -100 and 100")
        if not -100 <= turn <= 100:
            raise ValueError("Turn must be between -100 and 100")
        if duration < 0.025:
            raise ValueError("Duration must be at least 0.025 seconds")
        
        # Execute movement (blocking by default for safety)
        self.controller.move(speed, turn, duration, block=True)
    
    def get_camera_frame(self):
        """
        Get the latest camera frame as JPEG data.
        
        Returns:
            bytes: JPEG image data, or None if no frame available
        
        Raises:
            ValueError: If not connected
        """
        if not self.is_connected():
            raise ValueError("Robot not connected")
        
        try:
            frame = self.controller.get_pic(retries=5)
            return frame
        except Exception as e:
            print(f"Error getting camera frame: {e}")
            return None
    
    def capture_photo(self):
        """
        Capture a photo to the robot's internal storage.
        
        Note: Photos are stored on the robot and require FTP to retrieve.
        
        Raises:
            ValueError: If not connected
        """
        if not self.is_connected():
            raise ValueError("Robot not connected")
        
        self.controller.store_pic()
    
    def jump(self, jump_type='long'):
        """
        Make the robot jump!
        
        Args:
            jump_type: 'long' for long jump (distance) or 'high' for high jump (height)
        
        Raises:
            ValueError: If not connected or invalid jump type
        """
        if not self.is_connected():
            raise ValueError("Robot not connected")
        
        if jump_type not in ['long', 'high']:
            raise ValueError("Jump type must be 'long' or 'high'")
        
        # Import struct if not already imported
        import struct
        from sumopy.interface import SumoController
        
        # Create jump command based on XML specification
        # Class "Animations" id="2", Command "Jump" (offset 3 in the class)
        # Enum: 0=long, 1=high
        jump_type_value = 0 if jump_type == 'long' else 1
        
        cmd = SumoController.fab_cmd(
            4,  # ACK
            11,  # Command channel
            3,   # Jumping Sumo project id = 3
            2,   # class = Animations (id=2)
            3,   # Command = Jump (offset 3: JumpStop=0, JumpCancel=1, JumpLoad=2, Jump=3)
            struct.pack(
                '<I',  # u32 for enum
                jump_type_value,  # 0=long, 1=high
            )
        )
        self.controller._commands.append(cmd)
    
    def load_jump(self):
        """
        Load/compress the spring for jumping or kicking.
        
        This prepares the robot for a jump or kick without executing it immediately.
        After loading, call jump() or change to kicker posture.
        
        Raises:
            ValueError: If not connected
        """
        if not self.is_connected():
            raise ValueError("Robot not connected")
        
        import struct
        from sumopy.interface import SumoController
        
        # Class "Animations" id="2", Command "JumpLoad" (offset 2)
        cmd = SumoController.fab_cmd(
            4,   # ACK
            11,  # Command channel
            3,   # Jumping Sumo project id = 3
            2,   # class = Animations (id=2)
            2,   # Command = JumpLoad (offset 2)
            b''  # No arguments
        )
        self.controller._commands.append(cmd)
    
    def cancel_jump(self):
        """
        Cancel a loaded jump and return to previous state.
        
        Use this to abort a jump after calling load_jump().
        
        Raises:
            ValueError: If not connected
        """
        if not self.is_connected():
            raise ValueError("Robot not connected")
        
        import struct
        from sumopy.interface import SumoController
        
        # Class "Animations" id="2", Command "JumpCancel" (offset 1)
        cmd = SumoController.fab_cmd(
            4,   # ACK
            11,  # Command channel
            3,   # Jumping Sumo project id = 3
            2,   # class = Animations (id=2)
            1,   # Command = JumpCancel (offset 1)
            b''  # No arguments
        )
        self.controller._commands.append(cmd)
    
    def stop_jump(self):
        """
        Emergency stop for jump motor.
        
        Immediately stops the jump motor. Use for safety.
        
        Raises:
            ValueError: If not connected
        """
        if not self.is_connected():
            raise ValueError("Robot not connected")
        
        import struct
        from sumopy.interface import SumoController
        
        # Class "Animations" id="2", Command "JumpStop" (offset 0)
        cmd = SumoController.fab_cmd(
            4,   # ACK
            11,  # Command channel
            3,   # Jumping Sumo project id = 3
            2,   # class = Animations (id=2)
            0,   # Command = JumpStop (offset 0)
            b''  # No arguments
        )
        self.controller._commands.append(cmd)
    
    def change_posture(self, posture_type='standing'):
        """
        Change the robot's physical posture.
        
        Args:
            posture_type: 'standing', 'jumper', or 'kicker'
                - standing: Normal driving mode
                - jumper: Jump-ready position
                - kicker: Kicking stance (enables kicking actions)
        
        Raises:
            ValueError: If not connected or invalid posture type
        """
        if not self.is_connected():
            raise ValueError("Robot not connected")
        
        posture_types = {
            'standing': 0,
            'jumper': 1,
            'kicker': 2
        }
        
        if posture_type not in posture_types:
            raise ValueError(f"Posture type must be one of: {list(posture_types.keys())}")
        
        import struct
        from sumopy.interface import SumoController
        
        posture_value = posture_types[posture_type]
        
        # Class "Piloting" id="0", Command "Posture" (offset 1)
        cmd = SumoController.fab_cmd(
            4,   # ACK
            10,  # Piloting channel
            3,   # Jumping Sumo project id = 3
            0,   # class = Piloting (id=0)
            1,   # Command = Posture (offset 1)
            struct.pack(
                '<I',  # u32 for enum
                posture_value,
            )
        )
        self.controller._commands.append(cmd)
    
    def play_animation(self, animation_name='spin'):
        """
        Play one of the robot's built-in animations.
        
        Args:
            animation_name: Animation to play. Options:
                - 'stop': Stop ongoing animation
                - 'spin': Spinning in place
                - 'tap': Tapping motion
                - 'slowshake': Slow shaking
                - 'metronome': Metronome back-and-forth
                - 'ondulation': Standing dance
                - 'spinjump': Spin combined with jump
                - 'spintoposture': Spin ending in different posture
                - 'spiral': Spiral movement
                - 'slalom': Slalom-style movement
        
        Raises:
            ValueError: If not connected or invalid animation name
        """
        if not self.is_connected():
            raise ValueError("Robot not connected")
        
        animations = {
            'stop': 0,
            'spin': 1,
            'tap': 2,
            'slowshake': 3,
            'metronome': 4,
            'ondulation': 5,
            'spinjump': 6,
            'spintoposture': 7,
            'spiral': 8,
            'slalom': 9
        }
        
        if animation_name not in animations:
            raise ValueError(f"Animation must be one of: {list(animations.keys())}")
        
        import struct
        from sumopy.interface import SumoController
        
        animation_value = animations[animation_name]
        
        # Class "Animations" id="2", Command "SimpleAnimation" (offset 4)
        cmd = SumoController.fab_cmd(
            4,   # ACK
            11,  # Command channel
            3,   # Jumping Sumo project id = 3
            2,   # class = Animations (id=2)
            4,   # Command = SimpleAnimation (offset 4)
            struct.pack(
                '<I',  # u32 for enum
                animation_value,
            )
        )
        self.controller._commands.append(cmd)
    
    def disconnect(self):
        """Disconnect from the robot and clean up resources."""
        if self.controller is not None:
            try:
                # Send stop command before disconnecting
                self.controller.move(0, 0, 0.1, block=True)
            except Exception:
                pass  # Ignore errors during cleanup
            
            self.controller = None
            print("Disconnected from robot")
    
    def __del__(self):
        """Ensure cleanup on deletion."""
        self.disconnect()
