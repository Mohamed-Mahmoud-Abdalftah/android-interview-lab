---
id: ARC-Q012-ANSWER
question_id: ARC-Q012
status: reviewed
---
# ARC-Q012 — Complete model answer

<p dir="rtl" lang="ar">UI تقرأ stream واحدة من local database، فهي canonical داخل التطبيق. sync تكلم server التي تملك authority مشتركة بين الأجهزة، وبعد قبول أو conflict تكتب النتيجة/metadata محليًا. كده الشاشة لا تجمع مصدرين، وفي نفس الوقت client لا تدّعي إنها authority العالمية.</p>

**Spoken answer:** “Local storage is the app's read source of truth. The server can remain the cross-device authority; synchronization writes its accepted or conflict result back into local storage.”

**Common wrong answer:** Rendering network responses directly and local rows separately, which creates two competing UI truths.

**Follow-up 1:** What should refresh failure do to valid local data? Keep the data visible and expose freshness or refresh failure separately rather than replacing content with empty state.

**Follow-up 2:** Can different repositories use different sources of truth? Yes. Choose per data type and document ownership; authentication may be memory/server-centered while offline notes use disk.

**Rubric:** Separate app read authority, server conflict authority, sync write-back, and error/freshness state.
