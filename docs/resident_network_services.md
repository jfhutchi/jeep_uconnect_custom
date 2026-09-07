# Resident network and IPC services

Static network/API presence is not proof of bind, registration, execution, production enablement, or reachability.

| Component | Endpoint | Classification | Behavior | Unknowns |
|---|---|---|---|---|
| Tweddle SocketCommandSource | 127.0.0.1:11111/TCP | PROVED | Recovered one-line-per-connection JSON test-command listener with single-threaded blocking accept and LF-terminated non-null replies. | target bind success; effective Java socket permission; port availability; off-unit forwarding |
| Kona AppManagerImpl | SvcIPC com.harman.service.AppManager | PROVED | Permission-checked Java proxy submits install, uninstall, start, pause, stop, query, and chain operations to the resident native AppManager service. | live service registration; caller principal and effective policy; operation completion |
| Native AppManager AMS adapter | SvcIPC com.aicas.xlet.manager.AMS | PROVED | Recovered native request construction delegates authenticated package inspection and Xlet lifecycle operations to secure AMS. | live request outcome; AMS internal registry reconciliation |
| swdlMediaDetect external-installer path | SvcIPC com.harman.service.SoftwareInstaller | PROVED | Authenticated installer-media script registers the software-installer service and waits for AMS before staged package inspection/install. | external application-media manifest sample; live service registration |
| KIM3 Application Manager catalog client | configured remote downloadUrl/hu-url | STRONGLY INFERRED | Catalog metadata supplies a download URL; the resident client stages bytes, validates expected CRC32, and hands the file to native AppManager for separate secure validation. | production endpoint value; server authorization; live download; complete catalog response sample |

**UNKNOWN** Unless a row explicitly supplies dynamic evidence, listener execution and external reachability remain unknown.
