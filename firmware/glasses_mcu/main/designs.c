// Outward "design" screens: two ST7789 LCDs on one SPI bus, rendered in 40-line bands.
#include <math.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "driver/spi_master.h"
#include "driver/ledc.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_vendor.h"
#include "esp_lcd_panel_ops.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "esp_random.h"
#include "esp_log.h"
#include "asg.h"
#include "font6x8.h"

#define BAND 40
static const char *TAG = "designs";
static esp_lcd_panel_handle_t panel[2];
static uint16_t *buf[2];
static SemaphoreHandle_t done;

static bool on_done(esp_lcd_panel_io_handle_t io, esp_lcd_panel_io_event_data_t *e, void *ctx) {
    BaseType_t hp = pdFALSE; xSemaphoreGiveFromISR(done, &hp); return hp == pdTRUE;
}
static inline uint16_t rgb(float r, float g, float b) {               // 0..1 floats -> byte-swapped RGB565
    int R = r < 0 ? 0 : r > 1 ? 31 : (int)(r * 31), Gc = g < 0 ? 0 : g > 1 ? 63 : (int)(g * 63), B = b < 0 ? 0 : b > 1 ? 31 : (int)(b * 31);
    uint16_t c = (R << 11) | (Gc << 5) | B; return (c >> 8) | (c << 8);
}
static uint16_t hsv(float h, float s, float v) {
    h = fmodf(h, 360.f); if (h < 0) h += 360.f;
    float c = v * s, x = c * (1 - fabsf(fmodf(h / 60.f, 2) - 1)), m = v - c, r, g, b;
    if (h < 60) { r = c; g = x; b = 0; } else if (h < 120) { r = x; g = c; b = 0; } else if (h < 180) { r = 0; g = c; b = x; }
    else if (h < 240) { r = 0; g = x; b = c; } else if (h < 300) { r = x; g = 0; b = c; } else { r = c; g = 0; b = x; }
    return rgb(r + m, g + m, b + m);
}

void designs_backlight(uint8_t pct) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, (1023 * pct) / 100);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

// ---------- design pixel functions (eye: 0 = wearer-left screen, 1 = right) ----------
static float look_x, look_y, blink;   // updated once per frame

static uint16_t px_eyes(int x, int y, int eye, float t) {
    float cx = LCD_W / 2.f, cy = LCD_H / 2.f, dx = x - cx, dy = y - cy;
    float lid = 70.f * (1.f - blink);                                   // eyelid half-opening
    if (fabsf(dy) > lid * sqrtf(fmaxf(0, 1 - (dx * dx) / (118.f * 118.f)))) return rgb(0.05f, 0.05f, 0.07f);
    float ix = dx - look_x * 38.f, iy = dy - look_y * 22.f;          // both eyes look the same way
    float d = sqrtf(ix * ix + iy * iy);
    if (d < 17) return (ix + 6) * (ix + 6) + (iy + 7) * (iy + 7) < 30 ? rgb(1, 1, 1) : rgb(0.02f, 0.02f, 0.03f);
    if (d < 46) { float k = d / 46.f; return rgb(0.05f + 0.1f * k, 0.55f + 0.25f * k, 0.75f + 0.2f * k); }
    return rgb(0.93f, 0.93f, 0.95f);
}
static uint16_t px_rings(int x, int y, int eye, float t) {
    float dx = x - LCD_W / 2.f, dy = y - LCD_H / 2.f, d = sqrtf(dx * dx + dy * dy);
    float v = 0.5f + 0.5f * sinf(d * 0.12f - t * 5.f);
    return hsv(200 + 80 * sinf(t * 0.5f) + d * 0.6f, 0.9f, v);
}
static uint16_t px_rainbow(int x, int y, int eye, float t) {
    return hsv((x + eye * LCD_W) * 0.8f + y * 0.6f + t * 90.f, 0.85f, 1.0f);
}
static int text_px(int vx, int y, float t) {                           // scrolling text, 4x scaled font, spans both screens
    int len = strlen(G.text); if (!len) return 0;
    const int S = 4, CW = 6 * S, total = len * CW + 2 * LCD_W;
    int sx = (vx + (int)(t * 120.f)) % total - 2 * LCD_W + LCD_W;      // scroll right->left
    int ty = y - (LCD_H - 8 * S) / 2;
    if (sx < 0 || ty < 0 || ty >= 8 * S) return 0;
    int ci = sx / CW, col = (sx % CW) / S, row = ty / S;
    if (ci >= len || col >= 6) return 0;
    unsigned char c = G.text[ci]; if (c < 32 || c > 126) c = '?';
    return (FONT6x8[c - 32][col] >> row) & 1;
}
static uint16_t px_text(int x, int y, int eye, float t) {
    int vx = eye == 0 ? x : x + LCD_W;                                 // wearer-left screen shows the start
    return text_px(vx, y, t) ? hsv(t * 40.f + x, 0.7f, 1.0f) : rgb(0, 0, 0);
}

static void render(int eye, float t) {
    for (int y0 = 0; y0 < LCD_H; y0 += BAND) {
        uint16_t *b = buf[(y0 / BAND) & 1];
        xSemaphoreTake(done, pdMS_TO_TICKS(100));                       // this buffer's last transfer has finished
        for (int y = 0; y < BAND; y++) for (int x = 0; x < LCD_W; x++) {
            uint16_t c;
            switch (G.design) {
                case DESIGN_EYES:    c = px_eyes(x, y0 + y, eye, t); break;
                case DESIGN_RINGS:   c = px_rings(x, y0 + y, eye, t); break;
                case DESIGN_RAINBOW: c = px_rainbow(x, y0 + y, eye, t); break;
                case DESIGN_TEXT:    c = px_text(x, y0 + y, eye, t); break;
                default:             c = 0; break;
            }
            b[y * LCD_W + x] = c;
        }
        esp_lcd_panel_draw_bitmap(panel[eye], 0, y0, LCD_W, y0 + BAND, b);
    }
}

static void lcd_init(void) {
    spi_bus_config_t bus = { .sclk_io_num = PIN_SCK, .mosi_io_num = PIN_MOSI, .miso_io_num = -1,
                             .quadwp_io_num = -1, .quadhd_io_num = -1, .max_transfer_sz = LCD_W * BAND * 2 + 16 };
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO));
    const gpio_num_t cs[2] = { PIN_CS_L, PIN_CS_R };
    for (int i = 0; i < 2; i++) {
        esp_lcd_panel_io_handle_t io;
        esp_lcd_panel_io_spi_config_t ioc = { .dc_gpio_num = PIN_LCD_DC, .cs_gpio_num = cs[i], .pclk_hz = 40 * 1000 * 1000,
            .lcd_cmd_bits = 8, .lcd_param_bits = 8, .spi_mode = 0, .trans_queue_depth = 2, .on_color_trans_done = on_done };
        ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)SPI2_HOST, &ioc, &io));
        esp_lcd_panel_dev_config_t pc = { .reset_gpio_num = -1, .rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB, .bits_per_pixel = 16 };
        ESP_ERROR_CHECK(esp_lcd_new_panel_st7789(io, &pc, &panel[i]));
        esp_lcd_panel_reset(panel[i]);                                  // software reset (RST tied to 3V3)
        esp_lcd_panel_init(panel[i]);
        esp_lcd_panel_invert_color(panel[i], true);
        esp_lcd_panel_swap_xy(panel[i], true);                          // landscape
        esp_lcd_panel_mirror(panel[i], i == 0, i != 0);                 // [MEASURE] flip per mounting
        esp_lcd_panel_set_gap(panel[i], 20, 0);                         // 240x280 glass in 240x320 RAM
        esp_lcd_panel_disp_on_off(panel[i], true);
    }
    ledc_timer_config_t tc = { .speed_mode = LEDC_LOW_SPEED_MODE, .duty_resolution = LEDC_TIMER_10_BIT,
                               .timer_num = LEDC_TIMER_0, .freq_hz = 5000, .clk_cfg = LEDC_AUTO_CLK };
    ledc_timer_config(&tc);
    ledc_channel_config_t cc = { .gpio_num = PIN_LCD_BL, .speed_mode = LEDC_LOW_SPEED_MODE, .channel = LEDC_CHANNEL_0,
                                 .timer_sel = LEDC_TIMER_0, .duty = 0, .hpoint = 0 };
    ledc_channel_config(&cc);
}

static void task(void *arg) {
    float nx = 0, ny = 0; int64_t next_look = 0, next_blink = 0;
    while (1) {
        float t = esp_timer_get_time() / 1e6f;
        int off = G.visor_up || G.design == DESIGN_OFF;
        designs_backlight(off ? 0 : G.brightness);
        if (off) { vTaskDelay(pdMS_TO_TICKS(100)); continue; }
        int64_t now = esp_timer_get_time();                              // eyes: saccades + blinks + head-tilt bias
        if (now > next_look) { nx = ((esp_random() % 200) - 100) / 100.f; ny = ((esp_random() % 120) - 60) / 100.f; next_look = now + 600000 + esp_random() % 1800000; }
        float bias = fmaxf(-1, fminf(1, G.roll / 30.f));
        look_x += (fmaxf(-1, fminf(1, nx + bias)) - look_x) * 0.35f; look_y += (ny - look_y) * 0.35f;
        float bp = (now - next_blink) / 1e6f;
        blink = (bp > 0 && bp < 0.18f) ? sinf(bp / 0.18f * M_PI) : 0;
        if (bp > 0.18f) next_blink = now + 2500000 + esp_random() % 3000000;
        render(0, t); render(1, t);
        vTaskDelay(1);
    }
}

void designs_start(void) {
    done = xSemaphoreCreateCounting(2, 2);
    for (int i = 0; i < 2; i++) buf[i] = heap_caps_malloc(LCD_W * BAND * 2, MALLOC_CAP_DMA);
    lcd_init();
    ESP_LOGI(TAG, "outward screens ready");
    xTaskCreatePinnedToCore(task, "designs", 4096, NULL, 4, NULL, 1);
}
