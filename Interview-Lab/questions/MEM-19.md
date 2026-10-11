---
id: "MEM-19"
question: "What are cold start, warm start, and hot start?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "B"
phase: 1
priority: "P1"
order: 74
editorial_status: "reviewed"
---

# MEM-19

## Original interview question

What are cold start, warm start, and hot start?

## What the interviewer evaluates

- Distinguish process and Activity state at launch, with correct examples.
- Separate time to initial display from fully usable content.
- Benchmark each mode consistently and preserve correct state restoration.

## Explanation in Arabic

`Cold start` يحصل لما process غير موجودة، فالنظام يبدأها ويهيئ التطبيق وينشئ Activity ويرسم أول frame. `Warm start` عادة process موجودة لكن Activity المستهدفة تحتاج إنشاء/إعادة إنشاء. `Hot start` العملية والـActivity موجودان والتطبيق يرجع للواجهة؛ ده غالبًا أقصر لكن لا يعني صفر عمل. قياس startup لازم يحدد النوع، لأن مقارنة cold قبل التعديل بـhot بعده نتيجة مضللة. `TTID` يقيس ظهور أول frame، و`TTFD` يقيس أن المحتوى أصبح جاهزًا حسب `reportFullyDrawn`؛ شاشة splash سريعة مع بيانات متأخرة لا تساوي تجربة سريعة. تجنّب تهيئة كل SDK في `Application.onCreate` بدون ضرورة.

## Why it matters and how it works

Cold launch includes process creation, application initialization, Activity creation, inflation/composition, and first draw. Warm launch avoids process start but still creates an Activity. Hot launch resumes an existing Activity/process, though callbacks and redraw work remain. System and benchmark definitions focus on starting state, so document test setup. Correctness includes restoring route and session after cold launch rather than only minimizing the first-frame metric.

## Worked example

Benchmark an order app with three conditions: force-stop/kill process then launch for cold; keep process but remove Activity for warm; leave Activity stopped then return for hot. Record time to initial display and to meaningful order content, with identical cache and network conditions. Move nonessential analytics initialization out of the first-frame path while preserving authentication and route restoration. This is a proposed experiment, not a measured outcome.

## Trade-offs and decision criteria

Deferring work can improve initial display but may delay first interaction or hide errors, so measure fully drawn/interactive state as well. Aggressive caching speeds warm paths but increases memory and staleness. Baseline Profiles can help code execution on cold paths, but not a slow server. A splash screen must not conceal a broken restoration flow.

## Failure modes

A benchmark accidentally reuses process and calls the result cold. A startup optimization removes essential session validation and briefly exposes private UI. A fast blank frame improves TTID while TTFD worsens. Blocking ContentProvider or Application initialization still delays cold start even after Activity code is optimized. Examine trace and startup mode explicitly.

## Production perspective

Track startup metrics by mode, device tier, release, and entry source. Use Macrobenchmark with controlled `StartupMode` and production-sized state, and trace provider/Application/Activity work. Define separate budgets for first frame and usable content. After improvements, verify notification/deep-link cold entry and process-death restoration still work.

## Interview answer — short

“Cold start creates a process and Activity, warm start recreates an Activity in an existing process, and hot start returns to an existing Activity. I measure each separately and track both first frame and usable content.”

## Interview answer — structured

“The categories describe the app's starting state. Cold includes process and app initialization before the first Activity frame; warm keeps the process but needs an Activity; hot brings an existing Activity forward. The exact setup matters for a valid comparison. I measure time to initial display and time to fully drawn content, because a quick splash or empty frame can hide delayed usability. I trace Application, provider, and Activity work for cold start, defer only nonessential initialization, and test restoration after process death.”

## Interview answer — deep senior

“I first make the starting state reproducible. In cold start the process, Application, and Activity must be created; in warm start the process exists but the Activity must be created; in hot start an existing Activity returns to foreground. I do not compare these modes interchangeably. For each mode I measure TTID and a meaningful fully-drawn signal, with identical device, compilation, cache, account, and network conditions. A fast first frame that cannot accept input or has no order data is not a full user benefit. For a cold-start regression I trace ContentProvider and Application initialization, Activity setup, and first composition or layout, then defer only work that is not required for correctness. I verify deep-link and notification entry, expired session, and process-death restoration after optimization, and watch startup distributions in production rather than one best benchmark run.”

## Deep-dive talking points

Discuss process/Activity state, TTID versus TTFD, startup setup, Application/provider work, and restoration correctness.

## Follow-up questions

- Why is a hot start usually faster? **Answer:** it reuses a live process and Activity instead of creating both, though resume work still occurs.
- Can TTID improve while user experience worsens? **Answer:** yes; an early blank frame can appear while meaningful content or interaction is delayed.
- What must a cold-start benchmark control? **Answer:** process state, compilation, cache, account/data setup, device, and entry route.

## Self-check rubric

Define three modes, distinguish TTID and TTFD, configure a fair comparison, and protect cold-entry correctness.

## References and reviewed-on date

- [App startup time](https://developer.android.com/topic/performance/issues/launch-time) — cold/warm/hot definitions.
- [Macrobenchmark overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — StartupMode measurement.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The benchmark plan has not been device-executed.
