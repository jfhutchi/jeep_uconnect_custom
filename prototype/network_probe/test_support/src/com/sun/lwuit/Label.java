package com.sun.lwuit;

public class Label extends Component {
    private static final Object GATE = new Object();
    private static int mutationCount;
    private static boolean blockNextMutation;
    private static boolean blockedMutationEntered;
    private static boolean releaseBlockedMutation;
    private String text;

    public Label(String value) {
        setText(value);
    }

    public void setText(String value) {
        Display.requireSerialThread();
        synchronized (GATE) {
            if (blockNextMutation) {
                blockNextMutation = false;
                blockedMutationEntered = true;
                GATE.notifyAll();
                while (!releaseBlockedMutation) {
                    try {
                        GATE.wait();
                    } catch (InterruptedException error) {
                        Thread.currentThread().interrupt();
                        throw new AssertionError("label mutation interrupted");
                    }
                }
            }
        }
        text = value;
        mutationCount++;
    }

    public String getText() {
        return text;
    }

    public static int getMutationCount() {
        return mutationCount;
    }

    public static void blockNextMutation() {
        synchronized (GATE) {
            blockNextMutation = true;
            blockedMutationEntered = false;
            releaseBlockedMutation = false;
        }
    }

    public static boolean awaitBlockedMutation(long timeoutMillis)
            throws InterruptedException {
        long deadline = System.currentTimeMillis() + timeoutMillis;
        synchronized (GATE) {
            while (!blockedMutationEntered) {
                long remaining = deadline - System.currentTimeMillis();
                if (remaining <= 0) {
                    return false;
                }
                GATE.wait(remaining);
            }
            return true;
        }
    }

    public static void releaseBlockedMutation() {
        synchronized (GATE) {
            releaseBlockedMutation = true;
            GATE.notifyAll();
        }
    }

    public static void reset() {
        mutationCount = 0;
        synchronized (GATE) {
            blockNextMutation = false;
            blockedMutationEntered = false;
            releaseBlockedMutation = true;
            GATE.notifyAll();
        }
    }
}
