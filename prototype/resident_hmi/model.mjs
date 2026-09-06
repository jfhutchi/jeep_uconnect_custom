// PC reference semantics only: no network, filesystem, radio or vehicle transport.
export const FRESH_MS = 2000;
export const SESSION = Object.freeze({
  DISCONNECTED: 'disconnected', CONNECTED: 'connected', ACTIVE: 'active',
});
export const FOREGROUND = Object.freeze({
  UCONNECT: 'uconnect', PROJECTION: 'projection', TAKEOVER: 'takeover',
});
export const OVERLAY = Object.freeze({ NONE: 'none', COMFORT: 'comfort' });
export const PLATFORM = Object.freeze({ CARPLAY: 'carplay', ANDROID_AUTO: 'android_auto' });

const bool = value => typeof value === 'boolean';
const platform = value => value === null || Object.values(PLATFORM).includes(value);

function validSnapshot(state) {
  if (!state || state.version !== 2 || !Number.isSafeInteger(state.sequence)
      || state.sequence < 0 || !bool(state.serviceConnected)
      || !bool(state.camera) || !bool(state.critical)
      || !bool(state.comfortOverlay)) return false;
  const projection = state.projection;
  if (!projection || !Object.values(SESSION).includes(projection.session)
      || !platform(projection.platform) || !bool(projection.autoShow)
      || !bool(projection.callActive) || !bool(projection.messagePending)) return false;
  if (projection.session === SESSION.DISCONNECTED && projection.platform !== null) return false;
  if (projection.session !== SESSION.DISCONNECTED && projection.platform === null) return false;
  return !(state.camera && state.critical);
}

export class Shell {
  constructor() {
    this.foreground = FOREGROUND.UCONNECT;
    this.overlay = OVERLAY.NONE;
    this.preemptedForeground = FOREGROUND.UCONNECT;
    this.state = null;
    this.notice = 'Stock Uconnect foreground; projection disconnected';
    this.lastReceived = -Infinity;
    this.lastNow = -Infinity;
  }

  time(now) {
    if (!Number.isFinite(now) || now < this.lastNow) throw new Error('Non-monotonic time');
    this.lastNow = now;
  }

  fresh(now) {
    return Boolean(this.state?.serviceConnected && now >= this.lastReceived
      && now - this.lastReceived <= FRESH_MS);
  }

  projectionActive() {
    return this.state?.projection.session === SESSION.ACTIVE;
  }

  interactionOwner() {
    return this.projectionActive() ? 'projection' : 'uconnect';
  }

  nativePresentation() {
    const allowed = !this.projectionActive();
    return Object.freeze({
      owner: allowed ? 'uconnect' : 'projection',
      incomingCallForeground: allowed,
      messageForeground: allowed,
      messageTts: allowed,
    });
  }

  fallback(reason) {
    this.foreground = FOREGROUND.UCONNECT;
    this.overlay = OVERLAY.NONE;
    this.preemptedForeground = FOREGROUND.UCONNECT;
    this.notice = `Stock Uconnect foreground: ${reason}`;
  }

  returnToUconnect() {
    if (this.foreground === FOREGROUND.TAKEOVER) {
      throw new Error('Critical stock takeover owns foreground');
    }
    this.foreground = FOREGROUND.UCONNECT;
    this.notice = this.projectionActive()
      ? 'Stock Uconnect foreground; projection session remains active'
      : 'Stock Uconnect foreground';
  }

  showProjection(now) {
    this.time(now);
    if (!this.fresh(now)) throw new Error('Projection state unavailable');
    if (this.foreground === FOREGROUND.TAKEOVER) {
      throw new Error('Critical stock takeover owns foreground');
    }
    if (!this.projectionActive()) throw new Error('No active projection session');
    this.foreground = FOREGROUND.PROJECTION;
    this.notice = 'Existing projection session foregrounded; no reconnect';
  }

  receive(state, now) {
    this.tick(now);
    if (!validSnapshot(state)) {
      this.lastReceived = -Infinity;
      this.fallback('invalid service snapshot');
      throw new Error('Invalid snapshot');
    }
    if (this.state && state.sequence <= this.state.sequence) return false;

    const priorActive = this.projectionActive();
    const wasTakeover = this.foreground === FOREGROUND.TAKEOVER;
    this.state = JSON.parse(JSON.stringify(state));
    this.lastReceived = now;

    if (!state.serviceConnected) {
      this.fallback('integration service disconnected');
      return true;
    }

    const takeover = state.camera || state.critical;
    if (takeover) {
      if (!wasTakeover) this.preemptedForeground = this.foreground;
      this.foreground = FOREGROUND.TAKEOVER;
      this.overlay = OVERLAY.NONE;
      this.notice = state.camera ? 'Factory camera takeover' : 'Critical stock takeover';
      return true;
    }

    this.overlay = state.comfortOverlay ? OVERLAY.COMFORT : OVERLAY.NONE;
    if (wasTakeover) {
      const resumeProjection = this.preemptedForeground === FOREGROUND.PROJECTION
        && this.projectionActive();
      this.foreground = resumeProjection ? FOREGROUND.PROJECTION : FOREGROUND.UCONNECT;
      this.preemptedForeground = FOREGROUND.UCONNECT;
      this.notice = resumeProjection
        ? 'Projection restored after stock takeover'
        : 'Stock Uconnect restored after takeover';
    } else if (this.foreground === FOREGROUND.PROJECTION && !this.projectionActive()) {
      this.fallback('projection session ended');
    } else if (!priorActive && this.projectionActive() && state.projection.autoShow) {
      this.foreground = FOREGROUND.PROJECTION;
      this.notice = 'Projection session active and auto-shown';
    } else if (this.overlay === OVERLAY.COMFORT) {
      this.notice = 'Permitted stock comfort overlay';
    }
    return true;
  }

  tick(now) {
    this.time(now);
    if (this.state && !this.fresh(now)) this.fallback('stale integration state');
  }
}
