// PC transport scheduling boundary: expiration must precede any dispatch.
export function dispatchPending(shell, adapter, intent, mode, now) {
  shell.tick(now);
  if (shell.pending?.id !== intent.id) return false;
  const reply = mode === 'apply' ? adapter.send(intent) : { id: intent.id, status: 'rejected' };
  return shell.reply(reply, now);
}
