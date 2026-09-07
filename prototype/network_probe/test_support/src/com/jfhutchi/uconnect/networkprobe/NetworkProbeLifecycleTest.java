package com.jfhutchi.uconnect.networkprobe;

import java.awt.Container;

import javax.microedition.xlet.XletContext;

import com.sun.lwuit.Button;
import com.sun.lwuit.Display;
import com.sun.lwuit.Form;
import com.sun.lwuit.Label;

public final class NetworkProbeLifecycleTest {
    private static final class TestContext implements XletContext {
        private final Container container = new Container();
        private int destroyedCount;

        public ClassLoader getClassLoader() {
            return getClass().getClassLoader();
        }

        public Container getContainer() {
            return container;
        }

        public Object getXletProperty(String name) {
            return null;
        }

        public void notifyDestroyed() {
            destroyedCount++;
        }

        public void notifyPaused() {
        }

        public void resumeRequest() {
        }
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    private static void resetDoubles() {
        Display.reset();
        Label.reset();
        Form.reset();
        Button.reset();
    }

    private static Thread destroyInThread(
            final NetworkProbeXlet xlet,
            final Throwable[] failure) {
        Thread thread = new Thread(new Runnable() {
            public void run() {
                try {
                    xlet.destroyXlet(true);
                } catch (Throwable error) {
                    failure[0] = error;
                }
            }
        }, "DestroyXletTest");
        thread.start();
        return thread;
    }

    private static void requireBlocked(Thread thread, String message)
            throws InterruptedException {
        long deadline = System.currentTimeMillis() + 1000;
        while (thread.isAlive() && thread.getState() != Thread.State.BLOCKED
                && System.currentTimeMillis() < deadline) {
            Thread.sleep(1);
        }
        require(thread.getState() == Thread.State.BLOCKED, message);
    }

    private static void testQueuedCallbackIsInertAfterDestroy() throws Exception {
        resetDoubles();
        TestContext context = new TestContext();
        NetworkProbeXlet xlet = new NetworkProbeXlet(0);
        xlet.initXlet(context);
        xlet.startXlet();
        require(Display.pendingCount() == 1, "start must queue UI construction");
        Display.runNext();
        Display.runAll();

        xlet.onMessage("127.0.0.1", "HELLO FROM PHONE", 1);
        require(Display.pendingCount() == 1, "worker callback must be queued");
        int mutationsBeforeDestroy = Label.getMutationCount();
        xlet.destroyXlet(true);
        xlet.destroyXlet(true);
        Display.runAll();
        require(
            Label.getMutationCount() == mutationsBeforeDestroy,
            "queued callback mutated UI after destroy"
        );
        require(context.destroyedCount == 0, "AMS destroy must not notify itself");
    }

    private static void testStopNotifiesOnceAndDoesNotResurrect() throws Exception {
        resetDoubles();
        final TestContext context = new TestContext();
        final NetworkProbeXlet xlet = new NetworkProbeXlet(0);
        xlet.initXlet(context);
        xlet.startXlet();
        Display.runNext();
        Display.getInstance().callSerially(new Runnable() {
            public void run() {
                Button.click("Stop");
            }
        });
        Display.runAll();
        require(context.destroyedCount == 1, "Stop must notify destruction once");
        int mutationsAfterStop = Label.getMutationCount();
        xlet.onState("RECEIVED", "late callback");
        Display.runAll();
        require(
            Label.getMutationCount() == mutationsAfterStop,
            "late callback resurrected stopped UI"
        );
        xlet.destroyXlet(true);
        xlet.destroyXlet(true);
        require(context.destroyedCount == 1, "destroy must not duplicate notification");
    }

    private static void testDestroyCannotNullLabelsDuringCallback()
            throws Exception {
        resetDoubles();
        TestContext context = new TestContext();
        final NetworkProbeXlet xlet = new NetworkProbeXlet(0);
        xlet.initXlet(context);
        xlet.startXlet();
        Display.runNext();
        Display.runAll();

        xlet.onState("LISTENING", "port=0 address=127.0.0.1");
        Label.blockNextMutation();
        final Throwable[] uiFailure = new Throwable[1];
        Thread uiThread = new Thread(new Runnable() {
            public void run() {
                try {
                    Display.runNext();
                } catch (Throwable error) {
                    uiFailure[0] = error;
                }
            }
        }, "SerialUiTest");
        uiThread.start();
        require(
            Label.awaitBlockedMutation(1000),
            "UI callback did not reach guarded mutation"
        );

        Throwable[] destroyFailure = new Throwable[1];
        Thread destroyThread = destroyInThread(xlet, destroyFailure);
        requireBlocked(
            destroyThread,
            "destroy did not contend with guarded UI callback"
        );
        Label.releaseBlockedMutation();
        uiThread.join(1000);
        destroyThread.join(1000);
        require(!uiThread.isAlive(), "UI callback did not finish");
        require(!destroyThread.isAlive(), "destroy did not finish");
        require(uiFailure[0] == null, "destroy caused a UI callback failure");
        require(destroyFailure[0] == null, "destroy failed");
    }

    private static void testDestroyCannotRacePastStartGuard() throws Exception {
        resetDoubles();
        TestContext context = new TestContext();
        final NetworkProbeXlet xlet = new NetworkProbeXlet(0);
        xlet.initXlet(context);
        xlet.startXlet();
        Form.blockNextConstruction();

        final Throwable[] uiFailure = new Throwable[1];
        Thread uiThread = new Thread(new Runnable() {
            public void run() {
                try {
                    Display.runNext();
                } catch (Throwable error) {
                    uiFailure[0] = error;
                }
            }
        }, "SerialStartTest");
        uiThread.start();
        require(
            Form.awaitBlockedConstruction(1000),
            "start callback did not reach form construction"
        );

        Throwable[] destroyFailure = new Throwable[1];
        Thread destroyThread = destroyInThread(xlet, destroyFailure);
        requireBlocked(
            destroyThread,
            "destroy did not contend with guarded start callback"
        );
        Form.releaseBlockedConstruction();
        uiThread.join(1000);
        destroyThread.join(1000);
        require(!uiThread.isAlive(), "start callback did not finish");
        require(!destroyThread.isAlive(), "destroy did not finish");
        require(uiFailure[0] == null, "start/destroy race failed the UI callback");
        require(destroyFailure[0] == null, "destroy failed");
        require(Form.getShowCount() == 1, "start callback did not show one form");
    }

    public static void main(String[] args) throws Exception {
        testQueuedCallbackIsInertAfterDestroy();
        testStopNotifiesOnceAndDoesNotResurrect();
        testDestroyCannotNullLabelsDuringCallback();
        testDestroyCannotRacePastStartGuard();
        System.out.println("LIFECYCLE OK");
    }
}
