---
id: SCN-013
lesson_id: EXT-POS-01
status: reviewed
code_verification: not_run
---
# SCN-013 — Terminal times out after authorization submission

**Hypothetical POS incident.** The terminal sends an authorization, loses connectivity, shows “Declined,” and lets the cashier retry. The customer later sees two authorizations.

<p dir="rtl" lang="ar">أوقف blind retries وحافظ على attempt IDs وtimestamps وprovider references من غير card data. اجمع trace من terminal/backend/provider: هل الطلب الأول وصل؟ هل فيه idempotency key؟ هل retry استخدمت نفس business attempt ولا واحدة جديدة؟ كلمة timeout وحدها لا تحدد outcome.</p>

## Recovery

1. Mark the first attempt `Unknown`, preventing a new charge until policy permits.
2. Query the provider or backend source of truth using the original idempotency key.
3. If approved, surface the receipt once. If definitively absent/declined, permit a new identified attempt.
4. Handle reversal/void through the provider contract; never simulate it only in UI state.

<p dir="rtl" lang="ar">الإصلاح يحتاج state machine وidempotency end-to-end ومراقبة نسبة Unknown وزمن حسمها. rollback لا يرجع blind retry؛ ممكن يعطل الدفع مؤقتًا أو يحول لمسار يدوي آمن. اختبر provider sandbox وhardware disconnect في كل نقطة حرجة.</p>

The [JVM exercise](../Coding-Challenges/LAB-012-terminal-attempt-state-machine.md) proves only that transport loss becomes `Unknown` and terminal outcomes do not overwrite each other.

## Senior follow-ups

1. **Can the app decide to void locally?** No. A void or reversal is a provider-side operation with its own uncertain outcome.
2. **What metric matters?** Unknown rate and time-to-reconciliation by provider/device/version, plus duplicate-attempt prevention outcomes.
