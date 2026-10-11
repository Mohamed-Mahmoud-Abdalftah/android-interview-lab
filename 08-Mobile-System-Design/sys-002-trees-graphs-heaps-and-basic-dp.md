---
id: SYS-002
title: Trees, graphs, heaps and basic DP
module: 08-Mobile-System-Design
tier: Core
estimated_minutes: 65
prerequisite_ids: [SYS-001]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://kotlinlang.org/docs/collections-overview.html
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/PriorityQueue.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [SYS-Q006, SYS-Q007, SYS-Q008, SYS-Q009, SYS-Q010]
---

# SYS-002 — Trees, graphs, heaps and basic DP

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Tree traversal تختار DFS/BFS من المطلوب، graph تحتاج visited وdirection/weights، heap تدعم أفضل عنصر مش sorted iteration، وDP تخزن overlapping subproblems بعد تعريف state/transition/base.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Tree traversal تختار DFS/BFS من المطلوب، graph تحتاج visited وdirection/weights، heap تدعم أفضل عنصر مش sorted iteration، وDP تخزن overlapping subproblems بعد تعريف state/transition/base.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: اكتب graph contract، invariant، complexity، وoverflow. اختبر disconnected/cycle/duplicate edges وlarge weights.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
queue.add(start) // no visited; cycles forever
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة.</p>

```kotlin
queue.add(start); visited.add(start)
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اكتب graph contract، invariant، complexity، وoverflow. اختبر disconnected/cycle/duplicate edges وlarge weights. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">اكتب graph contract، invariant، complexity، وoverflow. اختبر disconnected/cycle/duplicate edges وlarge weights. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> BFS gives shortest edge count in an unweighted graph; DFS fits reachability and recursive structure with depth risks.</p>

**English, 20 seconds:** “BFS gives shortest edge count in an unweighted graph; DFS fits reachability and recursive structure with depth risks.”

**English, 60–90 seconds:** “BFS gives shortest edge count in an unweighted graph; DFS fits reachability and recursive structure with depth risks. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. I would implement this policy: اكتب graph contract، invariant، complexity، وoverflow. اختبر disconnected/cycle/duplicate edges وlarge weights. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain BFS and DFS choice under a production failure.** BFS gives shortest edge count in an unweighted graph; DFS fits reachability and recursive structure with depth risks.
2. **Explain Heap invariant under a production failure.** The root is the priority optimum; arbitrary iteration is not globally sorted.
3. **Explain Dijkstra precondition under a production failure.** Weights must be non-negative and stale heap entries need handling.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع SYS-Q006 إلى SYS-Q010، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

حل [LAB-030](../Coding-Challenges/LAB-030-sys-002-trees-graphs-heaps-and-basic-dp.md) وراجع الاختبار المرتبط.

حلّل [SCN-041](../Real-World-Scenarios/SCN-041-sys-002-trees-graphs-heaps-and-basic-dp.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
