package com.sun.lwuit;

import com.sun.lwuit.events.ActionListener;

public class Button extends Component {
    public Button(String text) {
    }

    public native void addActionListener(ActionListener listener);
}
