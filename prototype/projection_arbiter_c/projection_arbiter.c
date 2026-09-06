#include "projection_arbiter.h"

typedef char pa_arbiter_size_must_not_exceed_128_bytes[
    sizeof(PA_Arbiter) <= 128 ? 1 : -1];

static PA_Status pa_advance_time(PA_Arbiter *arbiter, uint64_t now_ms)
{
    if (arbiter == 0) {
        return PA_STATUS_INVALID;
    }
    if (arbiter->has_time && now_ms < arbiter->last_now_ms) {
        return PA_STATUS_NON_MONOTONIC_TIME;
    }
    arbiter->last_now_ms = now_ms;
    arbiter->has_time = true;
    return PA_STATUS_OK;
}

static void pa_fallback(PA_Arbiter *arbiter, PA_Notice notice,
                        bool invalidate_state)
{
    arbiter->foreground = PA_FOREGROUND_UCONNECT;
    arbiter->overlay = PA_OVERLAY_NONE;
    arbiter->preempted_foreground = PA_FOREGROUND_UCONNECT;
    if (invalidate_state) {
        arbiter->has_state = false;
    }
    arbiter->notice = notice;
}

static bool pa_valid_snapshot(const PA_Snapshot *snapshot)
{
    if (snapshot == 0 || snapshot->version != PA_SNAPSHOT_VERSION) {
        return false;
    }
    if (snapshot->projection_session < PA_SESSION_DISCONNECTED ||
        snapshot->projection_session > PA_SESSION_ACTIVE) {
        return false;
    }
    if (snapshot->platform < PA_PLATFORM_NONE ||
        snapshot->platform > PA_PLATFORM_ANDROID_AUTO) {
        return false;
    }
    if (snapshot->projection_session == PA_SESSION_DISCONNECTED &&
        snapshot->platform != PA_PLATFORM_NONE) {
        return false;
    }
    if (snapshot->projection_session != PA_SESSION_DISCONNECTED &&
        snapshot->platform == PA_PLATFORM_NONE) {
        return false;
    }
    return !(snapshot->camera && snapshot->critical);
}

void pa_init(PA_Arbiter *arbiter)
{
    if (arbiter == 0) {
        return;
    }
    *arbiter = (PA_Arbiter){0};
    arbiter->foreground = PA_FOREGROUND_UCONNECT;
    arbiter->overlay = PA_OVERLAY_NONE;
    arbiter->preempted_foreground = PA_FOREGROUND_UCONNECT;
    arbiter->notice = PA_NOTICE_STOCK_DISCONNECTED;
}

bool pa_projection_active(const PA_Arbiter *arbiter)
{
    return arbiter != 0 && arbiter->has_state &&
           arbiter->state.projection_session == PA_SESSION_ACTIVE;
}

bool pa_is_fresh(const PA_Arbiter *arbiter, uint64_t now_ms)
{
    return arbiter != 0 && arbiter->has_state &&
           arbiter->state.service_connected &&
           now_ms >= arbiter->last_received_ms &&
           now_ms - arbiter->last_received_ms <= PA_FRESH_MS;
}

PA_InteractionOwner pa_interaction_owner(const PA_Arbiter *arbiter)
{
    if (arbiter != 0 && arbiter->has_state && arbiter->state.critical) {
        return PA_OWNER_UCONNECT;
    }
    return pa_projection_active(arbiter) ?
           PA_OWNER_PROJECTION : PA_OWNER_UCONNECT;
}

PA_Presentation pa_native_presentation(const PA_Arbiter *arbiter)
{
    PA_Presentation result;
    bool allowed = pa_interaction_owner(arbiter) == PA_OWNER_UCONNECT;
    result.owner = allowed ? PA_OWNER_UCONNECT : PA_OWNER_PROJECTION;
    result.incoming_call_foreground = allowed;
    result.message_foreground = allowed;
    result.message_tts = allowed;
    return result;
}

PA_Status pa_tick(PA_Arbiter *arbiter, uint64_t now_ms)
{
    PA_Status status = pa_advance_time(arbiter, now_ms);
    if (status != PA_STATUS_OK) {
        return status;
    }
    if (arbiter->has_state && !pa_is_fresh(arbiter, now_ms)) {
        pa_fallback(arbiter, PA_NOTICE_STALE_STATE, true);
    }
    return PA_STATUS_OK;
}

PA_Status pa_receive(PA_Arbiter *arbiter, const PA_Snapshot *snapshot,
                     uint64_t now_ms)
{
    PA_Status status;
    bool prior_active;
    bool was_takeover;
    bool had_comfort_overlay;
    bool resume_projection;

    status = pa_tick(arbiter, now_ms);
    if (status != PA_STATUS_OK) {
        return status;
    }
    if (!pa_valid_snapshot(snapshot)) {
        pa_fallback(arbiter, PA_NOTICE_INVALID_STATE, true);
        return PA_STATUS_INVALID;
    }
    if (arbiter->has_sequence && snapshot->sequence <= arbiter->last_sequence) {
        return PA_STATUS_IGNORED;
    }

    prior_active = pa_projection_active(arbiter);
    was_takeover = arbiter->foreground == PA_FOREGROUND_TAKEOVER;
    had_comfort_overlay = arbiter->overlay == PA_OVERLAY_COMFORT;
    arbiter->state = *snapshot;
    arbiter->has_state = true;
    arbiter->last_sequence = snapshot->sequence;
    arbiter->has_sequence = true;
    arbiter->last_received_ms = now_ms;

    if (!snapshot->service_connected) {
        pa_fallback(arbiter, PA_NOTICE_SERVICE_DISCONNECTED, true);
        return PA_STATUS_OK;
    }

    if (snapshot->camera || snapshot->critical) {
        if (!was_takeover) {
            arbiter->preempted_foreground = arbiter->foreground;
        }
        arbiter->foreground = PA_FOREGROUND_TAKEOVER;
        arbiter->overlay = PA_OVERLAY_NONE;
        arbiter->notice = snapshot->camera ?
                          PA_NOTICE_CAMERA_TAKEOVER :
                          PA_NOTICE_CRITICAL_TAKEOVER;
        return PA_STATUS_OK;
    }

    arbiter->overlay = snapshot->comfort_overlay ?
                       PA_OVERLAY_COMFORT : PA_OVERLAY_NONE;
    if (was_takeover) {
        resume_projection =
            arbiter->preempted_foreground == PA_FOREGROUND_PROJECTION &&
            pa_projection_active(arbiter);
        arbiter->foreground = resume_projection ?
                              PA_FOREGROUND_PROJECTION :
                              PA_FOREGROUND_UCONNECT;
        arbiter->preempted_foreground = PA_FOREGROUND_UCONNECT;
        arbiter->notice = resume_projection ?
                          PA_NOTICE_PROJECTION_RESTORED :
                          PA_NOTICE_STOCK_RESTORED;
    } else if (arbiter->foreground == PA_FOREGROUND_PROJECTION &&
               !pa_projection_active(arbiter)) {
        pa_fallback(arbiter, PA_NOTICE_PROJECTION_ENDED, false);
    } else if (!prior_active && pa_projection_active(arbiter) &&
               snapshot->auto_show) {
        arbiter->foreground = PA_FOREGROUND_PROJECTION;
        arbiter->notice = PA_NOTICE_PROJECTION_AUTO_SHOWN;
    } else if (arbiter->overlay == PA_OVERLAY_COMFORT) {
        arbiter->notice = PA_NOTICE_COMFORT_OVERLAY;
    } else if (had_comfort_overlay) {
        if (arbiter->foreground == PA_FOREGROUND_PROJECTION) {
            arbiter->notice = PA_NOTICE_COMFORT_DISMISSED_TO_PROJECTION;
        } else if (pa_projection_active(arbiter)) {
            arbiter->notice = PA_NOTICE_STOCK_SESSION_ACTIVE;
        } else {
            arbiter->notice = PA_NOTICE_STOCK;
        }
    }
    return PA_STATUS_OK;
}

PA_Status pa_return_to_uconnect(PA_Arbiter *arbiter)
{
    if (arbiter == 0) {
        return PA_STATUS_INVALID;
    }
    if (arbiter->foreground == PA_FOREGROUND_TAKEOVER) {
        return PA_STATUS_TAKEOVER_ACTIVE;
    }
    arbiter->foreground = PA_FOREGROUND_UCONNECT;
    arbiter->notice = pa_projection_active(arbiter) ?
                      PA_NOTICE_STOCK_SESSION_ACTIVE : PA_NOTICE_STOCK;
    return PA_STATUS_OK;
}

PA_Status pa_show_projection(PA_Arbiter *arbiter, uint64_t now_ms)
{
    PA_Status status = pa_tick(arbiter, now_ms);
    if (status != PA_STATUS_OK) {
        return status;
    }
    if (!pa_is_fresh(arbiter, now_ms)) {
        return PA_STATUS_UNAVAILABLE;
    }
    if (arbiter->foreground == PA_FOREGROUND_TAKEOVER) {
        return PA_STATUS_TAKEOVER_ACTIVE;
    }
    if (!pa_projection_active(arbiter)) {
        return PA_STATUS_NO_ACTIVE_SESSION;
    }
    arbiter->foreground = PA_FOREGROUND_PROJECTION;
    arbiter->notice = PA_NOTICE_PROJECTION_RESUMED;
    return PA_STATUS_OK;
}
