package com.sun.lwuit;

import com.sun.lwuit.layouts.Layout;

public abstract class Container extends Component {
    public void addComponent(Object constraint, Component component) {
        Display.requireSerialThread();
    }

    public void setLayout(Layout layout) {
        Display.requireSerialThread();
    }
}
