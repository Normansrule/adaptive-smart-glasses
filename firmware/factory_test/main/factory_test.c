// Adaptive Smart Glasses — factory / bring-up test (ESP-IDF 5.5, Seeed XIAO ESP32-S3)
// Status: EXPERIMENTAL test tool. Verifies a hand-built unit against docs/pinout.md:
//   I2C devices + IDs, battery sense, PTT -> mic power gating (privacy), mic data,
//   both amplifiers (operator listens), MEDIA_EN held LOW.
// Open the serial monitor (idf.py monitor) and follow the prompts.
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "driver/i2s_std.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_log.h"

// ---- XIAO ESP32-S3 pin map (docs/pinout.md) ----
#define PIN_VBAT_ADC   GPIO_NUM_1    // D0  (ADC1_CH0) 100k/100k divider
#define PIN_PTT_SENSE  GPIO_NUM_2    // D1  via 1N4148 from MIC_3V3, 100k pulldown
#define PIN_SD_BONE    GPIO_NUM_3    // D2  MAX98357A #1 SD (low = shutdown)
#define PIN_SD_OUT     GPIO_NUM_4    // D3  MAX98357A #2 SD
#define PIN_SDA        GPIO_NUM_5    // D4
#define PIN_SCL        GPIO_NUM_6    // D5
#define PIN_MEDIA_EN   GPIO_NUM_43   // D6  safety-owned media gate, LOW
#define PIN_I2S_DIN    GPIO_NUM_44   // D7  <- mic DOUT
#define PIN_I2S_BCLK   GPIO_NUM_7    // D8
#define PIN_I2S_WS     GPIO_NUM_8    // D9
#define PIN_I2S_DOUT   GPIO_NUM_9    // D10 -> amps DIN

#define FS_HZ          16000
#define TONE_AMPL      0.08f         // ~-22 dBFS: conservative; firmware caps volume
static const char *TAG = "factory";

typedef struct { const char *name; int pass; char detail[64]; } result_t;
static result_t R[12]; static int nR = 0;
static void rec(const char *n, int pass, const char *fmt, ...) {
    va_list ap; va_start(ap, fmt); R[nR].name = n; R[nR].pass = pass;
    vsnprintf(R[nR].detail, sizeof R[nR].detail, fmt, ap); va_end(ap);
    printf("  [%s] %-24s %s\n", pass ? "PASS" : "FAIL", n, R[nR].detail); nR++;
}

static i2c_master_bus_handle_t bus;
static i2s_chan_handle_t tx, rx;

static esp_err_t rd8(uint8_t addr, uint8_t reg, uint8_t *v) {
    i2c_master_dev_handle_t d; i2c_device_config_t c = { .dev_addr_length = I2C_ADDR_BIT_LEN_7, .device_address = addr, .scl_speed_hz = 400000 };
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &c, &d));
    esp_err_t e = i2c_master_transmit_receive(d, &reg, 1, v, 1, 50);
    i2c_master_bus_rm_device(d); return e;
}
static esp_err_t vl53_rd(uint16_t reg, uint8_t *v) {           // VL53L5CX: 16-bit register address
    i2c_master_dev_handle_t d; i2c_device_config_t c = { .dev_addr_length = I2C_ADDR_BIT_LEN_7, .device_address = 0x29, .scl_speed_hz = 400000 };
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &c, &d));
    uint8_t a[2] = { reg >> 8, reg & 0xFF };
    esp_err_t e = i2c_master_transmit_receive(d, a, 2, v, 1, 50);
    i2c_master_bus_rm_device(d); return e;
}
static esp_err_t vl53_wr(uint16_t reg, uint8_t v) {
    i2c_master_dev_handle_t d; i2c_device_config_t c = { .dev_addr_length = I2C_ADDR_BIT_LEN_7, .device_address = 0x29, .scl_speed_hz = 400000 };
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &c, &d));
    uint8_t b[3] = { reg >> 8, reg & 0xFF, v };
    esp_err_t e = i2c_master_transmit(d, b, 3, 50);
    i2c_master_bus_rm_device(d); return e;
}

static void test_i2c(void) {
    i2c_master_bus_config_t bc = { .i2c_port = I2C_NUM_0, .sda_io_num = PIN_SDA, .scl_io_num = PIN_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT, .glitch_ignore_cnt = 7, .flags.enable_internal_pullup = true };
    ESP_ERROR_CHECK(i2c_new_master_bus(&bc, &bus));
    printf("I2C scan:"); for (int a = 0x08; a < 0x78; a++) if (i2c_master_probe(bus, a, 20) == ESP_OK) printf(" 0x%02X", a); printf("\n");

    uint8_t id = 0, rev = 0;                                     // ToF: device id 0xF0, revision 0x02
    int ok = vl53_wr(0x7FFF, 0x00) == ESP_OK && vl53_rd(0x0000, &id) == ESP_OK && vl53_rd(0x0001, &rev) == ESP_OK;
    vl53_wr(0x7FFF, 0x02);
    rec("ToF VL53L5CX @0x29", ok && id == 0xF0 && rev == 0x02, "id=0x%02X rev=0x%02X (want F0/02)", id, rev);

    uint8_t who = 0; int a = 0x6A;                               // LSM6DSOX WHO_AM_I = 0x6C
    if (rd8(0x6A, 0x0F, &who) != ESP_OK) { a = 0x6B; rd8(0x6B, 0x0F, &who); }
    rec("IMU LSM6DSOX", who == 0x6C, "@0x%02X WHO_AM_I=0x%02X (want 6C)", a, who);

    uint8_t chip = 0; a = 0x76;                                  // BME280 chip id 0x60 (0x58 = BMP280 clone!)
    if (rd8(0x76, 0xD0, &chip) != ESP_OK) { a = 0x77; rd8(0x77, 0xD0, &chip); }
    rec("BME280", chip == 0x60, "@0x%02X id=0x%02X%s", a, chip, chip == 0x58 ? " BMP280 clone: no humidity" : " (want 60)");
}

static void test_vbat(void) {
    adc_oneshot_unit_handle_t u; adc_oneshot_unit_init_cfg_t uc = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&uc, &u));
    adc_oneshot_chan_cfg_t cc = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(u, ADC_CHANNEL_0, &cc));
    adc_cali_handle_t cal = NULL; adc_cali_curve_fitting_config_t cf = { .unit_id = ADC_UNIT_1, .chan = ADC_CHANNEL_0, .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    adc_cali_create_scheme_curve_fitting(&cf, &cal);
    int sum = 0, mv = 0, raw;
    for (int i = 0; i < 16; i++) { adc_oneshot_read(u, ADC_CHANNEL_0, &raw);
        if (cal) { adc_cali_raw_to_voltage(cal, raw, &mv); sum += mv; } else sum += raw * 3100 / 4095; }
    float v = 2.0f * sum / 16 / 1000.0f;
    rec("Battery sense (D0)", v > 3.0f && v < 4.30f, "VBAT = %.2f V (want 3.0-4.3)", v);
}

static void i2s_init(void) {
    i2s_chan_config_t ch = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    ESP_ERROR_CHECK(i2s_new_channel(&ch, &tx, &rx));            // full duplex, shared BCLK / WS
    i2s_std_config_t c = {
        .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(FS_HZ),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = { .mclk = I2S_GPIO_UNUSED, .bclk = PIN_I2S_BCLK, .ws = PIN_I2S_WS, .dout = PIN_I2S_DOUT, .din = PIN_I2S_DIN },
    };
    c.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;                   // mic SEL=GND -> left; amps SD high -> left
    ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx, &c));
    ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx, &c));
    gpio_pulldown_en(PIN_I2S_DIN);                               // unpowered mic must read as silence
    ESP_ERROR_CHECK(i2s_channel_enable(tx)); ESP_ERROR_CHECK(i2s_channel_enable(rx));
}

// returns RMS of mic samples (24-bit in 32-bit slot) and count of distinct values
static float mic_rms(int *distinct) {
    static int32_t buf[512]; size_t n = 0; double acc = 0; int32_t first = 0; int diff = 0;
    for (int k = 0; k < 4; k++) i2s_channel_read(rx, buf, sizeof buf, &n, 200);   // flush
    i2s_channel_read(rx, buf, sizeof buf, &n, 200);
    int cnt = n / 4; first = buf[0] >> 8;
    for (int i = 0; i < cnt; i++) { int32_t s = buf[i] >> 8; acc += (double)s * s; if (s != first) diff++; }
    *distinct = diff; return cnt ? sqrtf(acc / cnt) : 0;
}

static int wait_ptt(int level, int seconds) {
    for (int i = 0; i < seconds * 20; i++) { if (gpio_get_level(PIN_PTT_SENSE) == level) return 1; vTaskDelay(pdMS_TO_TICKS(50)); }
    return 0;
}

static void test_ptt_mic(void) {
    int d; float r;
    int idle_low = gpio_get_level(PIN_PTT_SENSE) == 0;
    r = mic_rms(&d);
    rec("PTT released -> no mic", idle_low && d < 4, "sense=%d, mic changing samples=%d (want 0, ~0)", !idle_low, d);
    printf("\n>>> Press and HOLD the PTT button (right frame corner) and speak. Check the red LED is ON.\n");
    int pressed = wait_ptt(1, 15);
    vTaskDelay(pdMS_TO_TICKS(300));                              // mic start-up time
    r = mic_rms(&d);
    rec("PTT held -> sense high", pressed, pressed ? "D1 high" : "timeout: check SW2, D3, R4");
    rec("Mic data while held", pressed && d > 50 && r > 20, "rms=%.0f changing=%d", r, d);
    printf(">>> Release the PTT button. Check the red LED goes OFF.\n");
    int released = wait_ptt(0, 15); vTaskDelay(pdMS_TO_TICKS(300));
    r = mic_rms(&d);
    rec("Release -> mic unpowered", released && d < 4, "changing samples=%d (privacy gate)", d);
}

static void tone(gpio_num_t sd, const char *label) {
    static int32_t buf[256]; size_t w;
    gpio_set_level(PIN_SD_BONE, sd == PIN_SD_BONE); gpio_set_level(PIN_SD_OUT, sd == PIN_SD_OUT);
    vTaskDelay(pdMS_TO_TICKS(20));
    printf(">>> Listening check: %s should play a 1 kHz tone for 1 s now.\n", label);
    float ph = 0;
    for (int blk = 0; blk < FS_HZ / 256; blk++) {
        for (int i = 0; i < 256; i++) { buf[i] = (int32_t)(TONE_AMPL * 2147483647.0f * sinf(ph)); ph += 2 * M_PI * 1000 / FS_HZ; if (ph > 2 * M_PI) ph -= 2 * M_PI; }
        i2s_channel_write(tx, buf, sizeof buf, &w, 100);
    }
    memset(buf, 0, sizeof buf); for (int k = 0; k < 8; k++) i2s_channel_write(tx, buf, sizeof buf, &w, 100);
    gpio_set_level(sd, 0);
}

void app_main(void) {
    // Safety first: media gate LOW, both amps in shutdown (also keeps boost start-up load low)
    gpio_config_t o = { .pin_bit_mask = (1ULL << PIN_MEDIA_EN) | (1ULL << PIN_SD_BONE) | (1ULL << PIN_SD_OUT), .mode = GPIO_MODE_OUTPUT };
    gpio_config(&o); gpio_set_level(PIN_MEDIA_EN, 0); gpio_set_level(PIN_SD_BONE, 0); gpio_set_level(PIN_SD_OUT, 0);
    gpio_config_t in = { .pin_bit_mask = 1ULL << PIN_PTT_SENSE, .mode = GPIO_MODE_INPUT, .pull_down_en = 1 };
    gpio_config(&in);
    vTaskDelay(pdMS_TO_TICKS(1500));                             // time to open the monitor

    printf("\n===== Adaptive Smart Glasses factory test =====\n");
    rec("MEDIA_EN held LOW", gpio_get_level(PIN_MEDIA_EN) == 0, "D6 = 0");
    test_i2c();
    test_vbat();
    i2s_init();
    test_ptt_mic();
    tone(PIN_SD_BONE, "BONE transducer (right ear grip)");
    tone(PIN_SD_OUT, "OUTWARD speaker (right pod)");
    printf("    (amplifier checks are by ear: note PASS/FAIL on the QA sheet)\n");

    int fails = 0; for (int i = 0; i < nR; i++) fails += !R[i].pass;
    printf("\n===== RESULT: %s  (%d automatic checks, %d failed) =====\n", fails ? "FAIL" : "PASS", nR, fails);
    while (1) {                                                 // live view for debugging
        int d; float r = mic_rms(&d);
        ESP_LOGI(TAG, "PTT=%d  mic_rms=%.0f", gpio_get_level(PIN_PTT_SENSE), r);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
