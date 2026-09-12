import psutil
import time
import os
import sys
import ctypes
from ctypes import wintypes

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
BLOCK_HEADER = "# --- ProductivityHub Blocked Websites Start ---"
BLOCK_FOOTER = "# --- ProductivityHub Blocked Websites End ---"

class AppBlocker:
    def __init__(self, audio_mgr=None):
        self.audio_mgr = audio_mgr
        self.is_active = False
        self.blocked_list = set()
        self.blocked_websites = set()
        self.last_blocked_app = ""
        self.hosts_applied = False

    def set_blocked_apps(self, app_list):
        """Normalize executables to lowercase."""
        self.blocked_list = {app.strip().lower() for app in app_list if app.strip()}

    def set_blocked_websites(self, site_list):
        """Normalize website domain keywords to lowercase."""
        cleaned = set()
        for site in site_list:
            s = site.strip().lower()
            if s.startswith("http://"):
                s = s[7:]
            elif s.startswith("https://"):
                s = s[8:]
            if s.startswith("www."):
                s = s[4:]
            s = s.split('/')[0]
            if s:
                cleaned.add(s)
        self.blocked_websites = cleaned
        if self.is_active:
            self._apply_hosts_blocking()

    def set_active(self, active: bool):
        self.is_active = active
        if active:
            self._apply_hosts_blocking()
        else:
            self._remove_hosts_blocking()

    def _apply_hosts_blocking(self):
        if not self.blocked_websites:
            return
        try:
            entries = []
            for site in self.blocked_websites:
                entries.append(f"127.0.0.1 {site}")
                entries.append(f"127.0.0.1 www.{site}")

            content = []
            if os.path.exists(HOSTS_PATH):
                with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                
                inside = False
                for line in lines:
                    if BLOCK_HEADER in line:
                        inside = True
                        continue
                    if BLOCK_FOOTER in line:
                        inside = False
                        continue
                    if not inside:
                        content.append(line)

            # Add new block block
            new_block = f"\n{BLOCK_HEADER}\n" + "\n".join(entries) + f"\n{BLOCK_FOOTER}\n"
            full_text = "".join(content).rstrip() + new_block

            with open(HOSTS_PATH, "w", encoding="utf-8") as f:
                f.write(full_text)
            self.hosts_applied = True
        except Exception as e:
            # Hosts modification requires Administrator privileges
            self.hosts_applied = False

    def _remove_hosts_blocking(self):
        try:
            if not os.path.exists(HOSTS_PATH):
                return
            with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            content = []
            inside = False
            for line in lines:
                if BLOCK_HEADER in line:
                    inside = True
                    continue
                if BLOCK_FOOTER in line:
                    inside = False
                    continue
                if not inside:
                    content.append(line)

            with open(HOSTS_PATH, "w", encoding="utf-8") as f:
                f.writelines(content)
            self.hosts_applied = False
        except Exception:
            pass

    def check_and_enforce(self):
        """Scans active processes and window titles; enforces app and website blocking."""
        if not self.is_active:
            return []

        killed_apps = []

        # 1. Enforce Executable Process Blocking
        if self.blocked_list:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name']
                        if proc_name and proc_name.lower() in self.blocked_list:
                            proc.kill()
                            killed_apps.append(proc_name)
                            self.last_blocked_app = proc_name
                            if self.audio_mgr:
                                self.audio_mgr.play_blocked_warning()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
            except Exception as e:
                print(f"Error checking processes: {e}")

        # 2. Enforce Website Blocking via Active Window Title Scan (Fallback / Active defense)
        if self.blocked_websites and sys.platform.startswith("win"):
            try:
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd:
                    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value.lower()

                        # Check if foreground window title matches any blocked website domain/keyword
                        for site in self.blocked_websites:
                            # site keyword e.g. "youtube", "facebook", "tiktok", "twitter", "instagram"
                            domain_name = site.split('.')[0]
                            if site in title or (len(domain_name) >= 4 and domain_name in title):
                                # Send Ctrl+W to close active browser tab cleanly
                                now = time.time()
                                if now - getattr(self, '_last_tab_close_time', 0) > 0.8:
                                    self._last_tab_close_time = now
                                    VK_CONTROL = 0x11
                                    VK_W = 0x57
                                    KEYEVENTF_KEYUP = 0x0002
                                    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
                                    ctypes.windll.user32.keybd_event(VK_W, 0, 0, 0)
                                    ctypes.windll.user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
                                    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

                                killed_apps.append(f"موقع {site}")
                                self.last_blocked_app = f"موقع محظور ({site})"
                                if self.audio_mgr:
                                    self.audio_mgr.play_blocked_warning()
                                break
            except Exception:
                pass

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
