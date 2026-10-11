---
id: PRO-Q005-ANSWER
question_id: PRO-Q005
status: reviewed
---
# PRO-Q005 — Complete model answer

<p dir="rtl" lang="ar">أطلب unit tests للparser بقيم hostile، Android tests للmanifest والexported invocation والlifecycle، وdevice verification للـ App Links والcertificate الفعلية. على API أختبر حساب آخر، order غير موجودة، replay، concurrent requests، provider failure، وaudit بدون secrets. أراجع dependency/components/permissions وأعمل staged rollout مع monitoring وrollback آمن.</p>

**Spoken answer:** “I require evidence across the full boundary chain: parser tests, Android routing and component tests, domain verification on a signed build, and API authorization and idempotency tests.”

**Common wrong answer:** Calling the flow secure after a happy-path emulator test or a static scanner produces no findings.

**Follow-up 1:** What can a static analyzer prove here? It can flag suspicious patterns and exposure, but cannot prove backend ownership, runtime routing, or business idempotency.

**Follow-up 2:** What should production telemetry avoid? Avoid raw tokens, full URLs, card data, and unnecessary identifiers; record minimal privacy-safe outcome categories and correlation.

**Rubric:** Include unit, Android, device/domain, backend, concurrency, telemetry, rollout, and evidence limitations.
