// Adaptive Smart Glasses v0.2 — visor MCU firmware (ESP-IDF 5.5, Seeed XIAO ESP32-S3)
// Status: EXPERIMENTAL — compiles cleanly; not yet run on a finished unit.
//   * outward design screens (designs.c)      * phone control over BLE (ble.c)
//   * head pose + state to the brick over Wi-Fi UDP (net.c)
//   * IMU, visor hall switch, action button, battery sense (this file)
// Privacy note: the camera's power is switched by SW2 in hardware and the CAMERA-LIVE LED
// sits on that rail. Nothing in this firmware can power the camera or hide the LED.
#include <stdio.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "asg.h"

asg_state_t G = { .design = DESIGN_EYES, .brightness = 70, .ar_mode = AR_NORMAL, .text = "HELLO WORLD" };
static const char *TAG = "asg";
static i2c_master_dev_handle_t imu;
static int imu_ok;

// ---------------- IMU: LSM6DSOX @ 0x6A (or 0x6B) ----------------
static esp_err_t imu_wr(uint8_t r, uint8_t v) { uint8_t b[2] = { r, v }; return i2c_master_transmit(imu, b, 2, 20); }
static esp_err_t imu_rd(uint8_t r, uint8_t *d, size_t n) { return i2c_master_transmit_receive(imu, &r, 1, d, n, 20); }
static void imu_init(void) {
    i2c_master_bus_handle_t bus;
    i2c_master_bus_config_t bc = { .i2c_port = I2C_NUM_0, .sda_io_num = PIN_SDA, .scl_io_num = PIN_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT, .glitch_ignore_cnt = 7, .flags.enable_internal_pullup = true };
    ESP_ERROR_CHECK(i2c_new_master_bus(&bc, &bus));
    for (int a = 0x6A; a <= 0x6B && !imu_ok; a++) {
        if (i2c_master_probe(bus, a, 20) != ESP_OK) continue;
        i2c_device_config_t dc = { .dev_addr_length = I2C_ADDR_BIT_LEN_7, .device_address = a, .scl_speed_hz = 400000 };
        ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &dc, &imu));
        uint8_t who = 0; imu_rd(0x0F, &who, 1);
        imu_ok = (who == 0x6C);
        ESP_LOGI(TAG, "IMU @0x%02X WHO_AM_I=0x%02X %s", a, who, imu_ok ? "OK" : "unexpected");
    }
    if (!imu_ok) { ESP_LOGW(TAG, "IMU not found: check Qwiic cable"); return; }
    imu_wr(0x12, 0x44);   // CTRL3_C: BDU + auto-increment
    imu_wr(0x10, 0x60);   // CTRL1_XL: 416 Hz, +-2 g
    imu_wr(0x11, 0x60);   // CTRL2_G : 416 Hz, 250 dps
}
static void imu_task(void *arg) {
    int64_t last = esp_timer_get_time(); int n = 0;
    while (1) {
        if (imu_ok) {
            uint8_t d[12]; int16_t r[6];
            if (imu_rd(0x22, d, 12) == ESP_OK) {
                for (int i = 0; i < 6; i++) r[i] = (int16_t)(d[2 * i] | d[2 * i + 1] << 8);
                for (int i = 0; i < 3; i++) { G.gyr[i] = r[i] * 0.00875f; G.acc[i] = r[3 + i] * 0.000061f; }
                int64_t now = esp_timer_get_time(); float dt = (now - last) / 1e6f; last = now;
                // complementary filter (axes as mounted in the visor bridge — verify signs on the bench)
                float ap = atan2f(-G.acc[0], sqrtf(G.acc[1] * G.acc[1] + G.acc[2] * G.acc[2])) * 57.2958f;
                float ar = atan2f(G.acc[1], G.acc[2]) * 57.2958f;
                G.pitch = 0.98f * (G.pitch + G.gyr[1] * dt) + 0.02f * ap;
                G.roll  = 0.98f * (G.roll  + G.gyr[0] * dt) + 0.02f * ar;
                G.yaw  += G.gyr[2] * dt;
            }
        }
        if (++n % 2 == 0) net_send_pose();                              // 100 Hz to the brick
        vTaskDelay(pdMS_TO_TICKS(5));                                   // 200 Hz
    }
}

// ---------------- battery sense: D3 = VBAT/2 ----------------
static adc_oneshot_unit_handle_t adc; static adc_cali_handle_t cal;
static void vbat_init(void) {
    adc_oneshot_unit_init_cfg_t uc = { .unit_id = ADC_UNIT_1 }; adc_oneshot_new_unit(&uc, &adc);
    adc_oneshot_chan_cfg_t cc = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    adc_oneshot_config_channel(adc, ADC_CHANNEL_3, &cc);
    adc_cali_curve_fitting_config_t cf = { .unit_id = ADC_UNIT_1, .chan = ADC_CHANNEL_3, .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    if (adc_cali_create_scheme_curve_fitting(&cf, &cal) != ESP_OK) cal = NULL;
}
static int vbat_read_mv(void) {
    int raw, mv, sum = 0;
    for (int i = 0; i < 8; i++) { adc_oneshot_read(adc, ADC_CHANNEL_3, &raw);
        if (cal) { adc_cali_raw_to_voltage(cal, raw, &mv); } else mv = raw * 3100 / 4095; sum += mv; }
    return 2 * sum / 8;
}

void app_main(void) {
    esp_err_t e = nvs_flash_init();
    if (e == ESP_ERR_NVS_NO_FREE_PAGES || e == ESP_ERR_NVS_NEW_VERSION_FOUND) { nvs_flash_erase(); nvs_flash_init(); }
    gpio_config_t in = { .pin_bit_mask = (1ULL << PIN_HALL) | (1ULL << PIN_BUTTON), .mode = GPIO_MODE_INPUT, .pull_up_en = 1 };
    gpio_config(&in);
    imu_init();
    vbat_init();
    G.vbat_mv = vbat_read_mv();
    G.visor_up = gpio_get_level(PIN_HALL);

    printf("\n===== ASG v0.2 self-test =====\n");
    printf("  [%s] IMU LSM6DSOX\n", imu_ok ? "PASS" : "FAIL");
    printf("  [%s] Battery %d mV (expect 3000-4300; ~0 = switch off or USB only)\n", (G.vbat_mv > 3000 && G.vbat_mv < 4300) ? "PASS" : "WARN", G.vbat_mv);
    printf("  [INFO] Visor is %s (hall)\n", G.visor_up ? "UP" : "DOWN");
    printf("  Watch both outward screens: animated eyes should appear.\n\n");

    designs_start();
    ble_start();
    net_start();
    xTaskCreatePinnedToCore(imu_task, "imu", 4096, NULL, 5, NULL, 0);

    int held = 0, last_btn = 1; int64_t t_status = 0;
    while (1) {                                                         // 20 ms UI loop
        int up = gpio_get_level(PIN_HALL);
        if (up != G.visor_up) { G.visor_up = up; ESP_LOGI(TAG, "visor %s", up ? "UP" : "DOWN"); ble_notify_status(); }
        int b = gpio_get_level(PIN_BUTTON);
        if (b == 0) held++;
        if (b == 1 && last_btn == 0) {                                  // release
            if (held >= 50)      G.design = DESIGN_OFF;                 // >= 1 s: designs off (privacy / battery)
            else if (held >= 2)  G.design = (G.design + 1) % DESIGN_COUNT;
            held = 0; ble_notify_status();
        }
        last_btn = b;
        if (esp_timer_get_time() > t_status) {
            G.vbat_mv = vbat_read_mv(); ble_notify_status();
            t_status = esp_timer_get_time() + 2000000;
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
