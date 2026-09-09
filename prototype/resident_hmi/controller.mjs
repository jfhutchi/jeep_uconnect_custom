// PC-only scenario boundary; the adapter never connects to a radio.
export function applyScenario(shell, adapter, name, now) {
  return shell.receive(adapter.scenario(name), now);
}
