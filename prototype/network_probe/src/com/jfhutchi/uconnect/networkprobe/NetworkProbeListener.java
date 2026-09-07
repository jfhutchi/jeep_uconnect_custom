package com.jfhutchi.uconnect.networkprobe;

public interface NetworkProbeListener {
    void onState(String state, String detail);

    void onMessage(String clientAddress, String message, int receivedCount);
}
