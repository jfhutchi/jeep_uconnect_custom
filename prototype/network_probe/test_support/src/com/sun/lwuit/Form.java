package com.sun.lwuit;

public class Form extends Container {
    private static final Object GATE = new Object();
    private static boolean blockNextConstruction;
    private static boolean blockedConstructionEntered;
    private static boolean releaseBlockedConstruction;
    private static int showCount;

    public Form() {
        Display.requireSerialThread();
        synchronized (GATE) {
            if (blockNextConstruction) {
                blockNextConstruction = false;
                blockedConstructionEntered = true;
                GATE.notifyAll();
                while (!releaseBlockedConstruction) {
                    try {
                        GATE.wait();
                    } catch (InterruptedException error) {
                        Thread.currentThread().interrupt();
                        throw new AssertionError("form construction interrupted");
                    }
                }
            }
        }
    }

    public Container getContentPane() {
        return this;
    }

    public void show() {
        Display.requireSerialThread();
        showCount++;
    }

    public static void blockNextConstruction() {
        synchronized (GATE) {
            blockNextConstruction = true;
            blockedConstructionEntered = false;
            releaseBlockedConstruction = false;
        }
    }

    public static boolean awaitBlockedConstruction(long timeoutMillis)
            throws InterruptedException {
        long deadline = System.currentTimeMillis() + timeoutMillis;
        synchronized (GATE) {
            while (!blockedConstructionEntered) {
                long remaining = deadline - System.currentTimeMillis();
                if (remaining <= 0) {
                    return false;
                }
                GATE.wait(remaining);
            }
            return true;
        }
    }

    public static void releaseBlockedConstruction() {
        synchronized (GATE) {
            releaseBlockedConstruction = true;
            GATE.notifyAll();
        }
    }

    public static int getShowCount() {
        return showCount;
    }

    public static void reset() {
        showCount = 0;
        synchronized (GATE) {
            blockNextConstruction = false;
            blockedConstructionEntered = false;
            releaseBlockedConstruction = true;
            GATE.notifyAll();
        }
    }
}
