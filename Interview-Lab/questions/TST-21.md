---
id: "TST-21"
question: "A flaky test passes locally but fails on CI. Explain triage and mitigation."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 416
editorial_status: "reviewed"
---

# TST-21

## Original interview question

A flaky test passes locally but fails on CI. Explain triage and mitigation.

## What the interviewer evaluates

- CI-only flake diagnosis with evidence before mitigation.
- Test order, sharding, emulator/resource and race hypotheses.

## Explanation in Arabic

اختبار ينجح دائماً على جهازك المحلي (Local Machine) ولكنه يفشل بشكل متقطع على خوادم الـ CI (Flaky Test). اشرح منهجية التشخيص والحل الجذري؟

1. لماذا تفشل الاختبارات على الـ CI بينما تنجح محلياً؟
   - **اختلاف قوة المعالجة والـ Resources**: حاسوبك يملك 8-16 Core قوية، بينما خادم الـ CI يعمل على Virtual Machine بـ 2 Cores فقط وعليها ضغط عالي؛ أي عملية تعتمد على سباق توقيت أو تأخير بسيط ستفشل على الـ CI!
   - **اختلاف المنطقة الزمنية والـ Locale**: جهازك مضبوط على `GMT+2` بينما الـ CI مضبوط على `UTC`؛ إذا كان الكود يتعامل مع تواريخ ونصوص دون تحديد الـ Locale يدوياً، ستفشل الـ Assertions!
   - **تشغيل الاختبارات بالتوازي (Parallel Execution)**: الـ CI يشغل أكثر من Fork في نفس الوقت، مما يسبب تنافساً على الـ Ports أو قواعد البيانات المشتركة.

2. منهجية التشخيص خطوة بخطوة (Triage Protocol):
   - **الخطوة 1: إعادة إنتاج المشكلة محلياً عبر الضغط المكثف (Stress Testing)**: تشغيل الاختبار 100 مرة متتالية محلياً:
     `./gradlew test --tests MyFlakyTest --repeat 100`.
   - **الخطوة 2: فحص مخرجات الـ CI**: فحص صور الشاشة وسجلات الـ Logcat وملفات الـ HTML reports الناتجة عن الفشل.
   - **الخطوة 3: تحديد السبب الجذري**: هل هو بسبب `Thread.sleep`؟ هل هو بسبب `Dispatchers.Main`؟ هل هو بسبب الـ Timezone؟

3. الحل الجذري والوقاية:
   - استبدال أي انتظار عشوائي بـ `advanceUntilIdle()` أو Compose synchronization.
   - تثبيت الـ Locale والـ Timezone في الـ Test Setup (`Locale.setDefault(Locale.US)`).
   - عزل الاختبار فوراً في `@FlakyTest` لمنع تعطيل الـ PRs لحين إصلاحه.

## Practical walkthrough

تثبيت المنطقة الزمنية واللغة في اختبارات الـ JVM وإعادة إنتاج الاختبار المتقلب محلياً:
```bash
# 1. أمر تشغيل الاختبار المتكرر 50 مرة محلياً لاكتشاف أخطاء التزامن الخفية:
./gradlew testDebugUnitTest --tests "com.example.OrderHistoryTest" --rerun-tasks
```

```kotlin
// 2. ضبط إعدادات الـ Locale والـ Timezone برمجياً في Test Rule لمنع تباين الـ CI:
class DeterministicLocaleRule : TestWatcher() {
    private val originalLocale = Locale.getDefault()
    private val originalTimeZone = TimeZone.getDefault()

    override fun starting(description: Description) {
        Locale.setDefault(Locale.US)
        TimeZone.setDefault(TimeZone.getTimeZone("UTC"))
    }

    override fun finished(description: Description) {
        Locale.setDefault(originalLocale)
        TimeZone.setDefault(originalTimeZone)
    }
}
```

## Why it matters and how it works

CI differs in CPU contention, scheduling, filesystem, locale and emulator version. A deterministic test should synchronize on observable conditions, isolate fixtures and clean up global state. If repeated runs expose an app race, fix production code and add a lower-level regression test.

## Worked example

A Compose test fails only when run after logout tests. Rerun the pair in the same shard; discover a singleton fake retained session state. Reset DI/test DB per case and assert teardown. If the flake instead tracks low CPU, replace a fixed sleep with semantics wait or fake-clock control.

## Trade-offs and decision criteria

Retrying can keep a pipeline usable temporarily but increases cost and hides risk; quarantine needs owner, expiry and equivalent release coverage for high-risk flows. Longer timeouts may help legitimate slow operations but are not a race fix.

## Failure modes

Blindly increasing sleep from 1 to 5 seconds reduces one symptom while preserving an app concurrency bug. Preserve first-failure logs/screenshot and test ordering evidence; do not delete a payment gate.

## Production perspective

Track flake rate, affected branches/devices and time-to-fix. CI publishes first-attempt failure even when retry passes, enabling prioritization.

## Interview answer — short

Triage flaky CI tests by reproducing locally via stress-run loops (--repeat 100), inspecting CI logcat and failure screenshots, checking for CPU throttling and timing races, standardizing Locale/TimeZone to UTC, and replacing arbitrary sleeps with deterministic coroutine TestDispatchers.

## Interview answer — structured

A test that passes locally but fails intermittently on CI indicates an environmental assumption or timing vulnerability:

1. **Root Cause Analysis (Local vs. CI Discrepancies)**:
   - **CPU Throttling & Core Starvation**: CI virtual runners operate on resource-constrained containers (1–2 vCPUs) under high I/O load. Operations that execute in 5ms locally take 500ms on CI, exposing uncoordinated asynchronous race conditions.
   - **Locale & Timezone Drift**: Host developer machines run local timezones (e.g. Cairo GMT+2, US PST), while CI runs on `UTC`. Tests formatting dates or decimal numbers fail if assertions assume local time.
   - **Parallel Execution Contamination**: Shared files or static singletons leak state when Gradle runs parallel test workers on CI.

2. **Triaging Protocol**:
   - **Stress-Run Locally**: Execute the test 100 times in a loop locally: `./gradlew test --tests MyFlakyTest --rerun-tasks`.
   - **Inspect CI Artifacts**: Review Logcat dumps, stack traces, and emulator video recordings generated at failure time.

3. **Definitive Remediation**:
   - Replace all asynchronous timing sleeps with `StandardTestDispatcher` and Turbine.
   - Enforce explicit `Locale.US` and `UTC` timezones inside test setup rules.
   - Quarantine the test with a team alert ticket if immediate resolution cannot be found within 2 hours, preventing PR pipeline paralysis.

## Interview answer — deep senior

From an engineering governance and infrastructure perspective, managing flaky tests requires automated quarantine policies:

1. **Automated Quarantine Gateways**: Configure CI pipelines (e.g. using TestFlaky Gradle plugins) to automatically detect tests failing intermittently without code changes. Automatically tag them as `@Quarantine`, route them to an isolated non-blocking monitoring track, and create an automated engineering ticket assigned to the owning team.

2. **Emulator Snapshot & Cold Boot Stability**: For UI tests, CI emulators often flake during initial boot. Ensure CI setup scripts execute `adb wait-for-device` and check `sys.boot_completed=1` before triggering test execution.

3. **Zero-Flake SLA**: Establish a team SLA: a PR cannot merge if it introduces flaky tests. High-performing engineering cultures treat a 1% flaky test rate as equivalent to a broken build because it desensitizes engineers to legitimate regressions.

## How to answer in the interview

- **Why:** CI-only flakes may reveal shared state or a real race.
- **How:** capture shard, seed and logs, reproduce in order and fix the causal boundary.
- **Trade-off:** temporary quarantine versus coverage loss.
- **Failure case:** longer sleep only lowers failure frequency.
- **Production solution:** repeated original-shard run with owned quarantine policy.

## Deep-dive talking points

Prompt for first-failure artifact, same shard/order reproduction, race versus harness, owned quarantine.

## Follow-up questions

- **Interviewer:** "Why does Date formatting frequently cause tests to fail on CI?"
  **Answer:** "Because default SimpleDateFormat formats use the machine's local TimeZone and Locale; CI machines configured to UTC mismatch developer local timezones."

- **Interviewer:** "What is test quarantining?"
  **Answer:** "Moving an intermittently failing test into a separate non-blocking suite so it does not block pull requests while engineers investigate the root cause."

## Self-check rubric

Reproduce the CI-only failure with its shard/order/environment, preserve logs and seed, isolate shared state or timing, then verify repeated green runs. State when a retry masks rather than fixes the defect.

## References and reviewed-on date

- [Android testing guidance](https://developer.android.com/training/testing) — test environment and reliability.
- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — synchronization APIs.

Technically reviewed against primary documentation on 2026-10-13.
