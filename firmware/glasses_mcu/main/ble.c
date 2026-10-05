// BLE GATT service for the phone app (Web Bluetooth in the repo's web app, "Glasses" tab).
// Service 7a1e0000-5c3b-4c55-9b1d-a5e0a5e0a5e0
//   ...0001 design     u8  R/W   (0 eyes, 1 rings, 2 rainbow, 3 text, 4 off)
//   ...0002 brightness u8  R/W   (0-100 %)
//   ...0003 text       utf8 W    (<= 32 chars, shown by design 3)
//   ...0004 ar_mode    u8  R/W   (0 normal, 1 zoom, 2 edges, 3 low-light) -> forwarded to the brick
//   ...0005 status     8 B R/N   u16 vbat_mv, u8 visor_up, u8 design, u8 ar_mode, u8 wifi_up, i16 roll*10
#include <string.h>
#include "esp_log.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"
#include "asg.h"

static const char *TAG = "ble";
static uint16_t status_handle, conn = BLE_HS_CONN_HANDLE_NONE;
static uint8_t own_addr_type;

#define UUID(n) BLE_UUID128_INIT(0xe0,0xa5,0xe0,0xa5,0xe0,0xa5,0x1d,0x9b,0x55,0x4c,0x3b,0x5c, n,0x00,0x1e,0x7a)
static const ble_uuid128_t SVC = UUID(0x00), C_DESIGN = UUID(0x01), C_BRIGHT = UUID(0x02), C_TEXT = UUID(0x03),
                           C_AR = UUID(0x04), C_STATUS = UUID(0x05);

static int access(uint16_t ch, uint16_t ah, struct ble_gatt_access_ctxt *ctxt, void *arg) {
    const ble_uuid_t *u = ctxt->chr->uuid;
    if (ctxt->op == BLE_GATT_ACCESS_OP_READ_CHR) {
        if (!ble_uuid_cmp(u, &C_DESIGN.u)) return os_mbuf_append(ctxt->om, (void *)&G.design, 1);
        if (!ble_uuid_cmp(u, &C_BRIGHT.u)) return os_mbuf_append(ctxt->om, (void *)&G.brightness, 1);
        if (!ble_uuid_cmp(u, &C_AR.u))     return os_mbuf_append(ctxt->om, (void *)&G.ar_mode, 1);
        if (!ble_uuid_cmp(u, &C_STATUS.u)) {
            int16_t roll10 = (int16_t)(G.roll * 10);
            uint8_t s[8] = { G.vbat_mv & 0xFF, G.vbat_mv >> 8, G.visor_up, G.design, G.ar_mode, G.wifi_up, roll10 & 0xFF, (roll10 >> 8) & 0xFF };
            return os_mbuf_append(ctxt->om, s, sizeof s);
        }
        return BLE_ATT_ERR_UNLIKELY;
    }
    if (ctxt->op == BLE_GATT_ACCESS_OP_WRITE_CHR) {
        char b[33] = { 0 }; uint16_t n = 0;
        ble_hs_mbuf_to_flat(ctxt->om, b, sizeof b - 1, &n);
        if (!n) return 0;
        if (!ble_uuid_cmp(u, &C_DESIGN.u)) G.design = b[0] % DESIGN_COUNT;
        else if (!ble_uuid_cmp(u, &C_BRIGHT.u)) G.brightness = (uint8_t)b[0] > 100 ? 100 : (uint8_t)b[0];
        else if (!ble_uuid_cmp(u, &C_AR.u)) G.ar_mode = b[0] % AR_COUNT;
        else if (!ble_uuid_cmp(u, &C_TEXT.u)) { memcpy(G.text, b, n); G.text[n] = 0; G.design = DESIGN_TEXT; }
        ble_notify_status();
        return 0;
    }
    return BLE_ATT_ERR_UNLIKELY;
}

static const struct ble_gatt_svc_def svcs[] = {
    { .type = BLE_GATT_SVC_TYPE_PRIMARY, .uuid = &SVC.u, .characteristics = (struct ble_gatt_chr_def[]) {
        { .uuid = &C_DESIGN.u, .access_cb = access, .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_WRITE },
        { .uuid = &C_BRIGHT.u, .access_cb = access, .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_WRITE },
        { .uuid = &C_TEXT.u,   .access_cb = access, .flags = BLE_GATT_CHR_F_WRITE },
        { .uuid = &C_AR.u,     .access_cb = access, .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_WRITE },
        { .uuid = &C_STATUS.u, .access_cb = access, .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_NOTIFY, .val_handle = &status_handle },
        { 0 } } },
    { 0 }
};

static void advertise(void);
static int gap_event(struct ble_gap_event *ev, void *arg) {
    switch (ev->type) {
        case BLE_GAP_EVENT_CONNECT:
            if (ev->connect.status == 0) { conn = ev->connect.conn_handle; G.ble_connected = 1; ESP_LOGI(TAG, "phone connected"); }
            else advertise();
            break;
        case BLE_GAP_EVENT_DISCONNECT: conn = BLE_HS_CONN_HANDLE_NONE; G.ble_connected = 0; advertise(); break;
        case BLE_GAP_EVENT_ADV_COMPLETE: advertise(); break;
        default: break;
    }
    return 0;
}
static void advertise(void) {
    struct ble_hs_adv_fields f = { 0 };
    const char *name = ble_svc_gap_device_name();
    f.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
    f.name = (uint8_t *)name; f.name_len = strlen(name); f.name_is_complete = 1;
    ble_gap_adv_set_fields(&f);
    struct ble_hs_adv_fields rsp = { 0 };
    rsp.uuids128 = (ble_uuid128_t *)&SVC; rsp.num_uuids128 = 1; rsp.uuids128_is_complete = 1;
    ble_gap_adv_rsp_set_fields(&rsp);
    struct ble_gap_adv_params p = { .conn_mode = BLE_GAP_CONN_MODE_UND, .disc_mode = BLE_GAP_DISC_MODE_GEN };
    ble_gap_adv_start(own_addr_type, NULL, BLE_HS_FOREVER, &p, gap_event, NULL);
}
static void on_sync(void) { ble_hs_id_infer_auto(0, &own_addr_type); advertise(); }
static void host_task(void *param) { nimble_port_run(); nimble_port_freertos_deinit(); }

void ble_notify_status(void) { if (conn != BLE_HS_CONN_HANDLE_NONE) ble_gatts_chr_updated(status_handle); }

void ble_start(void) {
    ESP_ERROR_CHECK(nimble_port_init());
    ble_hs_cfg.sync_cb = on_sync;
    ble_svc_gap_init(); ble_svc_gatt_init();
    ble_svc_gap_device_name_set("ASG-Glasses");
    ble_gatts_count_cfg(svcs); ble_gatts_add_svcs(svcs);
    nimble_port_freertos_init(host_task);
    ESP_LOGI(TAG, "advertising as ASG-Glasses");
}
