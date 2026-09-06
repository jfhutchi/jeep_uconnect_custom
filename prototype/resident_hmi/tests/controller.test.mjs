import test from 'node:test';
import assert from 'node:assert/strict';
import { Shell } from '../model.mjs';
import { MockAdapter } from '../mock-adapter.mjs';
import { dispatchPending } from '../controller.mjs';

test('delayed callback expires intent before it can dispatch to adapter', () => {
  const shell = new Shell(); const adapter = new MockAdapter();
  shell.receive(adapter.snapshot(), 0); shell.resume(0);
  const intent = shell.request('media.playing', true, 0);
  assert.equal(dispatchPending(shell, adapter, intent, 'apply', 1500), false);
  assert.equal(adapter.snapshot().media.playing, false);
  assert.equal(shell.pending, null);
});

test('on-time controller dispatch updates observed state; rejection does not', () => {
  const shell = new Shell(); const adapter = new MockAdapter();
  shell.receive(adapter.snapshot(), 0); shell.resume(0);
  let intent = shell.request('media.playing', true, 0);
  assert.equal(dispatchPending(shell, adapter, intent, 'reject', 300), false);
  assert.equal(shell.state.media.playing, false);
  intent = shell.request('media.playing', true, 400);
  assert.equal(dispatchPending(shell, adapter, intent, 'apply', 700), true);
  assert.equal(shell.state.media.playing, true);
});
