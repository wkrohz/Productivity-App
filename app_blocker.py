import psutil
import time
import os

class AppBlocker:
    def __init__(self, audio_mgr=None):
        self.audio_mgr = audio_mgr
        self.is_active = False
        self.blocked_list = set()
        self.last_blocked_app = ""

    def set_blocked_apps(self, app_list):
        # Normalize executables to lowercase
        self.blocked_list = {app.strip().lower() for app in app_list if app.strip()}

    def check_and_enforce(self):
        """Scans active processes and terminates any matching blocked apps if block is active."""
        if not self.is_active or not self.blocked_list:
            return []

        killed_apps = []
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name and proc_name.lower() in self.blocked_list:
                        # Terminate blocked process
                        proc.kill()
                        killed_apps.append(proc_name)
                        self.last_blocked_app = proc_name
                        if self.audio_mgr:
                            self.audio_mgr.play_blocked_warning()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            print(f"Error checking processes: {e}")

        return killed_apps

    @staticmethod
    def get_running_apps():
        """Returns a sorted list of currently running user applications with names & executables."""
        apps = set()
        system_processes = {
            'explorer.exe', 'svchost.exe', 'system', 'idle', 'csrss.exe', 
            'services.exe', 'lsass.exe', 'smss.exe', 'wininit.exe', 'taskmgr.exe',
            'ctfmon.exe', 'conhost.exe', 'spoolsv.exe', 'python.exe', 'pythonw.exe'
        }
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name']
                    if name and name.lower().endswith('.exe') and name.lower() not in system_processes:
                        apps.add(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        return sorted(list(apps))
