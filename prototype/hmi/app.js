(() => {
  'use strict';

  class EventBus {
    constructor() {
      this.listeners = new Map();
    }

    on(eventName, handler) {
      if (!this.listeners.has(eventName)) {
        this.listeners.set(eventName, new Set());
      }
      this.listeners.get(eventName).add(handler);
      return () => this.listeners.get(eventName)?.delete(handler);
    }

    emit(eventName, payload) {
      for (const handler of this.listeners.get(eventName) ?? []) {
        handler(payload);
      }
    }
  }

  class MockVehicleService {
    constructor(bus) {
      this.bus = bus;
      this.state = {
        climate: {
          driverTemp: 72,
          passengerTemp: 72,
          fanSpeed: 3,
          auto: true,
          ac: true,
          sync: false,
          recirc: false,
          frontDefrost: false,
          rearDefrost: false,
          ventMode: 'AUTO'
        },
        comfort: {
          driverSeat: 0,
          passengerSeat: 0,
          heatedWheel: false
        },
        audio: {
          source: 'FM',
          frequency: 101.5,
          stationName: 'WK2 FM',
          presets: [88.3, 92.1, 96.9, 101.5, 104.7, 107.1]
        },
        projection: {
          platform: null,
          status: 'disconnected',
          autoShow: true
        },
        cameraActive: false,
        stockFallbackRequested: false
      };
    }

    snapshot() {
      return JSON.parse(JSON.stringify(this.state));
    }

    notify(domain) {
      this.bus.emit('vehicle:state', {
        domain,
        state: this.snapshot()
      });
    }

    adjustTemperature(zone, delta) {
      const key = zone === 'driver' ? 'driverTemp' : 'passengerTemp';
      const climate = this.state.climate;
      const next = Math.max(60, Math.min(85, climate[key] + delta));
      climate[key] = next;

      if (climate.sync && zone === 'driver') {
        climate.passengerTemp = next;
      }

      this.notify('climate');
    }

    adjustFan(delta) {
      const climate = this.state.climate;
      climate.fanSpeed = Math.max(0, Math.min(7, climate.fanSpeed + delta));
      if (delta !== 0) {
        climate.auto = false;
      }
      this.notify('climate');
    }

    toggleClimate(key) {
      const climate = this.state.climate;
      if (!(key in climate) || typeof climate[key] !== 'boolean') {
        return;
      }

      climate[key] = !climate[key];

      if (key === 'sync' && climate.sync) {
        climate.passengerTemp = climate.driverTemp;
      }

      if (key === 'auto' && climate.auto && climate.fanSpeed === 0) {
        climate.fanSpeed = 3;
      }

      this.notify('climate');
    }

    cycleSeat(zone) {
      const key = zone === 'driver' ? 'driverSeat' : 'passengerSeat';
      const current = this.state.comfort[key];
      this.state.comfort[key] = current === 0 ? 2 : current === 2 ? 1 : 0;
      this.notify('comfort');
    }

    toggleHeatedWheel() {
      this.state.comfort.heatedWheel = !this.state.comfort.heatedWheel;
      this.notify('comfort');
    }

    setAudioSource(source) {
      this.state.audio.source = source;
      this.notify('audio');
    }

    seek(delta) {
      const audio = this.state.audio;
      const raw = audio.frequency + delta;
      audio.frequency = Math.round(Math.max(87.5, Math.min(107.9, raw)) * 10) / 10;
      audio.stationName = 'Seeking demo';
      audio.source = 'FM';
      this.notify('audio');
    }

    tunePreset(frequency) {
      const audio = this.state.audio;
      audio.frequency = frequency;
      audio.stationName = frequency === 101.5 ? 'WK2 FM' : `Preset ${frequency.toFixed(1)}`;
      audio.source = 'FM';
      this.notify('audio');
    }

    connectProjection(platform) {
      if (!['android', 'carplay'].includes(platform)) {
        return;
      }

      this.state.projection.platform = platform;
      this.state.projection.status = 'connecting';
      this.notify('projection');

      window.setTimeout(() => {
        this.state.projection.status = 'active';
        this.state.audio.source = platform === 'android' ? 'Android Auto' : 'CarPlay';
        this.notify('projection');
      }, 550);
    }

    exitProjectionView() {
      if (this.state.projection.status === 'active') {
        this.state.projection.status = 'background';
        this.notify('projection');
      }
    }

    resumeProjection() {
      if (this.state.projection.platform) {
        this.state.projection.status = 'active';
        this.notify('projection');
      }
    }

    disconnectProjection() {
      this.state.projection.platform = null;
      this.state.projection.status = 'disconnected';
      this.state.audio.source = 'FM';
      this.notify('projection');
    }

    simulateCameraTakeover() {
      if (this.state.cameraActive) {
        return;
      }

      this.state.cameraActive = true;
      this.notify('camera');

      window.setTimeout(() => {
        this.state.cameraActive = false;
        this.notify('camera');
      }, 2600);
    }

    requestStockFallback() {
      this.state.stockFallbackRequested = true;
      this.notify('stockFallback');

      window.setTimeout(() => {
        this.state.stockFallbackRequested = false;
        this.notify('stockFallback');
      }, 1800);
    }
  }

  const bus = new EventBus();
  const vehicle = new MockVehicleService(bus);
  let currentView = 'home';
  let lastNonProjectionView = 'home';

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => Array.from(document.querySelectorAll(selector));

  function platformName(platform) {
    if (platform === 'android') return 'Android Auto';
    if (platform === 'carplay') return 'Apple CarPlay';
    return 'Projection';
  }

  function seatLabel(level) {
    if (level === 2) return 'HIGH';
    if (level === 1) return 'LOW';
    return 'OFF';
  }

  function setActiveButton(button, active) {
    button?.classList.toggle('active', Boolean(active));
  }

  function route(viewName) {
    if (!document.querySelector(`.view[data-view="${viewName}"]`)) {
      return;
    }

    if (currentView !== 'projection') {
      lastNonProjectionView = currentView;
    }

    currentView = viewName;
    $$('.view').forEach((view) => {
      view.classList.toggle('active', view.dataset.view === viewName);
    });

    $$('.app-bar [data-route]').forEach((button) => {
      button.classList.toggle('active', button.dataset.route === viewName);
    });

    render(vehicle.snapshot());
  }

  function renderClock() {
    const now = new Date();
    $('#clock').textContent = now.toLocaleTimeString([], {
      hour: 'numeric',
      minute: '2-digit'
    });
  }

  function render(state) {
    const { climate, comfort, audio, projection, cameraActive, stockFallbackRequested } = state;

    $('#driverTemp').textContent = `${climate.driverTemp}°`;
    $('#passengerTemp').textContent = `${climate.passengerTemp}°`;
    $('#homeDriverTemp').textContent = `${climate.driverTemp}°`;
    $('#homePassengerTemp').textContent = `${climate.passengerTemp}°`;
    $('#fanSpeed').textContent = climate.fanSpeed;
    $('#climateModeText').textContent = climate.auto ? 'AUTO' : `Fan ${climate.fanSpeed}`;
    $('#homeClimateSub').textContent = `${climate.auto ? 'AUTO' : 'MANUAL'} · Fan ${climate.fanSpeed}`;

    $$('[data-toggle]').forEach((button) => {
      setActiveButton(button, climate[button.dataset.toggle]);
    });

    $('#driverSeatState').textContent = seatLabel(comfort.driverSeat);
    $('#passengerSeatState').textContent = seatLabel(comfort.passengerSeat);
    $('#heatedWheelState').textContent = comfort.heatedWheel ? 'ON' : 'OFF';

    const driverSeatButton = $('[data-seat="driver"]');
    const passengerSeatButton = $('[data-seat="passenger"]');
    const wheelButton = $('#heatedWheel');
    setActiveButton(driverSeatButton, comfort.driverSeat > 0);
    setActiveButton(passengerSeatButton, comfort.passengerSeat > 0);
    setActiveButton(wheelButton, comfort.heatedWheel);

    const activeComfort = [];
    if (comfort.driverSeat) activeComfort.push(`Driver ${seatLabel(comfort.driverSeat)}`);
    if (comfort.passengerSeat) activeComfort.push(`Passenger ${seatLabel(comfort.passengerSeat)}`);
    if (comfort.heatedWheel) activeComfort.push('Wheel on');
    $('#homeComfortSub').textContent = activeComfort.length ? activeComfort.join(' · ') : 'All comfort systems off';

    $('#stationFrequency').textContent = audio.frequency.toFixed(1);
    $('#stationName').textContent = audio.stationName;
    $('#homeMediaTitle').textContent = audio.source === 'FM' ? `FM ${audio.frequency.toFixed(1)}` : audio.source;
    $('#homeMediaSub').textContent = audio.source === 'FM' ? audio.stationName : 'Active media source';
    $('#mediaSourceLabel').textContent = audio.source;
    $('#mediaTitle').textContent = audio.source === 'FM' ? 'Factory Radio' : audio.source;
    $('#mediaSubtitle').textContent = audio.source === 'FM' ? `${audio.frequency.toFixed(1)} · ${audio.stationName}` : 'Mock source selected';

    $$('.source-button[data-source]').forEach((button) => {
      setActiveButton(button, button.dataset.source === audio.source);
    });

    const projectionActive = projection.status === 'active';
    const projectionConnected = Boolean(projection.platform);
    const projectionName = platformName(projection.platform);

    $('#projectionBadge').classList.toggle('is-hidden', !projectionConnected);
    $('#projectionBadge').textContent = projectionConnected ? projectionName : 'Projection';
    $('#projectionStatusText').textContent = projection.status;
    $('#projectionChooser').classList.toggle('is-hidden', projectionConnected);
    $('#projectionActive').classList.toggle('is-hidden', !projectionConnected);
    $('#activeProjectionName').textContent = projectionName;

    if (projection.status === 'connecting') {
      $('#statusCenter').textContent = `Connecting ${projectionName}…`;
      $('#activeProjectionName').textContent = `Connecting ${projectionName}…`;
    } else if (projectionActive) {
      $('#statusCenter').textContent = `${projectionName} active`;
    } else if (projection.status === 'background') {
      $('#statusCenter').textContent = `${projectionName} connected`;
    } else if (stockFallbackRequested) {
      $('#statusCenter').textContent = 'Stock Uconnect fallback requested';
    } else {
      $('#statusCenter').textContent = 'Ready';
    }

    if (projectionConnected) {
      $('#homeProjectionTitle').textContent = projection.status === 'background' ? `Return to ${projectionName}` : projectionName;
      $('#homeProjectionSub').textContent = projectionActive ? 'Projection session active' : 'Device connected';
      $('#phoneStatus').textContent = projectionName;
      $('#phoneHeadline').textContent = `${projectionName} connected`;
      $('#phoneDetail').textContent = projectionActive
        ? 'Phone functions are handled by the native projection session.'
        : 'The phone remains connected. Open Projection to resume.';
    } else {
      $('#homeProjectionTitle').textContent = 'Connect a phone';
      $('#homeProjectionSub').textContent = 'Android Auto or Apple CarPlay';
      $('#phoneStatus').textContent = 'No device';
      $('#phoneHeadline').textContent = 'Pair or connect a phone';
      $('#phoneDetail').textContent = 'Projection-capable phones can launch Android Auto or CarPlay.';
    }

    $('#cameraOverlay').classList.toggle('is-hidden', !cameraActive);
  }

  function renderPresets() {
    const state = vehicle.snapshot();
    const presetRow = $('#presetRow');
    presetRow.replaceChildren();

    state.audio.presets.forEach((frequency) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = frequency.toFixed(1);
      button.classList.toggle('active', frequency === state.audio.frequency);
      button.addEventListener('click', () => {
        vehicle.tunePreset(frequency);
        renderPresets();
      });
      presetRow.appendChild(button);
    });
  }

  $$('[data-route]').forEach((button) => {
    button.addEventListener('click', () => {
      const target = button.dataset.route;
      const state = vehicle.snapshot();

      if (target === 'projection' && state.projection.status === 'background') {
        vehicle.resumeProjection();
      }

      route(target);
    });
  });

  $('#brandHome').addEventListener('click', () => route('home'));

  $$('[data-temp-zone]').forEach((button) => {
    button.addEventListener('click', () => {
      vehicle.adjustTemperature(button.dataset.tempZone, Number(button.dataset.tempDelta));
    });
  });

  $('#fanDown').addEventListener('click', () => vehicle.adjustFan(-1));
  $('#fanUp').addEventListener('click', () => vehicle.adjustFan(1));

  $$('[data-toggle]').forEach((button) => {
    button.addEventListener('click', () => vehicle.toggleClimate(button.dataset.toggle));
  });

  $$('[data-seat]').forEach((button) => {
    button.addEventListener('click', () => vehicle.cycleSeat(button.dataset.seat));
  });

  $('#heatedWheel').addEventListener('click', () => vehicle.toggleHeatedWheel());

  $$('.source-button[data-source]').forEach((button) => {
    button.addEventListener('click', () => vehicle.setAudioSource(button.dataset.source));
  });

  $('#seekDown').addEventListener('click', () => {
    vehicle.seek(-0.2);
    renderPresets();
  });

  $('#seekUp').addEventListener('click', () => {
    vehicle.seek(0.2);
    renderPresets();
  });

  $$('[data-connect-platform]').forEach((button) => {
    button.addEventListener('click', () => {
      vehicle.connectProjection(button.dataset.connectPlatform);
    });
  });

  $('#returnUconnect').addEventListener('click', () => {
    vehicle.exitProjectionView();
    route(lastNonProjectionView === 'projection' ? 'home' : lastNonProjectionView);
  });

  $('#disconnectProjection').addEventListener('click', () => vehicle.disconnectProjection());
  $('#cameraSimulation').addEventListener('click', () => vehicle.simulateCameraTakeover());
  $('#stockUiButton').addEventListener('click', () => vehicle.requestStockFallback());
  $('#stockUiSettings').addEventListener('click', () => vehicle.requestStockFallback());

  bus.on('vehicle:state', ({ domain, state }) => {
    render(state);
    if (domain === 'audio') {
      renderPresets();
    }
    if (domain === 'projection' && state.projection.status === 'active' && state.projection.autoShow) {
      route('projection');
    }
  });

  function fitDisplay() {
    const shell = $('.display-shell');
    if (window.innerWidth >= 680 && window.innerHeight >= 540) {
      shell.style.transform = '';
      return;
    }

    const scale = Math.min(window.innerWidth / 640, window.innerHeight / 480);
    shell.style.transform = `scale(${scale})`;
  }

  window.addEventListener('resize', fitDisplay);
  renderClock();
  window.setInterval(renderClock, 1000);
  renderPresets();
  render(vehicle.snapshot());
  route('home');
  fitDisplay();
})();
