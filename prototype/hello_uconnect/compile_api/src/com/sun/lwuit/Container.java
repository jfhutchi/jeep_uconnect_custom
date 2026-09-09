package com.sun.lwuit;

import com.sun.lwuit.layouts.Layout;

public abstract class Container extends Component {
    public native void addComponent(Object constraint, Component component);

    public native void setLayout(Layout layout);
}
