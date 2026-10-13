---
id: "MEM-24"
question: "How do you reduce slow app startup without breaking correctness?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "C"
phase: 1
priority: "P1"
order: 79
editorial_status: "reviewed"
---

# MEM-24

## Original interview question

How do you reduce slow app startup without breaking correctness?

## What the interviewer evaluates

- Measure cold/warm/hot and first-frame versus usable-content timing.
- Trace startup dependencies, defer safe work, and retain required initialization and navigation.
- Verify process-death restoration, auth, and failures after optimization.

## Explanation in Arabic

ابدأ بقياس cold start على جهاز يمثل المستخدمين، وحدد هل التأخير في `ContentProvider`/`Application.onCreate`، DI setup، disk I/O، أول composition، أو انتظار network. لا تؤجل كل شيء عشوائيًا: session/auth state اللازمة لمنع عرض بيانات حساسة يجب أن تكون صحيحة قبل توجيه المستخدم. انقل analytics أو prefetch غير ضروري بعد أول frame/وقت الخمول إذا كان آمنًا، واجعل dependencies lazy حيث لا تؤثر على أول شاشة. حافظ على شاشة loading صادقة بدل splash تخفي بطء البيانات. قس `TTID` و`TTFD` معًا، واختبر deep link والـnotification بعد process death.

## Practical walkthrough

في banking app، analytics init وdatabase read قبل أول frame بيطولوا cold start. trace يحدد مين فعلًا على critical path. أجّل analytics لو مش مطلوبة للواجهة الأولى، وخلي query async، لكن اعرض loading state آمنة لحد ما session/auth تتأكد؛ متعرضش account قديم عشان تكسب TTID. قس TTID وTTFD على جهاز متوسط ومنخفض، واختبر logout وoffline وdeep link بعد تغيير ترتيب initialization.

## Why it matters and how it works

Cold startup includes process creation, provider initialization, Application work, Activity creation, layout/composition, and drawing. A trace shows which spans lie on the critical path. Deferring independent noncritical work can shorten that path, but delaying required state merely moves latency or creates incorrect UI. Baseline Profiles can reduce code execution overhead for covered startup paths; they cannot fix synchronous I/O or server latency.

## Worked example

A banking app initializes several analytics SDKs and reads a database synchronously before drawing its account shell. A trace shows analytics is nonessential to the first view; move it to a safe later initialization boundary. Make the database query asynchronous and render a secure loading state until session validation and account summary are ready. Benchmark cold and warm starts, including an expired session and notification entry. This is an illustrative plan, not a measured app change.

## Trade-offs and decision criteria

Lazy initialization improves first display but can make the first use of a deferred feature slow; prewarm only where measured benefit warrants it. Showing a shell early improves TTID but may leave TTFD unchanged or worse. Caching can help startup but risks stale or cross-account data. A Baseline Profile addresses compilation cost while architecture work addresses I/O and rendering cost.

## Failure modes

Moving auth validation after private UI render briefly exposes sensitive content. Deferring a required notification router loses a cold-start deep link. A background initializer races the first feature request. A “faster” splash merely hides network waiting. Startup benchmarks with a warm cache misstate cold performance. Add explicit dependency readiness and error paths, and test restored process entry.

## Production perspective

Set per-device startup budgets for TTID and meaningful readiness. Use Macrobenchmark and Perfetto on release-like builds; record test mode, cache, account, and network state. Change one critical-path dependency at a time, run correctness UI tests, and compare staged rollout startup and crash metrics. Keep a rollback path if a deferred initialization creates field failures.

## Interview answer — short

“I trace the startup critical path, defer only nonessential work, and measure both first frame and usable content. I protect authentication, navigation, and process restoration while optimizing.”

## Interview answer — structured

“I benchmark cold, warm, and hot starts separately and inspect a trace of provider, Application, Activity, and first-render work. Main-thread disk I/O and unnecessary eager SDK initialization are common targets. I move independent work off the critical path or initialize it lazily, while keeping session checks and required routing correct. I measure TTID and TTFD, because a quick blank shell is not a useful startup. I test expired auth, offline launch, deep links, notification taps, and process death before declaring the change successful.”

## Interview answer — deep senior

“I start by defining what ‘ready’ means for the first user action, then measure cold startup on representative devices with a release-like build and controlled cache and account state. A Perfetto or Macrobenchmark trace shows provider and Application initialization, DI graph creation, disk access, Activity creation, and first render on the critical path. I remove or defer analytics and prefetch only when they are independent; required session validation and destination routing must still gate sensitive content. A lazy dependency needs a first-use latency and failure policy, or it merely shifts the delay. I compare TTID with time to fully drawn or interactive content, and use Baseline Profiles if compilation overhead is material. Finally I test cold notification and deep-link entry, offline/expired session, and process restoration, then monitor startup and crash cohorts in staged rollout. In a banking launch, deferring analytics is safe only if it does not gate navigation; deferring session validation can expose stale protected content. I measure the first usable account state, not just the first placeholder frame. A lazy dependency also needs a first-use latency and failure policy, which I exercise through logout, offline, and deep-link entry.”

## How to answer in the interview

- **Why:** Define a secure meaningful first interaction.
- **How:** Trace startup critical path and defer nonessential init.
- **Trade-off:** Deferral can shift delay into the first user action.
- **Failure case:** Early paint may expose stale protected data.
- **Production solution:** Measure TTID/TTFD and test offline and deep-link routing.

## Deep-dive talking points

Discuss startup critical path, secure readiness, TTID/TTFD, lazy initialization races, Baseline Profiles, and cold entry tests.

## Follow-up questions

- Why can a faster TTID be misleading? **Answer:** the first frame may be an empty shell while data and interaction remain delayed.
- What must not be deferred past private UI display? **Answer:** authorization or session checks required to avoid showing protected content to the wrong user.
- How do you test a startup optimization? **Answer:** benchmark the same cold/warm modes and run correctness flows for offline, expired auth, notification, and process restoration.

## Self-check rubric

Trace the critical path, identify safe deferral, protect auth/navigation, compare TTID and TTFD, and verify a cold external entry.

## References and reviewed-on date

- [App startup time](https://developer.android.com/topic/performance/issues/launch-time) — launch phases and improvement guidance.
- [Macrobenchmark overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — reproducible launch measurement.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — restoration boundaries.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. The banking example was not device-measured.
