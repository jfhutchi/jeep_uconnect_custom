import test from 'node:test';
import assert from 'node:assert/strict';
import { Shell, SCREENS } from '../model.mjs';
import { MockAdapter } from '../mock-adapter.mjs';

function setup() {
  const adapter = new MockAdapter();
  const shell = new Shell();
  shell.receive(adapter.snapshot(), 0);
  shell.resume(0);
  return { shell, adapter };
}

test('six routes are explicit; unknown routes are rejected', () => {
  const { shell } = setup();
  assert.deepEqual(SCREENS, ['Home', 'Media', 'Climate', 'Controls', 'Phone', 'Settings']);
  for (const screen of SCREENS) { shell.navigate(screen); assert.equal(shell.screen, screen); }
  assert.throws(() => shell.navigate('CAN'), /screen/);
});

test('intent does not change observed state before service acknowledgment', () => {
  const { shell, adapter } = setup();
  const old = shell.state.climate.driverC;
  const intent = shell.request('climate.driverC', 23, 0);
  assert.equal(shell.state.climate.driverC, old);
  assert.equal(shell.pending.id, intent.id);
  shell.reply(adapter.send(intent), 100);
  assert.equal(shell.state.climate.driverC, 23);
  assert.equal(shell.pending, null);
});

test('allowlist, range, types and capability checks fail closed', () => {
  const { shell, adapter } = setup();
  for (const [path, value] of [['raw.can', 1], ['climate.driverC', 99],
    ['climate.fan', 1.5], ['media.playing', 'yes'], ['comfort.wheel', 1]]) {
    assert.throws(() => shell.request(path, value, 0));
  }
  const state = adapter.snapshot(); state.capabilities.comfort = false;
  shell.receive(state, 1);
  assert.throws(() => shell.request('comfort.wheel', true, 1), /unavailable/);
});

test('camera preemption cancels intent and requires explicit return', () => {
  const { shell, adapter } = setup();
  const intent = shell.request('media.playing', true, 0);
  shell.receive(adapter.scenario('camera'), 50);
  assert.equal(shell.mode, 'camera');
  assert.equal(shell.pending, null);
  assert.throws(() => shell.request('media.playing', true, 50), /unavailable/);
  assert.equal(shell.reply(adapter.send(intent), 60), false);
  shell.receive(adapter.scenario('normal'), 100);
  assert.equal(shell.mode, 'stock');
  shell.resume(100);
  assert.equal(shell.mode, 'app');
});

test('manual fallback, disconnect and stale data never auto-resume', () => {
  const { shell, adapter } = setup();
  shell.fallback('manual');
  assert.throws(() => shell.request('media.playing', true, 0));
  shell.resume(0);
  shell.receive(adapter.scenario('offline'), 10);
  assert.equal(shell.mode, 'stock');
  assert.throws(() => shell.resume(10));
  shell.receive(adapter.scenario('normal'), 20);
  assert.equal(shell.mode, 'stock');
  shell.resume(20);
  shell.tick(2021);
  assert.equal(shell.mode, 'stock');
  assert.throws(() => shell.request('media.playing', true, 2021));
});

test('timeout, rejection and duplicate/late replies do not change state', () => {
  const { shell, adapter } = setup();
  let intent = shell.request('media.playing', true, 0);
  assert.throws(() => shell.request('media.playing', false, 0), /pending/);
  shell.tick(1001);
  assert.equal(shell.pending, null);
  assert.equal(shell.reply(adapter.send(intent), 1002), false);
  assert.equal(shell.state.media.playing, false);
  intent = shell.request('media.playing', true, 1100);
  shell.reply({ id: intent.id, status: 'rejected' }, 1101);
  assert.equal(shell.state.media.playing, false);
  assert.match(shell.notice, /rejected/);
});

test('malformed snapshots and out-of-order snapshots cannot enable actions', () => {
  const { shell, adapter } = setup();
  const old = adapter.snapshot();
  shell.receive(old, 1);
  assert.equal(shell.receive(old, 2), false);
  const bad = adapter.snapshot(); bad.climate.driverC = NaN;
  assert.throws(() => shell.receive(bad, 3), /snapshot/);
  assert.equal(shell.mode, 'stock');
  assert.throws(() => shell.resume(3));
});

test('snapshots are copied and time must be monotonic', () => {
  const { shell, adapter } = setup();
  const state = adapter.snapshot(); shell.receive(state, 10);
  state.climate.driverC = 30;
  assert.notEqual(shell.state.climate.driverC, 30);
  assert.throws(() => shell.tick(9), /time/);
});

test('every supported command is reflected by a newer mock snapshot', () => {
  const { shell, adapter } = setup();
  for (const [path, value] of [['climate.passengerC', 24], ['climate.fan', 5],
    ['climate.auto', false], ['comfort.driverSeat', 2], ['comfort.passengerSeat', 1],
    ['comfort.wheel', true], ['media.playing', true]]) {
    const intent = shell.request(path, value, 0);
    assert.equal(shell.reply(adapter.send(intent), 0), true);
    const [group, field] = path.split('.');
    assert.equal(shell.state[group][field], value);
  }
});

test('a late heartbeat cannot refresh away a stale interval', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.snapshot(), 5000);
  assert.equal(shell.mode, 'stock');
  assert.equal(shell.available('media', 5000), false);
  shell.resume(5000);
  assert.equal(shell.mode, 'app');
});
