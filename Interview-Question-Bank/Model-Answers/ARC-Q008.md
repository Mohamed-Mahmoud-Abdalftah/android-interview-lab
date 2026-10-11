---
id: ARC-Q008-ANSWER
question_id: ARC-Q008
status: reviewed
---
# ARC-Q008 — Complete model answer

<p dir="rtl" lang="ar"><strong>الإجابة بالمصري:</strong> مفيش اختيار واحد لكل الحالات. اسأل الأول: هل المعلومة لازم تفضل بعد recreation؟ هل ينفع تتكرر؟ وهل عدم ظهورها يضيع قرار مهم؟ حالة زي validation error أو dialog مطلوب لحد ما المستخدم يتصرف ممكن تبقى state ومعاها acknowledgment. Navigation تنفذها UI لما state/نتيجة المنتج تستدعيها، مع guard يمنع التكرار.</p>

<p dir="rtl" lang="ar">Channel أو SharedFlow للـ effect محتاجة سياسة buffer وreplay ووضوح عن غياب collector. لو event اتبعت والواجهة <code dir="ltr">STOPPED</code> ممكن تضيع أو تتأخر حسب الإعداد. تحويل كل حاجة لـ Boolean في state برضه يعمل إعادة تنفيذ بعد rotation لو ما فيش consume semantics. صمّم contract من تجربة المستخدم، وبعدها اختبر stop/start وrecreation.</p>

**Spoken answer:** “I choose based on lifetime and replay semantics. Durable user-visible decisions belong in state with explicit acknowledgement. UI effects need a documented delivery policy and lifecycle tests.”

**Common wrong answer:** “Use SingleLiveEvent for every effect.” A wrapper name does not define loss, replay, multiple collector, or process recreation semantics.

**Follow-up 1:** How do you avoid repeating navigation after rotation? Make the destination derive from durable application state or acknowledge a uniquely identified navigation request after the UI handles it.

**Follow-up 2:** Should a success snackbar survive process death? Usually that is a product choice; persist it only when missing the message would materially confuse the user.

**Rubric:** Discuss lifetime, replay, acknowledgement, collector absence, and a lifecycle test rather than naming a favorite primitive.
