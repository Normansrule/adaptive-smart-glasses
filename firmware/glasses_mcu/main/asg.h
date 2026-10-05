// Adaptive Smart Glasses v0.2 — shared pins + state (Seeed XIAO ESP32-S3 in the visor)
#pragma once
#include <stdint.h>
#include "driver/gpio.h"

// ---- pin map (docs/pinout.md) ----
#define PIN_CS_L      GPIO_NUM_1    // D0  left outward LCD chip-select
#define PIN_CS_R      GPIO_NUM_2    // D1  right outward LCD chip-select
#define PIN_LCD_DC    GPIO_NUM_3    // D2  data/command (shared)
#define PIN_VBAT_ADC  GPIO_NUM_4    // D3  ADC1_CH3, VBAT/2 divider
#define PIN_SDA       GPIO_NUM_5    // D4  IMU
#define PIN_SCL       GPIO_NUM_6    // D5
#define PIN_LCD_BL    GPIO_NUM_43   // D6  backlight PWM (shared)
#define PIN_HALL      GPIO_NUM_44   // D7  visor hall switch, LOW = magnet near = visor DOWN
#define PIN_SCK       GPIO_NUM_7    // D8  LCD SPI clock
#define PIN_BUTTON    GPIO_NUM_8    // D9  action button to GND
#define PIN_MOSI      GPIO_NUM_9    // D10 LCD SPI data

// ---- outward LCD geometry (Waveshare 1.69" 240x280, used landscape) ----
#define LCD_W 280
#define LCD_H 240

enum { DESIGN_EYES, DESIGN_RINGS, DESIGN_RAINBOW, DESIGN_TEXT, DESIGN_OFF, DESIGN_COUNT };
enum { AR_NORMAL, AR_ZOOM, AR_EDGES, AR_LOWLIGHT, AR_COUNT };   // brick passthrough modes

typedef struct {
    volatile uint8_t design, brightness, ar_mode, visor_up, ble_connected, wifi_up;
    volatile int     vbat_mv;
    volatile float   yaw, pitch, roll;      // degrees
    float            acc[3], gyr[3];        // g, dps
    char             text[33];
} asg_state_t;
extern asg_state_t G;

void designs_start(void);          // LCD task (designs on both outward screens)
void designs_backlight(uint8_t pct);
void ble_start(void);              // phone control (Web Bluetooth)
void ble_notify_status(void);
void net_start(void);              // Wi-Fi + UDP pose/state to the brick
void net_send_pose(void);
