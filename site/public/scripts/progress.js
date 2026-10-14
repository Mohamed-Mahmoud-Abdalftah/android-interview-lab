const STORAGE_KEY = 'android-academy-progress-v1';
const BASE = new URL('../', import.meta.url).pathname;

const isAr = () => document.documentElement.lang?.startsWith('ar') || location.pathname.includes('/ar/');

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
    const ar = isAr();

    const statusLabel = ar
      ? (done ? 'اتراجع واتسجل' : 'جاهز للمذاكرة')
      : (done ? 'Completed & Recorded' : 'Ready to Study');

    const buttonLabel = ar
      ? (done ? 'علّمه غير مكتمل' : 'علّم الدرس مكتمل')
      : (done ? 'Mark Incomplete' : 'Mark Complete');

    this.innerHTML = `<div class="progress-control"><div><strong>${statusLabel}</strong><div><bdi>${id}</bdi> — ${title}</div></div><button class="academy-button small" type="button" aria-pressed="${done}">${buttonLabel}</button></div>`;
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
    try {
      const response = await fetch(`${BASE}data/academy.json`);
      this.data = await response.json();
      this.render();
      window.addEventListener('academy-progress-change', () => this.render());
    } catch {
      // Offline fallback
    }
  }
  render() {
    if (!this.data) return;
    const state = readState();
    const completed = Object.keys(state.completed).length;
    const ready = this.data.stats.coreReviewed + this.data.stats.specialists;
    const percent = ready ? Math.round((completed / ready) * 100) : 0;
    const current = this.data.lessons.find((lesson) => lesson.id === state.currentLesson && lesson.route)
      ?? this.data.lessons.find((lesson) => lesson.route && !state.completed[lesson.id]);

    const ar = isAr();
    const titleText = ar ? 'تقدمك المحلي' : 'Your Local Progress';
    const progressDesc = ar
      ? `اتعملت <strong>${completed}</strong> من ${ready} وحدة متاحة. البيانات محفوظة في المتصفح ده بس.`
      : `Completed <strong>${completed}</strong> of ${ready} available units. Data is stored only in this browser.`;

    let continueBtn = '';
    if (current) {
      const currentRoute = ar && current.route ? `ar/${current.route.replace(/^\//, '')}` : current.route.replace(/^\//, '');
      const btnText = ar ? `كمّل: <bdi>${current.id}</bdi>` : `Continue: <bdi>${current.id}</bdi>`;
      continueBtn = `<a class="academy-button small" href="${BASE}${currentRoute}">${btnText}</a>`;
    } else {
      continueBtn = ar ? 'كل الوحدات المتاحة متعلمة كمكتملة.' : 'All available units are marked complete.';
    }

    const exportText = ar ? 'تصدير JSON' : 'Export JSON';
    const importText = ar ? 'استيراد JSON' : 'Import JSON';
    const modeBtnText = ar ? 'تبديل Learning / Practice' : 'Toggle Learning / Practice';

    this.innerHTML = `<section class="tool-panel" aria-labelledby="local-progress-title"><h2 id="local-progress-title">${titleText}</h2><p>${progressDesc}</p><div class="progress-meter" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${percent}"><span style="inline-size:${percent}%"></span></div><p>${continueBtn}</p><div class="tool-row"><button type="button" data-export>${exportText}</button><label class="academy-button small secondary">${importText}<input hidden type="file" accept="application/json" data-import></label><button type="button" data-mode>${modeBtnText}</button></div><p class="mode-label"></p></section>`;

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
      } catch {
        alert(ar ? 'ملف التقدم غير صالح أو إصداره غير مدعوم.' : 'Invalid or unsupported progress file.');
      }
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
    const ar = isAr();
    const mode = localStorage.getItem('android-academy-study-mode') || 'learning';
    document.documentElement.dataset.studyMode = mode;
    const label = this.querySelector('.mode-label');
    if (label) {
      if (ar) {
        label.textContent = mode === 'practice' ? 'Practice Mode: الإجابات بتظهر باختيارك.' : 'Learning Mode: الإجابات متاحة مباشرة.';
      } else {
        label.textContent = mode === 'practice' ? 'Practice Mode: Answers revealed on demand.' : 'Learning Mode: Answers visible directly.';
      }
    }
  }
}

customElements.define('academy-progress', AcademyProgress);
customElements.define('academy-dashboard', AcademyDashboard);
document.documentElement.dataset.studyMode = localStorage.getItem('android-academy-study-mode') || 'learning';
