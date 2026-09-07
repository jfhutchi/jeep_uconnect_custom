package javax.microedition.xlet;

public interface Xlet {
    void initXlet(XletContext context) throws XletStateChangeException;
    void startXlet() throws XletStateChangeException;
    void pauseXlet();
    void destroyXlet(boolean unconditional) throws XletStateChangeException;
}
