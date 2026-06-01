#pragma once
#include "Config.h"
#include <Arduino.h>

// ─── Application record ──────────────────────────────────────────────────────
struct Application {
  const char *name;         // Display name
  const char *command;      // Serial command sent to PC
  CategoryID  category;
  const uint16_t *icon;     // PROGMEM icon (may be nullptr → use letter icon)
  uint16_t    accentColor;  // pressed tint
  bool        favorite;
};

// ─── Icons forward declarations (defined in icons.h) ─────────────────────────
#include "icons.h"

// ─── App database ────────────────────────────────────────────────────────────
// To add an app: add one entry here + handle the command in pc_listener.py.
// Nothing else needs changing.

static Application APP_DB[] = {
  // ── Browsers ──────────────────────────────────────────────────────────────
  { "Chrome",       "OPEN_CHROME",      CAT_BROWSERS, icon_chrome,     0x2F13, false },
  { "Brave",        "OPEN_BRAVE",       CAT_BROWSERS, icon_brave,      0xFE40, false },
  { "Firefox",      "OPEN_FIREFOX",     CAT_BROWSERS, icon_firefox,    0xFC60, false },
  { "Edge",         "OPEN_EDGE",        CAT_BROWSERS, icon_edge,       0x145F, false },
  { "Opera GX",     "OPEN_OPERA_GX",    CAT_BROWSERS, icon_opera,      0xF800, false },

  // ── Development ───────────────────────────────────────────────────────────
  { "VS Code",      "OPEN_VSCODE",      CAT_DEV,      icon_vscode,     0x2D7F, false },
  { "Cursor",       "OPEN_CURSOR",      CAT_DEV,      icon_cursor,     0x4A69, false },
  { "Arduino",      "OPEN_ARDUINO",     CAT_DEV,      icon_arduino,    0x0A6B, false },
  { "Android St.",  "OPEN_ANDROIDSTUDIO",CAT_DEV,     icon_android_studio,    0x3D0A, false },
  { "Fusion 360",   "OPEN_FUSION360",   CAT_DEV,      icon_fusion360,  0xFE59, false },
  { "Blender",      "OPEN_BLENDER",     CAT_DEV,      icon_blender,    0xFD00, false },
  { "Unity Hub",    "OPEN_UNITY_HUB",   CAT_DEV,      icon_unity,    0x2104, false },
  { "Unity Editor", "OPEN_UNITY",       CAT_DEV,      icon_unity,    0x2104, false },
  { "Godot",        "OPEN_GODOT",       CAT_DEV,      icon_godot,    0x4C7F, false },
  { "eufyMake",     "OPEN_EUFYMAKE",    CAT_DEV,      icon_eufymake,   0xAF5F, false },
  { "VirtualBox",   "OPEN_VIRTUALBOX",  CAT_DEV,      icon_virtualbox,    0x0E5F, false },

  // ── Games ─────────────────────────────────────────────────────────────────
  { "Steam",        "OPEN_STEAM",       CAT_GAMES,    icon_steam,      0x2D7F, false },
  { "Epic Games",   "OPEN_EPIC",        CAT_GAMES,    icon_epic_games,    0x2104, false },
  { "MuMu Player",  "OPEN_MUMU",        CAT_GAMES,    icon_mumu_player,    0x5F9F, false },
  { "GameLoop",     "OPEN_GAMELOOP",    CAT_GAMES,    icon_gameloop,    0xF800, false },

  // ── Media ─────────────────────────────────────────────────────────────────
  { "VLC",          "OPEN_VLC",         CAT_MEDIA,    icon_vlc,        0xFD20, false },
  { "OBS Studio",   "OPEN_OBS",         CAT_MEDIA,    icon_obs,        0x2104, false },
  { "Spotify",      "OPEN_SPOTIFY",     CAT_MEDIA,    icon_spotify,    0x2780, false },

  // ── Communication ─────────────────────────────────────────────────────────
  { "Discord",      "OPEN_DISCORD",     CAT_COMM,     icon_discord,    0x335F, false },
  { "Telegram",     "OPEN_TELEGRAM",    CAT_COMM,     icon_telegram,   0x055F, false },
  { "WhatsApp",     "OPEN_WHATSAPP",    CAT_COMM,     icon_whatsapp,   0x2780, false },
  { "Zoom",         "OPEN_ZOOM",        CAT_COMM,     icon_zoom,    0x125F, false },
  { "Teams",        "OPEN_TEAMS",       CAT_COMM,     icon_teams,      0x5BEF, false },
  { "Outlook",      "OPEN_OUTLOOK",     CAT_COMM,     icon_outlook,    0x5B6D, false },

  // ── Tools ─────────────────────────────────────────────────────────────────
  { "File Explorer","OPEN_EXPLORER",    CAT_TOOLS,    icon_explorer,   0xFD00, false },
  { "Revo Uninst.", "OPEN_REVO",        CAT_TOOLS,    icon_revo_uninstaller,    0xF800, false },
  { "Wallpaper Eng","OPEN_WALLPAPER",   CAT_TOOLS,    icon_wallpaper_engine,    0x8C5F, false },
  { "7-Zip",        "OPEN_7ZIP",        CAT_TOOLS,    icon_7zip,    0xFD20, false },
  { "PowerToys",    "OPEN_POWERTOYS",   CAT_TOOLS,    icon_powertoys,    0xFD00, false },

  // ── System ────────────────────────────────────────────────────────────────
  { "Task Manager", "OPEN_TASKMGR",     CAT_SYSTEM,   icon_task_manager,    0x3D0A, false },
  { "Calculator",   "OPEN_CALC",        CAT_SYSTEM,   icon_calc,       0x145F, false },
  { "Notepad",      "OPEN_NOTEPAD",     CAT_SYSTEM,   icon_notepad,    0xFFF0, false },
  { "Paint",        "OPEN_PAINT",       CAT_SYSTEM,   icon_paint,    0x07FF, false },
  { "Settings",     "OPEN_SETTINGS",    CAT_SYSTEM,   icon_settings,   0x7BEF, false },
  { "Ctrl Panel",   "OPEN_CONTROL",     CAT_SYSTEM,   icon_control_panel,    0x5C5F, false },
  { "CMD",          "OPEN_CMD",         CAT_SYSTEM,   icon_terminal,   0x2104, false },
  { "PowerShell",   "OPEN_POWERSHELL",  CAT_SYSTEM,   icon_terminal,   0x4C5F, false },
  { "Regedit",      "OPEN_REGEDIT",     CAT_SYSTEM,   icon_regedit,    0x7BEF, false },
  { "Snip & Sketch","WIN_SCREENSHOT",   CAT_SYSTEM,   icon_snip_sketch,    0x07E0, false },
  { "Lock PC",      "SYS_LOCK",         CAT_SYSTEM,   icon_lock_pc,    0xF800, false },
  { "Sleep",        "SYS_SLEEP",        CAT_SYSTEM,   icon_sleep,    0x2D7F, false },
  { "Shutdown",     "SYS_SHUTDOWN",     CAT_SYSTEM,   icon_shutdown,    0xF800, false },
  { "Restart",      "SYS_RESTART",      CAT_SYSTEM,   icon_restart,    0xFD20, false },

  // ── Office ────────────────────────────────────────────────────────────────
  { "Word",         "OPEN_WORD",        CAT_OFFICE,   icon_word,       0x4AB5, false },
  { "Excel",        "OPEN_EXCEL",       CAT_OFFICE,   icon_excel,      0x3D0A, false },
  { "PowerPoint",   "OPEN_POWERPOINT",  CAT_OFFICE,   icon_powerpoint, 0xFA9A, false },
  { "OneNote",      "OPEN_ONENOTE",     CAT_OFFICE,   icon_onenote,    0x6B5D, false },
  { "Publisher",    "OPEN_PUBLISHER",   CAT_OFFICE,   icon_publisher,    0x0A6F, false },
  { "Access",       "OPEN_ACCESS",      CAT_OFFICE,   icon_access,    0xA000, false },
  { "Visio",        "OPEN_VISIO",       CAT_OFFICE,   icon_visio,    0x0A6F, false },
};

static const int APP_COUNT = sizeof(APP_DB) / sizeof(APP_DB[0]);

// ─── Recently launched (ring buffer, most recent first) ───────────────────────
#define RECENT_MAX 8
static int recentApps[RECENT_MAX] = { -1,-1,-1,-1,-1,-1,-1,-1 };
static int recentCount = 0;

// ─── AppDB namespace ─────────────────────────────────────────────────────────
namespace AppDB {

  void init() {
    // Could load favorites from NVS/Preferences here
  }

  void recordLaunch(int appIdx) {
    // Remove if already present
    for (int i = 0; i < recentCount; i++) {
      if (recentApps[i] == appIdx) {
        for (int j = i; j < recentCount - 1; j++)
          recentApps[j] = recentApps[j+1];
        recentCount--;
        break;
      }
    }
    // Prepend
    for (int i = min(recentCount, RECENT_MAX - 1); i > 0; i--)
      recentApps[i] = recentApps[i-1];
    recentApps[0] = appIdx;
    if (recentCount < RECENT_MAX) recentCount++;
  }

  void toggleFavorite(int appIdx) {
    if (appIdx >= 0 && appIdx < APP_COUNT)
      APP_DB[appIdx].favorite = !APP_DB[appIdx].favorite;
  }

  // Fill `out` with indices of apps matching category (and optional search).
  // Returns count.
  int filter(CategoryID cat, const char *search, int *out, int maxOut) {
    int n = 0;
    for (int i = 0; i < APP_COUNT && n < maxOut; i++) {
      const Application &a = APP_DB[i];
      if (cat == CAT_FAVORITES && !a.favorite) continue;
      if (cat == CAT_RECENT) {
        // handled separately
        continue;
      }
      if (cat != CAT_ALL && cat != CAT_FAVORITES && a.category != cat) continue;
      if (search && search[0]) {
        // simple case-insensitive substring
        String name(a.name); name.toLowerCase();
        String q(search);    q.toLowerCase();
        if (name.indexOf(q) < 0) continue;
      }
      out[n++] = i;
    }
    return n;
  }

  int filterRecent(const char *search, int *out, int maxOut) {
    int n = 0;
    for (int i = 0; i < recentCount && n < maxOut; i++) {
      int idx = recentApps[i];
      if (idx < 0) continue;
      if (search && search[0]) {
        String name(APP_DB[idx].name); name.toLowerCase();
        String q(search); q.toLowerCase();
        if (name.indexOf(q) < 0) continue;
      }
      out[n++] = idx;
    }
    return n;
  }
}
