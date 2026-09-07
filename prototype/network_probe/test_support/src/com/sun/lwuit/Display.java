package com.sun.lwuit;

import java.util.Vector;

public final class Display {
    private static final Display INSTANCE = new Display();
    private static final Vector QUEUE = new Vector();
    private static boolean serialThread;

    private Display() {
    }

    public static void init(Object container) {
    }

    public static Display getInstance() {
        return INSTANCE;
    }

    public void callSerially(Runnable runnable) {
        synchronized (QUEUE) {
            QUEUE.addElement(runnable);
        }
    }

    public static void runNext() {
        Runnable runnable;
        synchronized (QUEUE) {
            if (QUEUE.isEmpty()) {
                return;
            }
            runnable = (Runnable) QUEUE.remove(0);
        }
        serialThread = true;
        try {
            runnable.run();
        } finally {
            serialThread = false;
        }
    }

    public static void runAll() {
        while (pendingCount() > 0) {
            runNext();
        }
    }

    public static int pendingCount() {
        synchronized (QUEUE) {
            return QUEUE.size();
        }
    }

    public static void reset() {
        synchronized (QUEUE) {
            QUEUE.removeAllElements();
        }
        serialThread = false;
    }

    public static void requireSerialThread() {
        if (!serialThread) {
            throw new AssertionError("LWUIT mutation occurred outside serial queue");
        }
    }
}
