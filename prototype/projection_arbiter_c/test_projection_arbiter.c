#include "projection_arbiter.h"

#include <assert.h>
#include <stdio.h>

static PA_Snapshot active(uint64_t sequence)
{
    PA_Snapshot snapshot = {0};
    snapshot.version = PA_SNAPSHOT_VERSION;
    snapshot.sequence = sequence;
    snapshot.service_connected = true;
    snapshot.projection_session = PA_SESSION_ACTIVE;
    snapshot.platform = PA_PLATFORM_CARPLAY;
    snapshot.auto_show = true;
    return snapshot;
}

int main(void)
{
    PA_Arbiter arbiter;
    PA_Arbiter inactive_arbiter;
    PA_Arbiter offline_arbiter;
    PA_Arbiter background_arbiter;
    PA_Snapshot snapshot;
    PA_Snapshot delayed;
    PA_Presentation presentation;

    pa_init(&arbiter);
    snapshot = active(1);
    assert(pa_receive(&arbiter, &snapshot, 100) == PA_STATUS_OK);
    assert(arbiter.foreground == PA_FOREGROUND_PROJECTION);
    assert(pa_interaction_owner(&arbiter) == PA_OWNER_PROJECTION);
    assert(!pa_native_presentation(&arbiter).incoming_call_foreground);

    assert(pa_return_to_uconnect(&arbiter) == PA_STATUS_OK);
    assert(arbiter.foreground == PA_FOREGROUND_UCONNECT);
    assert(pa_projection_active(&arbiter));

    snapshot = active(2);
    assert(pa_receive(&arbiter, &snapshot, 200) == PA_STATUS_OK);
    assert(arbiter.foreground == PA_FOREGROUND_UCONNECT);
    assert(pa_show_projection(&arbiter, 250) == PA_STATUS_OK);
    assert(arbiter.foreground == PA_FOREGROUND_PROJECTION);
    assert(arbiter.last_sequence == 2);

    snapshot = active(3);
    snapshot.comfort_overlay = true;
    assert(pa_receive(&arbiter, &snapshot, 300) == PA_STATUS_OK);
    assert(arbiter.overlay == PA_OVERLAY_COMFORT);
    snapshot = active(4);
    assert(pa_receive(&arbiter, &snapshot, 400) == PA_STATUS_OK);
    assert(arbiter.overlay == PA_OVERLAY_NONE);
    assert(arbiter.notice == PA_NOTICE_COMFORT_DISMISSED_TO_PROJECTION);

    snapshot = active(5);
    snapshot.camera = true;
    assert(pa_receive(&arbiter, &snapshot, 500) == PA_STATUS_OK);
    assert(arbiter.foreground == PA_FOREGROUND_TAKEOVER);
    assert(pa_interaction_owner(&arbiter) == PA_OWNER_PROJECTION);
    snapshot = active(6);
    assert(pa_receive(&arbiter, &snapshot, 600) == PA_STATUS_OK);
    assert(arbiter.foreground == PA_FOREGROUND_PROJECTION);

    snapshot = active(7);
    snapshot.critical = true;
    assert(pa_receive(&arbiter, &snapshot, 700) == PA_STATUS_OK);
    assert(pa_interaction_owner(&arbiter) == PA_OWNER_UCONNECT);
    presentation = pa_native_presentation(&arbiter);
    assert(presentation.incoming_call_foreground);
    assert(presentation.message_foreground);
    assert(presentation.message_tts);
    snapshot = active(8);
    assert(pa_receive(&arbiter, &snapshot, 800) == PA_STATUS_OK);
    assert(pa_interaction_owner(&arbiter) == PA_OWNER_PROJECTION);

    snapshot = active(9);
    snapshot.platform = PA_PLATFORM_NONE;
    assert(pa_receive(&arbiter, &snapshot, 900) == PA_STATUS_INVALID);
    assert(!arbiter.has_state);
    assert(arbiter.last_sequence == 8);
    assert(pa_interaction_owner(&arbiter) == PA_OWNER_UCONNECT);

    snapshot = active(9);
    assert(pa_receive(&arbiter, &snapshot, 1000) == PA_STATUS_OK);
    delayed = snapshot;
    assert(pa_tick(&arbiter, 1000 + PA_FRESH_MS + 1) == PA_STATUS_OK);
    assert(!arbiter.has_state);
    assert(arbiter.last_sequence == 9);
    assert(pa_receive(&arbiter, &delayed, 1000 + PA_FRESH_MS + 2) ==
           PA_STATUS_IGNORED);
    assert(!arbiter.has_state);

    snapshot = active(10);
    assert(pa_receive(&arbiter, &snapshot, 1000 + PA_FRESH_MS + 3) ==
           PA_STATUS_OK);
    snapshot.sequence = 11;
    snapshot.projection_session = PA_SESSION_DISCONNECTED;
    snapshot.platform = PA_PLATFORM_NONE;
    snapshot.auto_show = false;
    assert(pa_receive(&arbiter, &snapshot, 1000 + PA_FRESH_MS + 4) ==
           PA_STATUS_OK);
    assert(arbiter.foreground == PA_FOREGROUND_UCONNECT);
    assert(pa_interaction_owner(&arbiter) == PA_OWNER_UCONNECT);
    assert(pa_native_presentation(&arbiter).message_tts);

    pa_init(&background_arbiter);
    snapshot = active(1);
    snapshot.auto_show = false;
    assert(pa_receive(&background_arbiter, &snapshot, 10) == PA_STATUS_OK);
    assert(background_arbiter.foreground == PA_FOREGROUND_UCONNECT);
    assert(pa_projection_active(&background_arbiter));
    assert(pa_interaction_owner(&background_arbiter) == PA_OWNER_PROJECTION);
    assert(!pa_native_presentation(&background_arbiter).message_foreground);

    pa_init(&offline_arbiter);
    snapshot = active(1);
    assert(pa_receive(&offline_arbiter, &snapshot, 10) == PA_STATUS_OK);
    delayed = snapshot;
    snapshot = active(2);
    snapshot.service_connected = false;
    assert(pa_receive(&offline_arbiter, &snapshot, 20) == PA_STATUS_OK);
    assert(!offline_arbiter.has_state);
    assert(offline_arbiter.foreground == PA_FOREGROUND_UCONNECT);
    assert(pa_interaction_owner(&offline_arbiter) == PA_OWNER_UCONNECT);
    assert(pa_native_presentation(&offline_arbiter).incoming_call_foreground);
    assert(pa_receive(&offline_arbiter, &delayed, 30) == PA_STATUS_IGNORED);
    assert(!offline_arbiter.has_state);

    pa_init(&inactive_arbiter);
    snapshot = active(1);
    snapshot.projection_session = PA_SESSION_CONNECTED;
    assert(pa_receive(&inactive_arbiter, &snapshot, 10) == PA_STATUS_OK);
    assert(inactive_arbiter.foreground == PA_FOREGROUND_UCONNECT);
    assert(pa_show_projection(&inactive_arbiter, 10) ==
           PA_STATUS_NO_ACTIVE_SESSION);
    assert(pa_show_projection(&inactive_arbiter, 9) ==
           PA_STATUS_NON_MONOTONIC_TIME);

    puts("projection_arbiter: all assertions passed");
    return 0;
}
