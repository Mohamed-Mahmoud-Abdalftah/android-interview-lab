import { emptyState, isDue, KEY, loadState, localDay, saveState, scheduleReview, STATUSES, validateState } from './lab-state.mjs';

const BASE = new URL('../', import.meta.url).pathname;
const isAr = () => document.documentElement.lang?.startsWith('ar') || location.pathname.includes('/ar/');

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

const link = (route) => {
  if (!route) return BASE;
  if (route.startsWith(BASE)) return route;
  return `${BASE}${route.replace(/^\//, '')}`;
};
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

const statusTextEn = { unseen: 'Unseen', learning: 'Learning', practicing: 'Practicing', confident: 'Confident', mastered: 'Mastered' };
const statusTextAr = { unseen: 'لم تتم رؤيته', learning: 'قيد التعلم', practicing: 'قيد التدريب', confident: 'واثق منه', mastered: 'متقن تماماً' };
const getStatusText = (status) => isAr() ? (statusTextAr[status] || status) : (statusTextEn[status] || status);

const normalize = (value) => (value || '').toLocaleLowerCase().normalize('NFKD').replace(/[\u064b-\u065f]/g, '').replace(/[أإآ]/g, 'ا').replace(/ى/g, 'ي');

const copyText = async (text, btn, originalLabel) => {
  if (!text) return;
  const ar = isAr();
  try {
    await navigator.clipboard.writeText(text);
    btn.textContent = ar ? '✓ تم النسخ!' : '✓ Copied!';
    setTimeout(() => { btn.textContent = originalLabel; }, 2000);
  } catch {
    btn.textContent = ar ? 'فشل النسخ' : 'Copy failed';
    setTimeout(() => { btn.textContent = originalLabel; }, 2000);
  }
};

const extractSectionText = (...headingIds) => {
  for (const id of headingIds) {
    const heading = document.getElementById(id);
    if (!heading) continue;
    const wrapper = heading.closest('.sl-heading-wrapper') || heading;
    let text = '';
    let sibling = wrapper.nextElementSibling;
    while (sibling && !sibling.classList.contains('sl-heading-wrapper') && !sibling.matches('h2, h3')) {
      text += sibling.textContent.trim() + '\n\n';
      sibling = sibling.nextElementSibling;
    }
    const cleaned = text.trim().replace(/^["“](.*)["”]$/s, '$1');
    if (cleaned) return cleaned;
  }
  return '';
};

const attachCodeCopy = () => {
  const ar = isAr();
  const copyLabel = ar ? 'نسخ الكود' : 'Copy code';
  const ariaLabel = ar ? 'نسخ الكود البرمجي' : 'Copy code snippet';
  document.querySelectorAll('pre').forEach((pre) => {
    if (!pre.hasAttribute('tabindex')) pre.setAttribute('tabindex', '0');
    if (pre.querySelector('.lab-code-copy-btn')) return;
    const code = pre.querySelector('code');
    if (!code) return;
    const btn = el('button', copyLabel, 'lab-code-copy-btn');
    btn.type = 'button';
    btn.setAttribute('aria-label', ariaLabel);
    btn.addEventListener('click', () => copyText(code.textContent, btn, copyLabel));
    pre.style.position = 'relative';
    pre.append(btn);
  });
};

if (typeof document !== 'undefined') {
  const initPre = () => {
    document.querySelectorAll('pre').forEach((pre) => {
      if (!pre.hasAttribute('tabindex')) pre.setAttribute('tabindex', '0');
    });
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPre);
  } else {
    initPre();
  }
}

const enhanceSpokenAnswersAndFollowups = () => {
  const ar = isAr();
  const shortH = document.getElementById('interview-answer--short') || document.getElementById('إجابة-المقابلة--ملخصة-وسريعة');
  const structH = document.getElementById('interview-answer--structured') || document.getElementById('إجابة-المقابلة--نموذجية-ومهيكلة');
  const deepH = document.getElementById('interview-answer--deep-senior') || document.getElementById('إجابة-المقابلة--مناقشة-senior-متعمقة');

  if (shortH && structH && deepH && !document.getElementById('lab-spoken-switcher')) {
    const wrap = shortH.closest('.sl-heading-wrapper') || shortH;
    const bar = el('div', '', 'lab-answer-switcher');
    bar.id = 'lab-spoken-switcher';
    bar.append(el('strong', ar ? '🎙️ إجابة المقابلة الشفهية: ' : '🎙️ Spoken Answer: ', 'lab-switcher-label'));

    const bestLabel = ar ? 'الإجابة النموذجية (60–90 ثانية) [افتراضي]' : 'Best Answer (60–90s) [Default]';
    const bBest = button(bestLabel, () => {
      structH.scrollIntoView({ behavior: 'smooth', block: 'center' });
      structH.classList.add('lab-target-highlight');
      setTimeout(() => structH.classList.remove('lab-target-highlight'), 2000);
    });
    bBest.className = 'lab-pill lab-pill-active';

    const quickLabel = ar ? '⚡ إجابة سريعة (~30 ثانية)' : '⚡ Quick (~30s)';
    const bQuick = button(quickLabel, () => {
      shortH.scrollIntoView({ behavior: 'smooth', block: 'center' });
      shortH.classList.add('lab-target-highlight');
      setTimeout(() => shortH.classList.remove('lab-target-highlight'), 2000);
    });
    bQuick.className = 'lab-pill';

    const deepLabel = ar ? '🧠 مناقشة Senior متعمقة (~2–3 دقائق)' : '🧠 Deep Senior (~2–3m)';
    const bDeep = button(deepLabel, () => {
      deepH.scrollIntoView({ behavior: 'smooth', block: 'center' });
      deepH.classList.add('lab-target-highlight');
      setTimeout(() => deepH.classList.remove('lab-target-highlight'), 2000);
    });
    bDeep.className = 'lab-pill';

    bar.append(bBest, bQuick, bDeep);
    wrap.parentNode.insertBefore(bar, wrap);
  }

  const fuH = document.getElementById('follow-up-questions') || document.getElementById('أسئلة-المتابعة-واعتراضات-المحاور');
  if (fuH && !document.getElementById('lab-fu-practice-btn')) {
    const fuWrap = fuH.closest('.sl-heading-wrapper') || fuH;
    const hideText = ar ? '🎙️ تدرّب بصوت عالٍ (إخفاء الإجابات)' : '🎙️ Practice Out Loud (Hide Answers)';
    const showText = ar ? '👁️ إظهار إجابات المرشح' : '👁️ Reveal Candidate Answers';

    const fuBtn = button(hideText, () => {
      const active = document.body.classList.toggle('lab-mask-followups');
      fuBtn.textContent = active ? showText : hideText;
      fuBtn.classList.toggle('lab-pill-active', active);
    });
    fuBtn.id = 'lab-fu-practice-btn';
    fuBtn.className = 'lab-pill';
    fuBtn.style.marginInlineStart = '0.75rem';
    fuWrap.append(fuBtn);
  }
};

class LabQuestion extends HTMLElement {
  connectedCallback() {
    this.id = this.getAttribute('question-id');
    this.revealed = false;
    this.render();
    window.addEventListener('lab-state-change', () => this.render());
    setTimeout(() => {
      attachCodeCopy();
      enhanceSpokenAnswersAndFollowups();
    }, 100);
  }
  render() {
    const ar = isAr();
    const state = loadState();
    const record = state.questions[this.id] || {};
    this.replaceChildren();

    // 1. Quick Navigation Pills
    const navPills = el('nav', '', 'lab-nav-pills');
    navPills.setAttribute('aria-label', ar ? 'الانتقال السريع لأقسام السؤال' : 'Jump to question section');

    const sections = ar ? [
      ['#ما-يقيّمه-المحاور', '📌 التقييم'],
      ['#الشرح-والمفهوم-التقني', '📖 الشرح'],
      ['#التطبيق-العملي-وسيناريو-الفشل', '💡 سيناريو'],
      ['#آلية-العمل-والتحليل-الهندسي', '⚙️ الآلية'],
      ['#مثال-تطبيقي-واختبار', '💻 كود وتطبيق'],
      ['#المفاضلات-الهندسية-ومعايير-القرار', '⚖️ المفاضلات'],
      ['#أنماط-الفشل-ومصائد-الأخطاء', '⚠️ مصائد الأخطاء'],
      ['#منظور-بيئة-العمل-الفعلي-production', '🚀 بيئة العمل'],
      ['#إجابة-المقابلة--ملخصة-وسريعة', '🎙️ إجابات المقابلة'],
      ['#طريقة-تقديم-الإجابة-في-المقابلة', '🎯 الأركان الـ 5'],
      ['.lab-tool', '✍️ مساحة التدريب'],
    ] : [
      ['#what-the-interviewer-evaluates', '📌 Evaluation'],
      ['#concept-and-technical-explanation', '📖 Explanation'],
      ['#practical-walkthrough', '💡 Walkthrough'],
      ['#why-it-matters-and-how-it-works', '⚙️ Mechanics'],
      ['#worked-example', '💻 Code Lab'],
      ['#trade-offs-and-decision-criteria', '⚖️ Trade-offs'],
      ['#failure-modes', '⚠️ Failure Modes'],
      ['#production-perspective', '🚀 Production'],
      ['#interview-answer--short', '🎙️ Spoken answers'],
      ['#how-to-answer-in-the-interview', '🎯 5 Pillars'],
      ['.lab-tool', '✍️ Practice Space'],
    ];

    for (const [target, labelText] of sections) {
      if (document.querySelector(target)) {
        const a = el('a', labelText, 'lab-pill');
        a.href = target;
        navPills.append(a);
      }
    }
    this.append(navPills);

    // 2. Active Recall Handling
    const isRecall = Boolean(record.activeRecall);
    const answerIds = [
      'interview-answer--short',
      'interview-answer--structured',
      'interview-answer--deep-senior',
      'how-to-answer-in-the-interview',
      'deep-dive-talking-points',
      'إجابة-المقابلة--ملخصة-وسريعة',
      'إجابة-المقابلة--نموذجية-ومهيكلة',
      'إجابة-المقابلة--مناقشة-senior-متعمقة',
      'طريقة-تقديم-الإجابة-في-المقابلة',
      'محاور-النقاش-المتقدم'
    ];

    answerIds.forEach((id) => {
      const h = document.getElementById(id);
      if (h) {
        const wrap = h.closest('.sl-heading-wrapper') || h;
        wrap.classList.add('lab-hidden-answer');
        let sib = wrap.nextElementSibling;
        while (sib && !sib.classList.contains('sl-heading-wrapper') && !sib.matches('h2')) {
          sib.classList.add('lab-hidden-answer');
          sib = sib.nextElementSibling;
        }
      }
    });

    const isHidden = isRecall && !this.revealed;
    document.body.classList.toggle('lab-recall-active', isHidden);

    if (isHidden) {
      const banner = el('div', '', 'lab-reveal-banner');
      banner.append(el('strong', ar ? '🎯 وضع الاسترجاع النشط' : '🎯 Active Recall Mode'));
      banner.append(el('p', ar ? 'تم إخفاء الإجابات النموذجية لتتمكن من صياغة إجابتك في مساحة التدريب أولاً.' : 'Spoken answers are hidden so you can formulate your response in the practice space first.', 'lab-muted'));
      const revealBtn = button(ar ? '👁️ كشف الإجابات النموذجية' : '👁️ Reveal Model Answers', () => {
        this.revealed = true;
        this.render();
      });
      revealBtn.className = 'academy-button';
      banner.append(revealBtn);
      this.append(banner);
    }

    // 3. Practice Panel
    const panel = el('section', '', 'lab-tool');
    const title = el('h2', ar ? 'مساحة التدريب الخاصة بك' : 'Your practice space');
    panel.append(title);
    const disclosure = el('p', ar ? 'ملاحظاتك وتقييماتك الذاتية محفوظة محلياً في هذا المتصفح. لا يتم تقييم أي إجابة تلقائياً.' : 'Your notes and self ratings stay in this browser. No answer is scored automatically.', 'lab-muted');
    panel.append(disclosure);

    // Mode Bar
    const modeBar = el('div', '', 'lab-mode-bar');
    const modeText = ar
      ? (isRecall ? 'الوضع: استرجاع نشط (إجابات مخفية)' : 'الوضع: قراءة كاملة (إجابات ظاهرة)')
      : (isRecall ? 'Mode: Active Recall (hidden answers)' : 'Mode: Full Reading (answers visible)');
    const modeLabel = el('span', modeText, 'lab-muted');

    const toggleText = ar
      ? (isRecall ? 'التبديل إلى وضع القراءة الكاملة' : 'التبديل إلى وضع الاسترجاع النشط')
      : (isRecall ? 'Switch to Full Study Mode' : 'Switch to Active Recall Mode');

    const toggleBtn = button(toggleText, () => {
      const next = loadState();
      next.questions[this.id] = { ...next.questions[this.id], activeRecall: !isRecall };
      this.revealed = false;
      saveState(next);
    });
    toggleBtn.className = 'lab-mode-btn';
    modeBar.append(modeLabel, toggleBtn);
    panel.append(modeBar);

    // Copy Answers Bar
    const copyBar = el('div', '', 'lab-copy-actions');
    const copy30Label = ar ? 'نسخ إجابة 30 ثانية' : 'Copy 30s Answer';
    const copy30 = button(copy30Label, () => copyText(extractSectionText('interview-answer--short', 'إجابة-المقابلة--ملخصة-وسريعة'), copy30, copy30Label));
    copy30.className = 'lab-copy-btn';

    const copy90Label = ar ? 'نسخ إجابة 90 ثانية مهيكلة' : 'Copy 90s Structured';
    const copy90 = button(copy90Label, () => copyText(extractSectionText('interview-answer--structured', 'إجابة-المقابلة--نموذجية-ومهيكلة'), copy90, copy90Label));
    copy90.className = 'lab-copy-btn';

    const copySeniorLabel = ar ? 'نسخ إجابة Senior متعمقة' : 'Copy Deep Senior';
    const copySenior = button(copySeniorLabel, () => copyText(extractSectionText('interview-answer--deep-senior', 'إجابة-المقابلة--مناقشة-senior-متعمقة'), copySenior, copySeniorLabel));
    copySenior.className = 'lab-copy-btn';

    copyBar.append(copy30, copy90, copySenior);
    panel.append(copyBar);

    const row = el('div', '', 'lab-controls');
    const label = el('label', ar ? 'التقدم: ' : 'Progress: ');
    const select = document.createElement('select');
    select.setAttribute('aria-label', `${ar ? 'تقدم السؤال' : 'Progress for'} ${this.id}`);
    for (const status of STATUSES) {
      const option = new Option(getStatusText(status), status);
      select.add(option);
    }
    select.value = record.status || 'unseen';
    select.addEventListener('change', () => {
      const next = loadState();
      next.questions[this.id] = { ...next.questions[this.id], status: select.value };
      saveState(next);
    });
    label.append(select);
    row.append(label);

    const bookmarkLabel = record.bookmarked
      ? (ar ? 'إزالة من المفضلة' : 'Remove bookmark')
      : (ar ? 'حفظ في المفضلة' : 'Bookmark');

    const bookmark = button(bookmarkLabel, () => {
      const next = loadState();
      next.questions[this.id] = { ...next.questions[this.id], bookmarked: !next.questions[this.id]?.bookmarked };
      saveState(next);
    });
    bookmark.setAttribute('aria-pressed', String(Boolean(record.bookmarked)));
    row.append(bookmark);
    panel.append(row);

    const noteLabel = el('label', ar ? 'ملاحظة خاصة / إجابتك الشخصية' : 'Private note / your answer');
    const textarea = document.createElement('textarea');
    textarea.rows = 6;
    textarea.maxLength = 10000;
    textarea.value = record.note || '';
    textarea.placeholder = ar
      ? 'أجب بنفسك أولاً، ثم قارن مع الشرح والإجابة المعتمدة.'
      : 'Answer first, then compare with a reviewed explanation when one is available.';
    noteLabel.append(textarea);
    panel.append(noteLabel);

    const saveMessage = el('span', '', 'lab-muted');
    saveMessage.setAttribute('aria-live', 'polite');
    panel.append(saveMessage);

    let saveTimer;
    textarea.addEventListener('input', () => {
      clearTimeout(saveTimer);
      saveTimer = setTimeout(() => {
        const next = loadState();
        next.questions[this.id] = { ...next.questions[this.id], note: textarea.value };
        const saved = saveState(next, false);
        saveMessage.textContent = ar
          ? (saved ? 'تم الحفظ محلياً' : 'تعذر الحفظ في هذا المتصفح')
          : (saved ? 'Saved locally' : 'Could not save in this browser');
      }, 350);
    });

    const review = el('fieldset', '', 'lab-review');
    review.append(el('legend', ar ? 'جدولة المراجعة المتباعدة' : 'Schedule a review'));

    const reviewGrades = ar
      ? [['again', 'إعادة · اليوم'], ['hard', 'صعب'], ['good', 'جيد'], ['easy', 'سهل']]
      : [['again', 'Again · today'], ['hard', 'Hard'], ['good', 'Good'], ['easy', 'Easy']];

    for (const [grade, labelText] of reviewGrades) {
      review.append(button(labelText, () => {
        const next = loadState();
        next.questions[this.id] = scheduleReview(next.questions[this.id], grade);
        saveState(next);
      }));
    }
    panel.append(review);

    const dueText = record.due
      ? (ar ? `المراجعة القادمة: ${record.due} · ${record.reviews || 0} مراجعة` : `Next review: ${record.due} · ${record.reviews || 0} review(s)`)
      : (ar ? 'لم تتم جدولة مراجعة بعد.' : 'No review scheduled yet.');
    const due = el('p', dueText, 'lab-muted');
    panel.append(due);
    this.append(panel);
  }
}

class LabDashboard extends HTMLElement {
  async connectedCallback() {
    try {
      this.data = (await dataPromise).questions;
      this.render();
      window.addEventListener('lab-state-change', () => this.render());
    } catch {
      this.textContent = isAr()
        ? 'فهرس الأسئلة غير متاح حالياً. أعد التحميل عند الاتصال بالإنترنت.'
        : 'Question index is unavailable. Reload when you are online.';
    }
  }
  render() {
    const ar = isAr();
    const state = loadState();
    const values = this.data.map((q) => state.questions[q.id] || {});
    const studied = values.filter((item) => item.status && item.status !== 'unseen').length;
    const due = values.filter((item) => isDue(item)).length;
    const bookmarks = values.filter((item) => item.bookmarked).length;
    const reviewedContent = this.data.filter((q) => q.editorialStatus === 'reviewed').length;
    this.replaceChildren();

    const grid = el('div', '', 'lab-stats');
    const statCards = ar
      ? [[studied, 'تم البدء'], [due, 'مستحقة اليوم'], [bookmarks, 'في المفضلة'], [reviewedContent, 'إجابات مراجعة']]
      : [[studied, 'Started'], [due, 'Due today'], [bookmarks, 'Bookmarked'], [reviewedContent, 'Reviewed answers']];

    for (const [count, label] of statCards) {
      const card = el('div', '', 'stat-card');
      card.append(el('strong', String(count)), el('span', label));
      grid.append(card);
    }
    this.append(grid);

    const resume = this.data.find((q) => !state.questions[q.id]?.status || state.questions[q.id]?.status === 'unseen');
    if (resume) {
      const continueLabel = ar ? `متابعة المذاكرة · ${resume.id}` : `Continue studying · ${resume.id}`;
      const start = el('a', continueLabel, 'academy-button small');
      start.href = link(ar && resume.routeAr ? resume.routeAr : resume.route);
      this.append(start);
    }

    const goal = el('label', ar ? 'الهدف اليومي من الأسئلة: ' : 'Daily question goal: ');
    const input = document.createElement('input');
    input.type = 'number';
    input.min = '1';
    input.max = '100';
    input.value = state.dailyGoal;
    input.addEventListener('change', () => {
      const next = loadState();
      next.dailyGoal = Math.min(100, Math.max(1, Number(input.value) || 10));
      saveState(next);
    });
    goal.append(input);
    this.append(goal);

    const controls = el('div', '', 'lab-controls');
    controls.append(button(ar ? 'تصدير التقدم' : 'Export progress', () => {
      const blob = new Blob([JSON.stringify(loadState(), null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'android-interview-lab-progress.json';
      anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }));

    const importLabel = el('label', ar ? 'استيراد التقدم' : 'Import progress');
    const file = document.createElement('input');
    file.type = 'file';
    file.accept = 'application/json';
    file.addEventListener('change', async () => {
      try {
        const parsed = JSON.parse(await file.files[0].text());
        const valid = validateState(parsed, new Set(this.data.map((q) => q.id)));
        const confirmMsg = ar
          ? 'استبدال تقدم المختبر في هذا المتصفح بملف التقدم المستورد؟'
          : 'Replace this browser’s Interview Lab progress with the imported file?';
        if (confirm(confirmMsg)) saveState(valid);
      } catch {
        alert(ar ? 'ملف التقدم غير صالح أو غير مدعوم. لم يتم تغيير أي شيء.' : 'Invalid or unsupported progress JSON. Nothing was changed.');
      }
      file.value = '';
    });
    importLabel.append(file);
    controls.append(importLabel);

    controls.append(button(ar ? 'إعادة ضبط تقدم المختبر' : 'Reset Interview Lab progress', () => {
      const resetMsg = ar
        ? 'حذف كافة الملاحظات والمفضلات وجلسات المراجعة من هذا المتصفح نهائياً؟'
        : 'Delete all Interview Lab notes, bookmarks, reviews, and sessions on this browser?';
      if (confirm(resetMsg)) saveState(emptyState());
    }));
    this.append(controls);
  }
}

class LabTopic extends HTMLElement {
  async connectedCallback() {
    try {
      this.data = (await dataPromise).questions.filter((q) => q.code === this.getAttribute('topic-code'));
      this.render();
      window.addEventListener('lab-state-change', () => this.render());
    } catch {
      this.textContent = isAr()
        ? 'تقدم الموضوع غير متاح أثناء تعذر تحميل الفهرس.'
        : 'Topic progress is unavailable while the question index cannot load.';
    }
  }
  render() {
    const ar = isAr();
    const state = loadState();
    const started = this.data.filter((q) => state.questions[q.id]?.status && state.questions[q.id].status !== 'unseen').length;
    const mastered = this.data.filter((q) => state.questions[q.id]?.status === 'mastered').length;
    const due = this.data.filter((q) => isDue(state.questions[q.id])).length;
    const next = this.data.find((q) => !state.questions[q.id]?.status || state.questions[q.id]?.status === 'unseen') || this.data.find((q) => isDue(state.questions[q.id]));
    this.replaceChildren();

    const box = el('div', '', 'lab-topic-progress');
    const summaryText = ar
      ? `${started}/${this.data.length} تم البدء · ${mastered} متقن · ${due} مستحقة`
      : `${started}/${this.data.length} started · ${mastered} mastered · ${due} due`;
    box.append(el('strong', summaryText));

    if (next) {
      const nextLabel = ar ? `الموصى به تالياً: ${next.id}` : `Recommended next: ${next.id}`;
      const anchor = el('a', nextLabel);
      anchor.href = link(ar && next.routeAr ? next.routeAr : next.route);
      box.append(anchor);
    } else {
      box.append(el('span', ar
        ? 'تم البدء في كافة الأسئلة. راجع البطاقات المستحقة أو تدرّب على سيناريوهات الـ Senior.'
        : 'All questions started. Review due cards or rehearse senior scenarios.'));
    }
    this.append(box);
  }
}

class LabExplorer extends HTMLElement {
  async connectedCallback() {
    try {
      this.data = (await dataPromise).questions;
      this.setup();
    } catch {
      this.textContent = isAr()
        ? 'فهرس الأسئلة غير متاح حالياً. أعد التحميل عند الاتصال بالإنترنت.'
        : 'Question index is unavailable. Reload when you are online.';
    }
  }
  setup() {
    const ar = isAr();
    this.replaceChildren();
    const controls = el('div', '', 'lab-filters');

    this.search = document.createElement('input');
    this.search.type = 'search';
    this.search.placeholder = ar ? 'ابحث برمز السؤال، الموضوع، أو كلمة تقنية…' : 'Search ID, topic, or keyword…';
    this.search.setAttribute('aria-label', ar ? 'البحث في الأسئلة المعتمدة' : 'Search canonical questions');
    controls.append(this.search);

    this.topic = document.createElement('select');
    this.topic.setAttribute('aria-label', ar ? 'الموضوع' : 'Topic');
    this.topic.add(new Option(ar ? 'جميع المواضيع' : 'All topics', ''));

    const topicCodes = [...new Set(this.data.map((q) => q.code))];
    for (const code of topicCodes) {
      const first = this.data.find((q) => q.code === code);
      const name = ar ? (first.topicAr || first.topic) : first.topic;
      this.topic.add(new Option(`${code} — ${name}`, code));
    }
    controls.append(this.topic);

    this.group = document.createElement('select');
    this.group.setAttribute('aria-label', ar ? 'المجموعة' : 'Group');
    const groupOptions = ar
      ? [['جميع المجموعات', ''], ['A · الأساسيات', 'A'], ['B · التطبيق العملي', 'B'], ['C · سيناريوهات Senior', 'C']]
      : [['All groups', ''], ['A · Fundamentals', 'A'], ['B · Practical', 'B'], ['C · Senior', 'C']];
    for (const [label, value] of groupOptions) this.group.add(new Option(label, value));
    controls.append(this.group);

    this.phase = document.createElement('select');
    this.phase.setAttribute('aria-label', ar ? 'المرحلة' : 'Phase');
    this.phase.add(new Option(ar ? 'جميع المراحل' : 'All phases', ''));
    for (let phase = 1; phase <= 5; phase++) {
      this.phase.add(new Option(ar ? `المرحلة ${phase}` : `Phase ${phase}`, String(phase)));
    }
    controls.append(this.phase);

    this.view = document.createElement('select');
    this.view.setAttribute('aria-label', ar ? 'فلتر التقدم' : 'Progress filter');
    const viewOptions = ar
      ? [['كل الحالات', ''], ['في المفضلة', 'bookmarked'], ['مستحقة للمراجعة', 'due'], ['لم تتم رؤيته', 'unseen'], ['قيد التعلم', 'learning'], ['قيد التدريب', 'practicing'], ['متقن تماماً', 'mastered']]
      : [['All progress', ''], ['Bookmarked', 'bookmarked'], ['Due review', 'due'], ['Unseen', 'unseen'], ['Learning', 'learning'], ['Practicing', 'practicing'], ['Mastered', 'mastered']];
    for (const [label, value] of viewOptions) this.view.add(new Option(label, value));
    controls.append(this.view);

    this.append(controls);

    this.count = el('p', '', 'lab-muted');
    this.count.setAttribute('aria-live', 'polite');
    this.append(this.count);

    this.list = el('div', '', 'lab-results');
    this.append(this.list);

    this.more = button(ar ? 'عرض 50 سؤالاً إضافياً' : 'Show 50 more', () => {
      this.limit += 50;
      this.render();
    });
    this.append(this.more);

    this.limit = 50;
    for (const control of [this.search, this.topic, this.group, this.phase, this.view]) {
      control.addEventListener('input', () => {
        this.limit = 50;
        this.render();
      });
    }
    window.addEventListener('lab-state-change', () => this.render());
    this.render();
  }
  render() {
    const ar = isAr();
    const state = loadState();
    const term = normalize(this.search.value.trim());

    const matches = this.data.filter((q) => {
      const record = state.questions[q.id] || {};
      const view = this.view.value;
      const haystack = normalize(`${q.id} ${q.question} ${q.questionAr || ''} ${q.topic} ${q.topicAr || ''} ${q.searchText || ''} ${q.searchTextAr || ''}`);
      return (!term || haystack.includes(term))
        && (!this.topic.value || q.code === this.topic.value)
        && (!this.group.value || q.group === this.group.value)
        && (!this.phase.value || String(q.phase) === this.phase.value)
        && (!view || (view === 'bookmarked' ? record.bookmarked : view === 'due' ? isDue(record) : (record.status || 'unseen') === view));
    });

    this.count.textContent = ar
      ? `${matches.length} سؤال مطابق · ${this.data.length} إجمالي الأسئلة`
      : `${matches.length} matching questions · ${this.data.length} total`;

    this.list.replaceChildren();
    for (const q of matches.slice(0, this.limit)) {
      const article = el('article', '', 'lab-result');
      const qText = ar ? (q.questionAr || q.question) : q.question;
      const qRoute = ar && q.routeAr ? q.routeAr : q.route;

      const anchor = el('a', `${q.id} · ${qText}`);
      anchor.href = link(qRoute);
      if (!ar) anchor.dir = 'ltr';

      const badge = ar
        ? `${q.code} · ${q.group} · المرحلة ${q.phase} · إجابة معتمدة`
        : `${q.code} · ${q.group} · Phase ${q.phase} · reviewed answer`;

      article.append(anchor, el('small', badge));
      this.list.append(article);
    }

    if (!matches.length) {
      this.list.append(el('p', ar ? 'لا توجد أسئلة مطابقة. جرب بحثاً أوسع أو امسح الفلاتر.' : 'No matching questions. Try a broader search or clear filters.'));
    }
    this.more.hidden = matches.length <= this.limit;
  }
}

class LabReview extends HTMLElement {
  async connectedCallback() {
    try {
      this.data = (await dataPromise).questions;
      this.render();
      window.addEventListener('lab-state-change', () => this.render());
    } catch {
      this.textContent = isAr()
        ? 'فهرس الأسئلة غير متاح حالياً. أعد التحميل عند الاتصال بالإنترنت.'
        : 'Question index is unavailable. Reload when you are online.';
    }
  }
  render() {
    const ar = isAr();
    const state = loadState();
    const due = this.data.filter((q) => isDue(state.questions[q.id]));
    const newQuestions = this.data.filter((q) => !state.questions[q.id]?.reviews);

    const descText = ar
      ? `${due.length} مستحقة · ${newQuestions.length} لم تُراجع بعد. خيارات التقييم تجدول الأيام على تقويمك المحلي.`
      : `${due.length} due · ${newQuestions.length} not yet reviewed. Review choices schedule local calendar days.`;
    this.replaceChildren(el('p', descText));

    const items = due.length ? due : newQuestions.slice(0, state.dailyGoal);
    const gradeLabels = ar
      ? [['again', 'إعادة'], ['hard', 'صعب'], ['good', 'جيد'], ['easy', 'سهل']]
      : [['again', 'again'], ['hard', 'hard'], ['good', 'good'], ['easy', 'easy']];

    for (const q of items.slice(0, 40)) {
      const card = el('article', '', 'lab-result');
      const qText = ar ? (q.questionAr || q.question) : q.question;
      const qRoute = ar && q.routeAr ? q.routeAr : q.route;

      const anchor = el('a', `${q.id} · ${qText}`);
      anchor.href = link(qRoute);
      if (!ar) anchor.dir = 'ltr';
      card.append(anchor);

      const actions = el('div', '', 'lab-controls');
      for (const [grade, label] of gradeLabels) {
        actions.append(button(label, () => {
          const next = loadState();
          next.questions[q.id] = scheduleReview(next.questions[q.id], grade);
          saveState(next);
        }));
      }
      card.append(actions);
      this.append(card);
    }

    if (!items.length) {
      this.append(el('p', ar ? 'لا توجد مراجعات مستحقة الآن. استكشف بنك الأسئلة لإضافة بطاقات.' : 'No reviews due. Explore the question bank to add a card.'));
    }
  }
}

class LabPractice extends HTMLElement {
  async connectedCallback() {
    try {
      this.data = (await dataPromise).questions;
      this.render();
    } catch {
      this.textContent = isAr()
        ? 'فهرس الأسئلة غير متاح حالياً. أعد التحميل عند الاتصال بالإنترنت.'
        : 'Question index is unavailable. Reload when you are online.';
    }
  }
  render() {
    const ar = isAr();
    this.replaceChildren();
    const state = loadState();
    const session = state.activeSession;

    if (session && Array.isArray(session.ids) && session.ids.length) {
      this.renderSession(session);
      return;
    }

    this.append(el('p', ar
      ? 'اختر موضوعاً ومدة زمنية. يتم حفظ الجلسة محلياً لاستئنافها عند إعادة التحميل. التقييمات ذاتية وخاصة بك.'
      : 'Select a topic and time. The session saves locally so a reload can resume it. Ratings are your own assessment.'));

    const controls = el('div', '', 'lab-controls');
    const topic = document.createElement('select');
    topic.setAttribute('aria-label', ar ? 'موضوع المقابلة' : 'Interview topic');
    topic.add(new Option(ar ? 'مواضيع مختلطة (شامل)' : 'Mixed topics', ''));

    const topicCodes = [...new Set(this.data.map((q) => q.code))];
    for (const code of topicCodes) {
      const first = this.data.find((q) => q.code === code);
      const name = ar ? (first.topicAr || first.topic) : first.topic;
      topic.add(new Option(`${code} — ${name}`, code));
    }
    controls.append(topic);

    const minutes = document.createElement('select');
    minutes.setAttribute('aria-label', ar ? 'المدة' : 'Duration');
    for (const duration of [10, 20, 30, 45]) {
      minutes.add(new Option(ar ? `${duration} دقيقة` : `${duration} minutes`, String(duration)));
    }
    controls.append(minutes);

    controls.append(button(ar ? 'ابدأ المقابلة التجريبية' : 'Start interview', () => {
      const pool = this.data.filter((q) => !topic.value || q.code === topic.value);
      const byGroup = ['A', 'B', 'C'].flatMap((group) =>
        pool.filter((q) => q.group === group).sort(() => Math.random() - .5).slice(0, Math.max(2, Math.ceil(Number(minutes.value) / 6)))
      );
      const ids = [...new Set(byGroup.map((q) => q.id))].slice(0, Math.max(3, Math.ceil(Number(minutes.value) / 2)));
      const next = loadState();
      next.activeSession = {
        ids,
        index: 0,
        startedAt: Date.now(),
        durationMinutes: Number(minutes.value),
        answers: {},
        ratings: {},
        revealed: false
      };
      saveState(next);
      this.render();
    }));
    this.append(controls);

    const history = state.sessions.slice(-5).reverse();
    if (history.length) {
      this.append(el('h2', ar ? 'الجلسات الأخيرة' : 'Recent sessions'));
      for (const item of history) {
        const histText = ar
          ? `${item.day} · ${item.answered}/${item.total} تم تقييمها ذاتياً · جلسة ${item.durationMinutes} دقيقة`
          : `${item.day} · ${item.answered}/${item.total} self rated · ${item.durationMinutes} minute session`;
        this.append(el('p', histText));
      }
    }
  }
  renderSession(session) {
    const ar = isAr();
    if (Date.now() >= session.startedAt + session.durationMinutes * 60000) {
      this.finish();
      return;
    }
    const q = this.data.find((item) => item.id === session.ids[session.index]);
    if (!q) {
      const next = loadState();
      next.activeSession = null;
      saveState(next);
      this.render();
      return;
    }

    const titleText = ar
      ? `السؤال ${session.index + 1} من ${session.ids.length} · ${q.id}`
      : `Question ${session.index + 1} of ${session.ids.length} · ${q.id}`;
    const title = el('h2', titleText);
    this.append(title);

    const timer = el('p', '', 'lab-timer');
    timer.setAttribute('role', 'timer');
    this.append(timer);

    const tick = () => {
      const remaining = Math.max(0, session.durationMinutes * 60 - Math.floor((Date.now() - session.startedAt) / 1000));
      const timeStr = `${String(Math.floor(remaining / 60)).padStart(2, '0')}:${String(remaining % 60).padStart(2, '0')}`;
      timer.textContent = ar ? `الوقت المتبقي: ${timeStr}` : `Time remaining: ${timeStr}`;
      if (!remaining) {
        clearInterval(this.interval);
        this.finish();
      }
    };
    clearInterval(this.interval);
    tick();
    this.interval = setInterval(tick, 1000);

    const promptText = ar ? (q.questionAr || q.question) : q.question;
    const prompt = el('blockquote', promptText, 'lab-prompt');
    if (!ar) prompt.dir = 'ltr';
    this.append(prompt);

    const answer = document.createElement('textarea');
    answer.rows = 7;
    answer.value = session.answers[q.id] || '';
    answer.placeholder = ar
      ? 'اكتب إجابتك الخاصة هنا أولاً قبل كشف نموذج الإجابة المعتمد.'
      : 'Type your own answer before revealing the source page.';
    answer.setAttribute('aria-label', ar ? 'إجابتك الشخصية' : 'Your answer');
    this.append(answer);

    answer.addEventListener('input', () => {
      const next = loadState();
      next.activeSession.answers[q.id] = answer.value;
      saveState(next);
    });

    const actions = el('div', '', 'lab-controls');
    const revealText = session.revealed
      ? (ar ? 'إخفاء صفحة الإجابة' : 'Hide source page')
      : (ar ? 'كشف صفحة الإجابة' : 'Reveal source page');

    actions.append(button(revealText, () => {
      const next = loadState();
      next.activeSession.revealed = !next.activeSession.revealed;
      saveState(next);
      this.render();
    }));

    if (session.revealed) {
      const qRoute = ar && q.routeAr ? q.routeAr : q.route;
      const source = el('p', ar ? 'افتح صفحة السؤال المعتمدة وقارن تسلسل أفكارك.' : 'Open the reviewed answer and compare your reasoning.');
      const sourceLink = el('a', ar ? 'فتح صفحة السؤال' : 'Open question page');
      sourceLink.href = link(qRoute);
      source.append(' ', sourceLink);
      this.append(source);
    }

    const rating = document.createElement('select');
    rating.setAttribute('aria-label', ar ? 'التقييم الذاتي' : 'Self rating');
    const ratingOptions = ar
      ? [['بدون تقييم ذاتي', ''], ['يحتاج مراجعة (ضعيف)', 'again'], ['جزئي (متوسط)', 'hard'], ['جيد ومتماسك', 'good'], ['قوي ومتقن', 'easy']]
      : [['No self rating', ''], ['Needs work', 'again'], ['Partial', 'hard'], ['Solid', 'good'], ['Strong', 'easy']];

    for (const [label, value] of ratingOptions) rating.add(new Option(label, value));
    rating.value = session.ratings[q.id] || '';
    rating.addEventListener('change', () => {
      const next = loadState();
      next.activeSession.ratings[q.id] = rating.value;
      saveState(next);
    });
    this.append(rating);

    actions.append(
      button(ar ? 'السابق' : 'Previous', () => this.move(-1)),
      button(ar ? 'التالي' : 'Next', () => this.move(1)),
      button(ar ? 'إنهاء الجلسة' : 'End session', () => this.finish())
    );
    this.append(actions);
  }
  move(delta) {
    const next = loadState();
    next.activeSession.index = Math.max(0, Math.min(next.activeSession.ids.length - 1, next.activeSession.index + delta));
    next.activeSession.revealed = false;
    saveState(next);
    this.render();
  }
  finish() {
    clearInterval(this.interval);
    const ar = isAr();
    const next = loadState();
    const session = next.activeSession;
    if (!session) return;

    const recap = {
      day: localDay(),
      total: session.ids.length,
      answered: Object.values(session.ratings).filter(Boolean).length,
      durationMinutes: session.durationMinutes,
      ratings: session.ratings
    };
    next.sessions.push(recap);
    next.sessions = next.sessions.slice(-30);
    next.activeSession = null;
    saveState(next);
    this.render();

    const summary = el('div', '', 'lab-summary');
    const endMsg = ar
      ? `انتهت الجلسة: تم تقييم ${recap.answered} من إجمالي ${recap.total} سؤال ذاتياً. لم يتم حساب أي درجة تقنية تلقائية.`
      : `Session ended: ${recap.answered} of ${recap.total} questions self rated. No automatic technical score was calculated.`;
    summary.append(el('strong', endMsg));

    for (const id of session.ids) {
      const item = this.data.find((q) => q.id === id);
      const qRoute = ar && item.routeAr ? item.routeAr : item.route;
      const row = el('p', `${id} · ${recap.ratings[id] || (ar ? 'غير مقيّم' : 'not rated')} · `);
      const anchor = el('a', ar ? 'مراجعة السؤال' : 'review question');
      anchor.href = link(qRoute);
      row.append(anchor);
      summary.append(row);
    }
    this.prepend(summary);
  }
  disconnectedCallback() {
    clearInterval(this.interval);
  }
}

for (const [name, type] of [
  ['lab-question', LabQuestion],
  ['lab-dashboard', LabDashboard],
  ['lab-topic', LabTopic],
  ['lab-explorer', LabExplorer],
  ['lab-review', LabReview],
  ['lab-practice', LabPractice]
]) customElements.define(name, type);
