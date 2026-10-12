import { emptyState, isDue, KEY, loadState, localDay, saveState, scheduleReview, STATUSES, validateState } from './lab-state.mjs';

const BASE = new URL('../', import.meta.url).pathname;
const dataPromise = fetch(`${BASE}data/interview-lab.json`).then((response) => {
  if (!response.ok) throw new Error('Question index unavailable');
  return response.json();
});
if ('serviceWorker' in navigator && (location.protocol === 'https:' || ['localhost', '127.0.0.1'].includes(location.hostname))) {
  navigator.serviceWorker.register(`${BASE}sw.js`, { scope: BASE }).then(async () => {
    await navigator.serviceWorker.ready;
    if (!navigator.serviceWorker.controller) {
      await new Promise((resolve) => navigator.serviceWorker.addEventListener('controllerchange', resolve, { once: true }));
    }
    if (document.readyState !== 'complete') await new Promise((resolve) => window.addEventListener('load', resolve, { once: true }));
    await dataPromise.catch(() => {});
    const cache = await caches.open('android-interview-lab-pages-v1');
    const urls = new Set([location.href, ...performance.getEntriesByType('resource').map((entry) => entry.name)]);
    await Promise.all([...urls].filter((url) => {
      const parsed = new URL(url);
      return parsed.origin === location.origin && parsed.pathname.startsWith(BASE);
    }).map(async (url) => {
      if (await cache.match(url)) return;
      try { await fetch(url); } catch { /* The current page remains usable online. */ }
    }));
  }).catch(() => {});
}
const link = (route) => `${BASE}${route.replace(/^\//, '')}`;
const el = (tag, text = '', className = '') => {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
};
const button = (text, action) => {
  const node = el('button', text);
  node.type = 'button';
  node.addEventListener('click', action);
  return node;
};
const statusText = { unseen: 'Unseen', learning: 'Learning', practicing: 'Practicing', confident: 'Confident', mastered: 'Mastered' };
const normalize = (value) => value.toLocaleLowerCase().normalize('NFKD').replace(/[\u064b-\u065f]/g, '').replace(/[أإآ]/g, 'ا').replace(/ى/g, 'ي');

class LabQuestion extends HTMLElement {
  connectedCallback() {
    this.id = this.getAttribute('question-id');
    this.render();
    window.addEventListener('lab-state-change', () => this.render());
  }
  render() {
    const state = loadState();
    const record = state.questions[this.id] || {};
    this.replaceChildren();
    const panel = el('section', '', 'lab-tool');
    const title = el('h2', 'Your practice space');
    panel.append(title);
    const disclosure = el('p', 'Your notes and self ratings stay in this browser. No answer is scored automatically.', 'lab-muted');
    panel.append(disclosure);
    const row = el('div', '', 'lab-controls');
    const label = el('label', 'Progress: ');
    const select = document.createElement('select');
    select.setAttribute('aria-label', `Progress for ${this.id}`);
    for (const status of STATUSES) {
      const option = new Option(statusText[status], status);
      select.add(option);
    }
    select.value = record.status || 'unseen';
    select.addEventListener('change', () => { const next = loadState(); next.questions[this.id] = { ...next.questions[this.id], status: select.value }; saveState(next); });
    label.append(select);
    row.append(label);
    const bookmark = button(record.bookmarked ? 'Remove bookmark' : 'Bookmark', () => {
      const next = loadState(); next.questions[this.id] = { ...next.questions[this.id], bookmarked: !next.questions[this.id]?.bookmarked }; saveState(next);
    });
    bookmark.setAttribute('aria-pressed', String(Boolean(record.bookmarked)));
    row.append(bookmark);
    panel.append(row);
    const noteLabel = el('label', 'Private note / your answer');
    const textarea = document.createElement('textarea');
    textarea.rows = 6;
    textarea.maxLength = 10000;
    textarea.value = record.note || '';
    textarea.placeholder = 'Answer first, then compare with a reviewed explanation when one is available.';
    noteLabel.append(textarea);
    panel.append(noteLabel);
    const saveMessage = el('span', '', 'lab-muted');
    saveMessage.setAttribute('aria-live', 'polite');
    panel.append(saveMessage);
    let saveTimer;
    textarea.addEventListener('input', () => {
      clearTimeout(saveTimer);
      saveTimer = setTimeout(() => {
        const next = loadState(); next.questions[this.id] = { ...next.questions[this.id], note: textarea.value };
        saveMessage.textContent = saveState(next, false) ? 'Saved locally' : 'Could not save in this browser';
      }, 350);
    });
    const review = el('fieldset', '', 'lab-review');
    review.append(el('legend', 'Schedule a review'));
    for (const [grade, labelText] of [['again', 'Again · today'], ['hard', 'Hard'], ['good', 'Good'], ['easy', 'Easy']]) {
      review.append(button(labelText, () => { const next = loadState(); next.questions[this.id] = scheduleReview(next.questions[this.id], grade); saveState(next); }));
    }
    panel.append(review);
    const due = el('p', record.due ? `Next review: ${record.due} · ${record.reviews || 0} review(s)` : 'No review scheduled yet.', 'lab-muted');
    panel.append(due);
    this.append(panel);
  }
}

class LabDashboard extends HTMLElement {
  async connectedCallback() {
    try { this.data = (await dataPromise).questions; this.render(); window.addEventListener('lab-state-change', () => this.render()); }
    catch { this.textContent = 'Question index is unavailable. Reload when you are online.'; }
  }
  render() {
    const state = loadState();
    const values = this.data.map((q) => state.questions[q.id] || {});
    const studied = values.filter((item) => item.status && item.status !== 'unseen').length;
    const due = values.filter((item) => isDue(item)).length;
    const bookmarks = values.filter((item) => item.bookmarked).length;
    const reviewedContent = this.data.filter((q) => q.editorialStatus === 'reviewed').length;
    this.replaceChildren();
    const grid = el('div', '', 'lab-stats');
    for (const [count, label] of [[studied, 'Started'], [due, 'Due today'], [bookmarks, 'Bookmarked'], [reviewedContent, 'Reviewed answers']]) {
      const card = el('div', '', 'stat-card'); card.append(el('strong', String(count)), el('span', label)); grid.append(card);
    }
    this.append(grid);
    const resume = this.data.find((q) => !state.questions[q.id]?.status || state.questions[q.id]?.status === 'unseen');
    if (resume) {
      const start = el('a', `Continue studying · ${resume.id}`, 'academy-button small');
      start.href = link(resume.route);
      this.append(start);
    }
    const goal = el('label', 'Daily question goal: ');
    const input = document.createElement('input'); input.type = 'number'; input.min = '1'; input.max = '100'; input.value = state.dailyGoal;
    input.addEventListener('change', () => { const next = loadState(); next.dailyGoal = Math.min(100, Math.max(1, Number(input.value) || 10)); saveState(next); });
    goal.append(input); this.append(goal);
    const controls = el('div', '', 'lab-controls');
    controls.append(button('Export progress', () => {
      const blob = new Blob([JSON.stringify(loadState(), null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'android-interview-lab-progress.json'; anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    }));
    const importLabel = el('label', 'Import progress');
    const file = document.createElement('input'); file.type = 'file'; file.accept = 'application/json';
    file.addEventListener('change', async () => {
      try {
        const parsed = JSON.parse(await file.files[0].text());
        const valid = validateState(parsed, new Set(this.data.map((q) => q.id)));
        if (confirm('Replace this browser’s Interview Lab progress with the imported file?')) saveState(valid);
      } catch { alert('Invalid or unsupported progress JSON. Nothing was changed.'); }
      file.value = '';
    });
    importLabel.append(file); controls.append(importLabel);
    controls.append(button('Reset Interview Lab progress', () => { if (confirm('Delete all Interview Lab notes, bookmarks, reviews, and sessions on this browser?')) saveState(emptyState()); }));
    this.append(controls);
  }
}

class LabTopic extends HTMLElement {
  async connectedCallback() {
    try { this.data = (await dataPromise).questions.filter((q) => q.code === this.getAttribute('topic-code')); this.render(); window.addEventListener('lab-state-change', () => this.render()); }
    catch { this.textContent = 'Topic progress is unavailable while the question index cannot load.'; }
  }
  render() {
    const state = loadState();
    const started = this.data.filter((q) => state.questions[q.id]?.status && state.questions[q.id].status !== 'unseen').length;
    const mastered = this.data.filter((q) => state.questions[q.id]?.status === 'mastered').length;
    const due = this.data.filter((q) => isDue(state.questions[q.id])).length;
    const next = this.data.find((q) => !state.questions[q.id]?.status || state.questions[q.id]?.status === 'unseen') || this.data.find((q) => isDue(state.questions[q.id]));
    this.replaceChildren();
    const box = el('div', '', 'lab-topic-progress');
    box.append(el('strong', `${started}/${this.data.length} started · ${mastered} mastered · ${due} due`));
    if (next) { const anchor = el('a', `Recommended next: ${next.id}`); anchor.href = link(next.route); box.append(anchor); }
    else box.append(el('span', 'All questions started. Review due cards or rehearse senior scenarios.'));
    this.append(box);
  }
}

class LabExplorer extends HTMLElement {
  async connectedCallback() {
    try { this.data = (await dataPromise).questions; this.setup(); }
    catch { this.textContent = 'Question index is unavailable. Reload when you are online.'; }
  }
  setup() {
    this.replaceChildren();
    const controls = el('div', '', 'lab-filters');
    this.search = document.createElement('input'); this.search.type = 'search'; this.search.placeholder = 'Search ID or English question…'; this.search.setAttribute('aria-label', 'Search canonical questions');
    controls.append(this.search);
    this.topic = document.createElement('select'); this.topic.setAttribute('aria-label', 'Topic'); this.topic.add(new Option('All topics', ''));
    for (const code of [...new Set(this.data.map((q) => q.code))]) this.topic.add(new Option(`${code} — ${this.data.find((q) => q.code === code).topic}`, code));
    controls.append(this.topic);
    this.group = document.createElement('select'); this.group.setAttribute('aria-label', 'Group');
    for (const [label, value] of [['All groups', ''], ['A · Fundamentals', 'A'], ['B · Practical', 'B'], ['C · Senior', 'C']]) this.group.add(new Option(label, value));
    controls.append(this.group);
    this.phase = document.createElement('select'); this.phase.setAttribute('aria-label', 'Phase'); this.phase.add(new Option('All phases', ''));
    for (let phase = 1; phase <= 5; phase++) this.phase.add(new Option(`Phase ${phase}`, String(phase)));
    controls.append(this.phase);
    this.view = document.createElement('select'); this.view.setAttribute('aria-label', 'Progress filter');
    for (const [label, value] of [['All progress', ''], ['Bookmarked', 'bookmarked'], ['Due review', 'due'], ['Unseen', 'unseen'], ['Learning', 'learning'], ['Practicing', 'practicing'], ['Mastered', 'mastered']]) this.view.add(new Option(label, value));
    controls.append(this.view);
    this.append(controls);
    this.count = el('p', '', 'lab-muted'); this.count.setAttribute('aria-live', 'polite'); this.append(this.count);
    this.list = el('div', '', 'lab-results'); this.append(this.list);
    this.more = button('Show 50 more', () => { this.limit += 50; this.render(); }); this.append(this.more);
    this.limit = 50;
    for (const control of [this.search, this.topic, this.group, this.phase, this.view]) control.addEventListener('input', () => { this.limit = 50; this.render(); });
    window.addEventListener('lab-state-change', () => this.render());
    this.render();
  }
  render() {
    const state = loadState();
    const term = normalize(this.search.value.trim());
    const matches = this.data.filter((q) => {
      const record = state.questions[q.id] || {};
      const view = this.view.value;
      return (!term || normalize(`${q.id} ${q.question} ${q.topic} ${q.searchText || ''}`).includes(term))
        && (!this.topic.value || q.code === this.topic.value)
        && (!this.group.value || q.group === this.group.value)
        && (!this.phase.value || String(q.phase) === this.phase.value)
        && (!view || (view === 'bookmarked' ? record.bookmarked : view === 'due' ? isDue(record) : (record.status || 'unseen') === view));
    });
    this.count.textContent = `${matches.length} matching questions · ${this.data.length} total`;
    this.list.replaceChildren();
    for (const q of matches.slice(0, this.limit)) {
      const article = el('article', '', 'lab-result');
      const anchor = el('a', `${q.id} · ${q.question}`); anchor.href = link(q.route); anchor.dir = 'ltr';
      article.append(anchor, el('small', `${q.code} · ${q.group} · Phase ${q.phase} · ${q.editorialStatus === 'reviewed' ? 'reviewed answer' : 'source question'}`));
      this.list.append(article);
    }
    if (!matches.length) this.list.append(el('p', 'No matching questions. Try a broader search or clear filters.'));
    this.more.hidden = matches.length <= this.limit;
  }
}

class LabReview extends HTMLElement {
  async connectedCallback() {
    try { this.data = (await dataPromise).questions; this.render(); window.addEventListener('lab-state-change', () => this.render()); }
    catch { this.textContent = 'Question index is unavailable. Reload when you are online.'; }
  }
  render() {
    const state = loadState();
    const due = this.data.filter((q) => isDue(state.questions[q.id]));
    const newQuestions = this.data.filter((q) => !state.questions[q.id]?.reviews);
    this.replaceChildren(el('p', `${due.length} due · ${newQuestions.length} not yet reviewed. Review choices schedule local calendar days.`));
    const items = due.length ? due : newQuestions.slice(0, state.dailyGoal);
    for (const q of items.slice(0, 40)) {
      const card = el('article', '', 'lab-result');
      const anchor = el('a', `${q.id} · ${q.question}`); anchor.href = link(q.route); anchor.dir = 'ltr'; card.append(anchor);
      const actions = el('div', '', 'lab-controls');
      for (const grade of ['again', 'hard', 'good', 'easy']) actions.append(button(grade, () => { const next = loadState(); next.questions[q.id] = scheduleReview(next.questions[q.id], grade); saveState(next); }));
      card.append(actions); this.append(card);
    }
    if (!items.length) this.append(el('p', 'No reviews due. Explore the question bank to add a card.'));
  }
}

class LabPractice extends HTMLElement {
  async connectedCallback() {
    try { this.data = (await dataPromise).questions; this.render(); }
    catch { this.textContent = 'Question index is unavailable. Reload when you are online.'; }
  }
  render() {
    this.replaceChildren();
    const state = loadState();
    const session = state.activeSession;
    if (session && Array.isArray(session.ids) && session.ids.length) { this.renderSession(session); return; }
    this.append(el('p', 'Select a topic and time. The session saves locally so a reload can resume it. Ratings are your own assessment.'));
    const controls = el('div', '', 'lab-controls');
    const topic = document.createElement('select'); topic.setAttribute('aria-label', 'Interview topic'); topic.add(new Option('Mixed topics', ''));
    for (const code of [...new Set(this.data.map((q) => q.code))]) topic.add(new Option(code, code));
    controls.append(topic);
    const minutes = document.createElement('select'); minutes.setAttribute('aria-label', 'Duration');
    for (const duration of [10, 20, 30, 45]) minutes.add(new Option(`${duration} minutes`, String(duration)));
    controls.append(minutes);
    controls.append(button('Start interview', () => {
      const pool = this.data.filter((q) => !topic.value || q.code === topic.value);
      const byGroup = ['A', 'B', 'C'].flatMap((group) => pool.filter((q) => q.group === group).sort(() => Math.random() - .5).slice(0, Math.max(2, Math.ceil(Number(minutes.value) / 6))));
      const ids = [...new Set(byGroup.map((q) => q.id))].slice(0, Math.max(3, Math.ceil(Number(minutes.value) / 2)));
      const next = loadState(); next.activeSession = { ids, index: 0, startedAt: Date.now(), durationMinutes: Number(minutes.value), answers: {}, ratings: {}, revealed: false }; saveState(next); this.render();
    }));
    this.append(controls);
    const history = state.sessions.slice(-5).reverse();
    if (history.length) { this.append(el('h2', 'Recent sessions')); for (const item of history) this.append(el('p', `${item.day} · ${item.answered}/${item.total} self rated · ${item.durationMinutes} minute session`)); }
  }
  renderSession(session) {
    if (Date.now() >= session.startedAt + session.durationMinutes * 60000) { this.finish(); return; }
    const q = this.data.find((item) => item.id === session.ids[session.index]);
    if (!q) { const next = loadState(); next.activeSession = null; saveState(next); this.render(); return; }
    const title = el('h2', `Question ${session.index + 1} of ${session.ids.length} · ${q.id}`); this.append(title);
    const timer = el('p', '', 'lab-timer'); timer.setAttribute('role', 'timer'); this.append(timer);
    const tick = () => {
      const remaining = Math.max(0, session.durationMinutes * 60 - Math.floor((Date.now() - session.startedAt) / 1000));
      timer.textContent = `Time remaining: ${String(Math.floor(remaining / 60)).padStart(2, '0')}:${String(remaining % 60).padStart(2, '0')}`;
      if (!remaining) { clearInterval(this.interval); this.finish(); }
    };
    clearInterval(this.interval); tick(); this.interval = setInterval(tick, 1000);
    const prompt = el('blockquote', q.question, 'lab-prompt'); prompt.dir = 'ltr'; this.append(prompt);
    const answer = document.createElement('textarea'); answer.rows = 7; answer.value = session.answers[q.id] || ''; answer.placeholder = 'Type your own answer before revealing the source page.'; answer.setAttribute('aria-label', 'Your answer'); this.append(answer);
    answer.addEventListener('input', () => { const next = loadState(); next.activeSession.answers[q.id] = answer.value; saveState(next); });
    const actions = el('div', '', 'lab-controls');
    actions.append(button(session.revealed ? 'Hide source page' : 'Reveal source page', () => { const next = loadState(); next.activeSession.revealed = !next.activeSession.revealed; saveState(next); this.render(); }));
    if (session.revealed) {
      const source = el('p', q.editorialStatus === 'reviewed' ? 'Open the reviewed answer and compare your reasoning.' : 'This ID currently has the original question only; do not treat it as a reviewed answer.');
      const sourceLink = el('a', 'Open question page'); sourceLink.href = link(q.route); source.append(' ', sourceLink); this.append(source);
    }
    const rating = document.createElement('select'); rating.setAttribute('aria-label', 'Self rating');
    for (const [label, value] of [['No self rating', ''], ['Needs work', 'again'], ['Partial', 'hard'], ['Solid', 'good'], ['Strong', 'easy']]) rating.add(new Option(label, value));
    rating.value = session.ratings[q.id] || '';
    rating.addEventListener('change', () => { const next = loadState(); next.activeSession.ratings[q.id] = rating.value; saveState(next); });
    this.append(rating);
    actions.append(button('Previous', () => this.move(-1)), button('Next', () => this.move(1)), button('End session', () => this.finish()));
    this.append(actions);
  }
  move(delta) {
    const next = loadState(); next.activeSession.index = Math.max(0, Math.min(next.activeSession.ids.length - 1, next.activeSession.index + delta)); next.activeSession.revealed = false; saveState(next); this.render();
  }
  finish() {
    clearInterval(this.interval);
    const next = loadState(); const session = next.activeSession;
    if (!session) return;
    const recap = { day: localDay(), total: session.ids.length, answered: Object.values(session.ratings).filter(Boolean).length, durationMinutes: session.durationMinutes, ratings: session.ratings };
    next.sessions.push(recap); next.sessions = next.sessions.slice(-30); next.activeSession = null; saveState(next);
    this.render();
    const summary = el('div', '', 'lab-summary');
    summary.append(el('strong', `Session ended: ${recap.answered} of ${recap.total} questions self rated. No automatic technical score was calculated.`));
    for (const id of session.ids) {
      const item = this.data.find((q) => q.id === id);
      const row = el('p', `${id} · ${recap.ratings[id] || 'not rated'} · `);
      const anchor = el('a', 'review question'); anchor.href = link(item.route); row.append(anchor); summary.append(row);
    }
    this.prepend(summary);
  }
  disconnectedCallback() { clearInterval(this.interval); }
}

for (const [name, type] of [['lab-question', LabQuestion], ['lab-dashboard', LabDashboard], ['lab-topic', LabTopic], ['lab-explorer', LabExplorer], ['lab-review', LabReview], ['lab-practice', LabPractice]]) customElements.define(name, type);
