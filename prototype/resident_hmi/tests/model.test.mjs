import test from 'node:test';
import assert from 'node:assert/strict';
import { FOREGROUND, OVERLAY, SESSION, Shell } from '../model.mjs';
import { MockAdapter } from '../mock-adapter.mjs';

function setup() {
  const adapter = new MockAdapter();
  const shell = new Shell();
  shell.receive(adapter.snapshot(), 0);
  return { shell, adapter };
}

test('active projection auto-shows and owns native interaction presentation', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('carplay'), 1);
  assert.equal(shell.foreground, FOREGROUND.PROJECTION);
  assert.equal(shell.projectionActive(), true);
  assert.deepEqual(shell.nativePresentation(), {
    owner: 'projection', incomingCallForeground: false,
    messageForeground: false, messageTts: false,
  });
});

test('return to Uconnect preserves session ownership and resume does not reconnect', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('carplay'), 1);
  const sequence = shell.state.sequence;
  shell.returnToUconnect();
  assert.equal(shell.foreground, FOREGROUND.UCONNECT);
  assert.equal(shell.state.projection.session, SESSION.ACTIVE);
  assert.equal(shell.nativePresentation().incomingCallForeground, false);
  shell.receive(adapter.scenario('normal'), 2);
  assert.equal(shell.foreground, FOREGROUND.UCONNECT);
  assert.ok(shell.state.sequence > sequence);
  const heartbeatSequence = shell.state.sequence;
  shell.showProjection(3);
  assert.equal(shell.foreground, FOREGROUND.PROJECTION);
  assert.equal(shell.state.sequence, heartbeatSequence);
  assert.match(shell.notice, /no reconnect/);
});

test('camera restores the preempted projection session through ownership state', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('carplay'), 1);
  shell.receive(adapter.scenario('camera'), 2);
  assert.equal(shell.foreground, FOREGROUND.TAKEOVER);
  assert.throws(() => shell.showProjection(2), /takeover/);
  shell.receive(adapter.scenario('normal'), 3);
  assert.equal(shell.foreground, FOREGROUND.PROJECTION);
  assert.equal(shell.projectionActive(), true);
});

test('camera returns to Uconnect when Uconnect was foreground', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('carplay'), 1);
  shell.returnToUconnect();
  shell.receive(adapter.scenario('camera'), 2);
  shell.receive(adapter.scenario('normal'), 3);
  assert.equal(shell.foreground, FOREGROUND.UCONNECT);
  assert.equal(shell.projectionActive(), true);
  assert.equal(shell.interactionOwner(), 'projection');
});

test('comfort overlay preserves underlying foreground and session', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('carplay'), 1);
  shell.receive(adapter.scenario('comfort'), 2);
  assert.equal(shell.overlay, OVERLAY.COMFORT);
  assert.equal(shell.foreground, FOREGROUND.PROJECTION);
  shell.receive(adapter.scenario('normal'), 3);
  assert.equal(shell.overlay, OVERLAY.NONE);
  assert.equal(shell.foreground, FOREGROUND.PROJECTION);
});

test('projection disconnect restores native phone and message presentation', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('android'), 1);
  assert.equal(shell.foreground, FOREGROUND.PROJECTION);
  shell.receive(adapter.scenario('projection-off'), 2);
  assert.equal(shell.foreground, FOREGROUND.UCONNECT);
  assert.deepEqual(shell.nativePresentation(), {
    owner: 'uconnect', incomingCallForeground: true,
    messageForeground: true, messageTts: true,
  });
  assert.throws(() => shell.showProjection(2), /active/);
});

test('critical takeover outranks comfort and projection', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('carplay'), 1);
  shell.receive(adapter.scenario('comfort'), 2);
  shell.receive(adapter.scenario('critical'), 3);
  assert.equal(shell.foreground, FOREGROUND.TAKEOVER);
  assert.equal(shell.overlay, OVERLAY.NONE);
  assert.equal(shell.interactionOwner(), 'uconnect');
  assert.equal(shell.nativePresentation().incomingCallForeground, true);
  shell.receive(adapter.scenario('normal'), 4);
  assert.equal(shell.foreground, FOREGROUND.PROJECTION);
  assert.equal(shell.interactionOwner(), 'projection');
});

test('connected but inactive session never becomes projection foreground', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('connected'), 1);
  assert.equal(shell.foreground, FOREGROUND.UCONNECT);
  assert.equal(shell.interactionOwner(), 'uconnect');
  assert.throws(() => shell.showProjection(1), /active/);
});

test('invalid, duplicate and stale state fail toward stock Uconnect', () => {
  const { shell, adapter } = setup();
  const state = adapter.snapshot();
  shell.receive(state, 1);
  assert.equal(shell.receive(state, 2), false);
  const invalid = adapter.snapshot();
  invalid.projection.session = SESSION.ACTIVE;
  invalid.projection.platform = null;
  assert.throws(() => shell.receive(invalid, 3), /snapshot/);
  assert.equal(shell.foreground, FOREGROUND.UCONNECT);
  assert.equal(shell.state, null);
  assert.equal(shell.interactionOwner(), 'uconnect');
  assert.equal(shell.nativePresentation().messageTts, true);

  shell.receive(adapter.scenario('carplay'), 4);
  shell.tick(2005);
  assert.equal(shell.foreground, FOREGROUND.UCONNECT);
  assert.equal(shell.state, null);
  assert.equal(shell.interactionOwner(), 'uconnect');
  assert.equal(shell.nativePresentation().incomingCallForeground, true);
  assert.throws(() => shell.showProjection(2005), /unavailable/);
});

test('snapshot copies are isolated and time is monotonic', () => {
  const { shell, adapter } = setup();
  const state = adapter.scenario('carplay');
  shell.receive(state, 10);
  state.projection.session = SESSION.DISCONNECTED;
  assert.equal(shell.projectionActive(), true);
  assert.throws(() => shell.tick(9), /time/);
});
