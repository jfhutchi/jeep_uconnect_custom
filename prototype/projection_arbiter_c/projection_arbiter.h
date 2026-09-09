#ifndef PROJECTION_ARBITER_H
#define PROJECTION_ARBITER_H

#include <stdbool.h>
#include <stdint.h>

#define PA_SNAPSHOT_VERSION UINT32_C(2)
#define PA_FRESH_MS UINT64_C(2000)

typedef enum {
    PA_STATUS_OK = 0,
    PA_STATUS_IGNORED,
    PA_STATUS_INVALID,
    PA_STATUS_NON_MONOTONIC_TIME,
    PA_STATUS_UNAVAILABLE,
    PA_STATUS_TAKEOVER_ACTIVE,
    PA_STATUS_NO_ACTIVE_SESSION
} PA_Status;

typedef enum {
    PA_SESSION_DISCONNECTED = 0,
    PA_SESSION_CONNECTED,
    PA_SESSION_ACTIVE
} PA_Session;

typedef enum {
    PA_PLATFORM_NONE = 0,
    PA_PLATFORM_CARPLAY,
    PA_PLATFORM_ANDROID_AUTO
} PA_Platform;

typedef enum {
    PA_FOREGROUND_UCONNECT = 0,
    PA_FOREGROUND_PROJECTION,
    PA_FOREGROUND_TAKEOVER
} PA_Foreground;

typedef enum {
    PA_OVERLAY_NONE = 0,
    PA_OVERLAY_COMFORT
} PA_Overlay;

typedef enum {
    PA_OWNER_UCONNECT = 0,
    PA_OWNER_PROJECTION
} PA_InteractionOwner;

typedef enum {
    PA_NOTICE_STOCK_DISCONNECTED = 0,
    PA_NOTICE_STOCK,
    PA_NOTICE_STOCK_SESSION_ACTIVE,
    PA_NOTICE_PROJECTION_AUTO_SHOWN,
    PA_NOTICE_PROJECTION_RESUMED,
    PA_NOTICE_PROJECTION_ENDED,
    PA_NOTICE_CAMERA_TAKEOVER,
    PA_NOTICE_CRITICAL_TAKEOVER,
    PA_NOTICE_PROJECTION_RESTORED,
    PA_NOTICE_STOCK_RESTORED,
    PA_NOTICE_COMFORT_OVERLAY,
    PA_NOTICE_COMFORT_DISMISSED_TO_PROJECTION,
    PA_NOTICE_INVALID_STATE,
    PA_NOTICE_STALE_STATE,
    PA_NOTICE_SERVICE_DISCONNECTED
} PA_Notice;

typedef struct {
    uint32_t version;
    uint64_t sequence;
    bool service_connected;
    bool camera;
    bool critical;
    bool comfort_overlay;
    PA_Session projection_session;
    PA_Platform platform;
    bool auto_show;
    bool call_active;
    bool message_pending;
} PA_Snapshot;

typedef struct {
    PA_InteractionOwner owner;
    bool incoming_call_foreground;
    bool message_foreground;
    bool message_tts;
} PA_Presentation;

typedef struct {
    PA_Foreground foreground;
    PA_Overlay overlay;
    PA_Foreground preempted_foreground;
    PA_Notice notice;
    PA_Snapshot state;
    uint64_t last_sequence;
    uint64_t last_received_ms;
    uint64_t last_now_ms;
    bool has_state;
    bool has_sequence;
    bool has_time;
} PA_Arbiter;

void pa_init(PA_Arbiter *arbiter);
bool pa_projection_active(const PA_Arbiter *arbiter);
bool pa_is_fresh(const PA_Arbiter *arbiter, uint64_t now_ms);
PA_InteractionOwner pa_interaction_owner(const PA_Arbiter *arbiter);
PA_Presentation pa_native_presentation(const PA_Arbiter *arbiter);
PA_Status pa_native_presentation_at(PA_Arbiter *arbiter, uint64_t now_ms,
                                    PA_Presentation *presentation);
PA_Status pa_tick(PA_Arbiter *arbiter, uint64_t now_ms);
PA_Status pa_receive(PA_Arbiter *arbiter, const PA_Snapshot *snapshot,
                     uint64_t now_ms);
PA_Status pa_return_to_uconnect(PA_Arbiter *arbiter);
PA_Status pa_show_projection(PA_Arbiter *arbiter, uint64_t now_ms);

#endif
