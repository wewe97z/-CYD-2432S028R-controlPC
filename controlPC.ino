/*
 * ControlPC Ultimate v2.0
 * ESP32-2432S028R (Cheap Yellow Display)
 * Full desktop companion system for Windows PC
 *
 * Upload this sketch, then run pc_listener.py on your PC.
 * Serial Monitor must be CLOSED while listener is running.
 */

#include <SPI.h>
#include <TFT_eSPI.h>
#include <XPT2046_Touchscreen.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include "Config.h"
#include "AppDB.h"
#include "UI/Theme.h"
#include "UI/StatusBar.h"
#include "UI/AppGrid.h"
#include "UI/CategoryBar.h"
#include "UI/QuickSettings.h"
#include "UI/SearchPanel.h"
#include "System/TouchHandler.h"
#include "System/Serial.h"
#include "System/Stats.h"
#include "icons.h"

// ─── Hardware ────────────────────────────────────────────────────────────────
TFT_eSPI    tft    = TFT_eSPI();
TFT_eSprite bufSpr = TFT_eSprite(&tft);   // full-row double-buffer sprite

SPIClass touchscreenSPI = SPIClass(VSPI);
XPT2046_Touchscreen touchscreen(XPT2046_CS, XPT2046_IRQ);

// ─── Global UI state ─────────────────────────────────────────────────────────
UIState    uiState;
AppGrid    appGrid(&tft, &bufSpr);
StatusBar  statusBar(&tft);
CategoryBar catBar(&tft);
QuickSettings qs(&tft, &bufSpr);
SearchPanel   sp(&tft, &bufSpr);

// ─── FreeRTOS tasks ──────────────────────────────────────────────────────────
TaskHandle_t statsTaskHandle  = nullptr;
TaskHandle_t serialTaskHandle = nullptr;

void statsTask(void *param) {
  for (;;) {
    if (WiFi.status() == WL_CONNECTED)
      Stats::fetchFromPC();   // requests stats string from PC listener
    vTaskDelay(pdMS_TO_TICKS(STATS_POLL_MS));
  }
}

void serialTask(void *param) {
  for (;;) {
    SerialComm::poll(uiState);
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}

// ─── Setup ───────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(BAUD_RATE);

  // Touch SPI
  touchscreenSPI.begin(XPT2046_CLK, XPT2046_MISO, XPT2046_MOSI, XPT2046_CS);
  touchscreen.begin(touchscreenSPI);
  touchscreen.setRotation(TOUCH_ROTATION);

  // TFT
  tft.init();
  tft.setRotation(SCREEN_ROTATION);
  tft.fillScreen(Theme::BG);

  // Row sprite (320 × ROW_H, 16-bit)
  bufSpr.setColorDepth(16);
  bufSpr.createSprite(SCREEN_W, ROW_H);

  // App database
  AppDB::init();

  // UI modules
  uiState.screen    = SCREEN_HOME;
  uiState.category  = CAT_ALL;
  uiState.page      = 0;
  uiState.scrollOff = 0;

  // WiFi (non-blocking)
  if (strlen(WIFI_SSID) > 0) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
  }

  // FreeRTOS tasks
  xTaskCreatePinnedToCore(statsTask,  "stats",  4096, nullptr, 1, &statsTaskHandle,  0);
  xTaskCreatePinnedToCore(serialTask, "serial", 2048, nullptr, 2, &serialTaskHandle, 1);

  // Draw initial screen
  drawFullScreen();

  Serial.println("READY");
}

// ─── Main loop (touch only — serial handled in task) ─────────────────────────
void loop() {
  TouchHandler::handle(touchscreen, uiState,
                       appGrid, catBar, qs, sp, statusBar,
                       tft, bufSpr);
  // Redraw only if UI state changed
  if (uiState.dirty) {
    drawFullScreen();
    uiState.dirty = false;
  }
  delay(8);
}

// ─── Full screen redraw ───────────────────────────────────────────────────────
void drawFullScreen() {
  tft.fillScreen(Theme::BG);
  statusBar.draw(uiState);

  switch (uiState.screen) {
    case SCREEN_HOME:
      catBar.draw(uiState);
      appGrid.draw(uiState);
      break;
    case SCREEN_QUICK_SETTINGS:
      qs.draw(uiState);
      break;
    case SCREEN_SEARCH:
      sp.draw(uiState);
      break;
    case SCREEN_MEDIA:
      drawMediaControls();
      break;
    case SCREEN_STATS:
      Stats::drawPanel(&tft, uiState);
      break;
  }
}

void drawMediaControls() {
  // Media control panel — rendered directly
  tft.fillRect(0, STATUS_H, SCREEN_W, SCREEN_H - STATUS_H, Theme::SURFACE);
  tft.setTextDatum(TC_DATUM);
  tft.setTextColor(Theme::TEXT_PRIMARY, Theme::SURFACE);
  tft.setTextSize(2);
  tft.drawString("Media Controls", SCREEN_W / 2, STATUS_H + 10);

  // Prev / Play / Next
  const int BTN_Y = STATUS_H + 70, BTN_R = 28;
  const int PREV_X = 80, PLAY_X = 160, NEXT_X = 240;
  tft.fillCircle(PREV_X, BTN_Y, BTN_R, Theme::ACCENT);
  tft.fillCircle(PLAY_X, BTN_Y, BTN_R + 6, Theme::ACCENT2);
  tft.fillCircle(NEXT_X, BTN_Y, BTN_R, Theme::ACCENT);
  tft.setTextColor(TFT_WHITE, Theme::ACCENT);
  tft.setTextSize(2);
  tft.setTextDatum(MC_DATUM);
  tft.drawString("|<", PREV_X, BTN_Y);
  tft.drawString(">||", PLAY_X, BTN_Y);
  tft.drawString(">|", NEXT_X, BTN_Y);

  // Volume
  tft.setTextColor(Theme::TEXT_SECONDARY, Theme::SURFACE);
  tft.setTextSize(1);
  tft.drawString("VOL-", 40,  BTN_Y + 55);
  tft.fillRect(60, BTN_Y + 48, 200, 14, Theme::SURFACE2);
  int volW = map(uiState.volume, 0, 100, 0, 200);
  tft.fillRect(60, BTN_Y + 48, volW, 14, Theme::ACCENT);
  tft.drawString("VOL+", 280, BTN_Y + 55);
  tft.drawString(String(uiState.volume) + "%", SCREEN_W / 2, BTN_Y + 55);

  // Back button
  tft.fillRoundRect(10, SCREEN_H - 40, 80, 28, 6, Theme::SURFACE2);
  tft.setTextColor(Theme::TEXT_PRIMARY, Theme::SURFACE2);
  tft.drawString("< Back", 50, SCREEN_H - 26);
}
