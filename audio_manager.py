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

    def _play_sound_file(self, filename, loop=True):
        if not self.enabled:
            return
        sound_path = self.get_asset_path(filename)
        if not sound_path:
            # fallback to generic alarm sound if filename missing
            sound_path = self.get_asset_path("alarmsound.mp4")
            if not sound_path:
                sound_path = self.get_asset_path("newsoundforalarm.mp4")

        try:
            self.player.stop()
            if sound_path:
                self.player.setSource(QUrl.fromLocalFile(sound_path))
                if loop:
                    self.player.setLoops(QMediaPlayer.Infinite)
                else:
                    self.player.setLoops(1)
                self.player.setPosition(0)
                self.player.play()
            else:
                winsound.Beep(880, 500)
        except Exception as e:
            print(f"Error playing sound {filename}: {e}")
            try:
                winsound.Beep(880, 500)
            except Exception:
                pass

    def play_loop_alarm(self):
        """Plays the general alarm sound in a continuous loop."""
        self._play_sound_file("newsoundforalarm.mp4", loop=True)

    def play_prayer_alarm(self):
        """Plays the prayer notification sound from logos sounds."""
        self._play_sound_file("newalarmsoundforpraying.mp4", loop=True)

    def play_water_alarm(self):
        """Plays the water reminder alarm sound."""
        self._play_sound_file("newsoundforalarm.mp4", loop=True)

    def play_eye_rest_alarm(self):
        """Plays the eye rest reminder alarm sound."""
        self._play_sound_file("newsoundforalarm.mp4", loop=True)

    def stop_alarm(self):
        """Stops sound playback."""
        try:
            self.player.stop()
        except Exception:
            pass

    def play_success_sound(self):
        """Stops any looping alarm and plays a cheerful completion sound/chime."""
        if not self.enabled:
            return
        self.stop_alarm()
        sound_path = self.get_asset_path("success.mp4")
        try:
            if sound_path and os.path.exists(sound_path):
                self.player.setSource(QUrl.fromLocalFile(sound_path))
                self.player.setLoops(1)
                self.player.setPosition(0)
                self.player.play()
            else:
                # Cheerful win chime arpeggio
                winsound.Beep(523, 100)  # C5
                winsound.Beep(659, 100)  # E5
                winsound.Beep(784, 100)  # G5
                winsound.Beep(1046, 250) # C6
        except Exception as e:
            print(f"Error playing success sound: {e}")

    def play_blocked_warning(self):
        """Plays a brief warning tone when a blocked app is attempt-closed."""
        if not self.enabled:
            return
        try:
            winsound.Beep(350, 150)
            winsound.Beep(250, 200)
        except Exception:
            pass

