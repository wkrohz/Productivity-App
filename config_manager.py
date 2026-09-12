import os
import json
import winreg
import sys

CONFIG_FILE = "productivity_config.json"

DEFAULT_CONFIG = {
    "startup_enabled": False,
    "blocked_apps": ["discord.exe", "steam.exe", "spotify.exe"],
    "blocked_websites": ["facebook.com", "twitter.com", "x.com", "instagram.com", "tiktok.com", "youtube.com"],
    "exercise_index": 0,
    "learning_schedules": [
        {"name": "جلسة التعلم المسائية", "start": "16:00", "end": "18:00", "active": True},
        {"name": "جلسة التعلم الليلية", "start": "20:00", "end": "22:00", "active": True}
    ],
    "water_interval_min": 40,
    "pushups_interval_min": 120,
    "water_enabled": True,
    "pushups_enabled": True,
    "sound_enabled": True,
    "volume": 80,
    "daily_stats": {
        "date": "",
        "water_count": 0,
        "pushups_count": 0,
        "learning_minutes": 0
    },
    "daily_tasks": [],
    "user_score": 0,
    "unlocked_badges": [],
    "weekly_history": {},
    "manual_session_active": False,
    "manual_session_end_time": "",
    "manual_session_is_strict": False,
    "portfolio_folders": [
        {
            "id": "folder_default_1",
            "title": "شهادات الدوارات والتعلم",
            "icon": "rocketlogo.png",
            "items": []
        }
    ],
    "prayer_times": {
        "enabled": True,
        "times": {
            "الفجر": "04:45",
            "الظهر": "12:15",
            "العصر": "15:35",
            "المغرب": "18:10",
            "العشاء": "19:40"
        }
    },
    "eye_rest_enabled": True,
    "eye_rest_interval_min": 20,
    "quick_launch": {
        "apps": ["code.exe"],
        "urls": ["https://www.youtube.com"]
    },
    "quick_launch_profiles": [
        {
            "id": "profile_1",
            "title": "🚀 بيئة البرمجة والتطوير",
            "apps": ["code.exe"],
            "urls": ["https://github.com", "https://stackoverflow.com"]
        },
        {
            "id": "profile_2",
            "title": "📖 بيئة التعلم والدراسة",
            "apps": [],
            "urls": ["https://www.youtube.com"]
        }
    ],
    "sunnah_reminders": {
        "enabled": True,
        "items": [
            {"id": "sunnah_duha", "name": "☀️ صلاة الضحى", "time": "09:30", "enabled": True},
            {"id": "sunnah_azkar_m", "name": "🌅 أذكار الصباح", "time": "06:30", "enabled": True},
            {"id": "sunnah_azkar_e", "name": "🌆 أذكار المساء", "time": "17:00", "enabled": True},
            {"id": "sunnah_qiyam", "name": "🌙 صلاة قيام الليل والوتر", "time": "02:00", "enabled": True},
            {"id": "sunnah_fajr", "name": "🌅 سنة الفجر (الركعتين)", "time": "04:30", "enabled": True}
        ]
    }
}

class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            config_path = os.path.join(base_dir, CONFIG_FILE)
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    merged = DEFAULT_CONFIG.copy()
                    merged.update(cfg)
                    return merged
            except Exception as e:
                print(f"Error loading config: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def set_startup(self, enable: bool):
        self.config["startup_enabled"] = enable
        self.save_config()

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "ProductivityHub"

        if getattr(sys, 'frozen', False):
            exe_path = f'"{sys.executable}"'
        else:
            exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Registry startup error: {e}")
            return False

    def is_startup_enabled(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "ProductivityHub"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
