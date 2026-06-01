"""
ControlPC Ultimate v2.0 — PC Listener
Listens on the CYD serial port and handles all commands.

New in v2:
  - System stats reporting (CPU/RAM/GPU/Disk/Net/Volume)
  - Media control (play/pause/prev/next)
  - Volume control
  - System commands (lock/sleep/shutdown/restart)
  - Screenshot
  - 50+ app launchers
  - GET_STATS polling from ESP32

Close Arduino Serial Monitor before running.
Run:  python pc_listener.py [COM_PORT]
"""

import ctypes
import glob
import os
import platform
import subprocess
import sys
import threading
import time
from typing import Callable, Optional

# ── Optional dependencies (non-fatal if missing) ──────────────────────────────
try:
    import serial
except ImportError:
    sys.exit("pyserial not installed. Run: pip install pyserial")

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("[warn] psutil not found — CPU/RAM stats disabled. pip install psutil")

try:
    from ctypes import wintypes
    import comtypes
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    HAS_PYCAW = True
except Exception:
    HAS_PYCAW = False
    print("[warn] pycaw not found — volume control disabled. pip install pycaw")

# ── Config ────────────────────────────────────────────────────────────────────
PORT      = "COM8"
BAUD      = 115200
STATS_KEY = "GET_STATS"    # ESP32 requests stats with this string

# ── App path helpers ──────────────────────────────────────────────────────────
def first_existing(paths: list) -> Optional[str]:
    for p in paths:
        if os.path.isfile(p):
            return p
    return None

def first_glob(patterns: list) -> Optional[str]:
    for pat in patterns:
        m = sorted(glob.glob(pat, recursive=True))
        if m:
            return m[0]
    return None

def launch(path: str, label: str) -> None:
    subprocess.Popen([path], shell=False)
    print(f"[+] {label}: {path}")

def shell_open(uri: str, label: str) -> None:
    subprocess.Popen(f"start {uri}", shell=True)
    print(f"[+] {label} via shell")

def winrun(cmd: str) -> None:
    subprocess.Popen(cmd, shell=True)

# ── Browser launchers ─────────────────────────────────────────────────────────
def open_chrome():
    p = first_existing([
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ])
    launch(p, "Chrome") if p else shell_open("chrome", "Chrome")

def open_brave():
    p = first_existing([
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    ])
    launch(p, "Brave") if p else print("Brave not found")

def open_firefox():
    p = first_existing([
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ])
    launch(p, "Firefox") if p else shell_open("firefox", "Firefox")

def open_edge():
    p = first_existing([
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ])
    launch(p, "Edge") if p else shell_open("microsoft-edge:", "Edge")

def open_opera_gx():
    p = first_existing([
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera GX\launcher.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera GX\opera.exe"),
    ])
    launch(p, "Opera GX") if p else print("Opera GX not found")

# ── Development tools ─────────────────────────────────────────────────────────
def open_vscode():
    p = first_existing([
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ])
    launch(p, "VS Code") if p else shell_open("vscode:", "VS Code")

def open_cursor():
    p = first_existing([
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\cursor\Cursor.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\cursor\Cursor.exe"),
        os.path.expandvars(r"%ProgramFiles%\Cursor\Cursor.exe"),
    ])
    launch(p, "Cursor") if p else print("Cursor not found")

def open_arduino():
    p = first_existing([
        r"C:\Program Files\Arduino IDE\Arduino IDE.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Arduino IDE\Arduino IDE.exe"),
    ])
    if not p:
        p = first_glob([r"C:\Program Files\**\Arduino IDE.exe"])
    launch(p, "Arduino IDE") if p else print("Arduino IDE not found")

def open_androidstudio():
    p = first_glob([
        r"C:\Program Files\Android\Android Studio\bin\studio64.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\AndroidStudio*\bin\studio64.exe"),
    ])
    launch(p, "Android Studio") if p else print("Android Studio not found")

def open_fusion360():
    p = first_glob([
        os.path.expandvars(r"%LOCALAPPDATA%\Autodesk\webdeploy\production\*\Fusion360.exe"),
        r"C:\Program Files\Autodesk\Fusion 360\Fusion360.exe",
    ])
    launch(p, "Fusion 360") if p else print("Fusion 360 not found")

def open_blender():
    p = first_existing([
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
    ])
    if not p:
        p = first_glob([r"C:\Program Files\Blender Foundation\**\blender.exe"])
    launch(p, "Blender") if p else print("Blender not found")

def open_unity_hub():
    p = first_existing([
        r"C:\Program Files\Unity Hub\Unity Hub.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Unity Hub\Unity Hub.exe"),
    ])
    launch(p, "Unity Hub") if p else print("Unity Hub not found")

def open_unity():
    p = first_glob([r"C:\Program Files\Unity\Hub\Editor\*\Editor\Unity.exe"])
    launch(p, "Unity Editor") if p else open_unity_hub()

def open_godot():
    p = first_glob([
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Godot*\Godot*.exe"),
        r"C:\Program Files\Godot\Godot.exe",
    ])
    launch(p, "Godot") if p else print("Godot not found")

def open_eufymake():
    p = first_glob([
        r"C:\Program Files\eufyMake Studio\*.exe",
        r"C:\Program Files\AnkerMake\eufyMake Studio\*.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\eufyMake Studio\*.exe"),
    ])
    launch(p, "eufyMake Studio") if p else print("eufyMake not found")

def open_virtualbox():
    p = first_existing([r"C:\Program Files\Oracle\VirtualBox\VirtualBox.exe"])
    launch(p, "VirtualBox") if p else print("VirtualBox not found")

# ── Games ─────────────────────────────────────────────────────────────────────
def open_steam():
    p = first_existing([
        r"C:\Program Files (x86)\Steam\steam.exe",
        r"C:\Program Files\Steam\steam.exe",
    ])
    launch(p, "Steam") if p else shell_open("steam:", "Steam")

def open_epic():
    p = first_existing([
        os.path.expandvars(r"%LOCALAPPDATA%\EpicGamesLauncher\Portal\Binaries\Win64\EpicGamesLauncher.exe"),
        r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe",
    ])
    launch(p, "Epic Games") if p else print("Epic Games not found")

def open_mumu():
    p = first_glob([r"C:\Program Files\MuMu Player*\shell\MuMuPlayer.exe"])
    launch(p, "MuMu Player") if p else print("MuMu Player not found")

def open_gameloop():
    p = first_glob([r"C:\Program Files\TxGameAssistant\App\GameLoop.exe",
                    os.path.expandvars(r"%APPDATA%\Tencent\GameLoop\*.exe")])
    launch(p, "GameLoop") if p else print("GameLoop not found")

# ── Media ─────────────────────────────────────────────────────────────────────
def open_vlc():
    p = first_existing([
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    ])
    launch(p, "VLC") if p else print("VLC not found")

def open_obs():
    p = first_existing([
        r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe",
    ])
    launch(p, "OBS Studio") if p else print("OBS not found")

def open_spotify():
    p = first_existing([
        os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\Spotify.exe"),
    ])
    launch(p, "Spotify") if p else shell_open("spotify:", "Spotify")

# ── Communication ─────────────────────────────────────────────────────────────
def open_discord():
    p = first_glob([os.path.expandvars(r"%LOCALAPPDATA%\Discord\app-*\Discord.exe")])
    launch(p, "Discord") if p else shell_open("discord:", "Discord")

def open_telegram():
    p = first_existing([
        os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Telegram Desktop\Telegram.exe"),
    ])
    launch(p, "Telegram") if p else print("Telegram not found")

def open_whatsapp():
    shell_open("whatsapp:", "WhatsApp")

def open_zoom():
    p = first_glob([os.path.expandvars(r"%APPDATA%\Zoom\bin\Zoom.exe")])
    launch(p, "Zoom") if p else shell_open("zoommtg:", "Zoom")

# ── Tools ─────────────────────────────────────────────────────────────────────
def open_explorer():
    winrun("explorer.exe")
    print("[+] File Explorer")

def open_revo():
    p = first_glob([r"C:\Program Files\VS Revo Group\Revo Uninstaller\RevoUninstaller.exe",
                    r"C:\Program Files (x86)\VS Revo Group\Revo Uninstaller\RevoUninstaller.exe"])
    launch(p, "Revo") if p else print("Revo not found")

def open_wallpaper():
    p = first_glob([os.path.expandvars(r"%ProgramFiles(x86)%\Steam\steamapps\common\wallpaper_engine\wallpaper64.exe")])
    launch(p, "Wallpaper Engine") if p else print("Wallpaper Engine not found")

def open_7zip():
    p = first_existing([r"C:\Program Files\7-Zip\7zFM.exe", r"C:\Program Files (x86)\7-Zip\7zFM.exe"])
    launch(p, "7-Zip") if p else print("7-Zip not found")

def open_powertoys():
    p = first_glob([os.path.expandvars(r"%LOCALAPPDATA%\PowerToys\PowerToys.exe"),
                    r"C:\Program Files\PowerToys\PowerToys.exe"])
    launch(p, "PowerToys") if p else print("PowerToys not found")

# ── System ────────────────────────────────────────────────────────────────────
def open_taskmgr():     winrun("taskmgr.exe");           print("[+] Task Manager")
def open_calc():        winrun("calc.exe");               print("[+] Calculator")
def open_notepad():     winrun("notepad.exe");            print("[+] Notepad")
def open_paint():       winrun("mspaint.exe");            print("[+] Paint")
def open_settings():    winrun("start ms-settings:");     print("[+] Settings")
def open_control():     winrun("control.exe");            print("[+] Control Panel")
def open_cmd():         winrun("start cmd.exe");          print("[+] CMD")
def open_powershell():  winrun("start powershell.exe");   print("[+] PowerShell")
def open_regedit():     winrun("regedit.exe");            print("[+] Regedit")

def win_screenshot():
    winrun("snippingtool /clip")
    print("[+] Screenshot")

def sys_lock():
    ctypes.windll.user32.LockWorkStation()
    print("[+] Lock")

def sys_sleep():
    winrun("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    print("[+] Sleep")

def sys_shutdown():
    winrun("shutdown /s /t 5")
    print("[+] Shutdown in 5s")

def sys_restart():
    winrun("shutdown /r /t 5")
    print("[+] Restart in 5s")

# ── Office ────────────────────────────────────────────────────────────────────
_OFFICE_EXE = {
    "OPEN_WORD":       ("WINWORD.EXE",  "Word"),
    "OPEN_EXCEL":      ("EXCEL.EXE",    "Excel"),
    "OPEN_POWERPOINT": ("POWERPNT.EXE", "PowerPoint"),
    "OPEN_OUTLOOK":    ("OUTLOOK.EXE",  "Outlook"),
    "OPEN_ONENOTE":    ("ONENOTE.EXE",  "OneNote"),
    "OPEN_TEAMS":      ("MS-TEAMS.EXE", "Teams"),
    "OPEN_PUBLISHER":  ("MSPUB.EXE",    "Publisher"),
    "OPEN_ACCESS":     ("MSACCESS.EXE", "Access"),
    "OPEN_VISIO":      ("VISIO.EXE",    "Visio"),
}

def open_office(command: str):
    exe, label = _OFFICE_EXE[command]
    p = first_glob([
        rf"C:\Program Files\Microsoft Office\**\{exe}",
        rf"C:\Program Files (x86)\Microsoft Office\**\{exe}",
    ])
    launch(p, label) if p else print(f"{label} not found ({exe})")

# ── Media control (sends keystrokes) ─────────────────────────────────────────
try:
    import win32api, win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_VOLUME_UP        = 0xAF
VK_VOLUME_DOWN      = 0xAE

def send_key(vk: int):
    if HAS_WIN32:
        win32api.keybd_event(vk, 0, 0, 0)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)

def media_play_pause(): send_key(VK_MEDIA_PLAY_PAUSE); print("[+] Play/Pause")
def media_next():       send_key(VK_MEDIA_NEXT_TRACK); print("[+] Next track")
def media_prev():       send_key(VK_MEDIA_PREV_TRACK); print("[+] Prev track")
def vol_up():           send_key(VK_VOLUME_UP);        print("[+] Vol up")
def vol_down():         send_key(VK_VOLUME_DOWN);      print("[+] Vol down")

# ── Stats collection ──────────────────────────────────────────────────────────
def get_stats_string() -> str:
    """Return 'STAT:cpu,ram,gpu,disk,net,vol\\n'"""
    cpu = ram = gpu = disk = net = vol = 0
    if HAS_PSUTIL:
        cpu  = int(psutil.cpu_percent(interval=None))
        ram  = int(psutil.virtual_memory().percent)
        disk = int(psutil.disk_usage("/").percent)
        # Network (bytes/s → KB/s, crude 1s sample)
        n1 = psutil.net_io_counters()
        time.sleep(0.2)
        n2 = psutil.net_io_counters()
        net = int((n2.bytes_recv - n1.bytes_recv + n2.bytes_sent - n1.bytes_sent) / 200)
    if HAS_PYCAW:
        try:
            sessions = AudioUtilities.GetSpeakers()
            interface = sessions.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume    = interface.QueryInterface(IAudioEndpointVolume)
            vol = int(volume.GetMasterVolumeLevelScalar() * 100)
        except Exception:
            pass
    return f"STAT:{cpu},{ram},{gpu},{disk},{net},{vol}"

# ── Command dispatch table ─────────────────────────────────────────────────────
HANDLERS: dict = {
    # Browsers
    "OPEN_CHROME":       open_chrome,
    "OPEN_BRAVE":        open_brave,
    "OPEN_FIREFOX":      open_firefox,
    "OPEN_EDGE":         open_edge,
    "OPEN_OPERA_GX":     open_opera_gx,
    # Dev
    "OPEN_VSCODE":       open_vscode,
    "OPEN_CURSOR":       open_cursor,
    "OPEN_ARDUINO":      open_arduino,
    "OPEN_ANDROIDSTUDIO":open_androidstudio,
    "OPEN_FUSION360":    open_fusion360,
    "OPEN_BLENDER":      open_blender,
    "OPEN_UNITY_HUB":    open_unity_hub,
    "OPEN_UNITY":        open_unity,
    "OPEN_GODOT":        open_godot,
    "OPEN_EUFYMAKE":     open_eufymake,
    "OPEN_VIRTUALBOX":   open_virtualbox,
    # Games
    "OPEN_STEAM":        open_steam,
    "OPEN_EPIC":         open_epic,
    "OPEN_MUMU":         open_mumu,
    "OPEN_GAMELOOP":     open_gameloop,
    # Media
    "OPEN_VLC":          open_vlc,
    "OPEN_OBS":          open_obs,
    "OPEN_SPOTIFY":      open_spotify,
    # Comm
    "OPEN_DISCORD":      open_discord,
    "OPEN_TELEGRAM":     open_telegram,
    "OPEN_WHATSAPP":     open_whatsapp,
    "OPEN_ZOOM":         open_zoom,
    # Tools
    "OPEN_EXPLORER":     open_explorer,
    "OPEN_REVO":         open_revo,
    "OPEN_WALLPAPER":    open_wallpaper,
    "OPEN_7ZIP":         open_7zip,
    "OPEN_POWERTOYS":    open_powertoys,
    # System
    "OPEN_TASKMGR":      open_taskmgr,
    "OPEN_CALC":         open_calc,
    "OPEN_NOTEPAD":      open_notepad,
    "OPEN_PAINT":        open_paint,
    "OPEN_SETTINGS":     open_settings,
    "OPEN_CONTROL":      open_control,
    "OPEN_CMD":          open_cmd,
    "OPEN_POWERSHELL":   open_powershell,
    "OPEN_REGEDIT":      open_regedit,
    "WIN_SCREENSHOT":    win_screenshot,
    "SYS_LOCK":          sys_lock,
    "SYS_SLEEP":         sys_sleep,
    "SYS_SHUTDOWN":      sys_shutdown,
    "SYS_RESTART":       sys_restart,
    # Office
    **{k: (lambda c=k: open_office(c)) for k in _OFFICE_EXE},
    # Media control
    "MEDIA_PLAY_PAUSE":  media_play_pause,
    "MEDIA_NEXT":        media_next,
    "MEDIA_PREV":        media_prev,
    "VOL_UP":            vol_up,
    "VOL_DOWN":          vol_down,
}

# ── Stats push thread ─────────────────────────────────────────────────────────
_ser_ref = None

def stats_thread():
    """Pushes stats every 5 s whether or not ESP32 requests them."""
    while True:
        time.sleep(5)
        if _ser_ref and _ser_ref.is_open:
            try:
                _ser_ref.write((get_stats_string() + "\n").encode())
            except Exception:
                pass

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global _ser_ref
    port = sys.argv[1] if len(sys.argv) > 1 else PORT
    print(f"\nControlPC Ultimate v2.0 — listening on {port} @ {BAUD}")
    print(f"Apps: {len(HANDLERS)} commands registered")
    if not HAS_PSUTIL:
        print("  Install psutil for CPU/RAM stats: pip install psutil")
    if not HAS_WIN32:
        print("  Install pywin32 for media keys: pip install pywin32")
    print("Press Ctrl+C to quit.\n")

    with serial.Serial(port, BAUD, timeout=1) as ser:
        _ser_ref = ser
        # Start stats push thread
        t = threading.Thread(target=stats_thread, daemon=True)
        t.start()

        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            if line == STATS_KEY:
                ser.write((get_stats_string() + "\n").encode())
                continue

            handler = HANDLERS.get(line)
            if handler:
                try:
                    handler()
                except Exception as e:
                    print(f"[err] {line}: {e}")
            else:
                print(f"[device] {line}")


if __name__ == "__main__":
    try:
        main()
    except serial.SerialException as e:
        print(f"\nSerial error: {e}")
        print("Close Arduino Serial Monitor and check COM port.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped.")
