package com.jfhutchi.uconnect.networkprobe;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;

public final class NetworkProbeServer implements Runnable {
    public static final int DEFAULT_PORT = 8888;
    public static final int MAX_MESSAGE_BYTES = 256;

    private static final int CLIENT_TIMEOUT_MILLIS = 5000;
    private static final int MAX_DETAIL_CHARS = 160;
    private static final String ACKNOWLEDGEMENT = "HELLO FROM UCONNECT\n";
    private static final String ERROR_EMPTY = "ERROR EMPTY MESSAGE\n";
    private static final String ERROR_INVALID = "ERROR INVALID MESSAGE\n";
    private static final String ERROR_TOO_LONG = "ERROR MESSAGE TOO LONG\n";

    private final int requestedPort;
    private final NetworkProbeListener listener;
    private volatile boolean running;
    private ServerSocket serverSocket;
    private Socket activeClient;
    private Thread worker;
    private int boundPort = -1;
    private int receivedCount;

    public NetworkProbeServer(int port, NetworkProbeListener probeListener) {
        if (port < 0 || port > 65535) {
            throw new IllegalArgumentException("port is outside 0..65535");
        }
        if (probeListener == null) {
            throw new IllegalArgumentException("listener is required");
        }
        requestedPort = port;
        listener = probeListener;
    }

    public synchronized void start() {
        if (running) {
            return;
        }
        if (worker != null) {
            throw new IllegalStateException("server worker is still stopping");
        }
        running = true;
        boundPort = -1;
        Thread newWorker = new Thread(this, "NetworkProbeServer");
        worker = newWorker;
        newWorker.start();
    }

    public void run() {
        ServerSocket localServer = null;
        try {
            localServer = new ServerSocket();
            localServer.setReuseAddress(true);
            localServer.bind(new InetSocketAddress(requestedPort));
            synchronized (this) {
                if (!running) {
                    closeServer(localServer);
                    return;
                }
                serverSocket = localServer;
                boundPort = localServer.getLocalPort();
                notifyAll();
            }
            notifyState("LISTENING", listeningDetail(boundPort));
            acceptClients(localServer);
        } catch (IOException error) {
            if (running) {
                notifyState("ERROR", errorDetail(error));
            }
        } finally {
            closeClient(currentClient());
            closeServer(localServer);
            synchronized (this) {
                activeClient = null;
                serverSocket = null;
                running = false;
                worker = null;
                notifyAll();
            }
        }
    }

    private void acceptClients(ServerSocket localServer) throws IOException {
        while (running) {
            Socket client = localServer.accept();
            synchronized (this) {
                if (!running) {
                    closeClient(client);
                    return;
                }
                activeClient = client;
            }
            try {
                handleClient(client);
            } catch (IOException error) {
                if (running) {
                    notifyState("ERROR", errorDetail(error));
                }
            } finally {
                closeClient(client);
                synchronized (this) {
                    if (activeClient == client) {
                        activeClient = null;
                    }
                }
            }
            if (running) {
                notifyState("LISTENING", listeningDetail(getPort()));
            }
        }
    }

    private void handleClient(Socket client) throws IOException {
        client.setSoTimeout(CLIENT_TIMEOUT_MILLIS);
        String clientAddress = client.getInetAddress().getHostAddress();
        notifyState("CONNECTED", clientAddress);

        InputStream input = client.getInputStream();
        byte[] messageBytes = new byte[MAX_MESSAGE_BYTES + 1];
        int length = 0;
        boolean terminated = false;
        while (true) {
            int value = input.read();
            if (value < 0) {
                notifyState("ERROR", "client disconnected before LF");
                return;
            }
            if (value == '\n') {
                terminated = true;
                break;
            }
            if (length == MAX_MESSAGE_BYTES) {
                if (value == '\r') {
                    int finalTerminator = input.read();
                    if (finalTerminator < 0) {
                        notifyState("ERROR", "client disconnected before LF");
                        return;
                    }
                    if (finalTerminator == '\n') {
                        terminated = true;
                        break;
                    }
                }
                writeReply(client, ERROR_TOO_LONG);
                notifyState("ERROR", "message exceeds 256 bytes");
                return;
            }
            messageBytes[length] = (byte) value;
            length++;
        }

        if (!terminated) {
            writeReply(client, ERROR_TOO_LONG);
            notifyState("ERROR", "message exceeds 256 bytes");
            return;
        }
        if (length > 0 && messageBytes[length - 1] == '\r') {
            length--;
        }
        if (length == 0) {
            writeReply(client, ERROR_EMPTY);
            notifyState("ERROR", "empty message");
            return;
        }
        for (int index = 0; index < length; index++) {
            int value = messageBytes[index] & 0xff;
            if (value < 32 || value > 126) {
                writeReply(client, ERROR_INVALID);
                notifyState("ERROR", "message is not printable ASCII");
                return;
            }
        }

        String message = new String(messageBytes, 0, length, "US-ASCII");
        int count;
        synchronized (this) {
            receivedCount++;
            count = receivedCount;
        }
        listener.onMessage(clientAddress, message, count);
        writeReply(client, ACKNOWLEDGEMENT);
    }

    private static void writeReply(Socket client, String reply) throws IOException {
        OutputStream output = client.getOutputStream();
        output.write(reply.getBytes("US-ASCII"));
        output.flush();
    }

    public void stop() {
        Socket client;
        ServerSocket server;
        synchronized (this) {
            running = false;
            client = activeClient;
            server = serverSocket;
            notifyAll();
        }
        closeClient(client);
        closeServer(server);
    }

    public boolean awaitListening(long timeoutMillis) throws InterruptedException {
        long deadline = System.currentTimeMillis() + timeoutMillis;
        synchronized (this) {
            while (boundPort < 0 && worker != null && running) {
                long remaining = deadline - System.currentTimeMillis();
                if (remaining <= 0) {
                    break;
                }
                wait(remaining);
            }
            return boundPort >= 0 && running;
        }
    }

    public boolean awaitStopped(long timeoutMillis) throws InterruptedException {
        Thread currentWorker;
        synchronized (this) {
            currentWorker = worker;
        }
        if (currentWorker != null) {
            currentWorker.join(timeoutMillis);
            return !currentWorker.isAlive();
        }
        return true;
    }

    public synchronized int getPort() {
        return boundPort;
    }

    private synchronized Socket currentClient() {
        return activeClient;
    }

    private void notifyState(String state, String detail) {
        listener.onState(state, limit(detail));
    }

    private static String listeningDetail(int port) {
        String address = "unavailable";
        try {
            address = InetAddress.getLocalHost().getHostAddress();
        } catch (IOException ignored) {
            // Address discovery is diagnostic; listening can still succeed.
        }
        return "port=" + port + " address=" + address;
    }

    private static String errorDetail(IOException error) {
        String message = error.getMessage();
        if (message == null || message.length() == 0) {
            return error.getClass().getName();
        }
        return error.getClass().getName() + ": " + message;
    }

    private static String limit(String value) {
        if (value == null) {
            return "unavailable";
        }
        if (value.length() > MAX_DETAIL_CHARS) {
            return value.substring(0, MAX_DETAIL_CHARS);
        }
        return value;
    }

    private static void closeClient(Socket client) {
        if (client == null) {
            return;
        }
        try {
            client.close();
        } catch (IOException ignored) {
            // Shutdown is already in progress; there is no recovery action.
        }
    }

    private static void closeServer(ServerSocket server) {
        if (server == null) {
            return;
        }
        try {
            server.close();
        } catch (IOException ignored) {
            // Shutdown is already in progress; there is no recovery action.
        }
    }
}
