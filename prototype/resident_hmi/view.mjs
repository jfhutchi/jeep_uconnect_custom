import { FOREGROUND, OVERLAY, PLATFORM, SESSION } from './model.mjs';

const escape = value => String(value).replace(/[&<>"']/g, char =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);

const yesNo = value => value ? 'allowed' : 'suppressed';

export function render(shell, now) {
  const state = shell.state;
  const projection = state?.projection;
  const policy = shell.nativePresentation();
  const platform = projection?.platform === PLATFORM.CARPLAY ? 'CarPlay'
    : projection?.platform === PLATFORM.ANDROID_AUTO ? 'Android Auto' : 'No device';

  let body;
  if (shell.foreground === FOREGROUND.TAKEOVER) {
    const camera = state?.camera;
    body = `<section class="handover"><p class="eyebrow">HIGHEST STOCK PRIORITY</p>
      <h1>${camera ? 'Factory camera takeover' : 'Critical stock takeover'}</h1>
      <p>Projection remains a background session when safe. The takeover owns
      foreground until the stock layer clears.</p></section>`;
  } else if (shell.foreground === FOREGROUND.PROJECTION) {
    body = `<section class="projection"><p class="eyebrow">FULL 640 x 480 APPLICATION</p>
      <h1>${escape(platform)} projection</h1>
      <p>This placeholder represents the phone-owned video surface. It does not
      implement or imitate a projection engine.</p>
      <button class="accent" data-return-uconnect>Return to Uconnect</button></section>`;
  } else {
    const resume = shell.projectionActive()
      ? `<button class="accent" data-show-projection>Return to ${escape(platform)}</button>` : '';
    body = `<section class="uconnect"><p class="eyebrow">ORDINARY FOREGROUND OWNER</p>
      <h1>Factory Uconnect</h1>
      <p>Radio, Media, Climate, Controls, Phone, Messaging and Settings remain
      stock-owned. This bench does not reproduce those screens.</p>${resume}</section>`;
  }

  const overlay = shell.foreground !== FOREGROUND.TAKEOVER
    && shell.overlay === OVERLAY.COMFORT
    ? `<section class="comfort-overlay"><strong>Stock comfort overlay</strong>
      <span>Temporary; underlying foreground and projection session preserved</span></section>`
    : '';

  const session = projection?.session ?? SESSION.DISCONNECTED;
  return `<header><div class="brand">TRAIL<span> / PROJECTION ARBITER</span></div>
      <span class="pill">PC MOCK</span></header>
    <main>${body}${overlay}</main>
    <div class="status" role="status">${escape(shell.notice)}</div>
    <footer class="ownership">
      <span>SESSION <strong>${escape(session)}</strong></span>
      <span>FOREGROUND <strong>${escape(shell.foreground)}</strong></span>
      <span>CALL UI <strong>${yesNo(policy.incomingCallForeground)}</strong></span>
      <span>SMS/TTS <strong>${yesNo(policy.messageTts)}</strong></span>
    </footer>`;
}
