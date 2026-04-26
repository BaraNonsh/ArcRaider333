"""
MultimediaController Module - Orchestrates video playback and audio feedback.

This module provides the MultimediaController class which handles:
- Video playback with aspect ratio preservation
- Audio feedback management
- State machine for multimedia transitions
"""

from enum import Enum
from typing import Optional
import os

try:
    import pygame
    import cv2
except ImportError as e:
    raise ImportError(
        f"Missing multimedia dependencies: {e}\n"
        "Install with: pip install pygame opencv-python"
    )


class MediaState(Enum):
    """State machine states for multimedia orchestration."""
    VIDEO_PLAYBACK = "video_playback"
    WAITING_FOR_INPUT = "waiting_for_input"
    FEEDBACK_AUDIO = "feedback_audio"
    IDLE = "idle"


class MultimediaController:
    """
    Manages multimedia playback including video and audio.

    This class abstracts OpenCV and Pygame operations, providing a clean
    interface for video display and audio feedback with proper state management.
    """

    def __init__(self, display_width: int = 800, display_height: int = 600):
        """
        Initialize the MultimediaController with display parameters.

        Args:
            display_width (int): Display window width in pixels. Defaults to 800.
            display_height (int): Display window height in pixels. Defaults to 600.

        Raises:
            RuntimeError: If Pygame audio initialization fails.
        """
        self.display_width = display_width
        self.display_height = display_height
        self.current_state = MediaState.IDLE

        # Initialize Pygame mixer for audio
        try:
            pygame.mixer.init()
            self._audio_available = True
        except Exception as e:
            print(f"Warning: Audio system unavailable - {e}")
            self._audio_available = False

        # Audio cache
        self.sound_cache: dict = {}

    def _load_sound(self, audio_path: str) -> Optional[pygame.mixer.Sound]:
        """
        Load and cache audio file.

        Args:
            audio_path (str): Path to audio file.

        Returns:
            Optional[pygame.mixer.Sound]: Loaded sound or None if loading fails.
        """
        if not self._audio_available:
            return None

        if audio_path in self.sound_cache:
            return self.sound_cache[audio_path]

        try:
            if os.path.exists(audio_path):
                sound = pygame.mixer.Sound(audio_path)
                self.sound_cache[audio_path] = sound
                return sound
            else:
                print(f"Warning: Audio file not found: {audio_path}")
                return None
        except Exception as e:
            print(f"Error loading audio {audio_path}: {e}")
            return None

    def _calculate_scaled_dimensions(
        self, frame_height: int, frame_width: int
    ) -> tuple:
        """
        Calculate scaled dimensions preserving aspect ratio.

        Args:
            frame_height (int): Original frame height.
            frame_width (int): Original frame width.

        Returns:
            tuple: (scaled_width, scaled_height) preserving aspect ratio.
        """
        aspect_ratio = frame_width / frame_height if frame_height > 0 else 1

        if aspect_ratio > self.display_width / self.display_height:
            # Frame is wider, scale by width
            scaled_width = self.display_width
            scaled_height = int(self.display_width / aspect_ratio)
        else:
            # Frame is taller, scale by height
            scaled_height = self.display_height
            scaled_width = int(self.display_height * aspect_ratio)

        return scaled_width, scaled_height

    def play_video(self, video_path: str) -> bool:
        """
        Play a video file with aspect ratio preservation.

        Args:
            video_path (str): Path to video file.

        Returns:
            bool: True if playback completed successfully, False otherwise.
        """
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return False

        self.current_state = MediaState.VIDEO_PLAYBACK

        try:
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                print(f"Error: Failed to open video: {video_path}")
                return False

            # Get video properties
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_delay = int(1000 / fps) if fps > 0 else 30

            print(f"Playing: {video_path} ({frame_width}x{frame_height} @ {fps}fps)")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Scale frame preserving aspect ratio
                scaled_width, scaled_height = self._calculate_scaled_dimensions(
                    frame_height, frame_width
                )
                frame_resized = cv2.resize(frame, (scaled_width, scaled_height))

                # Create canvas to center the frame
                canvas = cv2.zeros(
                    (self.display_height, self.display_width, 3), dtype="uint8"
                )
                x_offset = (self.display_width - scaled_width) // 2
                y_offset = (self.display_height - scaled_height) // 2
                canvas[
                    y_offset : y_offset + scaled_height,
                    x_offset : x_offset + scaled_width
                ] = frame_resized

                cv2.imshow("AnimalQuiz", canvas)

                # Allow user to skip with 'q' key
                if cv2.waitKey(frame_delay) & 0xFF == ord("q"):
                    break

            cap.release()
            cv2.destroyAllWindows()
            self.current_state = MediaState.IDLE
            return True

        except Exception as e:
            print(f"Error during video playback: {e}")
            self.current_state = MediaState.IDLE
            return False

    def play_feedback_audio(self, audio_path: str) -> None:
        """
        Play feedback audio (correct/incorrect sound).

        Args:
            audio_path (str): Path to audio file.
        """
        if not self._audio_available:
            return

        self.current_state = MediaState.FEEDBACK_AUDIO

        try:
            sound = self._load_sound(audio_path)
            if sound:
                sound.play()
                # Wait for sound to finish
                while pygame.mixer.get_busy():
                    pass
        except Exception as e:
            print(f"Error playing feedback audio: {e}")
        finally:
            self.current_state = MediaState.IDLE

    def get_state(self) -> MediaState:
        """
        Get current multimedia controller state.

        Returns:
            MediaState: Current state.
        """
        return self.current_state

    def is_audio_available(self) -> bool:
        """
        Check if audio system is available.

        Returns:
            bool: True if audio system initialized successfully.
        """
        return self._audio_available

    def cleanup(self) -> None:
        """Clean up multimedia resources."""
        try:
            cv2.destroyAllWindows()
            if self._audio_available:
                pygame.mixer.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Warning during cleanup: {e}")
