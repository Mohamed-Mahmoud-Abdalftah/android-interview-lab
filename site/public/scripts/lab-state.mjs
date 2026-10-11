export const KEY = 'android-interview-lab-v1';
export const STATUSES = ['unseen', 'learning', 'practicing', 'confident', 'mastered'];
export const GRADES = ['again', 'hard', 'good', 'easy'];

export function emptyState() {
  return { version: 1, questions: {}, dailyGoal: 10, sessions: [], activeSession: null };
}

export function localDay(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function addLocalDays(day, count) {
  const [year, month, date] = day.split('-').map(Number);
  return localDay(new Date(year, month - 1, date + count, 12));
}

export function scheduleReview(previous = {}, grade, today = localDay()) {
  if (!GRADES.includes(grade)) throw new Error('Invalid review grade');
  const priorInterval = Number.isInteger(previous.interval) ? previous.interval : 0;
  const interval = grade === 'again' ? 0
    : grade === 'hard' ? Math.max(1, Math.ceil(priorInterval * 1.2))
    : grade === 'good' ? Math.max(2, Math.ceil(priorInterval * 2.2))
    : Math.max(4, Math.ceil(priorInterval * 3));
  return {
    ...previous,
    status: grade === 'easy' && interval >= 14 ? 'mastered' : 'practicing',
    interval,
    due: addLocalDays(today, interval),
    lastReviewed: today,
    reviews: (previous.reviews || 0) + 1,
    lastGrade: grade,
  };
}

export function isDue(record, today = localDay()) {
  return Boolean(record?.due && record.due <= today);
}

export function validateState(value, validIds = null) {
  if (!value || value.version !== 1 || !value.questions || typeof value.questions !== 'object' || Array.isArray(value.questions)) throw new Error('Unsupported progress file');
  const next = emptyState();
  next.dailyGoal = Number.isInteger(value.dailyGoal) && value.dailyGoal >= 1 && value.dailyGoal <= 100 ? value.dailyGoal : 10;
  for (const [id, entry] of Object.entries(value.questions)) {
    if (!/^[A-Z]+-\d{2}$/.test(id) || (validIds && !validIds.has(id)) || !entry || typeof entry !== 'object' || Array.isArray(entry)) continue;
    next.questions[id] = {
      status: STATUSES.includes(entry.status) ? entry.status : 'unseen',
      bookmarked: entry.bookmarked === true,
      note: typeof entry.note === 'string' ? entry.note.slice(0, 10000) : '',
      interval: Number.isInteger(entry.interval) && entry.interval >= 0 ? entry.interval : 0,
      due: /^\d{4}-\d{2}-\d{2}$/.test(entry.due) ? entry.due : null,
      lastReviewed: /^\d{4}-\d{2}-\d{2}$/.test(entry.lastReviewed) ? entry.lastReviewed : null,
      reviews: Number.isInteger(entry.reviews) && entry.reviews >= 0 ? entry.reviews : 0,
      lastGrade: GRADES.includes(entry.lastGrade) ? entry.lastGrade : null,
    };
  }
  next.sessions = Array.isArray(value.sessions) ? value.sessions.filter((item) => item && typeof item === 'object' && Number.isInteger(item.total) && Number.isInteger(item.answered)).slice(-30) : [];
  const session = value.activeSession;
  if (session && typeof session === 'object' && Array.isArray(session.ids)
      && session.ids.length > 0 && session.ids.length <= 30
      && session.ids.every((id) => /^[A-Z]+-\d{2}$/.test(id) && (!validIds || validIds.has(id)))
      && Number.isInteger(session.index) && session.index >= 0 && session.index < session.ids.length
      && Number.isFinite(session.startedAt) && session.startedAt > 0
      && [10, 20, 30, 45].includes(session.durationMinutes)) {
    next.activeSession = {
      ids: session.ids,
      index: session.index,
      startedAt: session.startedAt,
      durationMinutes: session.durationMinutes,
      answers: Object.fromEntries(Object.entries(session.answers || {}).filter(([id, answer]) => session.ids.includes(id) && typeof answer === 'string').map(([id, answer]) => [id, answer.slice(0, 10000)])),
      ratings: Object.fromEntries(Object.entries(session.ratings || {}).filter(([id, grade]) => session.ids.includes(id) && GRADES.includes(grade))),
      revealed: session.revealed === true,
    };
  }
  return next;
}

export function loadState(validIds = null) {
  try { return validateState(JSON.parse(localStorage.getItem(KEY) || 'null'), validIds); }
  catch { return emptyState(); }
}

export function saveState(state, notify = true) {
  try { localStorage.setItem(KEY, JSON.stringify(state)); if (notify) window.dispatchEvent(new Event('lab-state-change')); return true; }
  catch { return false; }
}
