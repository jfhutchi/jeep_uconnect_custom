package com.jfhutchi.uconnect.networkprobe;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public final class NetworkProbeHost implements NetworkProbeListener {
    private static final long START_TIMEOUT_MILLIS = 3000;
    private static final long STOP_TIMEOUT_MILLIS = 3000;

    public void onState(String state, String detail) {
        if ("ERROR".equals(state)) {
            System.err.println("SERVER ERROR: " + detail);
        }
    }

    public void onMessage(String clientAddress, String message, int receivedCount) {
        // The host harness validates transport; protocol output stays on the socket.
    }

    private int run(int port) throws IOException, InterruptedException {
        NetworkProbeServer server = new NetworkProbeServer(port, this);
        server.start();
        if (!server.awaitListening(START_TIMEOUT_MILLIS)) {
            server.stop();
            server.awaitStopped(STOP_TIMEOUT_MILLIS);
            System.err.println("server did not start listening");
            return 2;
        }
        System.out.println("PORT " + server.getPort());
        System.out.flush();

        BufferedReader input = new BufferedReader(new InputStreamReader(System.in));
        String command = input.readLine();
        if (!"STOP".equals(command)) {
            System.err.println("expected STOP on stdin");
            server.stop();
            server.awaitStopped(STOP_TIMEOUT_MILLIS);
            return 2;
        }
        server.stop();
        server.stop();
        if (!server.awaitStopped(STOP_TIMEOUT_MILLIS)) {
            System.err.println("server worker did not stop");
            return 3;
        }
        return 0;
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("usage: NetworkProbeHost PORT");
            System.exit(2);
        }
        int port;
        try {
            port = Integer.parseInt(args[0]);
        } catch (NumberFormatException error) {
            System.err.println("invalid port");
            System.exit(2);
            return;
        }
        try {
            System.exit(new NetworkProbeHost().run(port));
        } catch (IOException error) {
            System.err.println("host I/O error: " + error.getClass().getName());
            System.exit(2);
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt();
            System.err.println("host interrupted");
            System.exit(2);
        }
    }
}
