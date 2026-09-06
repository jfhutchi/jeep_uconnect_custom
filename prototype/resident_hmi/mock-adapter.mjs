import { PLATFORM, SESSION } from './model.mjs';

// In-memory projection/arbitration simulation; no Harman/PPS wire implementation.
export class MockAdapter {
  constructor() {
    this.state = {
      version: 2,
      sequence: 0,
      serviceConnected: true,
      camera: false,
      critical: false,
      comfortOverlay: false,
      projection: {
        session: SESSION.DISCONNECTED,
        platform: null,
        autoShow: true,
        callActive: false,
        messagePending: false,
      },
    };
  }

  snapshot() {
    this.state.sequence += 1;
    return JSON.parse(JSON.stringify(this.state));
  }

  scenario(name) {
    const projection = this.state.projection;
    if (name === 'normal') {
      this.state.serviceConnected = true;
      this.state.camera = false;
      this.state.critical = false;
      this.state.comfortOverlay = false;
    } else if (name === 'carplay' || name === 'android') {
      this.state.serviceConnected = true;
      projection.session = SESSION.ACTIVE;
      projection.platform = name === 'carplay' ? PLATFORM.CARPLAY : PLATFORM.ANDROID_AUTO;
    } else if (name === 'connected') {
      projection.session = SESSION.CONNECTED;
      projection.platform = PLATFORM.CARPLAY;
      projection.callActive = false;
      projection.messagePending = false;
    } else if (name === 'camera') {
      this.state.camera = true;
      this.state.critical = false;
      this.state.comfortOverlay = false;
    } else if (name === 'critical') {
      this.state.critical = true;
      this.state.camera = false;
      this.state.comfortOverlay = false;
    } else if (name === 'comfort') {
      this.state.camera = false;
      this.state.critical = false;
      this.state.comfortOverlay = true;
    } else if (name === 'call' || name === 'message') {
      projection.session = SESSION.ACTIVE;
      projection.platform ??= PLATFORM.CARPLAY;
      projection.callActive = name === 'call';
      projection.messagePending = name === 'message';
    } else if (name === 'projection-off') {
      projection.session = SESSION.DISCONNECTED;
      projection.platform = null;
      projection.callActive = false;
      projection.messagePending = false;
      this.state.comfortOverlay = false;
    } else if (name === 'offline') {
      this.state.serviceConnected = false;
      this.state.camera = false;
      this.state.critical = false;
      this.state.comfortOverlay = false;
      projection.session = SESSION.DISCONNECTED;
      projection.platform = null;
      projection.callActive = false;
      projection.messagePending = false;
    } else {
      throw new Error('Unknown mock scenario');
    }
    return this.snapshot();
  }
}
