// The invalidation stream: one Server-Sent Events stream per case. A frame
// carries {seq, kind, case_id, ids} with opaque ids only; the client refetches the
// view it affects and never receives a payload. EventSource sends Last-Event-ID
// on reconnect, and the server answers with one "case" frame when the log moved.

export function openStream(caseId, refetch) {
  const source = new EventSource(`/api/cases/${caseId}/notices`);
  let pending = null;
  source.addEventListener("notice", () => {
    if (pending) return;
    pending = setTimeout(() => { pending = null; refetch(); }, 250);
  });
  return source;
}
