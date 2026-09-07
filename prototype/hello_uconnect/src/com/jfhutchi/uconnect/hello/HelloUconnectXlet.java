package com.jfhutchi.uconnect.hello;

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

public final class HelloUconnectXlet implements Xlet {
    private XletContext context;
    private Form form;
    private Label counterLabel;
    private int counter;
    private boolean destroyed;

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
                if (!destroyed) {
                    showHelloForm();
                }
            }
        });
    }

    public void pauseXlet() {
        // The stock lifecycle owns pause/foreground behavior; no worker exists.
    }

    public void destroyXlet(boolean unconditional)
            throws XletStateChangeException {
        destroyed = true;
        counterLabel = null;
        form = null;
        context = null;
    }

    private void showHelloForm() {
        if (form == null) {
            form = new Form();
            com.sun.lwuit.Container content = form.getContentPane();
            content.setLayout(new BorderLayout());

            Label title = new Label("Hello Uconnect");
            counterLabel = new Label(Integer.toString(counter));
            Button increment = new Button("Increment");
            Button exit = new Button("Exit");

            increment.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent event) {
                    counter++;
                    counterLabel.setText(Integer.toString(counter));
                }
            });
            exit.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent event) {
                    destroyed = true;
                    XletContext currentContext = context;
                    if (currentContext != null) {
                        currentContext.notifyDestroyed();
                    }
                }
            });

            content.addComponent("North", title);
            content.addComponent("Center", counterLabel);
            content.addComponent("West", increment);
            content.addComponent("East", exit);
        }
        form.show();
    }
}
