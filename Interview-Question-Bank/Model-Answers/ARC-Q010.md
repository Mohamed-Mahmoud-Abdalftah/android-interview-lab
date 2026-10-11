---
id: ARC-Q010-ANSWER
question_id: ARC-Q010
status: reviewed
---
# ARC-Q010 — Complete model answer

<p dir="rtl" lang="ar"><strong>الإجابة بالمصري:</strong> أعطي كل save request هوية، وآخذ snapshot من العنوان لحظة البداية. لما النتيجة ترجع، state holder تقبلها لو الهوية تطابق العملية الحالية؛ غير كده تعتبرها stale ولا تعرض success أو failure للـ draft الجديدة. لازم كمان أحدد سياسة البيانات: إلغاء القديم لو ممكن، version/optimistic concurrency لو الكتابات تتعارض، أو queue لو كل كتابة مطلوبة.</p>

<p dir="rtl" lang="ar">الحماية في UI وحدها لا تكفي؛ الطلب القديم ربما كتب A بعد B. repository أو server محتاج idempotency/version contract، وبعد غموض النتيجة اقرأ source of truth واعمل reconciliation. الاختبار يقلب ترتيب completion عمدًا ويفحص state والكتابات المسجلة، واختبار integration يثبت transaction الفعلية.</p>

**Spoken answer:** “I tag each save, snapshot its payload, and accept UI completion only for the current request. Separately, I protect persistence with cancellation where possible, idempotency or version checks, and reconciliation from the source of truth.”

**Common wrong answer:** “Cancel the first coroutine and the problem is solved.” Cancellation is cooperative and downstream work may already have committed.

**Follow-up 1:** What telemetry would help diagnose this in production? Record privacy-safe request identity, entity version, start and completion ordering, cancellation outcome, and final source-of-truth version.

**Follow-up 2:** How would process death change the design? Persist durable work and version information outside the ViewModel, then rebuild UI state from the repository after restart.

**Rubric:** Cover request identity, payload snapshot, persistence conflict policy, reconciliation, deterministic tests, and process death.
