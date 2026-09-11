import os
import sys
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import winsound

class AudioManager:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0) # Full volume

        # Find sound file
        sound_path = self.get_asset_path("alarmsound.mp4")
        if os.path.exists(sound_path):
            self.player.setSource(QUrl.fromLocalFile(sound_path))
            self.player.setLoops(QMediaPlayer.Infinite)

    def get_asset_path(self, filename):
        # Check bundled path
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        local_asset = os.path.join(base_dir, "assets", filename)
        if os.path.exists(local_asset):
            return local_asset

        downloads_asset = os.path.join(r"C:\Users\Wkroh\Downloads\logos sounds", filename)
        if os.path.exists(downloads_asset):
            return downloads_asset

        return ""

    def play_loop_alarm(self):
        """Plays the custom alarm sound in a continuous loop."""
        if not self.enabled:
            return
        try:
            self.player.setPosition(0)
            self.player.play()
        except Exception as e:
            print(f"Error playing sound: {e}")
            # Fallback beep
            try:
                winsound.Beep(880, 500)
            except Exception:
                pass

    def stop_alarm(self):
        """Stops sound playback."""
        try:
            self.player.stop()
        except Exception:
            pass

    def play_blocked_warning(self):
        """Plays a brief warning tone when a blocked app is attempt-closed."""
        if not self.enabled:
            return
        try:
            winsound.Beep(350, 150)
            winsound.Beep(250, 200)
        except Exception:
            pass
