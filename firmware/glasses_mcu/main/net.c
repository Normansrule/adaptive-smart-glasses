// Wi-Fi station to the brick's hotspot + UDP head-pose/state packets (100 Hz).
// Packet (little-endian, 44 bytes): "ASG2", u32 seq, u32 t_ms, f32 yaw,pitch,roll, f32 ax,ay,az,
//                                   u16 vbat_mv, u8 visor_up, u8 design, u8 ar_mode, u8 pad[3]
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "lwip/sockets.h"
#include "asg.h"

static const char *TAG = "net";
static int sock = -1;
static struct sockaddr_in dst;

typedef struct __attribute__((packed)) {
    char magic[4]; uint32_t seq, t_ms; float yaw, pitch, roll, ax, ay, az;
    uint16_t vbat_mv; uint8_t visor_up, design, ar_mode, pad[3];
} pose_pkt_t;
_Static_assert(sizeof(pose_pkt_t) == 44, "must match PKT in brick/passthrough.py");

static void on_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    if (base == WIFI_EVENT && (id == WIFI_EVENT_STA_START || id == WIFI_EVENT_STA_DISCONNECTED)) { G.wifi_up = 0; esp_wifi_connect(); }
    if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) { G.wifi_up = 1; ESP_LOGI(TAG, "connected to brick hotspot"); }
}

void net_start(void) {
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_event, NULL);
    esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_event, NULL);
    wifi_config_t wc = { 0 };
    strlcpy((char *)wc.sta.ssid, CONFIG_ASG_WIFI_SSID, sizeof wc.sta.ssid);
    strlcpy((char *)wc.sta.password, CONFIG_ASG_WIFI_PASS, sizeof wc.sta.password);
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wc));
    ESP_ERROR_CHECK(esp_wifi_start());
    esp_wifi_set_ps(WIFI_PS_NONE);                                       // lowest latency for head pose
    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    memset(&dst, 0, sizeof dst);
    dst.sin_family = AF_INET; dst.sin_port = htons(CONFIG_ASG_BRICK_PORT);
    inet_aton(CONFIG_ASG_BRICK_IP, &dst.sin_addr);
}

void net_send_pose(void) {
    static uint32_t seq;
    if (!G.wifi_up || sock < 0) return;
    pose_pkt_t p = { .magic = { 'A', 'S', 'G', '2' }, .seq = seq++, .t_ms = (uint32_t)(esp_timer_get_time() / 1000),
        .yaw = G.yaw, .pitch = G.pitch, .roll = G.roll, .ax = G.acc[0], .ay = G.acc[1], .az = G.acc[2],
        .vbat_mv = (uint16_t)G.vbat_mv, .visor_up = G.visor_up, .design = G.design, .ar_mode = G.ar_mode };
    sendto(sock, &p, sizeof p, MSG_DONTWAIT, (struct sockaddr *)&dst, sizeof dst);
}
