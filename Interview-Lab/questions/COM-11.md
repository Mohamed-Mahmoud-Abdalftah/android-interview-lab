---
id: "COM-11"
question: "Compare LaunchedEffect(Unit) and LaunchedEffect(key)."
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 240
editorial_status: "reviewed"
---

# COM-11

## Original interview question

Compare LaunchedEffect(Unit) and LaunchedEffect(key).

## What the interviewer evaluates

- Explain effect lifetime at one call site versus restart on changing identity.
- Identify stale capture and unnecessary restarts.
- Choose ViewModel ownership when work should outlive composition.

## Concept and technical explanation

LaunchedEffect is a composable effect handler that launches a coroutine scoped to the composition lifecycle. The crucial distinction lies in the key argument passed to it: LaunchedEffect(Unit) or LaunchedEffect(true) uses a constant key, guaranteeing that the coroutine runs exactly once when entering the composition and remains active until the composable leaves the composition tree. In contrast, LaunchedEffect(key) binds the coroutine lifecycle to a dynamic state variable. Whenever key evaluates to a new value via structural equality, Compose immediately cancels the currently executing coroutine job and launches a fresh coroutine with the updated key, ensuring the asynchronous operation stays synchronized with changing parameters.

## Practical walkthrough (English)

Contrasting static LaunchedEffect(Unit) with dynamic LaunchedEffect(key) in a search screen:
```kotlin
// ❌ ANTI-PATTERN: LaunchedEffect(Unit) misses dynamic query updates!
@Composable
fun StaleSearchScreen(query: String, viewModel: SearchViewModel) {
    // Runs ONLY ONCE when first entering composition!
    // When the user types a new query, this coroutine DOES NOT RESTART!
    LaunchedEffect(Unit) {
        viewModel.performSearch(query) // Captures stale initial query!
    }
}

// ✅ BEST PRACTICE: LaunchedEffect(key) cancels and restarts when parameter changes
@Composable
fun ReactiveSearchScreen(query: String, viewModel: SearchViewModel) {
    // Whenever 'query' changes, Compose cancels the previous search coroutine
    // and launches a new one with the updated query!
    LaunchedEffect(query) {
        if (query.isNotBlank()) {
            delay(300) // Built-in debounce mechanism!
            viewModel.performSearch(query)
        }
    }
}
```

## Explanation in Arabic

المقارنة بين `LaunchedEffect(Unit)` و `LaunchedEffect(key)` وكيف يؤثر اختيار الـ Key على الأداء والصحة:

1. كيف تعمل `LaunchedEffect(Unit)` أو `LaunchedEffect(true)`؟
   - تمرير قيمة ثابتة لا تتغير أبداً (مثل `Unit` أو `true`) يعني أن الـ Key **لن يتغير أبداً** طوال فترة بقاء هذا الـ Composable في شجرة الـ Composition.
   - النتيجة: يعمل الكود **مرة واحدة فقط (Run-Once)** عند دخول الـ Composable لأول مرة، ولا يُعاد تشغيله أثناء أي Recomposition، ويُلغى فقط عند مغادرة الشاشة بالكامل.
   - **الاستخدام المثالي**: بدء أنيميشن ابتدائي لمرة واحدة، أو استدعاء حدث لمرة واحدة للشاشة.

2. كيف تعمل `LaunchedEffect(key)`؟
   - عندما يتم تمرير متغير كـ Key (مثل `userId` أو `query` أو `filter`):
   - في كل Recomposition، يقارن Compose قيمة الـ Key الحالية بالقيمة السابقة عبر `equals()`.
   - إذا تغيرت القيمة: يقوم Compose **بإلغاء الكوروتين الجاري فوراً (Cancel Job)** ويبدأ كوروتين جديد بالقيمة الجديدة!
   - **الاستخدام المثالي**: البحث اللحظي مع الكتابة (Debounced search)، وإعادة تحميل البيانات عند تغيير الـ ID المختار.

3. أخطاء شائعة (Common Traps):
   - استخدام `LaunchedEffect(Unit)` لجلب بيانات تعتمد على بارامتر `id` متغير: إذا تغير الـ `id` لاحقاً، لن يُعاد جلب البيانات ويظل المحتوى قديماً!
   - تمرير Key يتغير في كل فريم (مثل قيمة سكرول عشوائية): يؤدي إلى إلغاء وإعادة إطلاق الكوروتين 60 مرة في الثانية وإجهاد المعالج.

## Practical walkthrough

مقارنة عملية توضح متى نستخدم Unit ومتى نستخدم Dynamic Key:
```kotlin
// ❌ خطأ: استخدام Unit مع بارامتر ديناميكي؛ عند اختيار مستخدم آخر لن يتم تحديث البيانات:
@Composable
fun BadUserProfile(userId: String) {
    LaunchedEffect(Unit) {
        // 💥 إذا تغير userId لن يعمل هذا الكود مرة ثانية!
        loadUserData(userId)
    }
}

// ✅ الكود السليم: تمرير userId كـ Key؛ عند تغير الـ ID يُلغى الطلب القديم ويبدأ الجديد:
@Composable
fun GoodUserProfile(userId: String) {
    LaunchedEffect(userId) {
        // يُلغى الطلب السابق ويبدأ طلب المستخدم الجديد فوراً:
        loadUserData(userId)
    }
}

// ✅ استخدام سليم لـ Unit: مهام لا تعتمد على أي متغير وتعمل مرة واحدة فقط:
@Composable
fun SplashScreen(onTimeout: () -> Unit) {
    LaunchedEffect(Unit) {
        delay(2000)
        onTimeout()
    }
}
```

## Why it matters and how it works

LaunchedEffect ties a coroutine to composition and its key set. A stable key avoids restart during ordinary recomposition at the same call site. A changed key cancels the old coroutine and starts the block again. The key should represent the identity that requires a new operation; unrelated state in the key causes needless cancellation, while missing identity causes stale work.

## Worked example

`LaunchedEffect(articleId)` scrolls to or loads information for the current article. Navigating from article A to B without leaving the same composable call site cancels A's composition-owned operation and starts B's. A one-time entrance animation with no input identity can use `Unit`. If the repository load belongs to a ViewModel and must survive temporary UI absence, invoke it from that owner instead.

### Compose/Kotlin walkthrough

```kotlin
@Composable
fun ArticleScreen(articleId: String, onVisible: suspend (String) -> Unit) {
    LaunchedEffect(articleId) { onVisible(articleId) }
    Text("Article $articleId")
}
// A -> B at the same call site cancels A's effect and starts B's.
// For a callback that can change without restarting, use rememberUpdatedState.
```

## Trade-offs and decision criteria

Constant keys are simple for call-site lifetime tasks, but can conceal stale inputs. Variable keys handle identity changes but restart expensive work when keys change frequently. A ViewModel operation follows its own lifecycle and can better coordinate deduplication, caching or navigation.

## Failure modes

A user ID changes while a Unit-keyed effect continues listening to the old account. A lambda passed as key changes every recomposition and restarts the effect repeatedly. A long payment submission is canceled when the composable exits, leaving unknown status without a durable recovery path.

## Production perspective

Document each effect's identity and cancellation semantics. Test navigation between IDs without recreating the whole Activity, and observe side-effect starts under recomposition. For durable or high-value requests, use a stable owner and backend recovery.

## Interview answer — short

LaunchedEffect(Unit) executes its suspending block once when entering composition and only cancels when the composable leaves the composition entirely. In contrast, LaunchedEffect(key) binds coroutine execution to dynamic state. Whenever the key changes, Compose cancels the existing coroutine and restarts a new one with the latest value. Using Unit for dynamic parameters produces stale state bugs, while using a rapidly changing key causes continuous cancellation thrashing.

## Interview answer — structured

Mastering the key semantics of LaunchedEffect is essential for preventing coroutine lifecycle leaks and stale asynchronous operations in Jetpack Compose.
When you pass a constant like Unit or true to LaunchedEffect, you instruct the Compose runtime that the side-effect has no external dynamic dependencies. The runtime allocates the coroutine scope when the composable enters the composition tree and maintains that scope untouched across subsequent recompositions. It only cancels the job when the composable unmounts. This makes LaunchedEffect(Unit) ideal for one-time initialization tasks, such as triggering an initial analytics screen-view beacon or requesting runtime Bluetooth permissions upon screen opening.
However, passing Unit when the coroutine reads a changing parameter is a hazardous anti-pattern that creates stale closures.
If a screen accepts an itemId and you launch your network fetch inside LaunchedEffect(Unit), changing the itemId will never trigger a reload because the key never changes.
Passing LaunchedEffect(itemId) solves this cleanly.
Whenever itemId updates, Compose cancels the running coroutine and starts a new one with the fresh identifier.
If a network call was in flight, its cancellation signal cascades upstream, terminating the active HTTP connection and conserving mobile data.

## Interview answer — deep senior

Under the hood, LaunchedEffect delegates to the Composer's internal effect management APIs and integrates directly with Kotlin Coroutines cancellation machinery.
When the Compose compiler processes LaunchedEffect, it stores a LaunchedEffectImpl object inside the SlotTable. This object retains the previous key argument and the running Job reference.
During each recomposition pass, the Composer executes an equality comparison between the current key argument and the key stored in the slot using standard structural equality (equals).
If the keys are equal, the Composer skips the effect entirely, allowing the running coroutine job to proceed undisturbed.
If the key has changed, the Composer executes Job.cancel() on the existing coroutine job. This throws a CancellationException inside the coroutine, cleanly canceling any suspending network calls, delay timers, or database transactions.
Once cancellation completes, the Composer launches a brand-new coroutine on the composition's Apply-dispatcher, passing the latest lambda block.
Senior engineers must be cautious with key selection. Passing an unstable object or an object that generates new instances on every recomposition triggers cancellation thrashing, where the coroutine is cancelled and relaunched on every single frame before finishing its work.
Conversely, if an effect reads multiple changing state values, developers should pass multiple keys or a consolidated data holder to ensure complete synchronization.

## How to answer in the interview

- **Why:** keys define when composition-owned work restarts.
- **How:** compare A to B under Unit versus articleId.
- **Trade-off:** restarting cancels in-flight work.
- **Failure case:** missing key leaves stale identity; excess keys cause needless restarts.
- **Production solution:** key by work identity and move durable work to ViewModel.

## Deep-dive talking points

Explain call-site identity, cancellation, key selection, stale captures, and durable ownership.

## Follow-up questions

- **Interviewer:** "What is the consequence of passing an object with broken `equals()` as a key in `LaunchedEffect`?"
  **Answer:** "If `equals()` always returns false (or defaults to identity equality for unmemoized instances), `LaunchedEffect` will cancel and restart on every single recomposition, causing infinite loops and UI thrashing."

- **Interviewer:** "How do you access the latest value of a changing callback inside `LaunchedEffect(Unit)`?"
  **Answer:** "Wrap the callback in `val currentCallback by rememberUpdatedState(onTimeout)`. The effect won't restart, but invoking `currentCallback()` accesses the latest callback passed from the parent."

## Self-check rubric

Choose keys for two examples, explain cancellation, and identify one task that belongs outside composition.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — key and cancellation behavior.

Technically reviewed against primary documentation on 2026-10-13.
