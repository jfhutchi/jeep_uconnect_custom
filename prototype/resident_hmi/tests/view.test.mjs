import test from 'node:test';
import assert from 'node:assert/strict';
import { Shell, SCREENS } from '../model.mjs';
import { MockAdapter } from '../mock-adapter.mjs';
import { render } from '../view.mjs';

test('all six screens render navigation, mock label and fallback', () => {
  const shell = new Shell(); const adapter = new MockAdapter();
  shell.receive(adapter.snapshot(), 0); shell.resume(0);
  for (const screen of SCREENS) {
    shell.navigate(screen); const html = render(shell, 0);
    assert.match(html, /PC MOCK/);
    assert.match(html, /data-fallback/);
    const navigation = html.slice(html.indexOf('<nav'));
    assert.equal((navigation.match(/data-screen=/g) || []).length, 6);
    assert.match(html, new RegExp(`aria-current="page">${screen}`));
  }
});

test('camera and fallback replace custom actions, never imitate live video', () => {
  const shell = new Shell(); const adapter = new MockAdapter();
  shell.receive(adapter.scenario('camera'), 0);
  const camera = render(shell, 0);
  assert.match(camera, /Stock camera has priority/);
  assert.doesNotMatch(camera, /data-command|data-resume|<video/);
  shell.receive(adapter.scenario('normal'), 1);
  assert.match(render(shell, 1), /data-resume/);
  assert.doesNotMatch(render(shell, 1), /data-command/);
});

test('service text is escaped and unavailable controls disabled', () => {
  const shell = new Shell(); const adapter = new MockAdapter();
  const state = adapter.snapshot(); state.media.title = '<script>bad</script>';
  state.capabilities.media = false;
  shell.receive(state, 0); shell.resume(0); shell.navigate('Media');
  const html = render(shell, 0);
  assert.doesNotMatch(html, /<script>/);
  assert.match(html, /&lt;script&gt;/);
  assert.match(html, /data-command="media.playing"[^>]*disabled/);
});
