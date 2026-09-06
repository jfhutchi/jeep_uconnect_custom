import test from 'node:test';
import assert from 'node:assert/strict';
import { Shell } from '../model.mjs';
import { MockAdapter } from '../mock-adapter.mjs';
import { render } from '../view.mjs';

function setup() {
  const shell = new Shell();
  const adapter = new MockAdapter();
  shell.receive(adapter.snapshot(), 0);
  return { shell, adapter };
}

test('ordinary foreground is explicitly stock Uconnect, not replacement screens', () => {
  const { shell } = setup();
  const html = render(shell, 0);
  assert.match(html, /Factory Uconnect/);
  assert.match(html, /Radio, Media, Climate, Controls, Phone, Messaging and Settings remain/);
  assert.doesNotMatch(html, /data-show-projection|data-return-uconnect/);
});

test('projection has explicit return and active background has resume control', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('carplay'), 1);
  let html = render(shell, 1);
  assert.match(html, /CarPlay projection/);
  assert.match(html, /data-return-uconnect/);
  assert.match(html, /CALL UI <strong>suppressed/);
  shell.returnToUconnect();
  html = render(shell, 2);
  assert.match(html, /Factory Uconnect/);
  assert.match(html, /data-show-projection/);
  assert.match(html, /Return to CarPlay/);
  assert.match(html, /SMS\/TTS <strong>suppressed/);
});

test('camera hides projection and comfort overlay preserves it', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('carplay'), 1);
  shell.receive(adapter.scenario('comfort'), 2);
  let html = render(shell, 2);
  assert.match(html, /Stock comfort overlay/);
  assert.match(html, /data-return-uconnect/);
  shell.receive(adapter.scenario('camera'), 3);
  html = render(shell, 3);
  assert.match(html, /Factory camera takeover/);
  assert.doesNotMatch(html, /Stock comfort overlay|data-show-projection|data-return-uconnect/);
  assert.doesNotMatch(html, /<video/);
});

test('projection disconnect restores native presentation labels', () => {
  const { shell, adapter } = setup();
  shell.receive(adapter.scenario('android'), 1);
  shell.receive(adapter.scenario('projection-off'), 2);
  const html = render(shell, 2);
  assert.match(html, /CALL UI <strong>allowed/);
  assert.match(html, /SMS\/TTS <strong>allowed/);
});
