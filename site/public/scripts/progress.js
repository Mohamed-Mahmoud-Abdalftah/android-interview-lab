const STORAGE_KEY = 'android-academy-progress-v1';
const BASE = new URL('../', import.meta.url).pathname;

function emptyState() {
  return { version: 1, completed: {}, currentLesson: null, bookmarks: {}, notes: {} };
}

function readState() {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
    if (!value || value.version !== 1 || typeof value.completed !== 'object') return emptyState();
    return { ...emptyState(), ...value };
  } catch { return emptyState(); }
}

function writeState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  window.dispatchEvent(new CustomEvent('academy-progress-change', { detail: state }));
}

class AcademyProgress extends HTMLElement {
  connectedCallback() {
    this.render();
    window.addEventListener('academy-progress-change', () => this.render());
  }
  render() {
    const id = this.getAttribute('lesson-id');
    const title = this.getAttribute('lesson-title') || id;
    const state = readState();
    const done = Boolean(state.completed[id]);
    this.innerHTML = `<div class="progress-control"><div><strong>${done ? 'اتراجع واتسجل' : 'جاهز للمذاكرة'}</strong><div><bdi>${id}</bdi> — ${title}</div></div><button class="academy-button small" type="button" aria-pressed="${done}">${done ? 'علّمه غير مكتمل' : 'علّم الدرس مكتمل'}</button></div>`;
    this.querySelector('button').addEventListener('click', () => {
      const next = readState();
      if (next.completed[id]) delete next.completed[id];
      else next.completed[id] = new Date().toISOString();
      next.currentLesson = id;
      writeState(next);
    });
  }
}

class AcademyDashboard extends HTMLElement {
  async connectedCallback() {
    const response = await fetch(`${BASE}data/academy.json`);
    this.data = await response.json();
    this.render();
    window.addEventListener('academy-progress-change', () => this.render());
  }
  render() {
    if (!this.data) return;
    const state = readState();
    const completed = Object.keys(state.completed).length;
    const ready = this.data.stats.coreReviewed + this.data.stats.specialists;
    const percent = ready ? Math.round((completed / ready) * 100) : 0;
    const current = this.data.lessons.find((lesson) => lesson.id === state.currentLesson && lesson.route)
      ?? this.data.lessons.find((lesson) => lesson.route && !state.completed[lesson.id]);
    this.innerHTML = `<section class="tool-panel" aria-labelledby="local-progress-title"><h2 id="local-progress-title">تقدمك المحلي</h2><p>اتعملت <strong>${completed}</strong> من ${ready} وحدة متاحة. البيانات محفوظة في المتصفح ده بس.</p><div class="progress-meter" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${percent}"><span style="inline-size:${percent}%"></span></div><p>${current ? `<a class="academy-button small" href="${BASE}${current.route.replace(/^\//, '')}">كمّل: <bdi>${current.id}</bdi></a>` : 'كل الوحدات المتاحة متعلمة كمكتملة.'}</p><div class="tool-row"><button type="button" data-export>تصدير JSON</button><label class="academy-button small secondary">استيراد JSON<input hidden type="file" accept="application/json" data-import></label><button type="button" data-mode>تبديل Learning / Practice</button></div><p class="mode-label"></p></section>`;
    this.querySelector('[data-export]').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(readState(), null, 2)], { type: 'application/json' });
      const link = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: 'android-academy-progress.json' });
      link.click(); URL.revokeObjectURL(link.href);
    });
    this.querySelector('[data-import]').addEventListener('change', async (event) => {
      try {
        const value = JSON.parse(await event.target.files[0].text());
        if (value.version !== 1 || !value.completed || typeof value.completed !== 'object') throw new Error('invalid');
        writeState({ ...emptyState(), ...value });
      } catch { alert('ملف التقدم غير صالح أو إصداره غير مدعوم.'); }
    });
    this.querySelector('[data-mode]').addEventListener('click', () => {
      const practice = document.documentElement.dataset.studyMode !== 'practice';
      document.documentElement.dataset.studyMode = practice ? 'practice' : 'learning';
      localStorage.setItem('android-academy-study-mode', practice ? 'practice' : 'learning');
      this.updateMode();
    });
    this.updateMode();
  }
  updateMode() {
    const mode = localStorage.getItem('android-academy-study-mode') || 'learning';
    document.documentElement.dataset.studyMode = mode;
    const label = this.querySelector('.mode-label');
    if (label) label.textContent = mode === 'practice' ? 'Practice Mode: الإجابات بتظهر باختيارك.' : 'Learning Mode: الإجابات متاحة مباشرة.';
  }
}

customElements.define('academy-progress', AcademyProgress);
customElements.define('academy-dashboard', AcademyDashboard);
document.documentElement.dataset.studyMode = localStorage.getItem('android-academy-study-mode') || 'learning';
