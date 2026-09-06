import test from 'node:test';
import assert from 'node:assert/strict';
import { FOREGROUND, Shell } from '../model.mjs';
import { MockAdapter } from '../mock-adapter.mjs';
import { applyScenario } from '../controller.mjs';

test('scenario controller applies a newer copied snapshot', () => {
  const shell = new Shell();
  const adapter = new MockAdapter();
  shell.receive(adapter.snapshot(), 0);
  assert.equal(applyScenario(shell, adapter, 'carplay', 1), true);
  assert.equal(shell.foreground, FOREGROUND.PROJECTION);
});

test('scenario controller rejects unknown mock input', () => {
  const shell = new Shell();
  const adapter = new MockAdapter();
  shell.receive(adapter.snapshot(), 0);
  assert.throws(() => applyScenario(shell, adapter, 'write-can', 1), /scenario/);
});
