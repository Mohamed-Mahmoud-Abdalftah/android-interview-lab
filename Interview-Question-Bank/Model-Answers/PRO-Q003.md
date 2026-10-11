---
id: PRO-Q003-ANSWER
question_id: PRO-Q003
status: reviewed
---
# PRO-Q003 — Complete model answer

<p dir="rtl" lang="ar">Intent filter تصف routing للimplicit intents، لكن caller قد يرسل explicit intent للcomponent المصدّرة. اقفل component لو مش محتاجة خارج التطبيق، أو استخدم permission مناسبة وتحقق من caller/input/session والauthorization قبل الأثر. ما تمررش secrets في implicit intents، واستخدم explicit destination أو chooser حسب تجربة المستخدم.</p>

**Spoken answer:** “Intent filters route messages; they do not authorize callers. I minimize exported components and enforce permission, input, and business authorization checks at the component boundary.”

**Common wrong answer:** Assuming a path pattern in the manifest prevents direct explicit invocation with different extras.

**Follow-up 1:** Is `exported=false` enough for all internal components? It removes external callers, while internal untrusted data and WebView or SDK flows still require validation.

**Follow-up 2:** When is an implicit intent appropriate? Use it when user choice is intended and avoid sensitive payloads; show a chooser where appropriate.

**Rubric:** Explain routing versus authorization, exported minimization, permissions, validation, and sensitive payload handling.
