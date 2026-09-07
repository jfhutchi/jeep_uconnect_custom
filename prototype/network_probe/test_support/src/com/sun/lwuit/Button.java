package com.sun.lwuit;

import java.util.Vector;

import com.sun.lwuit.events.ActionEvent;
import com.sun.lwuit.events.ActionListener;

public class Button extends Component {
    private static final Vector BUTTONS = new Vector();
    private final String text;
    private ActionListener listener;

    public Button(String value) {
        Display.requireSerialThread();
        text = value;
        BUTTONS.addElement(this);
    }

    public void addActionListener(ActionListener value) {
        Display.requireSerialThread();
        listener = value;
    }

    public static void click(String value) {
        Display.requireSerialThread();
        for (int index = 0; index < BUTTONS.size(); index++) {
            Button button = (Button) BUTTONS.elementAt(index);
            if (button.text.equals(value) && button.listener != null) {
                button.listener.actionPerformed(new ActionEvent());
                return;
            }
        }
        throw new AssertionError("button not found: " + value);
    }

    public static void reset() {
        BUTTONS.removeAllElements();
    }
}
