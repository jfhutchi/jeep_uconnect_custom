package com.sun.lwuit;

public final class Display {
    private Display() {
    }

    public static native void init(Object container);

    public static native Display getInstance();

    public native void callSerially(Runnable runnable);
}
