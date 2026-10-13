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

`LaunchedEffect(Unit)` executes its coroutine once upon entering composition and cancels it only when leaving composition. `LaunchedEffect(key)` executes on entry and automatically cancels and restarts its coroutine whenever `key` changes (via `equals()`). Choosing the wrong key leads to either stale data or thrashing restarts.

## Interview answer — structured

The difference between `LaunchedEffect(Unit)` and `LaunchedEffect(key)` lies in restart semantics based on key equality.

1. **`LaunchedEffect(Unit)`**: Because `Unit` is a constant singleton, its key never changes. The coroutine launches when the composable initially enters the composition and remains running until the composable leaves the composition tree. It is ideal for fire-and-forget one-off operations that are independent of changing inputs, such as playing a screen-entry sound or showing an introductory prompt.

2. **`LaunchedEffect(key)`**: Takes one or more dynamic keys (e.g. `query`, `filterId`). On every recomposition pass, Compose compares current keys against their previous instances using `equals()`. If any key has changed, Compose automatically cancels the running coroutine job cooperatively and launches a new one with the updated values. This is essential for operations like dynamic querying, pagination, or debouncing input.

## Interview answer — deep senior

A dangerous production bug occurs when developers use `LaunchedEffect(Unit)` while capturing changing parameters inside its lambda closure. Because the coroutine never restarts, the captured closure holds **stale references** to variables from the initial composition pass. If those variables must not restart the effect, developers should use `rememberUpdatedState` to read the freshest value without restarting the coroutine.

Conversely, passing unstable or constantly changing keys (like `currentTimeMillis()` or non-memoized objects) triggers **restart thrashing**: canceling and spawning hundreds of coroutines per second, pegging the CPU and dropping frames.

If an effect depends on multiple inputs, Compose supports vararg keys: `LaunchedEffect(key1, key2)`. The effect restarts if either key changes.

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
