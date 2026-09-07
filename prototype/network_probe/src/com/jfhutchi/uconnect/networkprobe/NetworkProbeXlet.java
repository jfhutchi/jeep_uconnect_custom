package com.jfhutchi.uconnect.networkprobe;

import java.awt.Container;

import javax.microedition.xlet.Xlet;
import javax.microedition.xlet.XletContext;
import javax.microedition.xlet.XletStateChangeException;

import com.sun.lwuit.Button;
import com.sun.lwuit.Display;
import com.sun.lwuit.Form;
import com.sun.lwuit.Label;
import com.sun.lwuit.events.ActionEvent;
import com.sun.lwuit.events.ActionListener;
import com.sun.lwuit.layouts.BorderLayout;

public final class NetworkProbeXlet implements Xlet, NetworkProbeListener {
    private static final int MAX_DETAIL_CHARS = 160;

    private final int port;
    private XletContext context;
    private NetworkProbeServer server;
    private Form form;
    private Label stateLabel;
    private Label addressLabel;
    private Label messageLabel;
    private volatile boolean destroyed;

    public NetworkProbeXlet() {
        this(NetworkProbeServer.DEFAULT_PORT);
    }

    NetworkProbeXlet(int listenPort) {
        port = listenPort;
    }

    public void initXlet(XletContext xletContext)
            throws XletStateChangeException {
        context = xletContext;
        Container root = context.getContainer();
        root.setVisible(true);
        Display.init(root);
    }

    public void startXlet() throws XletStateChangeException {
        Display.getInstance().callSerially(new Runnable() {
            public void run() {
                synchronized (NetworkProbeXlet.this) {
                    if (!destroyed) {
                        showProbeForm();
                        startServer();
                    }
                }
            }
        });
    }

    public void pauseXlet() {
        // The platform owns pause/foreground behavior; the server remains resident.
    }

    public void destroyXlet(boolean unconditional)
            throws XletStateChangeException {
        stop(false);
    }

    public void onState(final String state, final String detail) {
        if (destroyed) {
            return;
        }
        final String safeState = limit(state, 16);
        final String safeDetail = limit(detail, MAX_DETAIL_CHARS);
        Display.getInstance().callSerially(new Runnable() {
            public void run() {
                synchronized (NetworkProbeXlet.this) {
                    if (destroyed || stateLabel == null) {
                        return;
                    }
                    stateLabel.setText(
                        "State: " + safeState + " | Port: " + port
                    );
                    if ("LISTENING".equals(safeState)) {
                        addressLabel.setText(
                            "Local address: " + addressFromDetail(safeDetail)
                        );
                    } else if ("ERROR".equals(safeState)) {
                        messageLabel.setText("Error: " + safeDetail);
                    }
                }
            }
        });
    }

    public void onMessage(
            final String clientAddress,
            final String message,
            final int receivedCount) {
        if (destroyed) {
            return;
        }
        final String safeClient = limit(clientAddress, 64);
        final String safeMessage = limit(
            message, NetworkProbeServer.MAX_MESSAGE_BYTES
        );
        Display.getInstance().callSerially(new Runnable() {
            public void run() {
                synchronized (NetworkProbeXlet.this) {
                    if (destroyed || stateLabel == null) {
                        return;
                    }
                    stateLabel.setText("State: RECEIVED | Port: " + port);
                    messageLabel.setText(
                        "Last client: " + safeClient
                        + " | Last message: " + safeMessage
                        + " | Messages received: " + receivedCount
                    );
                }
            }
        });
    }

    private void showProbeForm() {
        if (form == null) {
            form = new Form();
            com.sun.lwuit.Container content = form.getContentPane();
            content.setLayout(new BorderLayout());

            Label title = new Label("Uconnect Network Probe");
            stateLabel = new Label("State: STARTING | Port: " + port);
            addressLabel = new Label("Local address: unavailable");
            messageLabel = new Label(
                "Last client: unavailable | Last message: unavailable"
                + " | Messages received: 0"
            );
            Button stopButton = new Button("Stop");
            stopButton.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent event) {
                    stop(true);
                }
            });

            content.addComponent("North", title);
            content.addComponent("Center", stateLabel);
            content.addComponent("West", addressLabel);
            content.addComponent("East", messageLabel);
            content.addComponent("South", stopButton);
        }
        form.show();
    }

    private synchronized void startServer() {
        if (destroyed || server != null) {
            return;
        }
        NetworkProbeServer newServer = new NetworkProbeServer(port, this);
        server = newServer;
        newServer.start();
    }

    private void stop(boolean notifyContext) {
        NetworkProbeServer currentServer;
        XletContext currentContext;
        synchronized (this) {
            if (destroyed) {
                return;
            }
            destroyed = true;
            currentServer = server;
            currentContext = context;
            server = null;
            context = null;
            stateLabel = null;
            addressLabel = null;
            messageLabel = null;
            form = null;
        }
        if (currentServer != null) {
            currentServer.stop();
        }
        if (notifyContext && currentContext != null) {
            currentContext.notifyDestroyed();
        }
    }

    private static String addressFromDetail(String detail) {
        String marker = "address=";
        int start = detail.indexOf(marker);
        if (start < 0) {
            return "unavailable";
        }
        String address = detail.substring(start + marker.length());
        if (address.length() == 0) {
            return "unavailable";
        }
        return limit(address, 64);
    }

    private static String limit(String value, int maximum) {
        if (value == null || value.length() == 0) {
            return "unavailable";
        }
        if (value.length() > maximum) {
            return value.substring(0, maximum);
        }
        return value;
    }
}
