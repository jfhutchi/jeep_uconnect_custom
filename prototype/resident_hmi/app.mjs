import { Shell } from './model.mjs';
import { MockAdapter } from './mock-adapter.mjs';
import { applyScenario } from './controller.mjs';
import { render } from './view.mjs';

const shell = new Shell();
const adapter = new MockAdapter();
const root = document.querySelector('#hmi');
const now = () => performance.now();
let paused = false;
let lastHTML = '';

function paint() {
  const html = render(shell, now());
  if (html === lastHTML) return;
  root.innerHTML = html;
  lastHTML = html;
}

function report(error) {
  shell.fallback('adapter/UI error');
  shell.notice = `Error: ${error.message}`;
  paint();
}

shell.receive(adapter.snapshot(), now());
paint();

root.addEventListener('click', event => {
  const button = event.target.closest('button');
  if (!button) return;
  try {
    if (button.hasAttribute('data-return-uconnect')) shell.returnToUconnect();
    else if (button.hasAttribute('data-show-projection')) shell.showProjection(now());
    paint();
  } catch (error) {
    report(error);
  }
});

document.querySelector('#scenarios').addEventListener('click', event => {
  const name = event.target.closest('button')?.dataset.scenario;
  if (!name) return;
  try {
    paused = name === 'stale';
    if (!paused) applyScenario(shell, adapter, name, now());
    paint();
  } catch (error) {
    report(error);
  }
});

const heartbeat = setInterval(() => {
  try {
    if (!paused) shell.receive(adapter.snapshot(), now());
    shell.tick(now());
    paint();
  } catch (error) {
    report(error);
  }
}, 500);
window.addEventListener('pagehide', () => clearInterval(heartbeat));
