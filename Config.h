#pragma once

// ─── WiFi (optional — leave blank to disable) ────────────────────────────────
#define WIFI_SSID   ""
#define WIFI_PASS   ""

// ─── Serial ──────────────────────────────────────────────────────────────────
#define BAUD_RATE   115200

// ─── Touch SPI pins (XPT2046 on CYD) ────────────────────────────────────────
#define XPT2046_IRQ  36
#define XPT2046_MOSI 32
#define XPT2046_MISO 39
#define XPT2046_CLK  25
#define XPT2046_CS   33

// ─── Display ─────────────────────────────────────────────────────────────────
#define SCREEN_W        320
#define SCREEN_H        240
#define SCREEN_ROTATION 3
#define TOUCH_ROTATION  3

// ─── Touch calibration (raw → pixels) ───────────────────────────────────────
#define TOUCH_X_MIN  200
#define TOUCH_X_MAX  3700
#define TOUCH_Y_MIN  240
#define TOUCH_Y_MAX  3800

// ─── Layout ──────────────────────────────────────────────────────────────────
#define STATUS_H    28     // top status bar
#define CAT_BAR_H   26     // category filter bar
#define FOOTER_H    0      // no footer in v2 (dots in status bar)
#define GRID_TOP    (STATUS_H + CAT_BAR_H)
#define GRID_COLS   4
#define GRID_ROWS   2
#define GRID_H      (SCREEN_H - GRID_TOP)
#define COL_W       (SCREEN_W / GRID_COLS)
#define ROW_H       (GRID_H  / GRID_ROWS)
#define ICON_CELL_W  56
#define ICON_CELL_H  56
#define LABEL_H      14
#define APPS_PER_PAGE (GRID_COLS * GRID_ROWS)   // 8

// ─── Gesture thresholds ──────────────────────────────────────────────────────
#define SWIPE_MIN       45
#define TAP_MAX_MOVE    20
#define SWIPE_LIVE_MIN  20
#define SLIDE_STEPS     14
#define LIVE_DRAG_THRESH 4
#define CMD_COOLDOWN_MS 600

// ─── Stats polling ───────────────────────────────────────────────────────────
#define STATS_POLL_MS 3000

// ─── Screen IDs ──────────────────────────────────────────────────────────────
enum ScreenID {
  SCREEN_HOME = 0,
  SCREEN_QUICK_SETTINGS,
  SCREEN_SEARCH,
  SCREEN_MEDIA,
  SCREEN_STATS,
};

// ─── Category IDs ────────────────────────────────────────────────────────────
enum CategoryID {
  CAT_ALL = 0,
  CAT_FAVORITES,
  CAT_BROWSERS,
  CAT_DEV,
  CAT_GAMES,
  CAT_MEDIA,
  CAT_COMM,
  CAT_TOOLS,
  CAT_SYSTEM,
  CAT_OFFICE,
  CAT_RECENT,
  CAT_COUNT
};

// ─── UI State ────────────────────────────────────────────────────────────────
struct UIState {
  ScreenID   screen    = SCREEN_HOME;
  CategoryID category  = CAT_ALL;
  int        page      = 0;
  int        scrollOff = 0;       // live swipe offset (px)
  bool       dirty     = true;

  // Stats (updated by stats task)
  int  cpuPct   = 0;
  int  ramPct   = 0;
  int  gpuPct   = 0;
  int  diskPct  = 0;
  int  netKbps  = 0;
  int  volume   = 50;
  bool wifiOK   = false;
  char trackTitle[48] = "";

  // Search
  char searchBuf[32] = "";
  int  searchLen      = 0;

  // Quick settings
  int brightness = 200;
};
