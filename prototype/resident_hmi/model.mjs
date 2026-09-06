// Reference semantics only: no browser, filesystem, network or RA4 transport.
export const SCREENS = Object.freeze(['Home', 'Media', 'Climate', 'Controls', 'Phone', 'Settings']);
export const FRESH_MS = 2000;
export const COMMAND_MS = 1000;
const integer = (low, high) => value => Number.isInteger(value) && value >= low && value <= high;
const boolean = value => typeof value === 'boolean';
export const FIELDS = Object.freeze({
  'climate.driverC': integer(16, 30), 'climate.passengerC': integer(16, 30),
  'climate.fan': integer(0, 7), 'climate.auto': boolean,
  'comfort.driverSeat': integer(0, 2), 'comfort.passengerSeat': integer(0, 2),
  'comfort.wheel': boolean, 'media.playing': boolean,
});

export function validValue(path, value) {
  return Object.hasOwn(FIELDS, path) && FIELDS[path](value);
}

function validSnapshot(state) {
  return state && state.version === 1 && Number.isSafeInteger(state.sequence) && state.sequence >= 0
    && boolean(state.connected) && boolean(state.camera)
    && ['climate', 'comfort', 'media'].every(key => boolean(state.capabilities?.[key]))
    && Object.entries(FIELDS).every(([path, valid]) => {
      const [group, field] = path.split('.'); return valid(state[group]?.[field]);
    }) && typeof state.media.title === 'string' && state.media.title.length <= 80
    && ['disconnected', 'connected'].includes(state.phone?.connection)
    && state.phone.projection === 'unavailable';
}

export class Shell {
  constructor() {
    this.screen = 'Home'; this.mode = 'stock'; this.state = null;
    this.pending = null; this.notice = 'Waiting for service state';
    this.lastReceived = -Infinity; this.lastNow = -Infinity; this.nextId = 1;
  }

  time(now) {
    if (!Number.isFinite(now) || now < this.lastNow) throw new Error('Non-monotonic time');
    this.lastNow = now;
  }

  fresh(now) {
    return Boolean(this.state?.connected && now >= this.lastReceived && now - this.lastReceived <= FRESH_MS);
  }

  available(group, now) {
    return this.mode === 'app' && this.fresh(now) && !this.state.camera
      && this.state.capabilities[group] === true;
  }

  navigate(screen) {
    if (!SCREENS.includes(screen)) throw new Error('Unknown screen');
    this.screen = screen;
  }

  fallback(reason = 'manual') {
    this.mode = this.state?.camera ? 'camera' : 'stock';
    this.pending = null; this.notice = `Stock UI requested: ${reason}`;
  }

  resume(now) {
    this.time(now);
    if (!this.fresh(now) || this.state.camera) throw new Error('Custom UI unavailable');
    this.mode = 'app'; this.notice = 'Mock services ready';
  }

  receive(state, now) {
    // Expire the previous observation before a fresh arrival can hide a gap.
    this.tick(now);
    if (!validSnapshot(state)) {
      this.lastReceived = -Infinity;
      this.fallback('invalid service snapshot');
      throw new Error('Invalid snapshot');
    }
    if (this.state && state.sequence <= this.state.sequence) return false;
    const wasCamera = this.mode === 'camera';
    this.state = JSON.parse(JSON.stringify(state)); this.lastReceived = now;
    if (state.camera) this.fallback('camera preemption');
    else if (!state.connected) this.fallback('service disconnected');
    else if (wasCamera) this.fallback('camera ended; explicit return required');
    return true;
  }

  request(path, value, now) {
    this.tick(now);
    if (!validValue(path, value)) throw new Error('Unsupported command or value');
    if (!this.available(path.split('.')[0], now)) throw new Error('Service unavailable');
    if (this.pending) throw new Error('One command already pending');
    const intent = { id: this.nextId++, path, value };
    this.pending = { ...intent, deadline: now + COMMAND_MS };
    this.notice = 'Waiting for observed service state';
    return intent;
  }

  reply(reply, now) {
    this.tick(now);
    if (!this.pending || reply?.id !== this.pending.id) return false;
    this.pending = null;
    if (reply.status !== 'applied') { this.notice = 'Service rejected command'; return false; }
    if (!this.receive(reply.snapshot, now)) { this.notice = 'Out-of-order response ignored'; return false; }
    this.notice = this.mode === 'app' ? 'Observed state updated (mock)' : this.notice;
    return true;
  }

  tick(now) {
    this.time(now);
    if (this.mode === 'app' && !this.fresh(now)) this.fallback('stale service state');
    if (this.pending && now >= this.pending.deadline) {
      this.pending = null; this.notice = 'Command timed out; no automatic retry';
    }
  }
}
