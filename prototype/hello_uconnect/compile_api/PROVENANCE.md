# Compile API provenance

These files are independently authored, declaration-only compile stubs. They
are not vendor implementations, are not a Kona SDK, and must never be included
in the application JAR or a target package. Empty constructors and `native`
method declarations exist only so an ordinary Java compiler can type-check the
original source; no stub is executable as an implementation.

## Recovered signatures used by Hello

| Declaration | Existing repository evidence |
| --- | --- |
| `Xlet.initXlet(XletContext)`, `startXlet()`, `pauseXlet()`, `destroyXlet(boolean)`, with the observed state-change exception contract | `reports/ra4_resident_xlet_view_path.md` identifies the selected stock `AbstractHUXlet` lifecycle methods; `reports/ra4_ams_destroy_cleanup_contract.md` independently resolves the AMS call to `javax/microedition/xlet/Xlet.destroyXlet(Z)V`. The exact recovered interface declarations supplied for this authorized continuation are recorded in the approved design. |
| `XletContext.getContainer()Ljava/awt/Container;` and `notifyDestroyed()V` | Exact stock call descriptors and bytecode locations are in `reports/ra4_resident_xlet_view_path.md:63` and its reproducible selected-JAR command at `reports/ra4_resident_xlet_view_path.md:152`. |
| Other `XletContext` members | The recovered interface metadata supplied for this continuation establishes `getClassLoader`, `getXletProperty`, `notifyPaused` and `resumeRequest`. Hello does not reference them; they remain declarations only and therefore cannot enlarge the payload dependency surface. |
| `Display.init(Object)`, `Display.getInstance()`, `Display.callSerially(Runnable)` | Exact stock descriptors are in `reports/ra4_resident_xlet_view_path.md:63`; the selected User Guide JAR hash and path are in `reports/ra4_resident_xlet_view_path.md:31`. |
| `Form.<init>()`, `Form.getContentPane()`, `Form.show()` | The selected stock `AbstractHUXlet.access$600` calls and descriptors are summarized in `reports/ra4_resident_xlet_view_path.md:63` and reproduced by its bounded invocation-inventory command. |
| `BorderLayout.<init>()`, `Container.setLayout(Layout)`, `Container.addComponent(Object,Component)` | The same selected stock method contains these exact calls. The layout constraint strings are arguments to the proved `Object` slot, not additional vendor declarations. |
| `Label.<init>(String)`, `Button.<init>(String)`, `Button.addActionListener(ActionListener)` | The same selected stock method contains these exact calls. Its button listener establishes the stock action-event lane. |
| `ActionListener.actionPerformed(ActionEvent)` | The recovered listener interface declaration supplied for this continuation matches the selected stock button-listener type used by `addActionListener`. |
| `Label.setText(String)` | A bounded 2026-09-07 invocation inventory of the already selected User Guide JAR (SHA-256 `382026942a6cde768c4c3762497523c3300a5c3fa101d8661b2b0dfacfe3b260`) found 10 calls with descriptor `(Ljava/lang/String;)V`; for example `com/tweddle/help/ui/view/ImageMapView.selectHotspotButton` at BCI 64. |

The Java SE types (`Object`, `String`, `Integer`, `Runnable`, `ClassLoader`,
`Exception`, and `java.awt.Container`) are compiler platform types rather than
reconstructed vendor declarations. The payload validator still permits only the
exact Java SE owners and members that the compiled Hello artifact actually uses.

## Bounded reproduction

The committed `analysis_tools.jvm_call_inventory` tool can reproduce the stock
LWUIT references without extracting implementation bodies:

```powershell
$py = 'analysis_work/post_reboot_20260906/venv/Scripts/python.exe'
$jar = 'analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/079aa169-df8f-48b4-b331-4ed51dbf6b12/prog/jars/079aa169-df8f-48b4-b331-4ed51dbf6b12.jar'
& $py -m analysis_tools.jvm_call_inventory $jar --member '^com/tweddle/core/AbstractHUXlet\.class$' --owner '^javax/microedition/xlet|^java/awt/Container$|^com/sun/lwuit'
& $py -m analysis_tools.jvm_call_inventory $jar --member '.*\.class$' --owner '^com/sun/lwuit/Label$' --method '^setText$'
```
