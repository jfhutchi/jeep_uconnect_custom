import { SCREENS } from './model.mjs';

const escape = value => String(value).replace(/[&<>"']/g, char =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);

export function render(shell, now) {
  const state = shell.state;
  const command = (path, value, label) => `<button data-command="${path}" data-value="${value}"
    ${!shell.available(path.split('.')[0], now) || shell.pending ? 'disabled' : ''}>${escape(label)}</button>`;
  const route = (screen, label) => `<button class="accent" data-screen="${screen}">${label}</button>`;
  const stepper = (path, value, title, low, high, suffix = '') => `<article class="panel">
    <h2>${title}</h2><div class="reading">${value}<small>${suffix}</small></div><div class="row">
    ${command(path, Math.max(low, value - 1), `- ${title}`)}
    ${command(path, Math.min(high, value + 1), `+ ${title}`)}</div></article>`;
  let body;
  if (shell.mode !== 'app') {
    body = `<section class="handover"><p class="eyebrow">PRIORITY / STOCK AUTHORITY</p>
      <h1>${shell.mode === 'camera' ? 'Stock camera has priority' : 'Stock UI requested'}</h1>
      <p>This is a PC simulation. No radio surface is controlled.<br>Factory camera and fallback remain integration gates.</p>
      ${shell.mode !== 'camera' && shell.fresh(now) ? '<button class="accent" data-resume>Resume mock shell</button>' : ''}</section>`;
  } else {
    const c = state.climate; const h = state.comfort;
    const pages = {
      Home: () => `<div class="heading"><h1>Ready for the road.</h1><span>GRAND CHEROKEE / CONCEPT</span></div>
        <div class="grid home"><article class="panel feature"><p class="eyebrow">NOW PLAYING</p>
        <h2>${escape(state.media.title)}</h2><p>${state.media.playing ? 'Playing' : 'Paused'} / Mock media service</p>
        ${route('Media', 'Open media &rarr;')}</article><article class="panel">
        <p class="eyebrow">CABIN</p><div class="reading">${c.driverC}<small> / ${c.passengerC} C</small></div>
        <p>Fan ${c.fan} / ${c.auto ? 'Auto' : 'Manual'}</p>${route('Climate', 'Adjust climate')}</article></div>`,
      Media: () => `<div class="heading"><h1>Media</h1><span>STOCK AUDIO AUTHORITY</span></div>
        <article class="panel wide"><p class="eyebrow">DEMO PLAYLIST / NO AUDIO OUTPUT</p>
        <h2>${escape(state.media.title)}</h2><p>Metadata and playback state only. No codecs or media bundled.</p>
        ${command('media.playing', !state.media.playing, state.media.playing ? 'Pause playback' : 'Play media')}</article>`,
      Climate: () => `<div class="heading"><h1>Climate</h1><span>OBSERVED MOCK VALUES / CELSIUS</span></div>
        <div class="grid climate">${stepper('climate.driverC', c.driverC, 'Driver', 16, 30, ' C')}
        ${stepper('climate.passengerC', c.passengerC, 'Passenger', 16, 30, ' C')}</div>
        <div class="climate-strip"><span>FAN ${c.fan}</span>${command('climate.fan', Math.max(0, c.fan - 1), 'Fan -')}
        ${command('climate.fan', Math.min(7, c.fan + 1), 'Fan +')}
        ${command('climate.auto', !c.auto, c.auto ? 'Auto: on' : 'Auto: off')}</div>`,
      Controls: () => `<div class="heading"><h1>Comfort</h1><span>CAPABILITY-GATED / MOCK</span></div>
        <div class="comfort-list"><article class="control-row"><h2>Driver heated seat</h2>
        ${command('comfort.driverSeat', (h.driverSeat + 1) % 3, ['Off', 'Low', 'High'][h.driverSeat])}</article>
        <article class="control-row"><h2>Passenger heated seat</h2>
        ${command('comfort.passengerSeat', (h.passengerSeat + 1) % 3, ['Off', 'Low', 'High'][h.passengerSeat])}</article>
        <article class="control-row"><h2>Heated steering wheel</h2>
        ${command('comfort.wheel', !h.wheel, h.wheel ? 'On' : 'Off')}</article></div>`,
      Phone: () => `<div class="heading"><h1>Phone</h1><span>PROJECTION DEFERRED</span></div>
        <article class="panel wide"><p class="eyebrow">MOCK PHONE / ${escape(state.phone.connection)}</p>
        <h2>Keep the connection simple.</h2><p>Calls and pairing remain stock-owned. CarPlay and Android Auto are placeholders, not implemented engines.</p>
        <span class="pill">Projection unavailable</span></article>`,
      Settings: () => `<div class="heading"><h1>System</h1><span>RESIDENT-FIRST / STOCK PRESERVED</span></div>
        <article class="panel wide"><h2>Small by design.</h2><p>640 x 480 / Six screens / No bundled assets</p>
        <p>45 MB stock reserve / 15 MB installed cap<br>Vehicle settings: read-only seam; real adapter unavailable.</p>
        <p class="muted">No changes persist after reload. This browser is PC-only.</p></article>`,
    };
    body = pages[shell.screen]();
  }
  return `<header><div class="brand">TRAIL<span> / RA4</span></div><span class="pill">PC MOCK</span>
    <button data-fallback>Stock UI</button></header><main>${body}</main>
    <div class="status" role="status">${escape(shell.notice)}</div>
    <nav aria-label="Primary">${SCREENS.map(screen => `<button data-screen="${screen}"
    ${shell.mode !== 'app' ? 'disabled' : ''} aria-current="${shell.screen === screen ? 'page' : 'false'}">${screen}</button>`).join('')}</nav>`;
}
