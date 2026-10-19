---
id: "MEM-01"
question: "What is memory management in Android? What does garbage collection do?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 56
editorial_status: "reviewed"
---

# MEM-01

## Original interview question

What is memory management in Android? What does garbage collection do?

## What the interviewer evaluates

- Distinguish managed heap collection from full process memory and Android process management.
- Explain reachability, retained references, allocation churn, and resource ownership.
- Diagnose a leak or jank with measurement rather than a universal heap or GC promise.

## Concept and technical explanation

An Android app process has an ART-managed heap for Java and Kotlin objects alongside native, graphics, stack, code, and other memory. The heap limit varies by device; `ActivityManager.getMemoryClass()` reports the approximate normal heap class for the current device. Managed heap size and physical process footprint are different measurements. Under system pressure Android may kill a lower-priority process, so important user state must survive process recreation.

ART's garbage collector traces managed objects reachable from roots such as active stacks, static fields, and JNI references. It reclaims objects that become unreachable. It cannot collect an obsolete Activity while a listener still references it. It also cannot replace explicit closing of streams, cursors, native handles, and other owned resources. Collection work and allocation rate can affect latency; exact pauses depend on runtime and device.

## Practical walkthrough (English)

Suppose opening and closing a photo screen repeatedly raises memory usage. Reproduce on a representative device and inspect a heap dump for retained Activities. If an application-scoped listener holds the old view, unregister it at the appropriate lifecycle boundary. If no screen is retained but scrolling raises the footprint, inspect image decode sizes, native or graphics memory, allocations, and frame timing. A cache can reduce repeated decoding but needs a budget. A falling managed-heap chart alone does not establish that the whole process is healthy.

## Explanation in Arabic

الـ Memory في Android مش رقم واحد. عندك Managed Heap لكائنات Kotlin وJava، وعندك Native وGraphics وStack وغيره. حجم الـ Heap المسموح بيختلف حسب الجهاز، و`getMemoryClass()` يديك فئة الحد التقريبية على الجهاز الحالي؛ ما ينفعش أحفظ رقم ثابت لكل Android. والـ OS ممكن ينهي Process أقل أولوية وقت ضغط الذاكرة، فحالة المستخدم المهمة لازم تتعاد بعد Process Death.

الـ Garbage Collector في ART يشوف كائنات الـ Managed Heap اللي لسه ممكن توصل لها من GC Roots، ويرجع مساحة الكائنات اللي بقت Unreachable. لو Singleton ماسك Activity قديمة، هي لسه Reachable، فالـ GC مش هيحل المشكلة. وهو كمان مش بديل عن قفل Stream أو Cursor أو تحرير مورد Native بملكية واضحة. تكرار Allocations ممكن يزود شغل الـ GC ويأثر على سلاسة الشاشة؛ التأثير الحقيقي يتقاس على الجهاز.

## Practical walkthrough

لو شاشة صور بتفتح وتقفل وMemory بتعلى كل مرة، أعيد نفس الرحلة على جهاز مناسب وأشوف Heap Dump: هل Activity قديمة لسه محتفظ بيها Listener؟ ساعتها أصلح Ownership وأشيل التسجيل عند Lifecycle المناسب. لو مفيش Retained Activity لكن الاستهلاك بيعلى وقت Scroll، أبص على حجم الصور وقت Decode وعلى Native/Graphics Memory، وأقيس Frame Timing وAllocations. ممكن Cache تقلل فك الصور المتكرر، بس لازم Budget واضح بدل ما تفضل تكبر.

## Why it matters and how it works

A leak is a reference keeping an object alive after its intended owner is gone. Churn is repeated short-lived allocation that can add collector CPU work or pauses without a leak. An oversized image or native buffer can increase the process footprint even if managed object counts appear stable. Process death under memory pressure is a separate concern and can occur without a Java out-of-memory exception.

## Worked example

Diagnostic example: after repeated open/close cycles, a heap dump shows old photo Activities retained by one application-scoped observer. Remove the observer at the view lifecycle boundary and repeat the same journey. Separately, decode thumbnails near display size and measure native or graphics footprint and frame timing. This is a method, not an asserted benchmark result.

## Trade-offs and decision criteria

A bounded image cache trades memory for less decoding work. Pooling objects in a hot path adds ownership complexity and should follow measured allocation pressure. Calling `System.gc()` is not a reliable fix for a retained reference or oversized allocation. Use heap dumps for retained graphs, allocation profiling for churn, and process metrics for native or graphics pressure.

## Failure modes

A static listener retains an Activity and its view tree. Repeated allocations can add GC work and affect frame deadlines. Large images or native buffers consume memory outside a simple managed-object count. An unclosed stream or cursor remains owned. Low-memory process death need not call `onDestroy()` for state saving.

## Production perspective

Compare the same journey and device class before and after a change. Inspect retained graphs, Java and native categories, graphics footprint, and PSS where relevant. Track OOM events and process deaths separately. Test low-memory devices and preserve essential user state through process recreation. Avoid universal heap-size or pause-duration claims.

## Interview answer — short

Android memory management includes the ART managed heap and the rest of the process, including native and graphics memory. The GC reclaims managed objects that are no longer reachable. It cannot free an Activity still held by a listener, or replace closing a file or cursor. I diagnose rising memory by checking retained references, allocations, and the full process footprint instead of calling `System.gc()`.

## Interview answer — structured

I separate three things: ART's managed heap, the rest of process memory, and Android's decision to keep or kill a process under pressure. The heap limit varies by device. ART's GC traces reachable managed objects and reclaims those no longer reachable. That is automatic memory reclamation, not automatic ownership of every resource.

If a photo screen keeps growing after repeated navigation, I inspect a heap dump for old Activities held by a listener. If there is no retained screen but scrolling stutters, I check allocation rate, image decode size, native or graphics memory, and frame timing. A leak and temporary allocation churn need different fixes.

I remove the leaked reference at the correct lifecycle boundary, use size-aware image loading, and bound caches. A GC call cannot fix a reachable leak. I repeat the measurement on a representative device and test that essential UI state returns after Android kills the process.

## Interview answer — deep senior

The managed heap is only part of an Android process. ART allocates Kotlin and Java objects there and uses reachability from GC roots to identify what can be reclaimed. A singleton, active listener, thread, or JNI global can keep an obsolete graph alive. Collector implementations and pauses vary across Android versions and devices, so I avoid saying GC is pause-free or every app has one fixed heap size.

I distinguish retention from churn. A retained Activity after its screen is gone points to an ownership problem; I take a heap dump and trace the path to a root. Frequent short-lived allocations may raise GC CPU work or delay frames even when the steady-state heap does not grow. I profile allocations and frame timing on the affected device. Native buffers, decoded images, and graphics resources can affect process footprint beyond a simple Java-object count; I inspect the relevant memory categories and PSS.

GC does not close a stream at a predictable time or know when a listener should stop owning a screen. I close resources explicitly and unregister observers at their lifecycle boundary. For an image-heavy screen, I decode to the needed size and set a bounded cache; caching reduces repeated work but increases retained memory. I compare the same journey before and after the change rather than relying on an invented benchmark. Android may kill a cached process under pressure without an OOM exception or final callback, so important state has to be recoverable.

## How to answer in the interview

Define managed heap reachability, separate it from full process memory and process death, then walk through one leak-versus-churn diagnosis. Name the measurement and fix for each.

## Deep-dive talking points

GC roots and retained graphs; churn versus leaks; native and graphics footprint; device-dependent heap limits; bounded caches; resource closing; process recreation.

## Follow-up questions

- **Interviewer:** "Will `System.gc()` fix a leak?" **Answer:** "No. A reachable object is still live, and a manual request is not a reliable memory policy. I find and remove the retaining reference."
- **Interviewer:** "Can GC close a Cursor or Stream for me?" **Answer:** "I close resources at their ownership boundary; GC timing is not a lifecycle contract."
- **Interviewer:** "Why can memory pressure rise while the Java heap looks stable?" **Answer:** "Native buffers or graphics allocations may be growing. I inspect the whole process footprint."

## Self-check rubric

Can I explain reachability, distinguish leak from churn, name a non-heap resource, and choose the measurement that tests each hypothesis?

## References and reviewed-on date

- [Android memory management overview](https://developer.android.com/topic/performance/memory-overview) — heap, GC, memory limits, and process pressure.
- [Android memory guidance](https://developer.android.com/topic/performance/memory) — diagnostic tools and memory categories.

Technically reviewed against current primary Android documentation on 2026-10-19; agent editorial review, not human verification.
