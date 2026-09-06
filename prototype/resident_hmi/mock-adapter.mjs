import { validValue } from './model.mjs';

// Entirely in-memory simulation. These paths are NOT Harman or PPS wire names.
export class MockAdapter {
  constructor() {
    this.state = {
      version: 1, sequence: 0, connected: true, camera: false,
      capabilities: { climate: true, comfort: true, media: true },
      climate: { driverC: 21, passengerC: 22, fan: 3, auto: true },
      comfort: { driverSeat: 0, passengerSeat: 0, wheel: false },
      media: { title: 'Mountain roads / Demo playlist', playing: false },
      phone: { connection: 'connected', projection: 'unavailable' },
    };
  }

  snapshot() {
    this.state.sequence += 1;
    return JSON.parse(JSON.stringify(this.state));
  }

  send(intent) {
    if (!intent || !Number.isSafeInteger(intent.id) || !validValue(intent.path, intent.value)) {
      throw new Error('Invalid mock intent');
    }
    const [group, field] = intent.path.split('.');
    if (!this.state.connected || this.state.camera || !this.state.capabilities[group]) {
      return { id: intent.id, status: 'rejected' };
    }
    this.state[group][field] = intent.value;
    return { id: intent.id, status: 'applied', snapshot: this.snapshot() };
  }

  scenario(name) {
    if (!['normal', 'camera', 'offline'].includes(name)) throw new Error('Unknown mock scenario');
    this.state.camera = name === 'camera';
    this.state.connected = name !== 'offline';
    return this.snapshot();
  }
}
