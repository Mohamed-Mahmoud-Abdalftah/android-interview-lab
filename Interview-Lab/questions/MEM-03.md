---
id: "MEM-03"
question: "Compare stack and heap at a high level. What lives on each?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 58
editorial_status: "reviewed"
---

# MEM-03

## Original interview question

Compare stack and heap at a high level. What lives on each?

## What the interviewer evaluates

- Give a useful stack-frame versus managed-heap model without false “all primitives on stack” rules.
- Explain references, object lifetime, thread stacks, and allocation behavior in Java/Kotlin on ART.
- Connect deep recursion and retained objects to different failures.

## Explanation in Arabic

كل thread لها call stack فيها frames لاستدعاءات الدوال: return addresses، local slots وبيانات التنفيذ. الـmanaged heap فيه objects وarrays اللي عمرها قد يمتد بعد انتهاء الدالة. المتغير المحلي ممكن يكون reference في stack frame يشير إلى object في heap؛ ولا يصح نقول “كل primitive على stack وكل object على heap” كقاعدة حرفية لأن compiler وruntime ممكن يعملوا optimization. الـstack تنمو مع الاستدعاء المتكرر، والـheap تتأثر بالـallocations والـretention. `StackOverflowError` من recursion عميق مختلف عن `OutOfMemoryError` بسبب heap أو موارد أخرى.

## Why it matters and how it works

Method invocation creates a frame with locals and operand state for that thread; it leaves the frame on return. Objects generally occupy the managed heap and remain until unreachable and collected. A local reference can temporarily make a heap object reachable; capturing that object in a longer-lived callback extends its life beyond the call. ART may optimize representation, so the model guides reasoning but is not a promise about every byte's physical location.

## Worked example

`fun render(photo: Photo) { val label = photo.title }` adds a frame and local references during the call, while the `Photo` instance can outlive it if a repository cache retains it. A recursive tree walker with no depth bound can exhaust its thread stack; replacing it with an explicit deque can bound stack depth while still using heap memory. This is explanatory Kotlin, not a benchmark or standalone Android component.

## Trade-offs and decision criteria

Recursion is concise for bounded trees but risks stack exhaustion with adversarial depth. An iterative algorithm moves traversal state to a heap collection and requires an explicit memory bound. Avoid premature “stack allocation” optimization claims in Kotlin; profile actual allocations and retention. Thread creation also consumes stack and native memory, so an unbounded thread pool is a process-memory problem.

## Failure modes

A self-recursive parser with no termination reaches `StackOverflowError`. A singleton retains a huge object graph on the heap long after methods return. Thousands of threads consume stack/native memory. Confusing the two can lead to treating an OOM as recursion or expecting a local variable to free a cached object. Use stack traces, heap dumps, and thread/memory profiles to distinguish.

## Production perspective

When a production crash reports stack overflow, inspect the recursive call path and input depth; cap depth or use iteration. When memory grows, inspect heap retaining paths and non-heap categories. Avoid a blanket “clear all locals” fix: ownership, cache limits, and thread scheduling matter more than surface syntax.

## Interview answer — short

“A thread stack holds active call frames and local execution state. The heap holds managed objects whose lifetime can outlast one call. A local reference may point to a heap object, so the primitive-versus-object slogan is too simplistic.”

## Interview answer — structured

“Each thread has a stack of frames for active calls, including local slots and return flow. Managed objects and arrays generally live in the heap and are reclaimed when unreachable. A stack local may hold a reference to a heap object; a callback or cache can keep that object alive after the method returns. Deep recursion threatens stack space, while retained objects and large allocations threaten heap or process memory. Runtime optimizations mean I use this as a reasoning model, not a strict byte-placement rule.”

## Interview answer — deep senior

“I explain stack and heap in terms of lifetime and ownership. A thread's stack represents nested execution; returning from a function removes its frame. The managed heap supports objects that can survive that function, depending on references from live frames, static fields, and other roots. A reference stored in a frame can keep an object reachable for the call, but a singleton or long-lived callback can retain it far longer. Recursion depth can exhaust stack space; a heap OOM has a different diagnostic path, and native/thread memory also affects the process. ART optimizations may elide allocations or change representation, so I do not claim every primitive always sits on stack. I use crash stacks and heap/thread profiles to decide whether to bound recursion, release retained graphs, or limit thread creation.”

## Deep-dive talking points

Discuss frames, references, object lifetime, compiler optimization, recursion depth, thread stacks, and heap retention.

## Follow-up questions

- Does returning from a function immediately destroy an object it created? **Answer:** no; the object can remain reachable through another reference and GC timing is not immediate.
- Can a local reference keep a heap object alive? **Answer:** yes while it is considered live by the runtime; another owner may keep it longer.
- Is `StackOverflowError` the same as heap OOM? **Answer:** no; it normally indicates excessive call-stack depth, though both are memory-related failures.

## Self-check rubric

Define a frame, explain a local-to-heap reference, reject the primitive slogan, and diagnose recursion versus retention.

## References and reviewed-on date

- [JVM runtime data areas](https://docs.oracle.com/en/java/javase/26/docs/specs/jvms/jvms-2.html#jvms-2.5) — stacks and heap conceptual model.
- [Android memory overview](https://developer.android.com/topic/performance/memory-overview) — ART process and heap behavior.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The Kotlin examples are illustrative.
