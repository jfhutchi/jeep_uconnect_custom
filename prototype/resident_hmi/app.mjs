import { Shell } from './model.mjs';
import { MockAdapter } from './mock-adapter.mjs';
import { render } from './view.mjs';
import { dispatchPending } from './controller.mjs';

const shell = new Shell();
const adapter = new MockAdapter();
const root = document.querySelector('#hmi');
const now = () => performance.now();
let paused = false;
let responseMode = 'apply';
let lastHTML = '';
function paint() {
  const html = render(shell, now());
  if (html === lastHTML) return;
  const focused = document.activeElement;
  const focusKey = focused?.dataset.command || focused?.dataset.screen;
  root.innerHTML = html; lastHTML = html;
  if (focusKey) {
    const target = [...root.querySelectorAll('button')].find(button =>
      (button.dataset.command || button.dataset.screen) === focusKey);
    if (target && !target.disabled) target.focus({ preventScroll: true });
  }
}
function report(error) {
  shell.fallback('adapter/UI error');
  shell.notice = `Error: ${error.message}`;
  paint();
}

shell.receive(adapter.snapshot(), now()); shell.resume(now()); paint();
root.addEventListener('click', event => {
  const button = event.target.closest('button');
  if (!button || button.disabled) return;
  try {
    if (button.hasAttribute('data-fallback')) shell.fallback('manual');
    else if (button.hasAttribute('data-resume')) shell.resume(now());
    else if (button.dataset.screen) shell.navigate(button.dataset.screen);
    else if (button.dataset.command) {
      const intent = shell.request(button.dataset.command, JSON.parse(button.dataset.value), now());
      // This delay simulates transport; it never connects to a vehicle endpoint.
      const mode = responseMode;
      if (mode !== 'timeout') setTimeout(() => {
        try {
          dispatchPending(shell, adapter, intent, mode, now());
          paint();
        } catch (error) { report(error); }
      }, 300);
    }
    paint();
  } catch (error) { report(error); }
});

document.querySelector('#scenarios').addEventListener('click', event => {
  const name = event.target.closest('button')?.dataset.scenario;
  if (!name) return;
  paused = name === 'stale';
  if (!paused) shell.receive(adapter.scenario(name), now());
  paint();
});
document.querySelector('#response-mode').addEventListener('change', event => {
  responseMode = event.target.value;
});
const heartbeat = setInterval(() => {
  try { if (!paused) shell.receive(adapter.snapshot(), now()); shell.tick(now()); paint(); }
  catch (error) { report(error); }
}, 500);
window.addEventListener('pagehide', () => clearInterval(heartbeat));
