package javax.microedition.xlet;

import java.awt.Container;

public interface XletContext {
    ClassLoader getClassLoader();
    Container getContainer();
    Object getXletProperty(String name);
    void notifyDestroyed();
    void notifyPaused();
    void resumeRequest();
}
