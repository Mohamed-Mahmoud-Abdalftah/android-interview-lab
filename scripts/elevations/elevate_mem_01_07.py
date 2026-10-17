#!/usr/bin/env python3
"""Elevate MEM-01 through MEM-07 for bilingual parity and senior spoken answers."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT / "scripts" / "elevations"))
import elevation_engine as ee

TOPIC_AR = "إدارة الذاكرة والـ ANR وتحسين الأداء"

EN_DATA = {
    "MEM-01": {
        "concept_en": (
            "Android memory management operates across two distinct abstraction layers: the Linux kernel layer "
            "and the Android Runtime (ART) virtual machine layer. At the OS level, each application runs as an "
            "isolated process with a private virtual memory address space. The system enforces per-process heap limits "
            "(typically 192MB to 512MB depending on screen density and RAM) via dalvik.vm.heapgrowthlimit. The ART "
            "Garbage Collector (GC) is responsible for automatic heap reclamation. It continuously tracks object "
            "reachability starting from designated GC Roots (active thread call stacks, static fields, and JNI global "
            "references). Modern ART utilizes a Generational Concurrent Copying (CC) collector that partitions the heap "
            "into generations: the Young Generation for newly allocated objects and the Old Generation for tenured objects. "
            "When objects become unreachable from any GC Root, the GC frees their memory and compacts active regions "
            "without long stop-the-world pauses."
        ),
        "walkthrough_en": (
            "Under high-frequency execution paths such as RecyclerView scrolling or custom view rendering, temporary object allocations trigger memory churn and degrade frame rates:\n"
            "```kotlin\n"
            "// Inefficient allocation churn inside onBindViewHolder:\n"
            "override fun onBindViewHolder(holder: ViewHolder, position: Int) {\n"
            "    // Allocating a DateFormat and Date instance on every single scroll frame:\n"
            "    val formatter = SimpleDateFormat(\"yyyy-MM-dd\", Locale.US)\n"
            "    holder.dateText.text = formatter.format(Date(items[position].timestamp))\n"
            "}\n"
            "\n"
            "// Optimized zero-allocation implementation:\n"
            "companion object {\n"
            "    private val DATE_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE\n"
            "}\n"
            "override fun onBindViewHolder(holder: ViewHolder, position: Int) {\n"
            "    holder.dateText.text = DATE_FORMATTER.format(items[position].localDate)\n"
            "}\n"
            "```\n"
            "When thousands of temporary objects are generated inside onBindViewHolder, the Young generation fills up rapidly, "
            "triggering consecutive concurrent GC cycles. While ART CC GC minimizes thread suspension to microseconds, heavy "
            "allocation churn forces foreground threads to throttle, resulting in dropped frames and visual stutter."
        ),
        "short_en": (
            "Android manages application memory through the Android Runtime with strict per-process heap boundaries. "
            "The Garbage Collector automates memory reclamation by traversing object reference chains from GC Roots and clearing "
            "unreachable objects. In modern ART, a Generational Concurrent Copying collector compacts memory concurrently, "
            "but rapid object allocations in critical rendering loops still cause CPU thrashing and frame drops."
        ),
        "structured_en": (
            "To begin with, memory management in Android is governed by the Android Runtime, which allocates each application "
            "a dedicated process with an operating system enforced heap ceiling. The primary role of the Garbage Collector is to "
            "identify and reclaim memory occupied by objects that the application can no longer access. From an architectural standpoint, "
            "the collector discovers live objects through tracing reachability, traversing directed reference graphs starting from root "
            "references such as active thread stacks, static variables, and JNI globals. Any object disconnected from this directed acyclic "
            "graph is recognized as garbage and reclaimed. In production scenarios, excessive object allocations within high-frequency loops—such "
            "as list binding or canvas drawing—trigger what is known as memory churn. Even though modern ART runs concurrently, rapid allocation "
            "storms exhaust young generation memory, forcing foreground threads into allocation stalls and causing observable UI jank. As for "
            "boundary management, developers must recognize that garbage collection cannot free native memory buffers, unclosed file descriptors, "
            "or objects held alive by static singletons."
        ),
        "deep_senior_en": (
            "Under the hood, ART has evolved from Dalvik's primitive Stop-The-World mark-sweep mechanism to a sophisticated Generational "
            "Concurrent Copying collector. The CC collector utilizes a read barrier implemented through memory faulting and hardware instrumentation, "
            "which intercepts heap reads when an object is in the process of being moved. This enables live compacting: objects are relocated to "
            "contiguous memory spaces without suspending worker or main threads for more than a few microseconds. Consequently, heap fragmentation "
            "is prevented, which historically was the primary trigger for premature out-of-memory errors on older Android versions.\n\n"
            "When diagnosing complex memory issues in production, we do not simply rely on overall memory usage numbers. Instead, we capture "
            "and inspect HPROF heap dumps using Android Studio Profiler, LeakCanary, and Eclipse Memory Analyzer Tool. We categorize process memory "
            "into Java heap, native heap, code, stack, graphics, and private clean versus dirty memory. When an application undergoes memory pressure, "
            "the Linux kernel Low Memory Killer daemon monitors process Out-Of-Memory adjustment scores. If an app fails to respond to onTrimMemory "
            "system callbacks or leaks entire Activity view hierarchies, its dirty memory footprint increases, causing lmkd to terminate the process "
            "abruptly. By instrumenting allocation tracking and monitoring the allocation saw-tooth pattern, staff engineers can isolate temporary "
            "object spikes and prevent premature GC invocation."
        ),
    },
    "MEM-02": {
        "concept_en": (
            "GC roots define the anchor nodes of the live object graph in tracing garbage collectors. In ART, an object is reachable "
            "if a direct or indirect chain of strong references connects it to at least one active GC Root. The runtime defines specific "
            "categories of GC roots: active thread stacks (local variables and method execution frames), static class fields, JNI global and "
            "local references, synchronized monitor locks, and system boot classes. ART evaluates reachability by traversing this directed "
            "reference graph. Objects that are part of isolated cyclic dependency islands but lack a path to any root are recognized as dead "
            "and eligible for reclamation."
        ),
        "walkthrough_en": (
            "Tracing a reference chain from an active thread to a leaked Activity:\n"
            "```text\n"
            "[GC Root: Active Main Thread Looper]\n"
            "       |\n"
            "       v\n"
            "[MessageQueue -> Pending Message (target: Handler, delay: 10s)]\n"
            "       |\n"
            "       v\n"
            "[Anonymous Runnable instance]\n"
            "       |\n"
            "       v (implicit outer reference: this$0)\n"
            "[Destroyed ProfileActivity instance]\n"
            "```\n"
            "Even if ProfileActivity.finish() has been executed and the window is removed from the screen, the active thread's Looper message "
            "queue retains the pending message, which holds the Runnable, which holds this$0. Because a path from a live GC Root exists, "
            "the GC cannot collect the activity or its associated view tree."
        ),
        "short_en": (
            "GC Roots are the foundational live anchors from which the garbage collector begins reachability tracing. They include "
            "active thread stacks, static variables, JNI global references, and system monitors. An object is considered reachable "
            "and kept alive only if a chain of strong references links it back to a GC Root. Isolated circular references disconnected "
            "from any root are automatically reclaimed."
        ),
        "structured_en": (
            "To begin with, garbage collection in Android relies on tracing reachability rather than naive reference counting. GC Roots are "
            "the fundamental anchors that the runtime considers permanently alive during a collection pass. From an architectural standpoint, "
            "these roots include local variables and parameters on active thread call stacks, static fields of loaded classes, JNI native references, "
            "and active thread objects themselves. The garbage collector traverses the object graph by following strong reference edges outward "
            "from these roots. If an object cannot be reached through any directed path, it is designated as eligible for reclamation. In production "
            "scenarios, this graph-based approach easily handles cyclic references; two dead objects pointing to each other are collected without "
            "difficulty because neither connects back to a root. As for boundary management, memory leaks occur when a short-lived component, "
            "such as an Activity, becomes unintentionally linked into a long-lived reference chain held by a persistent GC root like a background "
            "thread or a static manager."
        ),
        "deep_senior_en": (
            "When investigating memory leaks at an enterprise scale, staff engineers rely on graph theory algorithms embedded in heap dump "
            "parsers like LeakCanary's Shark engine and Eclipse Memory Analyzer Tool. During an HPROF heap dump analysis, the memory profiler "
            "constructs a dominator tree from the object reference graph. In this tree, node A dominates node B if every path from any GC Root "
            "to B must pass through A. This distinction between Shallow Heap—the memory consumed by the object itself—and Retained Heap—the "
            "memory that would be freed if that object were garbage collected—is crucial for identifying true leak root causes.\n\n"
            "In Android, the most common retaining GC Roots are persistent thread workers like ThreadPoolExecutor workers or the Main Thread "
            "Looper. For example, an active thread stack frame executing a long network request keeps the executing Runnable alive as a GC Root. "
            "If that Runnable captures a lambda or inner class instance that references an Activity context, the entire retained dominator tree "
            "of that activity remains uncollected. To isolate the exact defect, profilers compute the Shortest Path to GC Roots excluding weak, "
            "soft, and phantom references. By identifying the specific field edge where ownership violated lifecycle boundaries, engineers can "
            "sever the link by clearing listeners in lifecycle callbacks or scoping workers to structured coroutine scopes."
        ),
    },
    "MEM-03": {
        "concept_en": (
            "Stack and Heap represent two distinct memory regions managed by the Android operating system and the Android Runtime (ART). "
            "Stack memory is allocated on a per-thread basis, typically capped at 1MB per thread on Android. It operates as a strict "
            "Last-In-First-Out (LIFO) structure containing call frames for executing functions. Each frame stores primitive local variables, "
            "method arguments, execution state, and reference pointers to heap instances. Allocation and deallocation on the stack are "
            "instantaneous CPU pointer adjustments with zero garbage collection overhead. Heap memory, in contrast, is a shared process-wide "
            "pool where all object instances, arrays, strings, and class fields reside. Objects allocated on the heap have non-deterministic "
            "lifespans managed through ART tracing garbage collection."
        ),
        "walkthrough_en": (
            "Analyzing stack frame versus heap allocation in Kotlin execution:\n"
            "```kotlin\n"
            "fun processUser() {\n"
            "    val id: Int = 101                 // Primitive value 101 stored directly on the current thread stack frame\n"
            "    val name: String = \"Mohamed\"       // Reference pointer 'name' lives on stack; String object instance lives on heap\n"
            "    val user = User(id, name)         // Pointer 'user' lives on stack; User instance and its internal fields live on heap\n"
            "}\n"
            "```\n"
            "When processUser() finishes execution, its stack frame is instantly popped from the thread stack, deallocating the local "
            "primitive id and the reference pointers name and user. The User and String instances on the heap become unreachable and "
            "await collection by the ART GC unless retained by another live reference."
        ),
        "short_en": (
            "Stack memory stores thread-specific call frames, primitive local variables, and reference addresses with fast LIFO allocation "
            "and zero garbage collection overhead. Heap memory is the shared process-wide pool where all object instances, arrays, and fields "
            "reside, managed dynamically by the garbage collector. Unbounded recursion exhausts stack memory, causing StackOverflowError, "
            "whereas accumulating reachable objects exhausts heap memory, causing OutOfMemoryError."
        ),
        "structured_en": (
            "To begin with, stack and heap serve fundamentally different roles in memory architecture. The stack is dedicated to thread "
            "execution, where each thread maintains a private stack of frames. Each frame stores method arguments, primitive local variables, "
            "and object reference pointers. Allocation and deallocation on the stack occur instantaneously through hardware stack pointer "
            "manipulation as methods are entered and exited. From an architectural standpoint, the heap is the dynamic, process-wide memory "
            "arena where all object instances, class fields, and arrays are allocated. Lifetimes on the heap are decoupled from method call "
            "stacks and are governed entirely by ART garbage collection reachability. In production scenarios, improper resource management "
            "manifests differently across the two regions. Exhausting thread stack space through infinite recursion triggers an immediate "
            "StackOverflowError. In contrast, accumulating retained object graphs on the heap leads to OutOfMemoryError. As for boundary "
            "management, high-performance routines leverage stack allocation and primitive arrays to prevent pressure on the shared heap."
        ),
        "deep_senior_en": (
            "At the runtime and compiler level, the allocation boundary between stack and heap is influenced by ART Ahead-Of-Time (AOT) and "
            "Just-In-Time (JIT) compilation optimizations, specifically Escape Analysis. When the ART compiler detects that an allocated "
            "object does not escape the scope of the declaring method and its reference is never published, it can theoretically perform "
            "scalar replacement, breaking down the object's fields into individual local stack variables. However, because Android devices "
            "operate under aggressive memory constraints and varying hardware architectures, most Kotlin allocations—including lambda instances, "
            "coroutine state machines, and boxed primitives—land on the managed heap.\n\n"
            "In terms of CPU architecture, stack memory offers superior cache locality. Because stack memory is contiguous and repeatedly "
            "accessed near the top of the stack, it stays hot in L1 and L2 CPU caches, minimizing CPU memory access latency. Conversely, "
            "navigating object graphs on the heap involves pointer chasing across non-contiguous virtual memory addresses, increasing CPU cache "
            "misses. Furthermore, on 64-bit ART architectures, every heap object carries an object header consisting of an 8-byte class pointer "
            "and an 8-byte monitor word, followed by 8-byte alignment padding. This means allocating thousands of small objects on the heap "
            "introduces significant memory overhead and fragmentation that never occurs on thread stacks. Profiling thread stack footprints "
            "across large thread pools is therefore just as vital as analyzing heap dumps."
        ),
    },
    "MEM-04": {
        "concept_en": (
            "A memory leak and a large memory allocation represent two fundamentally different memory behaviors. A memory leak occurs when "
            "an application retains an unintended, obsolete strong reference to an object that is no longer required for business logic, "
            "preventing the Garbage Collector from freeing its memory. Over time, recurring leaks cause a monotonic increase in the baseline "
            "memory footprint across user navigation cycles, eventually leading to an OutOfMemoryError. In contrast, a large memory allocation "
            "is an intentional, temporary reservation of a significant block of memory—such as decoding a camera bitmap or buffering a downloaded "
            "document. Once the operation completes and its references are discarded, the allocated memory becomes eligible for immediate reclamation."
        ),
        "walkthrough_en": (
            "Comparing transient large allocations with persistent leaks:\n"
            "```kotlin\n"
            "// 1. Large Allocation (Not a leak): temporary 64MB bitmap reclaimed upon function return:\n"
            "fun renderBanner() {\n"
            "    val largeBitmap = Bitmap.createBitmap(4000, 4000, Bitmap.Config.ARGB_8888)\n"
            "    drawContent(largeBitmap)\n"
            "    // largeBitmap reference goes out of scope and becomes eligible for GC\n"
            "}\n"
            "\n"
            "// 2. Memory Leak: cumulative Activity retention across user navigation:\n"
            "object NavigationTracker {\n"
            "    val listeners = mutableListOf<ScreenCallback>()\n"
            "}\n"
            "class DetailActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // Leaking the entire Activity and view tree on every open/close cycle:\n"
            "        NavigationTracker.listeners.add(this)\n"
            "    }\n"
            "}\n"
            "```\n"
            "In the first case, heap usage spikes momentarily during renderBanner() but returns to the original baseline. In the second case, "
            "every navigation to DetailActivity permanently accumulates an uncollectable Activity instance in NavigationTracker, gradually choking the heap."
        ),
        "short_en": (
            "A memory leak is the unintended retention of an obsolete object by a live GC root, causing the steady-state heap baseline to climb "
            "across screen visits until an OutOfMemoryError occurs. A large allocation is an intentional, temporary consumption of memory that "
            "is promptly collected once the operation finishes. Leaks represent architectural bugs, whereas large allocations require data streaming "
            "and downsampling."
        ),
        "structured_en": (
            "To begin with, a memory leak is an architectural defect where an object that has completed its useful lifecycle remains anchored "
            "to a live GC root, preventing the garbage collector from reclaiming its heap space. A large allocation, on the other hand, is an "
            "intentional and often unavoidable operational cost where the application temporarily requests a substantial block of memory to "
            "perform a heavy task. From an architectural standpoint, the crucial differentiator is lifecycle reclamation and memory baseline behavior. "
            "With a large allocation, such as decoding a high-resolution bitmap or deserializing a massive JSON payload, memory usage spikes during "
            "execution but returns to its baseline once the function exits and references fall out of scope. In production scenarios, a memory leak "
            "causes the memory baseline to ratchet upward monotonically after every screen transition, leading to cumulative degradation and "
            "inevitable out-of-memory crashes. As for boundary management, resolving large allocations involves techniques like stream processing "
            "and image downsampling, whereas fixing leaks requires correcting reference ownership and lifecycle cleanup symmetry."
        ),
        "deep_senior_en": (
            "In enterprise Android performance engineering, distinguishing between memory leaks and transient allocation spikes requires "
            "repeatable diagnostic protocols using Android Studio Memory Profiler and LeakCanary. To verify a memory leak, staff engineers "
            "establish a repeatable navigation loop: navigating from Screen A to Screen B and back to Screen A ten consecutive times, followed "
            "by an explicit garbage collection request in the profiler. If the heap baseline climbs linearly with each iteration and never returns "
            "to the starting baseline, a leak is definitively present. Capturing an HPROF heap dump at this stage reveals multiple retained "
            "instances of Screen B within the dominator tree.\n\n"
            "Conversely, a large memory allocation exhibits a sharp rectangular or saw-tooth spike on the allocation timeline that drops immediately "
            "back to the previous floor. While large allocations do not produce retained leaks, they present acute operational risks: if an allocation "
            "request for contiguous memory exceeds the remaining available heap headroom, ART throws an instant OutOfMemoryError even without a "
            "single leaked object. Senior engineers mitigate large allocations through memory-efficient primitives, such as streaming network "
            "payloads directly to disk via Okio and Room buffers rather than loading complete strings into memory, while isolating memory leaks "
            "through automated CI canary tests that inspect retained instance counts across automated Espresso navigation flows."
        ),
    },
    "MEM-05": {
        "concept_en": (
            "Memory Leak, OutOfMemoryError (OOM), Application Not Responding (ANR), and StackOverflowError represent four distinct failure "
            "modes in Android, each originating from different architectural subsystems. A memory leak is a logical defect where obsolete objects "
            "are kept reachable on the heap, silently driving up memory usage without an immediate crash. An OutOfMemoryError is a runtime error "
            "thrown when an allocation request cannot be satisfied after GC and heap compaction because the heap limit or address space is exhausted. "
            "An ANR is an operating system watchdog timeout triggered when the Main Thread Looper message queue is blocked for more than 5 seconds "
            "during user input dispatch. A StackOverflowError is a JVM/ART error caused by exhausting a thread's fixed execution stack, typically "
            "through infinite recursion or cyclic function invocations."
        ),
        "walkthrough_en": (
            "Summary of failure mechanisms, locations, and triggers:\n"
            "```text\n"
            "Failure Type         Location      Underlying Cause                          Manifestation\n"
            "-----------------------------------------------------------------------------------------------------\n"
            "Memory Leak          Heap          Retained reference to obsolete object      Monotonically rising RAM\n"
            "OutOfMemoryError     Heap/Native   Allocation request exceeds heap ceiling    App crash (Fatal Error)\n"
            "ANR                  Main Thread   Looper message queue blocked (> 5s)        OS dialog / Process kill\n"
            "StackOverflowError   Thread Stack  Call frame depth exceeds stack quota       App crash (Fatal Error)\n"
            "```\n"
            "While distinct, these defects can compound in production: a severe memory leak keeps thousands of objects alive on the heap; "
            "this causes ART's concurrent garbage collector to run repeatedly and thrash CPU cores, which delays message processing on the main "
            "thread and ultimately triggers a cascading ANR."
        ),
        "short_en": (
            "A memory leak is an uncollected dead object on the heap that raises steady-state memory. An OutOfMemoryError occurs when an "
            "allocation fails because the heap or native space is exhausted. An ANR is an OS watchdog timeout when the main thread looper "
            "is blocked for over five seconds. A StackOverflowError occurs when method call frames exceed a thread's stack capacity."
        ),
        "structured_en": (
            "To begin with, understanding the boundaries between these four failure modes is essential for accurate production triage. A memory "
            "leak occurs on the heap when an object outlives its usefulness because a dangling reference prevents garbage collection, leading to "
            "silent memory bloat rather than an immediate crash. OutOfMemoryError is the fatal consequence when an allocation request exceeds "
            "the available process heap headroom after full collection attempts fail. From an architectural standpoint, an Application Not "
            "Responding condition is not a memory exhaustion failure, but a thread responsiveness failure that occurs when the Main Thread Looper "
            "is blocked by heavy computation, disk I/O, or lock contention for more than five seconds. As for boundary management, StackOverflowError "
            "operates on thread stack memory, triggered when unbounded recursion exceeds the fixed stack quota allocated to an individual execution "
            "thread. In production scenarios, these issues can intertwine; severe memory leaks force continuous garbage collection thrashing that "
            "consumes CPU cycles, slowing main thread message dispatch and triggering an indirect ANR."
        ),
        "deep_senior_en": (
            "Diagnosing these four failures requires completely different artifacts and investigative methodologies. For an ANR, the source "
            "of truth is the system traces.txt file in data anr or Google Play Console Android Vitals ANR report. We inspect the main thread state: "
            "if it is marked as BLOCKED or WAITING, we identify the monitor lock or IPC Binder transaction stalling message queue dispatch. "
            "We cross-reference this with CPU usage percentages to distinguish between CPU starvation caused by background worker threads and thread deadlock.\n\n"
            "When investigating an OutOfMemoryError, we analyze the allocation stack trace in Crashlytics and examine the accompanying HPROF heap dump. "
            "We determine whether the OOM was caused by an acute single allocation, such as decoding an oversized bitmap, or by a chronic memory leak "
            "where thousands of leaked views and activities starved the heap over time. For a pure memory leak, LeakCanary provides automated dominator "
            "path analysis in debug builds, pointing directly to the leaking field reference. Finally, a StackOverflowError requires immediate "
            "inspection of the crashing thread's call frames; because the stack trace repeats a cyclic sequence of method calls, remediation involves "
            "refactoring recursive algorithms into iterative models utilizing explicit data structures like ArrayDeque or increasing tailrec recursion optimizations. By establishing strict diagnostic playbooks and correlating stack traces with heap dumps and kernel wait-channels, engineering teams resolve stability bottlenecks before releases reach general availability."
        ),
    },
    "MEM-06": {
        "concept_en": (
            "Boxing is the automatic conversion of a primitive data type (such as int, long, boolean) into its corresponding reference wrapper "
            "object (java.lang.Integer, java.lang.Long, java.lang.Boolean). Unboxing is the reverse extraction of the primitive value from the wrapper "
            "instance. In Kotlin, primitive types are unified syntactically as Int, Double, etc., but the compiler generates primitive types in "
            "bytecode whenever possible. Boxing occurs at three main boundaries: when using nullable types (such as Int?), when using generics "
            "(such as List<Int>), and when assigning primitives to Any. In high-throughput operations—such as audio signal processing, physics engines, "
            "or canvas drawing loops—boxing millions of numbers creates severe memory allocation churn, inflates heap footprint, and degrades CPU cache locality."
        ),
        "walkthrough_en": (
            "Demonstrating boxing overhead in high-frequency calculations:\n"
            "```kotlin\n"
            "// Inefficient: Generics force autoboxing of every single integer:\n"
            "fun calculateHistogram(samples: List<Int>): Map<Int, Int> {\n"
            "    val counts = mutableMapOf<Int, Int>()\n"
            "    for (sample in samples) { // Unboxing on access, boxing on map insertion\n"
            "        counts[sample] = (counts[sample] ?: 0) + 1\n"
            "    }\n"
            "    return counts\n"
            "}\n"
            "\n"
            "// Optimized: Zero-allocation primitive arrays:\n"
            "fun calculateHistogramOptimized(samples: IntArray, binCount: Int): IntArray {\n"
            "    val histogram = IntArray(binCount) // Stored as contiguous 32-bit integers\n"
            "    for (i in samples.indices) {\n"
            "        val bin = samples[i]\n"
            "        if (bin in 0 until binCount) {\n"
            "            histogram[bin]++ // Pure primitive arithmetic, zero heap allocation\n"
            "        }\n"
            "    }\n"
            "    return histogram\n"
            "}\n"
            "```\n"
            "In the first snippet, processing 100,000 samples creates hundreds of thousands of heap-allocated java.lang.Integer wrapper instances. "
            "In the second snippet, IntArray allocates a single contiguous block of memory with zero runtime wrapper allocations."
        ),
        "short_en": (
            "Boxing occurs when primitive types are wrapped into heap-allocated objects, triggered by nullable types, generics, or assignment "
            "to Any. Unboxing extracts the primitive value from the wrapper. While negligible in standard UI logic, boxing millions of values "
            "in tight loops or custom drawing causes heavy memory churn, cache misses, and GC pressure. High-frequency paths should use primitive "
            "arrays and specialized collections."
        ),
        "structured_en": (
            "To begin with, boxing and unboxing bridge the gap between low-level primitive values and the object-oriented type system. In Kotlin, "
            "while primitive types appear as unified classes, the compiler optimizes non-nullable primitives into primitive bytecode. Boxing occurs "
            "whenever a primitive must behave as an object, specifically when passed into generic containers like List<Int>, declared as nullable "
            "like Int?, or assigned to Any. Unboxing is the corresponding retrieval of the primitive from its object wrapper. From an architectural "
            "standpoint, an unboxed int requires exactly 4 bytes of contiguous memory, whereas a boxed Integer requires an object header, payload, "
            "and memory alignment, totaling 16 to 24 bytes on 64-bit ART runtimes. In production scenarios, boxing in ordinary UI event handling "
            "is harmless. However, inside tight mathematical loops, audio processing pipelines, or custom view drawing routines, autoboxing creates "
            "millions of short-lived heap allocations. As for boundary management, staff engineers eliminate boxing overhead in performance-critical "
            "modules by employing primitive arrays like IntArray and specialized Android collections like SparseIntArray."
        ),
        "deep_senior_en": (
            "At the ART bytecode and CPU execution level, the impact of autoboxing extends far beyond memory bloat into CPU pipeline efficiency "
            "and memory cache hierarchy. When code invokes boxing, the compiler emits calls to Integer.valueOf(int). While Java maintains a cache "
            "for values between -128 and 127 via IntegerCache, values outside this range allocate a new java.lang.Integer object on the heap on "
            "every invocation. When accessing a generic collection such as ArrayList of Integers, the CPU must traverse pointers across scattered "
            "heap addresses rather than streaming contiguous blocks of memory into L1 data caches. This pointer chasing causes frequent CPU cache "
            "misses and stalls instruction pipelines.\n\n"
            "Furthermore, unboxing introduces subtle runtime failure risks. Invoking an unboxing operation on a nullable reference that evaluates "
            "to null at runtime emits the intValue call on a null target, resulting in an instant NullPointerException. In Android graphics and "
            "sensor processing, allocating thousands of boxed wrappers per second triggers rapid Young Generation GC sweeps that halt the rendering "
            "pipeline. To avoid this overhead in modern Kotlin architectures, engineers leverage @JvmInline value class wrappers to achieve "
            "type-safe abstractions with zero runtime allocation, utilize specialized primitive sparse arrays such as SparseArray and LongSparseArray, "
            "and adopt flat primitive buffers like ByteBuffer when streaming high-throughput binary or network data."
        ),
    },
    "MEM-07": {
        "concept_en": (
            "The distinction between int and java.lang.Integer is a foundational aspect of Java and Kotlin interoperability. In Java, int is "
            "a primitive value type that represents a 32-bit signed integer stored by value directly on thread stack frames or embedded within class "
            "memory layouts. It has zero object overhead and can never hold a null reference. In contrast, java.lang.Integer is a full reference "
            "type that wraps an int inside an object allocated on the heap, allowing it to represent null and participate in generic collections. "
            "In Kotlin, this duality is abstracted into the unified Int type. Non-nullable Int compiles directly to primitive int in bytecode, "
            "whereas nullable Int? or generic T compiles to java.lang.Integer. When interoperating with Java APIs that lack nullability annotations, "
            "Kotlin treats types as platform types (Int!), creating potential unboxing crashes if null is received."
        ),
        "walkthrough_en": (
            "Java interoperability pitfalls with primitives and wrappers:\n"
            "```kotlin\n"
            "// Java API signature:\n"
            "// public class LegacyAnalytics {\n"
            "//     public static Integer getScoreOrNull();\n"
            "//     public static void trackMetric(int count);\n"
            "// }\n"
            "\n"
            "// Kotlin caller:\n"
            "fun processAnalytics() {\n"
            "    // Platform type pitfall: getScoreOrNull() returns Integer!\n"
            "    val score: Int = LegacyAnalytics.getScoreOrNull() // If null, throws NullPointerException at runtime during unboxing!\n"
            "\n"
            "    // Safe handling:\n"
            "    val safeScore: Int? = LegacyAnalytics.getScoreOrNull()\n"
            "    if (safeScore != null) {\n"
            "        LegacyAnalytics.trackMetric(safeScore) // Automatic safe unboxing to primitive int\n"
            "    }\n"
            "}\n"
            "```\n"
            "By explicitly typing the returned platform type as Int?, the Kotlin compiler enforces null-safety checks before unboxing to primitive "
            "int, preventing unexpected application crashes."
        ),
        "short_en": (
            "In Java, primitive int is a 4-byte non-nullable value type, while Integer is a nullable heap object wrapper. Kotlin unifies both "
            "under Int, mapping non-nullable Int to primitive int and nullable Int? or generics to Integer. When calling unannotated Java APIs, "
            "Kotlin creates platform types (Int!), which cause fatal NullPointerExceptions if unboxed without explicit null checks."
        ),
        "structured_en": (
            "To begin with, the difference between int and Integer stems from Java's split type system between primitives and reference objects. "
            "A primitive int stores a raw 32-bit value directly in memory without object headers, offering maximum CPU execution speed and zero heap "
            "overhead, but cannot represent the absence of a value. Conversely, java.lang.Integer is a heap-allocated wrapper object that supports "
            "nullability and generic typing. From an architectural standpoint, Kotlin eliminates this syntactical duality by exposing a single Int type. "
            "Under the hood, the Kotlin compiler maps non-nullable Int to primitive int, while mapping nullable Int? and generic parameters to "
            "java.lang.Integer. In production scenarios, interoperability issues arise when interfacing with legacy Java code lacking JSR-305 "
            "nullability annotations. In these cases, Kotlin infers platform types, and attempting to treat a null Integer as a non-nullable primitive "
            "triggers an immediate NullPointerException during implicit unboxing. As for boundary management, senior engineers always specify "
            "explicit nullability on Java integration boundaries to prevent unboxing crashes."
        ),
        "deep_senior_en": (
            "Delving into ART bytecode compilation and JNI bridge mechanics, the translation between Kotlin and Java reveals critical architectural "
            "trade-offs. When decompiling Kotlin bytecode, a non-nullable Int declaration compiles directly to JVM opcode instructions such as "
            "ILOAD, ISTORE, and IADD. However, as soon as nullability is introduced with Int?, the compiler synthesizes method calls to "
            "Integer.valueOf(int) for boxing and Integer.intValue() for unboxing. In addition to the memory inflation—where a 64-bit ART runtime "
            "incurs 16 bytes for each Integer instance compared to 4 bytes for primitive int—reference identity comparison presents subtle correctness "
            "traps. Java caches Integer instances within the range of -128 to 127 via IntegerCache. Comparing two Integer references with the "
            "referential equality operator inside this range evaluates to true due to cached identity, but identical values outside this range "
            "evaluate to false unless using structural equals().\n\n"
            "At the JNI and native boundary, this distinction dictates performance. Passing a primitive int array across the JNI bridge allows the "
            "native runtime to use GetPrimitiveArrayCritical to pin the underlying memory buffer, enabling zero-copy pointer access in C++ without "
            "garbage collector interference. In contrast, passing an array of Integer objects requires traversing individual object pointers, creating "
            "immense JNI crossing overhead and preventing vectorization. In large-scale Android applications, staff engineers enforce NonNull and "
            "Nullable annotations across all Java libraries and utilize primitive arrays for high-throughput data models to ensure safe, zero-overhead "
            "Java-Kotlin interoperability."
        ),
    },
}

AR_DATA = {
    "MEM-01": {
        "id": "MEM-01",
        "questionAr": "ما هي إدارة الذاكرة في أندرويد؟ وما الذي يفعله مجمّع النفايات (Garbage Collector)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- التمييز الدقيق بين استعادة ذاكرة الـ Heap المدارة وحدود ذاكرة العملية على مستوى نظام التشغيل والذاكرة الأصلية (Native Memory).\n"
            "- فهم خوارزميات الوصول (Reachability) وتكلفة استدعاء الـ GC دون الادعاء الخاطئ بقدرة المطور على إجبار النظام على تنظيف مثالي للذاكرة.\n"
            "- ربط معدل حجز الكائنات السريع (Allocation Churn) وتراكم الكائنات المسربة بسقوط الفريمات (Jank) وأخطاء نفاد الذاكرة (OOM) والقياس الفعلي في بيئة الإنتاج."
        ),
        "why_it_matters_ar": (
            "نظام أندرويد يخصص لكل تطبيق مساحة ذاكرة محددة تعرف بسقف الـ Heap المدار بواسطة بيئة تشغيل ART. مجمع النفايات أو الـ GC يعمل في الخلفية لتتبع "
            "الكائنات الحية عبر شجرة مراجع تبدأ من جذور الـ GC Roots، ويقوم بتحرير مساحات الكائنات التي انقطعت صلتها بهذه الجذور. في الإصدارات الحديثة، يعتمد ART "
            "على جامع النسخ المتزامن Generational Concurrent Copying الذي يجمع وينقل الكائنات الحية لتقليل التجزئة (Fragmentation) في الذاكرة دون إيقاف خيوط "
            "المعالجة لفترات طويلة. ومع ذلك، فإن إنشاء كائنات مؤقتة بمعدل مرتفع للغاية يجبر المحرك على تكثيف دورات التنظيف، مما يستهلك أنوية المعالج ويتسبب في تأخير "
            "معالجة رسوميات الشاشة. كما أن الـ GC لا يتعامل تلقائياً مع تسريبات الموارد الخارجية مثل ملفات القنوات المفتوحة أو الذاكرة الرسومية المخصصة للـ Bitmaps إلا عند إفلات المراجع تماماً."
        ),
        "worked_example_ar": (
            "عند تمرير قائمة سريعة، إنشاء كائنات داخل دالة التثبيت يسبب ضغطاً هائلاً على الـ GC:\n"
            "```kotlin\n"
            "// ❌ كود يسبب Memory Churn داخل RecyclerView:\n"
            "override fun onBindViewHolder(holder: ViewHolder, position: Int) {\n"
            "    val formatter = SimpleDateFormat(\"yyyy-MM-dd\", Locale.US)\n"
            "    holder.dateText.text = formatter.format(Date(items[position].timestamp))\n"
            "}\n"
            "\n"
            "// ✅ كود محسّن يعيد استخدام الكائن الثابت:\n"
            "companion object {\n"
            "    private val DATE_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE\n"
            "}\n"
            "override fun onBindViewHolder(holder: ViewHolder, position: Int) {\n"
            "    holder.dateText.text = DATE_FORMATTER.format(items[position].localDate)\n"
            "}\n"
            "```\n"
            "في الكود المحسّن تم منع إنشاء ملايين الكائنات المؤقتة أثناء التمرير، مما أزال الـ GC Spikes تماماً وحافظ على استقرار معدل الـ 60 أو 120 فريم في الثانية."
        ),
        "trade_offs_ar": (
            "استخدام التخزين المؤقت (Caching) يقلل من تكرار إنشاء الكائنات ولكنه يحجز مساحة مستمرة في الـ Heap؛ لذا يجب دائماً وضع سقف أعلى لحجم الكاش وتفريغه "
            "عند استقبال تنبيهات نقص الذاكرة. تقنيات الـ Object Pooling تقلل معدل الحجز في المسارات الحرجة مثل الألعاب أو معالجة الصوت، لكنها تزيد من تعقيد إدارة "
            "الملكية وتزامن الخيوط ولا ينبغي اللجوء إليها دون قياس مسبق. استدعاء `System.gc()` يدوياً لا يضمن تنظيفاً فورياً بل يربك جدولة النظام ويسبب وقفات غير مبررة؛ "
            "والحل الأصح دائماً هو تصحيح دورة حياة الكائنات وترشيد أحجام الصور."
        ),
        "failure_modes_ar": (
            "تسريب مراجع الـ Activity يمنع الـ GC من تحرير شجرة الواجهة بأكملها مما يؤدي إلى تآكل الـ Heap تدريجياً حتى وقوع OutOfMemoryError. الإفراط في إنشاء "
            "الكائنات المؤقتة داخل حلقات تكرارية أو داخل `onDraw` يولد ما يعرف بـ Allocation Churn ويسقط فريمات العرض. تخصيص مصفوفات ضخمة أو صور عالية الدقة دفعة واحدة "
            "قد يفجر استثناء OOM فوراً حتى لو كان عدد الكائنات المدارة صغيراً. عدم إغلاق مؤشرات قواعد البيانات والـ Streams يستهلك موارد النظام الأصلية دون قدرة الـ GC على استعادتها بكفاءة."
        ),
        "production_perspective_ar": (
            "في التطبيقات الضخمة، يتم تتبع استهلاك الذاكرة عبر أجهزة اختبار حقيقية ذات مواصفات متواضعة ومراقبة مؤشرات Android Vitals ونسب الـ OOM في كل إصدار. "
            "لا نكتفي بقياس قمة الاستهلاك (Peak) بل نراقب الخط القاعدي (Baseline) للذاكرة بعد تكرار فتح وإغلاق الشاشات عشرات المرات. يجب التعامل بجدية مع إشارات "
            "`onTrimMemory` لتخفيف الكاش المؤقت دون مساس بالبيانات غير المحفوظة للمستخدم، والاعتماد على Android Studio Profiler لمراقبة مسارات الحجز وتوزيع الـ PSS بدقة."
        ),
        "how_to_answer_ar": (
            "- **الأساس النظري:** ابدأ بتوضيح دور بيئة تشغيل ART في تخصيص الـ Heap وحدود العملية، وكيف يتعقب الـ GC مسارات الوصول انطلاقاً من الـ GC Roots.\n"
            "- **التطبيق العملي:** اربط بين معدل إنشاء الكائنات وسلاسة الواجهة، مستشهداً بمثال الـ RecyclerView وكيف يؤثر التخصيص المتكرر على وقت المعالج.\n"
            "- **العمق الهندسي:** ناقش تطور الـ GC إلى خوارزمية Concurrent Copying واشرح الفارق بين تسريب الذاكرة واستنزاف الذاكرة الأصلية بواسطة الـ Bitmaps."
        ),
        "talking_points_ar": (
            "ناقش خوارزميات الـ Tracing Garbage Collection، وتفاصيل الـ Generational Collection في ART، ودور قراءة الحواجز (Read Barriers) في إتاحة الـ Compaction المتزامن، "
            "وكيفية قراءة وتفسير ملفات الـ HPROF عبر الأدوات المتقدمة مثل LeakCanary و Eclipse MAT."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"هل استدعاء `System.gc()` يجبر النظام على تنظيف الذاكرة في الحال؟\"\n"
            "  **المرشح:** \"إطلاقاً، استدعاء `System.gc()` هو مجرد تلميح (Hint) لبيئة التشغيل، وغالباً ما تتجاهله أو تنفذه في وقت غير مناسب مما يتسبب في إيقاف خيوط التطبيق وحدوث تهنيج مرئي؛ لذلك نعتبره Anti-pattern في كود الإنتاج.\"\n\n"
            "- **المحاور:** \"أين يتم تخزين بكسلات الـ Bitmaps في إصدارات أندرويد الحديثة مقارنة بالقديمة؟\"\n"
            "  **المرشح:** \"منذ أندرويد 8.0 أوريو، تم نقل بكسلات الصور بالكامل إلى الـ Native Memory وإدارتها عبر `NativeAllocationRegistry`، بعد أن كانت مخزنة داخل Java Heap في الإصدارات السابقة، مما قلل ضغط تجزئة الـ Heap المدار.\""
        ),
        "self_check_ar": (
            "اشرح مفهوم مسارات الوصول من الـ GC Roots؛ حدد مصدرين لاستهلاك الذاكرة خارج الـ Java Heap؛ فرّق بين الـ Churn والـ Leak؛ ووضح استراتيجية التعامل مع تنبيهات نقص الذاكرة في التطبيق."
        ),
        "references_ar": (
            "- [نظرة عامة على إدارة الذاكرة في أندرويد](https://developer.android.com/topic/performance/memory-overview) — سلوك بيئة تشغيل ART ومجمّع النفايات.\n"
            "- [إدارة ذاكرة التطبيق وتحسين الأداء](https://developer.android.com/topic/performance/memory) — إرشادات عملية لتفادي الضغط على الـ GC.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "إدارة الذاكرة في أندرويد تعتمد على نظام تشغيل ART الذي يخصص لكل تطبيق سقف ذاكرة محدد للـ Heap. مجمّع النفايات أو الـ GC هو محرك ذكي يتعقب الكائنات "
            "الحية بدءاً من جذور الـ GC Roots ويحرر تلقائياً مساحة أي كائن لم يعد قابلاً للوصول. في بيئات أندرويد الحديثة يعمل الـ GC بشكل متزامن لتقليل تجميد التطبيق، "
            "ولكن الإفراط في إنشاء الكائنات المؤقتة يسبب ضغطاً متواصلاً على المعالج ويسقط فريمات الشاشة."
        ),
        "best_answer_ar": (
            "في أندرويد، بنتعامل مع الذاكرة من منظورين: نظام التشغيل والـ ART Runtime. كل تطبيق بيشتغل في عملية معزولة ليها حد أقصى للـ Heap بتحدده الشركة المصنعة للجهاز.\n\n"
            "دور الـ Garbage Collector الأساسي هو إدارة مساحة الـ Heap أوتوماتيكياً. هو بيمشي ورا المراجع الحية انطلاقاً من الـ GC Roots، وأي كائن مقطوع الصلة بالشجرة "
            "دي بيعتبره Garbage ويحرره. بيئة تشغيل ART الحديثة بتعتمد على Generational Concurrent Copying GC؛ وده معناه إن الكائنات الجديدة بتتحط في Young Generation "
            "وبتتنظف بسرعة بدون تعطيل كبير للواجهة، مع نقل الكائنات المعمرة للـ Old Generation وعمل Compaction لمنع تجزئة الرام.\n\n"
            "المشكلة الحقيقية بتظهر لما بنعمل Allocation Churn، زي إننا ننشئ Formatters أو Bitmaps داخل لفة الـ RecyclerView أو `onDraw`. هنا الـ GC بيضطر يشتغل بكثافة "
            "لملاحقة الطلب، وده بيستهلك الـ CPU وبيتسبب في سقوط فريمات وتشنج في الشاشة. دورنا كمهندسين إننا نرشد إنشاء الكائنات ونفصل الموارد بدقة لتجنب الـ Jank والـ OOM."
        ),
        "deep_answer_ar": (
            "لو غصنا في أعماق بيئة تشغيل ART من أندرويد 8.0 فما فوق، هنلاقي إن الـ Garbage Collector انتقل من أسلوب الـ Concurrent Mark-Sweep القديم إلى الـ Generational "
            "Concurrent Copying أو الـ CC GC. الميزة الثورية هنا هي استخدام الـ Read Barrier عبر العتاد والتعليمات البرمجية، وده بيسمح للـ GC إنه ينقل الكائنات الحية في "
            "الذاكرة لتجميعها ومنع الـ Fragmentation في نفس اللحظة اللي التطبيق شغال فيها، مع فترات توقف للـ Threads بتتقاس بالمايكروثانية مش بالميلي ثانية.\n\n"
            "لكن نقطة الانهيار الحقيقية بتيجي من الـ Memory Limits الصارمة. كل عملية ليها سقف محدد بنعرفه من `getMemoryClass`، والـ Linux Kernel بيراقبنا بواسطة الـ Low "
            "Memory Killer daemon أو `lmkd`. لو التطبيق فضل يراكم مراجع ميتة عبر تسريبات في الـ Singletons أو احتفظ بشاشات Activity مدمرة، مساحة الـ Dirty Memory بتزيد، "
            "ولما الجهاز يتعرض لضغط ذاكرة، الـ Kernel مش بيستنى الـ OOM Exception، بل بيبعت إشارة SIGKILL وينهي العملية فوراً بناءً على درجة الـ oom_adj الخاصة بيها.\n\n"
            "في التحليل المتقدم للإنتاج، بنسحب Heap Dumps بصيغة HPROF ونحللها بـ LeakCanary و MAT عشان نقيس الـ Retained Size مش بس الـ Shallow Size، ونفرق بين Java Heap "
            "والـ Native Memory اللي بقت بتشيل بكسلات الـ Bitmaps من خلال الـ `NativeAllocationRegistry`. الحل الهندسي مش إننا ننادي `System.gc`، بل إننا نراقب مسارات "
            "الـ Allocations ونستجيب لنداءات `onTrimMemory` ونمنع الـ Churn في مسارات الرسم والتمرير."
        ),
    },
    "MEM-02": {
        "id": "MEM-02",
        "questionAr": "ما هي جذور مجمّع النفايات (GC Roots)؟ وكيف يحدد الـ GC إمكانية الوصول للكائنات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- تعريف الـ GC Roots وسلاسل المراجع القوية (Strong References) بدلاً من الفهم الخاطئ بأن عدم ظهور الكائن على الشاشة يعني حذفه.\n"
            "- تفسير كيف يجمع الـ GC الجزر المعزولة ذات الاعتماديات الدائرية (Cyclic References) بينما يعجز عن تنظيف Activity مسربة.\n"
            "- استخدام مسار أقصر طريق للجذر (Shortest Path to GC Root) في تحليل تفريغ الذاكرة (Heap Dump) لتشخيص أخطاء الملكية."
        ),
        "why_it_matters_ar": (
            "يعتمد الـ Garbage Collector في أندرويد على خوارزمية تتبع الوصول (Tracing Reachability) للتمييز بين الكائنات الحية والميتة. تبدأ عملية الفحص من نقاط "
            "ارتكاز ثابتة تسمى الـ GC Roots، وتشمل خيوط المعالجة النشطة، المتغيرات الثابتة (Static Fields)، ومراجع JNI الأصلية. يتتبع الـ GC جميع المراجع القوية "
            "المتصلة بهذه الجذور مباشرة أو بالتبعية. إذا كان الكائن جزءاً من دائرة مغلقة تشير فيها كائنات ميتة لبعضها البعض دون أي اتصال بـ GC Root حي، فإن النظام "
            "يعتبرها جميعاً غير قابلة للوصول ويقوم بتحريرها بأمان. في المقابل، إذا ارتبطت شاشة منتهية بمستمع مسجل في خيط خلفي نشط، تظل الشاشة حية وتتسرب الذاكرة."
        ),
        "worked_example_ar": (
            "يوضح المخطط التالي كيف تبقي رسالة مؤجلة في خيط نشط شاشة مدمرة عالقة في الذاكرة:\n"
            "```text\n"
            "[GC Root: Active Main Thread Looper]\n"
            "       |\n"
            "       v\n"
            "[MessageQueue -> Pending Message]\n"
            "       |\n"
            "       v\n"
            "[Anonymous Runnable instance]\n"
            "       |\n"
            "       v (implicit outer reference: this$0)\n"
            "[Destroyed ProfileActivity instance]\n"
            "```\n"
            "حتى بعد استدعاء `finish()` على `ProfileActivity`، فإن استمرار وجود الرسالة المؤجلة في طابور الـ Main Looper يشكل مسار مراجع حياً من GC Root يمنع الـ GC من تحرير الشاشة."
        ),
        "trade_offs_ar": (
            "المراجع الضعيفة (WeakReference) والناعمة (SoftReference) تكسر سلاسل الوصول القوية وتسمح للـ GC بتنظيف الكائنات عند الحاجة، ولكنها تضيف تعقيداً "
            "للتعامل مع القيم التي قد تصبح `null` فجأة في أي لحظة. الاعتماد على إلغاء التسجيل اليدوي المتناظر (Symmetrical Cleanup) في دورة الحياة يضمن التحرير "
            "الحتمي للكائنات دون مخاطرة بقاء مراجع معلقة. محاولة استبدال كل المراجع القوية بمراجع ضعيفة يعتبر تصميماً سيئاً؛ والأفضل هو احترام حدود دورة الحياة ونطاقات الـ Coroutines."
        ),
        "failure_modes_ar": (
            "تسجيل مستمع في كائن Singleton دون إلغاء تسجيله يربط الشاشة بـ GC Root دائم ويمنع مسحها مدى الحياة. إرسال مهام مؤجلة عبر Handler دون إلغائها في `onDestroy` "
            "يبقي الشاشة عالقة طوال فترة الانتظار. الاحتفاظ بـ Thread أو Coroutine نشط للأبد في الخلفية يمثل GC Root مستمر يحتفظ بكل ما تم تمريره له. الاعتقاد بأن "
            "الاعتماديات الدائرية تسبب تسريباً في أندرويد هو خطأ شائع، فالـ GC يتعامل معها بسلاسة طالما انقطعت عن الجذور."
        ),
        "production_perspective_ar": (
            "في بيئات الإنتاج، تُستخدم مكتبة LeakCanary في نسخ التطوير لمراقبة الكائنات المتبقية تلقائياً وتوليد شجرة المراجع التي تربط الكائن المسرب بأقرب GC Root. "
            "عند فحص ملفات HPROF عبر Android Studio Profiler أو MAT، يقوم المهندسون بحساب الـ Retained Size وتحليل شجرة السيطرة (Dominator Tree) لمعرفة الكائن الجذري "
            "المسؤول عن حجز أكبر كتلة ذاكرة في الـ Heap، ثم قطع الرابط بتصحيح النطاق واستخدام `repeatOnLifecycle` و `viewModelScope`."
        ),
        "how_to_answer_ar": (
            "- **التعريف الهندسي:** عرّف الـ GC Roots بأنها نقاط البداية الحية لشجرة المراجع، مثل الـ Threads النشطة والمتغيرات الثابتة.\n"
            "- **خوارزمية الوصول:** اشرح كيف يسير الـ GC خلف المراجع القوية، ووضح لماذا لا تمثل الـ Circular References مشكلة للـ Tracing GC.\n"
            "- **الربط بالواقع:** اربط المفهوم بتسريب الـ Activity واشرح كيف تستخدم أدوات فحص الذاكرة مسار Shortest Path to GC Root لحل المشكلة."
        ),
        "talking_points_ar": (
            "ناقش تصنيفات الـ GC Roots المختلفة (Thread Stacks, JNI Globals, Static Fields, Monitors)، والفرق بين خوارزميات Reference Counting و Tracing GC، "
            "ودور شجرة السيطرة (Dominator Tree) في تحديد الكائنات التي تحجب الذاكرة عن التحرير."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"لو كائنين بيشيروا لبعضهم البعض (A points to B, B points to A) ومحدش تاني ماسكهم، هل هيتسربوا؟\"\n"
            "  **المرشح:** \"لأ مش هيتسربوا إطلاقاً في أندرويد؛ لأن بيئة تشغيل ART بتعتمد على Tracing Garbage Collection مش Reference Counting، وطالما الجزيرة دي مفهاش مسار واصل لأي GC Root حي، الـ GC بيعتبرهم كائنات ميتة وبيحررهم فوراً.\"\n\n"
            "- **المحاور:** \"ما هي أشهر أنواع الـ GC Roots اللي بتسبب تسريبات Activity في أندرويد؟\"\n"
            "  **المرشح:** \"أشهرهم خيوط العمل النشطة (Active Threads والـ Coroutines المعلقة) والمتغيرات الثابتة (Static Singletons) وطابور رسائل الـ Main Looper اللي شايل Runnables مأجلة.\""
        ),
        "self_check_ar": (
            "اذكر أربعة أنواع للـ GC Roots؛ اشرح كيف يتعامل مجمع النفايات مع الحلقات المفرغة (Cyclic References)؛ وفرق بين الـ Shallow Heap والـ Retained Heap."
        ),
        "references_ar": (
            "- [تتبع مسار الوصول وإدارة الذاكرة](https://developer.android.com/topic/performance/memory-overview) — خوارزميات فحص الوصول في ART.\n"
            "- [دليل LeakCanary لتحليل مسارات الجذور](https://square.github.io/leakcanary/fundamentals-how-leakcanary-works/) — فهم سلاسل المراجع والـ Dominator Trees.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "جذور مجمّع النفايات أو الـ GC Roots هي نقاط الارتكاز الثابتة التي يبدأ منها الـ GC تتبع الذاكرة للتأكد من الكائنات الحية، وتشمل متغيرات الـ Stack "
            "للخيوط النشطة، والمتغيرات الثابتة، ومراجع JNI. يعتبر الكائن قابلاً للوصول وحياً إذا كانت هناك سلسلة مراجع قوية تربطه بأي GC Root، وأي كائن تنقطع "
            "صلته بهذه الجذور يتم تنظيفه فوراً حتى لو كان يحتوي على دورات مراجع داخلية."
        ),
        "best_answer_ar": (
            "في أندرويد، الـ Garbage Collector مش بيعد المراجع بنظام الـ Reference Counting، بل بيشتغل بنظام Tracing Reachability انطلاقاً من كائنات أساسية بيعتبرها النظام حية دائماً وهي الـ GC Roots.\n\n"
            "الجذور دي بتشمل أربع فئات رئيسية: أولاً إطارات استدعاء الدوال والمتغيرات المحلية على خيوط التنفيذ النشطة (Thread Stacks)، ثانياً المتغيرات الثابتة (Static Fields) "
            "المرتبطة بالـ Classes المحملة، ثالثاً مراجع JNI العالمية والمحلية، ورابعاً أقفال التزامن (Thread Monitors). الـ GC بيمشي من الجذور دي زي الشجرة، وأي كائن يوصله "
            "بـ Strong Reference بيفضل في الذاكرة.\n\n"
            "الميزة الكبرى للنظام ده إنه بيحل معضلة الـ Circular References تلقائياً؛ لو كائنين ماسكين بعض لكن مفيش أي خط واصل ليهم من GC Root، بيتم كنسهم في الدورة الجاية. "
            "التسريب الحقيقي بيحصل لما كائن قصير العمر زي الـ Activity يتعلق بالغلط في GC Root طويل العمر، زي Thread شغال في الخلفية أو Static Manager، وده بيخلي الـ GC "
            "عاجز عن حذفه لأن مسار الوصول ما زال قائماً."
        ),
        "deep_answer_ar": (
            "لو فحصنا الأمر من زاوية نظرية الرسوم البيانية (Graph Theory) وتحليل ملفات الـ HPROF، الـ GC بيبني Directed Graph بيمثل الذاكرة. في أدوات زي Android Studio "
            "Profiler و LeakCanary Shark Engine، بنعتمد على مفهوم شجرة السيطرة أو الـ Dominator Tree. في الشجرة دي، الـ Node A بيعتبر Dominator للـ Node B لو كان كل "
            "مسار من أي GC Root رايح لـ B لازم يعدي بالضرورة على A. وده اللي بيخلينا نفرق بين الـ Shallow Heap اللي هو حجم الكائن نفسه، والـ Retained Heap اللي هيرجع "
            "للنظام لو حررنا الـ Dominator Node.\n\n"
            "أخطر GC Roots في أندرويد هي الـ Thread Pools ومحركات الـ Looper. لما بنبعت Message مؤجلة عبر Handler، الـ Message بتدخل في الـ Native MessageQueue الخاصة "
            "بالـ Main Thread اللي هو GC Root مستمر. لو الـ Message دي شايلة Runnable داخلي غير ثابت، الـ Bytecode بيولد حقل خفي اسمه `this$0` بيشير للـ Activity الخارجية. "
            "وبالتالي، الشاشة كلها بشجرة الـ Views ومصفوفات الرسوميات بتفضل مشدودة للـ Thread Stack لحد ما الرسالة تتنفذ.\n\n"
            "في فرق البنية التحتية، بنشغل تحليلات آلية بتطلع الـ Shortest Path to GC Roots مع استبعاد المراجع الضعيفة (Weak and Soft References)، وبنعتمد على اختبارات "
            "تكامل بترصد بقاء الـ Retained Instances بعد انتهاء الشاشات، وبنحول كل العمليات الطويلة لـ Structured Concurrency عبر `viewModelScope` عشان نضمن إن إلغاء "
            "المهام يقطع رابط الـ Continuation بالـ Thread Pool فوراً."
        ),
    },
    "MEM-03": {
        "id": "MEM-03",
        "questionAr": "قارن بين الـ Stack والـ Heap في أندرويد. وما الذي يعيش على كل منهما؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- تقديم نموذج معماري دقيق لإطارات الـ Stack ومساحة الـ Heap المدارة دون الوقوع في الفخ الخاطئ بأن جميع الـ Primitives تعيش على الـ Stack دائماً.\n"
            "- توضيح عمر المراجع والكائنات وخيوط المعالجة وسلوك التخصيص في Java و Kotlin داخل بيئة تشغيل ART.\n"
            "- ربط الاستدعاء الذاتي اللانهائي (Deep Recursion) بـ StackOverflowError وتراكم الكائنات الحية بـ OutOfMemoryError."
        ),
        "why_it_matters_ar": (
            "الذاكرة في أندرويد تنقسم تشغيلياً إلى منطقتين رئيسيتين: الـ Stack والـ Heap. الـ Stack يخصص لكل خيط معالجة (Thread) مساحة محددة (غالباً 1 ميجابايت)، "
            "ويعمل بنظام الداخل آخراً يخرج أولاً (LIFO). يحتوي الـ Stack على إطارات الدوال المستدعاة والمتغيرات المحلية ومؤشرات العناوين، ويتميز بسرعة فائقة وانعدام الحاجة "
            "لمجمع النفايات؛ حيث يتم تحرير المساحة بمجرد خروج التنفيذ من نطاق الدالة. في المقابل، الـ Heap هو مساحة الذاكرة المدارة والمشتركة بين جميع خيوط التطبيق، "
            "وهو المكان الذي تُخلق فيه كافة الكائنات (Objects) والمصفوفات والـ Strings، ويخضع بالكامل لرقابة وتنظيف مجمع النفايات (GC)."
        ),
        "worked_example_ar": (
            "تحليل سطر برمجي لمعرفة توزيع الذاكرة بين الـ Stack والـ Heap:\n"
            "```kotlin\n"
            "fun processUser() {\n"
            "    val id: Int = 101                 // القيمة 101 مخزنة مباشرة في إطار الـ Stack للخيط الحالي\n"
            "    val name: String = \"Mohamed\"       // المؤشر name على الـ Stack، بينما كائن الـ String ومصفوفة حروفه على الـ Heap\n"
            "    val user = User(id, name)         // المؤشر user على الـ Stack، وكائن User وحقوله الداخلية على الـ Heap\n"
            "}\n"
            "```\n"
            "بمجرد انتهاء تنفيذ دالة `processUser()`، يُحذف إطار الدالة من الـ Stack فوراً، وتسقط المؤشرات المحلية، بينما تظل كائنات `User` و `String` على الـ Heap بانتظار دورة الـ GC القادمة."
        ),
        "trade_offs_ar": (
            "الـ Stack فائق السرعة ويستفيد من الـ CPU Cache Locality ولكنه محدود المساحة للغاية ومقيد بنطاق تنفيذ الخيط الحالي؛ والإفراط في الاستدعاء الذاتي يفجّر "
            "`StackOverflowError`. في المقابل، الـ Heap مرن وكبير ويسمح بمشاركة البيانات بين مختلف أجزاء التطبيق وخيوطه، لكنه يدفع ضريبة حجز الذاكرة وتكلفة مسح الـ GC "
            "وتجزئة الذاكرة. يجب الحذر من الاعتقاد الخاطئ بأن المتغيرات الأولية تعيش على الـ Stack دائماً؛ فإذا كان المتغير الأولي حقلاً داخل Class، فإنه يُخزن كجزء من جسم الكائن على الـ Heap."
        ),
        "failure_modes_ar": (
            "الاستدعاء الذاتي غير المنتهي (Infinite Recursion) أو هياكل البيانات العميقة جداً بدون حدود تؤدي إلى نفاد مساحة الـ Stack وحصول `StackOverflowError` فوري "
            "لا يستطيع الـ GC إنقاذه. على الجانب الآخر، حجز ملايين الكائنات الصغيرة أو تسريب مراجع الشاشات يملأ الـ Heap ويؤدي إلى `OutOfMemoryError`. إنشاء عدد ضخم "
            "من خيوط المعالجة المستقلة يستهلك ذاكرة النظام الإجمالية لأن كل خيط يحجز Stack خاص به يقتطع من ذاكرة الـ RAM المتاحة للتطبيق."
        ),
        "production_perspective_ar": (
            "في الأنظمة عالية الأداء، يحرص المهندسون على استبدال الخوارزميات التكرارية العميقة بحلول تعتمد على الحلقات (Iteration) وهياكل بيانات مثل `ArrayDeque` لتفادي "
            "خطر الـ StackOverflowError تماماً. كما يتم تفادي إنشاء كائنات وسيطة في مسارات معالجة البيانات الضخمة، والاعتماد على مصفوفات الـ Primitives أو تقنية "
            "`@JvmInline value class` لتخفيف الضغط على الـ Heap والاستفادة من سرعة تخزين القيم في سجلات المعالج والـ Stack."
        ),
        "how_to_answer_ar": (
            "- **المقارنة المعمارية:** وضح الفارق الجوهري في الهيكلية؛ الـ Stack خاص بالخيط ويعمل بـ LIFO وسريع جداً، والـ Heap مشترك وتديره بيئة تشغيل ART عبر الـ GC.\n"
            "- **محتويات كل منطقة:** بيّن ما يعيش على الـ Stack (المتغيرات المحلية والمراجع) وما يعيش على الـ Heap (الكائنات والمصفوفات والحقول).\n"
            "- **أخطاء كل منطقة:** قارن بين الـ StackOverflowError والـ OutOfMemoryError، واذكر الاستثناء الشهير بأن الحقول الأولية داخل الكلاس تعيش على الـ Heap."
        ),
        "talking_points_ar": (
            "ناقش مفهوم الـ Escape Analysis وقدرة المترجم على تطبيق الـ Scalar Replacement، والفرق في أداء الـ L1/L2 CPU Cache بين الـ Stack المتصل والـ Heap المتفرق، "
            "وهيكل كائن الذاكرة في أنظمة 64-bit وحجم الـ Object Header ومحاذاة الذاكرة (Memory Alignment)."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"هل كل الـ Primitive Types بتعيش دائماً على الـ Stack؟\"\n"
            "  **المرشح:** \"لأ، ده خطأ شائع جداً. الـ Primitives بتعيش على الـ Stack فقط لو كانت متغيرات محلية (Local Variables) داخل دالة. لكن لو الـ Primitive عبارة عن حقل (Member Variable) داخل Class، قيمته بتتخزن كجزء من جسم الكائن نفسه على الـ Heap.\"\n\n"
            "- **المحاور:** \"إيه اللي بيحصل في الذاكرة لما بنستدعي Coroutine مقارنة بإنشاء Thread جديد؟\"\n"
            "  **المرشح:** \"الـ Thread التقليدي بيحجز مساحة Stack كاملة من نظام التشغيل (حوالي 1MB)، بينما الـ Coroutine هي كائن Continuation خفيف الوزن بيتخزن على الـ Heap بدون حجز Stack مستقل، وده اللي بيسمح بتشغيل مئات الآلاف من الـ Coroutines بالتوازي.\""
        ),
        "self_check_ar": (
            "فرّق بدقة بين حقول الكائنات والمتغيرات المحلية؛ اشرح آلية تحرير ذاكرة الـ Stack مقارنة بالـ Heap؛ واذكر سبب حدوث كل من StackOverflowError و OutOfMemoryError."
        ),
        "references_ar": (
            "- [نظرة على بنية الذاكرة في أندرويد](https://developer.android.com/topic/performance/memory-overview) — توزيع مناطق الذاكرة في ART.\n"
            "- [توثيق JVM والـ Stack Frames](https://docs.oracle.com/javase/specs/jvms/se17/html/jvms-2.html#jvms-2.5) — مواصفات إطارات تنفيذ الخيوط والـ Heap.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "الـ Stack هو ذاكرة سريعة مخصصة لكل خيط معالجة بنظام LIFO، بتخزن إطارات استدعاء الدوال والمتغيرات المحلية ومؤشرات العناوين، وبتتحرر لحظياً بمجرد "
            "انتهاء الدالة بدون تدخل مجمع النفايات. الـ Heap هو مساحة الذاكرة المدارة والمشتركة للعملية كلها، بتعيش عليها كل الكائنات والمصفوفات، وإدارتها "
            "بتتم عبر الـ Garbage Collector. الاستدعاء الذاتي اللانهائي يسبب StackOverflowError، بينما تراكم الكائنات المسربة يسبب OutOfMemoryError."
        ),
        "best_answer_ar": (
            "الفرق بين الـ Stack والـ Heap في أندرويد بيمثل الركيزة الأساسية لفهم الأداء وإدارة الموارد. الـ Stack مخصص لكل خيط على حدة بحجم ثابت وصغير، ومسؤوليته "
            "متابعة مسار تنفيذ الكود عبر الـ Call Frames. كل ما دالة تتنادى، بيتعمل Frame جديد بيشيل المتغيرات المحلية ومؤشرات العناوين، وبمجرد ما الدالة تنتهي، "
            "الـ Frame بيسقط فوراً بدون أي تكلفة على الـ Garbage Collector.\n\n"
            "الـ Heap على النقيض، هو الحاوية الكبيرة المشتركة بين كل الخيوط. أي كائن بنعمله بـ `new` أو في Kotlin زي كائنات الـ Data Classes والـ Bitmaps والـ Strings، "
            "بيسكن على الـ Heap. حتى لو كان عندنا متغير أولي زي `Int`، لكنه متعرف كحقل جوه Class، فهو هيعيش على الـ Heap كجزء من الكائن ده.\n\n"
            "من الناحية الهندسية، الـ Stack مشكلته الأساسية هي الـ `StackOverflowError` لو حصل استدعاء ذاتي عميق غير منتهي، بينما الـ Heap مشكلته هي الـ `OutOfMemoryError` "
            "لو راكمنا كائنات حية أكتر من سقف الـ Heap المتاح للتطبيق. عشان كده المسارات عالية الحساسية بنعتمد فيها على التخزين المتصل ونقل البيانات بدون كائنات وسيطة."
        ),
        "deep_answer_ar": (
            "لو بصينا للموضوع على مستوى عتاد الـ CPU والمترجم، هنلاقي إن الـ Stack بيتميز بـ Cache Locality مذهلة؛ لأن البيانات كلها متصلة وورا بعضها في قمة الـ Stack، "
            "فبتفضل دايماً سخنة ومحفوظة في كاش المعالج L1 و L2. على العكس، الـ Heap بيتطلب Pointer Chasing، وده بيعمل CPU Cache Misses كتير لأن الكائنات متبعثرة في الـ Virtual Memory.\n\n"
            "في بيئة ART على معمارية 64-bit، كل كائن على الـ Heap بيشيل Object Header وزنه 16 بايت (8 بايت للـ Class Pointer و 8 بايت للـ Monitor Word والـ Lock State)، "
            "غير الـ Alignment Padding لمضاعفات الـ 8 بايت. يعني كائن صغير جداً بيستهلك أضعاف حجم بياناته الحقيقية على الـ Heap، وده مش موجود في الـ Stack.\n\n"
            "المترجم الحديث بيحاول يعمل Escape Analysis، ولو لقى إن الكائن مش بيهرب برة نطاق الدالة ومحدش هيشوفه برة، نظرياً يقدر يعمل Scalar Replacement ويفتت حقوله "
            "لمتغيرات على الـ Stack. لكن في أندرويد نظراً لطبيعة الـ Kotlin Lambdas وتوليد الـ State Machines في الـ Coroutines، أغلب الكائنات بتنتهي على الـ Heap. "
            "وفي الفرق المتقدمة، بنراقب استهلاك الـ Thread Stacks لما بنشغل Thread Pools ضخمة؛ لأن كل Thread بيحجز ميجابايت من الـ Native Virtual Memory، والحل الأفضل "
            "هو استخدام Coroutines خفيفة على الـ Heap بدل فتح خيوط نظام كتيرة."
        ),
    },
    "MEM-04": {
        "id": "MEM-04",
        "questionAr": "ما هو تسريب الذاكرة (Memory Leak)؟ وما الفرق بينه وبين تخصيص الذاكرة الضخم (Large Allocation)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- تعريف تسريب الذاكرة كعيب معماري يتمثل في بقاء مراجع لكائنات منتهية الوظيفة، وليس مجرد استهلاك مرتفع للذاكرة أو وقوع OOM.\n"
            "- المقارنة الدقيقة بين الخط القاعدي المستمر للذاكرة بعد الخروج من الشاشات وبين الارتفاع المؤقت المشروع في حالات الـ Large Allocation.\n"
            "- وصف اختبار عملي متكرر لتفريغ الذاكرة (Heap Dump) وتصحيح حدود الملكية."
        ),
        "why_it_matters_ar": (
            "الخلط بين تسريب الذاكرة وتخصيص الذاكرة الضخم يؤدي إلى تشخيص خاطئ للأداء. تسريب الذاكرة هو بقاء مرجع قوي غير مقصود يربط كائناً لم يعد مستخدماً في "
            "منطق التطبيق بجذر حي من جذور الـ GC Roots، مما يحرم مجمع النفايات من تحرير مساحته. هذا يؤدي إلى ارتفاع تراكمي مستمر في استهلاك الذاكرة الأساسي مع كل "
            "تنقل للمستخدم داخل التطبيق حتى ينفد الـ Heap ويقع الـ OOM. أما تخصيص الذاكرة الضخم فهو حجز مشروع ومؤقت لكتلة ذاكرة كبيرة، مثل قراءة صورة كاميرا كاملة "
            "الدقة أو معالجة ملف ضخم؛ وبمجرد انتهاء المهمة وخروج المتغير من النطاق، تصبح المساحة متاحة للتنظيف الفوري."
        ),
        "worked_example_ar": (
            "المقارنة البرمجية بين الحجز المؤقت الضخم والتسريب التراكمي:\n"
            "```kotlin\n"
            "// 1. Large Allocation (ليس تسريباً): يحجز 64MB لمعالجة مؤقتة ثم يُحرر فوراً:\n"
            "fun renderBanner() {\n"
            "    val largeBitmap = Bitmap.createBitmap(4000, 4000, Bitmap.Config.ARGB_8888)\n"
            "    drawContent(largeBitmap)\n"
            "    // بمجرد انتهاء الدالة، يفقد largeBitmap مرجعه ويصبح جاهزاً للـ GC فوراً\n"
            "}\n"
            "\n"
            "// 2. Memory Leak (تسريب): كائن مهمل يظل محبوساً للأبد في Singleton:\n"
            "object NavigationTracker {\n"
            "    val listeners = mutableListOf<ScreenCallback>()\n"
            "}\n"
            "class DetailActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // تسريب: الشاشة تُضاف إلى قائمة الـ Singleton ولا تُحذف أبداً عند الخروج!\n"
            "        NavigationTracker.listeners.add(this)\n"
            "    }\n"
            "}\n"
            "```\n"
            "في الحالة الأولى يرتفع الذاكرة لحظياً ثم يهبط للصفر، أما في الحالة الثانية يتراكم كائن `DetailActivity` جديد في كل مرة يفتح المستخدم الشاشة."
        ),
        "trade_offs_ar": (
            "التعامل مع الـ Large Allocations يتطلب تقنيات التقسيم والتدفق (Streaming) وإعادة التحجيم (Downsampling) لتقليل قمة الاستهلاك اللحظي (Peak Memory). "
            "في المقابل، حل الـ Memory Leaks يتطلب حوكمة معمارية حاسمة لدورة الحياة، وضمان التناظر في إضافة وإزالة المستمعين، وتفادي حفظ مراجع الـ Context في "
            "كائنات طويلة الأجل. التضحية بتخزين الصور مؤقتاً قد يحسن الذاكرة لكنه يزيد من استهلاك الشبكة؛ لذا يجب ضبط ميزانية واضحة للكاش بدلاً من منعه تماماً."
        ),
        "failure_modes_ar": (
            "تراكم تسريبات الشاشات يؤدي إلى تآكل الـ Heap ببطء وتكرار دورات الـ GC حتى يتشنج التطبيق ثم ينهار بـ `OutOfMemoryError`. على الجانب الآخر، محاولة حجز "
            "صورة بدقة 48 ميجابكسل دفعة واحدة قد تفجر OOM فورياً في لحظة واحدة حتى لو كان التطبيق خالياً تماماً من أي تسريب ذاكرة؛ لأن النظام لا يجد مساحة متصلة "
            "كافية للطلب. الاعتماد على `System.gc()` لإخفاء التسريب لا يجدي نفعاً لأن المراجع المسربة لا تزال متصلة بالـ GC Roots."
        ),
        "production_perspective_ar": (
            "في بيئات الإنتاج، نراقب الـ Baseline Memory بعد سيناريو تنقل متكرر: فتح وإغلاق الشاشة 10 مرات متتالية. إذا كان منحنى الذاكرة يصعد كدرجات السلم "
            "(Sawtooth climbing baseline) ولا يعود لنقطة البداية بعد الضغط على زر استدعاء الـ GC في الـ Profiler، فهذا دليل قاطع على وجود تسريب. نستخدم LeakCanary "
            "في الـ Debug Builds لرصد مسارات التسريب تلقائياً، ونستخدم Crashlytics لمراقبة استثناءات الـ OOM الناتجة عن الـ Large Allocations في أجهزة المستخدمين."
        ),
        "how_to_answer_ar": (
            "- **التعريف الدقيق:** وضّح أن التسريب هو خطأ في الاحتفاظ بمراجع كائنات منتهية، بينما الحجز الضخم هو استهلاك تشغيلي مشروع ومؤقت.\n"
            "- **سلوك المنحنى:** اشرح كيف يرفع التسريب الـ Baseline للأبد، بينما يسبب الحجز الضخم Spike مؤقت يزول بانتهاء المهمة.\n"
            "- **طريقة العلاج:** فرّق بين حل التسريب بإصلاح المراجع ودورة الحياة، وبين حل الحجز الضخم بالـ Downsampling والـ Streaming."
        ),
        "talking_points_ar": (
            "ناقش مفهوم الـ Retained Size مقابل الـ Shallow Size، وطريقة قراءة شجرة الـ Dominators في HPROF، واستراتيجيات ضغط وتحجيم الصور بالـ `inSampleSize` "
            "ومعالجة البيانات المتدفقة عبر مكتبات مثل Okio دون تحميل الملفات بالكامل في الذاكرة."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"لو التطبيق ضرب OOM، هل ده معناه بنسبة 100% إنه فيه Memory Leak؟\"\n"
            "  **المرشح:** \"لأ مش شرط نهائياً. التطبيق ممكن يكون سليم 100% من التسريبات، لكن حاول يفك تشفير صورة عالية الدقة أو يقرا ملف JSON حجمه 80 ميجابايت دفعة واحدة في الذاكرة، فطلب حجز كتلة متصلة أكبر من المساحة المتبقية وضرب OOM فوراً.\"\n\n"
            "- **المحاور:** \"إزاي تتأكد عملياً إن شاشة معينة بتسرب ذاكرة أثناء الاختبار؟\"\n"
            "  **المرشح:** \"بفتح الشاشة وأقفلها 10 مرات ورا بعض، وبعدها أعمل Force GC في Android Studio Profiler. لو استهلاك الـ Heap رجع للخط الأصلي يبقى سليمة، ولو فضل يزيد وثابت عند رقم عالي يبقى فيه مراجع Activity لسه محبوسة.\""
        ),
        "self_check_ar": (
            "فرّق بين الـ Peak والـ Baseline في منحنى الذاكرة؛ اشرح كيف يؤدي كل منهما لحدوث OOM؛ وصف بروتوكول الكشف العملي عن التسريب عبر الـ Profiler."
        ),
        "references_ar": (
            "- [فحص وإصلاح تسريبات الذاكرة](https://developer.android.com/topic/performance/memory-overview) — دليل أندرويد الرسمي لتحليل الـ Heap.\n"
            "- [أساسيات عمل LeakCanary](https://square.github.io/leakcanary/fundamentals-how-leakcanary-works/) — فهم كيفية رصد الكائنات المتبقية.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "تسريب الذاكرة هو بقاء مرجع قوي غير مقصود لكائن انتهت مهمته، مما يمنع مجمع النفايات من مسحه ويرفع استهلاك الذاكرة الأساسي باستمرار مع كل شاشة "
            "حتى ينهار التطبيق. أما تخصيص الذاكرة الضخم فهو حجز مؤقت لكتلة ذاكرة كبيرة لتنفيذ مهمة مشروعة، وتعود الذاكرة لمستواها الطبيعي فور انتهاء الدالة. "
            "التسريب يُعالج بإصلاح دورات الحياة والمراجع، بينما الحجز الضخم يُعالج بالتدفق والتحجيم."
        ),
        "best_answer_ar": (
            "تسريب الذاكرة والـ Large Allocation مفهومين مختلفين جوهرياً في هندسة أندرويد. تسريب الذاكرة عيب معماري؛ كائن خلص شغله تماماً زي شاشة Activity بعد "
            "ما المستخدم داس Back، لكنه لسه مربوط بـ GC Root حي زي Static Singleton أو خيط خلفي. النتيجة إن مساحة الكائن ده بتفضل محبوسة، والـ Baseline للذاكرة "
            "بيفضل يعلى مع كل زيارة للشاشة لحد ما يوصل لسقف الـ Heap ويحصل OutOfMemoryError.\n\n"
            "أما الـ Large Allocation فهو استهلاك مشروع للذاكرة بس بحجم كبير جداً ومؤقت. مثلاً لما نقرأ صورة من الكاميرا عشان نعرضها، بنحجز 50 أو 60 ميجابايت "
            "في لحظتها، وده بيعمل Spike حاد في منحنى الذاكرة. لكن بمجرد ما الدالة تخلص والمتغير يخرج برة الـ Scope، المرجع بيسقط والـ GC بيقدر يرجع الذاكرة "
            "كلها لنفس الخط القاعدي الأصلي.\n\n"
            "الفرق ده بيحدد طريقة الحل في بيئة الإنتاج: التسريب بنحله بمراجعة ملكية الكائنات واستخدام `WeakReference` أو تنظيف المستمعين في `onDestroy`. "
            "أما الحجز الضخم بنحله بإننا منعملش Load للبيانات كاملة، بل نستخدم Subsampling في الصور ونقرا الملفات عبر Streams عشان نحافظ على سقف الاستهلاك اللحظي."
        ),
        "deep_answer_ar": (
            "في التحليل الهندسي المتقدم للـ Heap، بنستخدم Android Studio Memory Profiler عشان نميز بين الحالتين باختبار عملي صارم. بنعمل Loop تنقل: نفتح شاشة B "
            "ونقفلها 10 مرات متتالية، ونطلب Explicit GC في الـ Profiler. لو لقينا الرسم البياني عامل درجات سلم بتطلع لفوق ومبترجعش لأصلها، وبسحب HPROF Dump لقينا 10 نسخ "
            "من `ActivityB` موجودين في شجرة الـ Dominator، فده تسريب ذاكرة مؤكد وناتج عن رابط غير مقطوع.\n\n"
            "في المقابل، الـ Large Allocation بيبان على الـ Profiler كقمة حادة مستطيلة بترجع فوراً للأرض. لكن خطورته التشغيلية بتكمن في إنه ممكن يسبب OOM لحظي "
            "حتى في غياب أي تسريب! لو التطبيق مستهلك 150 ميجابايت من سقف 192 ميجابايت، وطلبنا حجز مصفوفة بكسلات 50 ميجابايت متصلة، بيئة ART مش هتلاقي الـ Contiguous Block "
            "المطلوب وهترمي OOM فوراً.\n\n"
            "عشان كده كـ Staff Engineers، بنحط استراتيجية مزدوجة: لمواجهة الـ Large Allocations بنجبر المطورين على استخدام مكتبات تحميل الصور الحديثة زي Coil اللي "
            "بتستخدم `inSampleSize` و `inBitmap` لإعادة استخدام مساحات البايت المحجوزة مسبقاً، ونعتمد على Okio لتدفق البيانات من الشبكة للقرص مباشرة. ولمواجهة الـ Leaks "
            "بندمج LeakCanary في الـ Pull Requests ونمنع دمج أي كود بيسيب شاشات معلقة في شجرة الـ Dominator Tree."
        ),
    },
    "MEM-05": {
        "id": "MEM-05",
        "questionAr": "قارن بين تسريب الذاكرة (Memory Leak)، وخطأ نفاد الذاكرة (OOM)، وتجمد التطبيق (ANR)، وامتلاء الـ Stack (StackOverflowError).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- الفصل المعماري الدقيق بين مسارات الوصول (Reachability)، وفشل حجز الذاكرة (Allocation Failure)، واستجابة خيط الواجهة (Thread Responsiveness)، ونفاد سعة استدعاء الدوال.\n"
            "- اختيار الأدلة والملفات التشخيصية المناسبة لكل عرض بدلاً من تفسير أي تهنيج أو سقوط بأنه تسريب ذاكرة.\n"
            "- توضيح كيف يمكن لعيب في نظام معين أن يساهم في إشعال عيب آخر (مثل تسبب الـ Leak الشديد في حدوث ANR غير مباشر)."
        ),
        "why_it_matters_ar": (
            "هذه المشاكل الأربع تمثل الكوابيس الأكثر شيوعاً في استقرار تطبيقات أندرويد، ولكل منها موقع حدوث وسبب جذري مختلف تماماً:\n"
            "- **Memory Leak:** يحدث على الـ Heap، سببه بقاء مرجع لكائن منتهي، ويظهر في صورة استهلاك ذاكرة متصاعد ببطء دون انهيار فوري.\n"
            "- **OutOfMemoryError (OOM):** استثناء برمجي قاتل يحدث على الـ Heap أو الـ Native Memory عندما يفشل النظام في تلبية طلب تخصيص ذاكرة لعدم كفاية المساحة.\n"
            "- **ANR (Application Not Responding):** مراقبة على مستوى نظام التشغيل تتدخل عندما يعجز خيط الواجهة (Main Thread) عن معالجة مدخلات المستخدم خلال 5 ثوانٍ.\n"
            "- **StackOverflowError:** خطأ فادح في بيئة التشغيل يحدث على مساحة الـ Stack الخاصة بالخيط نتيجة استدعاء ذاتي عميق يتجاوز سعة إطارات الخيط."
        ),
        "worked_example_ar": (
            "جدول مقارنة حاسم وسريع بين الكوارث الأربع:\n"
            "```text\n"
            "نوع المشكلة         مكان الحدوث   السبب الجوهري                     النتيجة الظاهرة\n"
            "----------------------------------------------------------------------------------------------------\n"
            "Memory Leak         الـ Heap      كائن ميت ممسوك بمرجع قوي          ارتفاع مستمر في الرام بدون كراش فوري\n"
            "OutOfMemoryError    الـ Heap/Native طلب حجز يفوق السقف المتاح        انهيار فوري للتطبيق (Crash)\n"
            "ANR                 الـ Main Looper تجميد خيط الواجهة لأكثر من 5 ثوان  ظهور نافذة النظام وإنهاء العملية\n"
            "StackOverflowError  الـ Stack     تجاوز سعة إطارات استدعاء الدوال    انهيار فوري للتطبيق (Crash)\n"
            "```\n"
            "في الإنتاج، تسريب الذاكرة الحاد قد يملأ الـ Heap ويجبر الـ GC على العمل المتواصل بنسبة 100% CPU، مما يؤخر رسائل خيط الواجهة ويؤدي في النهاية لـ ANR متسلسل."
        ),
        "trade_offs_ar": (
            "محاولة تفادي الـ OOM عبر التخزين المستمر على القرص قد تزيد عمليات الـ I/O على خيط خاطئ وتتسبب في حدوث ANR؛ لذا يجب دائماً نقل العمليات للـ Background Threads. "
            "تحويل الخوارزميات الذاتية (Recursive) إلى خوارزميات تعتمد على هياكل بيانات على الـ Heap يحمي تماماً من الـ StackOverflowError ولكنه يتطلب حذراً لعدم "
            "إرهاق الـ Heap بكائنات وسيطة. كل حل هندسي لمشكلة يجب ألا يفتح الباب لمشكلة أخرى."
        ),
        "failure_modes_ar": (
            "الاستدعاء الدائري اللانهائي في دوال `toString()` أو `equals()` يفجر `StackOverflowError` في أجزاء من الثانية. تنفيذ قراءة ملفات أو استعلامات Room المتزامنة "
            "على خيط الـ Main Thread يطلق فوراً مهلة الـ 5 ثوان ويسبب ANR. تحميل صور غير محجمة يسبب OOM مفاجئ. التسريبات المتراكمة من شاشات الـ Activities تسبب تآكلاً "
            "تدريجياً ينتهي إما بـ OOM أو بـ ANR ناتج عن كثرة توقفات الـ GC."
        ),
        "production_perspective_ar": (
            "في بيئات العمل الضخمة، يُخصص لكل مشكلة أداة رصد متقدمة: ملفات `/data/anr/traces.txt` و Google Play Console Android Vitals لتشخيص الـ ANR؛ ملفات تفريغ الـ HPROF "
            "و Crashlytics OOM Traces لتشخيص نفاد الذاكرة؛ تقارير LeakCanary لرصد التسريبات؛ وتتبع الـ Stack Traces الدائرية في Firebase لحل الـ StackOverflowError فوراً."
        ),
        "how_to_answer_ar": (
            "- **المقارنة المنظمة:** ابدأ بفرز المشاكل الأربع بحسب مكان الحدوث (Stack, Heap, Main Thread) ونوع الأثر (بطء، تجميد، كراش فوري).\n"
            "- **العلاقات المتبادلة:** اشرح كيف يقود تسريب الذاكرة إلى OOM، وكيف يمكن أن يقود التسريب الشديد أو الـ I/O الثقيل إلى ANR.\n"
            "- **منهجية التتبع:** اذكر الأداة الدقيقة التي تستخدمها لتشخيص كل عيب من واقع خبرتك العملية في الإنتاج."
        ),
        "talking_points_ar": (
            "ناقش مهلات الـ ANR المختلفة (Input 5s, BroadcastReceiver 10/20s, Service 20s)، وحجم إطار الـ Stack لكل خيط، وكيفية قراءة حالات الخيوط (BLOCKED, WAITING) "
            "داخل ملف الـ traces.txt، وعلاقة الـ Low Memory Killer بإنهاء العمليات دون إلقاء OOM."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"هل ممكن تسريب الذاكرة (Memory Leak) يتسبب في حدوث ANR؟\"\n"
            "  **المرشح:** \"أيوة جداً. لو الـ Heap امتلأ تماماً بالكائنات المسربة، بيئة ART بتدخل في حالة GC Thrashing؛ مجمع النفايات بيفضل شغال بأقصى طاقة ويستهلك الـ CPU بنسبة 100% في محاولة يائسة لتحرير أي بايت، وده بيعطل خيط الواجهة عن معالجة اللمسات ورسم الفريمات فيتجاوز 5 ثوانٍ ويضرب ANR.\"\n\n"
            "- **المحاور:** \"لو خيط الواجهة دخل في Infinite Loop، هل هيضرب StackOverflowError ولا ANR؟\"\n"
            "  **المرشح:** \"لو كانت اللفة حلقة تكرارية عادية زي `while(true)`، الخيط مش هيضيف إطارات جديدة على الـ Stack وبالتالي مش هيحصل StackOverflowError، لكنه هيعلق خيط الواجهة وهيضرب ANR بعد 5 ثوانٍ. أما لو اللفة كانت دالة بتنادي نفسها بدون شرط توقف، هيضرب StackOverflowError في لحظتها.\""
        ),
        "self_check_ar": (
            "حدد موقع حدوث وسبب كل عيب من العيوب الأربعة؛ اشرح سيناريو يربط بين عيبين منهما؛ واذكر الملف أو الأداة المستخدمة في تشخيص كل مشكلة."
        ),
        "references_ar": (
            "- [تشخيص أخطاء توقف التطبيق ANR](https://developer.android.com/topic/performance/vitals/anr) — مهلات وسلوك خيط الواجهة.\n"
            "- [التعامل مع نفاد الذاكرة في أندرويد](https://developer.android.com/topic/performance/memory-overview) — استثناءات الـ OOM وتحليل الـ Heap.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "تسريب الذاكرة هو بقاء كائنات ميتة على الـ Heap ترفع استهلاك الرام تدريجياً دون كراش فوري. الـ OOM هو كراش بيحصل لما طلب حجز مساحة جديدة على الـ Heap "
            "أو الـ Native يفشل تماماً. الـ ANR هو تجميد لخيط الواجهة لأكثر من 5 ثوانٍ يتدخل بسببه نظام التشغيل لإنهاء العملية. والـ StackOverflowError هو انهيار "
            "فوري بسبب امتلاء إطارات استدعاء الدوال على الـ Stack نتيجة استدعاء ذاتي عميق."
        ),
        "best_answer_ar": (
            "عشان نفصل بين المصطلحات دي بمنهجية هندسية واضحة، لازم نبص لمكان وقوع كل مشكلة وطبيعة ظهورها للمستخدم.\n\n"
            "أولاً: تسريب الذاكرة (Memory Leak) بيحصل على الـ Heap، وهو عيب منطقي في الكود بيخلي كائن منتهي يفضل ممسوك بمرجع قوي. المشكلة دي مبتقفلش التطبيق في لحظتها، "
            "لكنها بتقلل المساحة المتاحة بمرور الوقت. ثانياً: خطأ نفاد الذاكرة (OutOfMemoryError) هو النتيجة الحتمية لما الـ Heap يتخنق والتطبيق يطلب حجز كائن جديد "
            "والنظام ملقاش مساحة، فبيرمي Error فوري يوقع التطبيق.\n\n"
            "ثالثاً: تجمد التطبيق (ANR) ملوش علاقة بحجم الـ Heap مباشرة، بل بزمن استجابة خيط الواجهة الرئيسي. لو الـ Main Thread انشغل بقراءة قاعدة بيانات أو دخل في "
            "Lock Contention لمدة 5 ثوانٍ أثناء تفاعل المستخدم، نظام التشغيل بيظهر رسالة التطبيق لا يستجيب. رابعاً: الـ StackOverflowError بيحصل على الـ Stack المخصص "
            "للخيط لما دوال تنادي بعضها في Infinite Recursion وتتجاوز سقف الـ 1 ميجابايت لإطارات الدوال.\n\n"
            "في بيئة العمل، بنربط بينهم لأن التسريب الشديد بيجهد المعالج بدورات تنظيف متواصلة للـ GC، وده ممكن يأخر رسائل الـ Main Thread ويولد ANR غير مباشر."
        ),
        "deep_answer_ar": (
            "في إدارة الحوادث على مستوى الإنتاج (Production Incident Triage)، التفريق بين المشاكل دي بيعتمد على قراءة الـ Artifacts الصحيحة وليس التخمين.\n\n"
            "لو العرض ANR، وجهتنا الوحيدة هي ملف `/data/anr/traces.txt` أو تقارير Android Vitals. بنفتح الـ Thread Dump ونبص على الـ `main` thread: لو حالته `BLOCKED`، "
            "بنعرف إنه مستني Mutex ماسكه Background Thread، ولو حالته `WAITING` في Binder IPC call، بنعرف إنه مستني خدمة نظام مهنجة، وبنقيس نسبة الـ CPU عشان نشوف هل كان "
            "فيه GC Thrashing أو استهلاك مفرط للأنوية.\n\n"
            "لو العرض OutOfMemoryError، بنحلل الـ Stack Trace في Crashlytics عشان نعرف السطر اللي طلب الحجز، وبنسحب HPROF Heap Dump عشان نفرق بين حالتين: هل هو Acute OOM "
            "بسبب Bitmap عملاقة طلبت 60 ميجابايت في كود سليم؟ ولا هو Chronic OOM بسبب تراكم 20 شاشة Activity مسربة في الـ Dominator Tree استنزفت الـ Heap تدريجياً؟\n\n"
            "لو العرض StackOverflowError، بنلاقي Stack Trace ضخم بيكرر نفس استدعاءات الدوال في شكل حلقة مفرغة، وحله بيكون تحويل الخوارزمية لنمط الـ Iteration باستخدام "
            "`ArrayDeque` أو تطبيق تحسينات `tailrec`. فهم الحدود الفاصلة دي هو اللي بيخلي فريق الهندسة يحدد المسؤوليات ويصلح العيب الجذري في دقائق بدل إضاعة الوقت في تحسينات عشوائية."
        ),
    },
    "MEM-06": {
        "id": "MEM-06",
        "questionAr": "ما الذي يسبب الـ Boxing والـ Unboxing؟ ومتى يؤثر ذلك فعلياً على الأداء؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- تحديد حدود تحويل الأنواع الأولية إلى كائنات مغلفة (Primitive-to-Wrapper) عند استخدام الأنواع القابلة للقيمة الفارغة (Nullable) والحاويات العامة (Generics).\n"
            "- تفسير تكلفة حجز الكائنات على الـ Heap، ومخاطر فك التغليف للقيم الفارغة (Null-unboxing)، وفقدان كفاءة كاش المعالج (CPU Cache Misses).\n"
            "- الاختيار الدقيق لمصفوفات الأنواع الأولية في مسارات الحسابات الكثيفة دون المبالغة في تحسين شاشات الواجهة العادية."
        ),
        "why_it_matters_ar": (
            "الـ Boxing هو تحويل النوع الأولي البسيط (مثل `int` أو `long`) إلى كائن مرجعي مغلف على الـ Heap (مثل `java.lang.Integer` أو `Long`). والـ Unboxing هو العملية "
            "العكسية لاستخراج القيمة الرقمية البسيطة من داخل الكائن. في Kotlin تظهر كل الأرقام بشكل موحد كـ `Int` أو `Double`، لكن المترجم يحرص على تحويلها إلى Primitives "
            "في الـ Bytecode لتوفير الأداء. ومع ذلك، يُجبر المترجم على تطبيق الـ Boxing في ثلاث حالات رئيسية: عند استخدام الأنواع القابلة لـ `null` مثل `Int?`، أو عند "
            "استخدام الـ Generics مثل `List<Int>`، أو عند تمرير القيمة لـ `Any`. في شاشات العرض العادية يكون الأثر مهملاً، ولكن في مسارات معالجة الصوت، أو الرسوميات المخصصة "
            "في `onDraw`، أو معالجة مصفوفات الأرقام الضخمة، يتسبب الـ Boxing في حجز ملايين الكائنات المؤقتة، مما يخلق Memory Churn عنيفاً ويسقط فريمات الشاشة."
        ),
        "worked_example_ar": (
            "مقارنة بين كود يسبب ملايين عمليات الـ Boxing وكود محسّن بدون أي حجز على الـ Heap:\n"
            "```kotlin\n"
            "// ❌ كود غير فعال: استخدام الحاويات العامة يجبر النظام على عمل Autoboxing لكل رقم:\n"
            "fun calculateHistogram(samples: List<Int>): Map<Int, Int> {\n"
            "    val counts = mutableMapOf<Int, Int>()\n"
            "    for (sample in samples) {\n"
            "        counts[sample] = (counts[sample] ?: 0) + 1\n"
            "    }\n"
            "    return counts\n"
            "}\n"
            "\n"
            "// ✅ كود محسّن: استخدام مصفوفات الأنواع الأولية (Zero-Allocation Primitive Array):\n"
            "fun calculateHistogramOptimized(samples: IntArray, binCount: Int): IntArray {\n"
            "    val histogram = IntArray(binCount) // مصفوفة واحدة متصلة من أرقام 32-bit\n"
            "    for (i in samples.indices) {\n"
            "        val bin = samples[i]\n"
            "        if (bin in 0 until binCount) {\n"
            "            histogram[bin]++ // عمليات حسابية أولية نقية بدون إنشاء أي كائن على الـ Heap\n"
            "        }\n"
            "    }\n"
            "    return histogram\n"
            "}\n"
            "```\n"
            "في المثال الثاني تم إلغاء إنشاء مئات الآلاف من كائنات `Integer` و `Entry` على الـ Heap، مما وفر عشرات الميجابايت وأزال توقفات الـ GC بالكامل."
        ),
        "trade_offs_ar": (
            "استخدام `List<Int>` في Kotlin يمنح المطور مرونة هائلة ودعماً لكافة دوال البرمجة الوظيفية مثل `map` و `filter`، وهو الخيار الأمثل لقوائم الواجهة العادية "
            "التي تحتوي على عشرات العناصر. في المقابل، التحول إلى `IntArray` أو `SparseIntArray` يفرض التعامل مع دوال منخفضة المستوى وأقل مرونة، ولكنه ضروري وحاسم "
            "في المسارات الحسابية الكثيفة ومعالجة إشارات الحساسات لتجنب الـ Memory Churn. لا يجب التضحية بنظافة الكود وسهولة قراءته إلا إذا أثبت الـ Profiler وجود عنق زجاجة حقيقي."
        ),
        "failure_modes_ar": (
            "محاولة فك تغليف كائن مغلف يحمل القيمة `null` (Null-unboxing) يولد استثناء `NullPointerException` فوري عند محاولة استخراج القيمة الأولية منه. الإفراط "
            "في استخدام `List<Int>` في حلقات معالجة الصور أو الصوت يملأ الـ Young Generation بكائنات `Integer` ويجبر مجمع النفايات على إيقاف التطبيق وسقوط الفريمات. "
            "مقارنة الكائنات المغلفة باستخدام `==` و `===` قد تسبب أخطاء منطقية خفية بسبب تخزين القيم الصغيرة مؤقتاً في كاش النظام."
        ),
        "production_perspective_ar": (
            "في التطبيقات الكبيرة، نراقب مسارات الحجز السريعة عبر Allocation Tracker في Android Studio Profiler. إذا لاحظنا نمط المنشار المتكرر (Sawtooth Pattern) "
            "الناتج عن كائنات `java.lang.Integer`، نقوم بالتدخل واستبدال المجموعات العامة بمجموعات أندرويد المتخصصة للأنواع الأولية مثل `SparseArray` و `SparseIntArray` "
            "و `LongSparseArray`، ونعتمد على `@JvmInline value class` لتغليف المعرفات الرقمية دون تكلفة إنشاء كائنات في الـ Runtime."
        ),
        "how_to_answer_ar": (
            "- **التعريف البرمجي:** اشرح مفهوم الـ Boxing كتحويل من Primitive إلى Wrapper، والـ Unboxing كعملية استخراج عكسية.\n"
            "- **مواضع الحدوث في Kotlin:** بيّن الحالات الثلاث (Nullable types, Generics, Any) وكيف يتعامل معها مترجم Kotlin.\n"
            "- **الأثر الفعلي:** فرّق بين الاستخدام العادي غير المؤثر في الـ UI، والاستخدام الكثيف في الحسابات والرسوميات الذي يسبب GC Churn ويفسد تجربة المستخدم."
        ),
        "talking_points_ar": (
            "ناقش حجم كائن الـ Integer على أنظمة 64-bit (16 بايت مقابل 4 بايت للـ Primitive)، وتأثير الـ Pointer Chasing على فقدان كاش المعالج (CPU Cache Misses)، "
            "وآلية عمل `IntegerCache` للقيم بين -128 و 127، وتقنية `@JvmInline value class` في إزالة عبء التغليف."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"ليه `Int?` بياخد مساحة أكبر في الذاكرة من `Int` في Kotlin؟\"\n"
            "  **المرشح:** \"لأن `Int` غير القابل للـ null بيترجم مباشرة في الـ Bytecode لـ primitive `int` حجمه 4 بايت بس على الـ Stack. أما `Int?` فهو قابل للـ null، والـ JVM مبيعرفش يحط null في primitive، فالمترجم بيضطر يعمله Boxing في كائن `java.lang.Integer` على الـ Heap، وده بيكلف 16 بايت في أنظمة 64-bit بسبب الـ Object Header ومحاذاة الذاكرة.\"\n\n"
            "- **المحاور:** \"إيه الفرق بين `Array<Int>` و `IntArray` في Kotlin؟\"\n"
            "  **المرشح:** \"`Array<Int>` بتترجم لـ `Integer[]` في Java، يعني مصفوفة من المؤشرات اللي بتشاور على كائنات مغلفة مبعثرة على الـ Heap مع كل تكاليف الـ Boxing. أما `IntArray` بتترجم لـ `int[]`، يعني كتلة ذاكرة متصلة من الأرقام الأولية الخام بدون أي كائنات مغلفة وبأعلى كفاءة للمعالج.\""
        ),
        "self_check_ar": (
            "اشرح متى يُجبر مترجم Kotlin على عمل Boxing؛ قارن بين حجم `int` و `Integer` في الذاكرة؛ وحدد ثلاث مجموعات بديلة في أندرويد لتفادي التغليف."
        ),
        "references_ar": (
            "- [الأنواع الأولية في توثيق Kotlin](https://kotlinlang.org/docs/basic-types.html#numbers) — تمثيل الأرقام والـ Autoboxing في الـ Bytecode.\n"
            "- [تحسين مجموعات البيانات في أندرويد](https://developer.android.com/reference/android/util/SparseIntArray) — استخدام Sparse Arrays لتفادي عبء التغليف.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "الـ Boxing هو تحويل النوع الأولي البسيط زي `int` لكائن مغلف على الـ Heap زي `Integer`، والـ Unboxing هو استخراج القيمة منه. بيحصل تلقائياً في Kotlin "
            "لما نستخدم `Int?` القابل للـ null أو مع الـ Generics زي `List<Int>`. في الشاشات العادية تأثيره مهمل، لكن في الحلقات التكرارية الكبيرة ومعالجة الرسوميات "
            "أو الصوت بيحجز ملايين الكائنات ويسبب ضغطاً هائلاً على مجمع النفايات، وحله استخدام `IntArray` ومجموعات الـ Sparse."
        ),
        "best_answer_ar": (
            "في Kotlin، بنشوف كل الأنواع موحدة كـ `Int` و `Long` عشان تجربة المطور تكون نظيفة، لكن تحت الكابوت في الـ Bytecode، المترجم بيحاول طول الوقت يستخدم الـ "
            "Primitives بتاعة الـ Java عشان الأداء والذاكرة.\n\n"
            "الـ Autoboxing بيحصل مجبراً لما الـ Primitive يحتاج يتصرف كـ Object. ده بيحصل تحديداً في تلات سيناريوهات: أولاً لو المتغير يقبل `null` زي `Int?`، لأن الـ "
            "Primitive مينفعش يشيل `null` في الـ JVM. ثانياً مع الـ Generics زي `List<Int>` أو `Map<Int, String>` لأن الـ Type Erasure بيتعامل مع كائنات مش أرقام أولية. "
            "وثالثاً لو مررنا الرقم لـ `Any`.\n\n"
            "تأثير ده بيبان لما نقارن الذاكرة: الـ Primitive `int` بيستهلك 4 بايت بس على الـ Stack أو جوه الكائن، بينما الـ Boxed `Integer` بيستهلك من 16 لـ 24 بايت على "
            "الـ Heap بسبب الـ Object Header والـ Alignment. لو بنعالج شاشة عادية فيها 20 عنصر، الأثر مش ملحوظ. لكن لو بنعمل تدوير بيانات أو رسم في دالة `onDraw` أو "
            "معالجة مستشعرات بتلف آلاف المرات في الثانية، الـ Boxing هيولد ملايين الكائنات المؤقتة، وده هيسبب Memory Churn ويسقط فريمات العرض فوراً."
        ),
        "deep_answer_ar": (
            "على مستوى الـ Bytecode ومعمارية المعالج، تأثير الـ Boxing بيمتد لسرعة الـ CPU Pipeline وكفاءة الكاش. المترجم بيولد نداء لدالة `Integer.valueOf(int)` عند التغليف، "
            "ودالة `Integer.intValue()` عند فك التغليف. جافا بتوفر كاش للأرقام من -128 لـ 127 من خلال `IntegerCache`، لكن أي رقم برة النطاق ده بينشئ كائن جديد تماماً على الـ Heap.\n\n"
            "المشكلة الكبرى هنا هي الـ Pointer Chasing وفقدان الـ Cache Locality. لما بنستخدم `ArrayList<Integer>`، المعالج مبيقدرش يقرا مصفوفة أرقام متصلة ويسحبها للـ L1 "
            "Data Cache، بل بيضطر يقرأ مؤشر، ويروح يدور على عنوان الكائن المبعثر في الـ RAM، وده بيعمل CPU Cache Misses متكررة بتعطل الـ Execution Pipelines.\n\n"
            "غير كده، فك التغليف بيحمل مخاطرة وقوع `NullPointerException` خفي؛ لو كائن `Integer` كان بقيمة `null` وجينا نستخدمه في عملية حسابية، الـ Runtime هيستدعي "
            "`intValue()` على مؤشر فاضي ويوقع التطبيق. كـ Staff Engineers، بنحل المشاكل دي في المسارات الحرجة باعتماد مصفوفات الـ Primitives زي `IntArray` و `FloatArray`، "
            "واستخدام مجموعات أندرويد المحسنة زي `SparseIntArray` لتفادي تغليف المفتاح والقيمة، والاعتماد على `@JvmInline value class` للحصول على Type Safety كاملة في "
            "الكود مع صفر كائنات مغلفة في الـ Bytecode. كمان في واجهات المستخدم الحديثة المعتمدة على Jetpack Compose، تجنب الـ Autoboxing في معالجة الحالات الرقمية المتكررة بيمنع إعادة تكوين الكومبوزابلز وإهدار موارد البطارية بدون داعٍ."
        ),
    },
    "MEM-07": {
        "id": "MEM-07",
        "questionAr": "اشرح الفارق بين int و Integer في التوافقية مع Java (Java Interoperability).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": (
            "- التمييز بين النوع الأولي `int` غير القابل للـ null والكائن المرجعي `java.lang.Integer` القابل للـ null في سياق لغة Java.\n"
            "- تفسير كيفية ربط Kotlin لهذين النوعين بالنوع الموحد `Int` ومخاطر الأنواع غير المحددة (Platform Types `Int!`) عند استدعاء كود Java.\n"
            "- تحديد مصائد مطابقة الهوية ومقارنة الكائنات وتفادي استثناءات فك التغليف للقيمة الفارغة (Null-unboxing Pitfalls)."
        ),
        "why_it_matters_ar": (
            "فهم الفارق بين `int` و `Integer` أمر جوهري عند بناء تطبيقات أندرويد حديثة تتفاعل مع مكتبات Java أو كود قديم. في Java، `int` هو نوع أولي (Primitive) "
            "يخزن قيمة رقمية صريحة بحجم 32-bit ولا يمكن أن يكون `null` على الإطلاق، مع كفاءة قصوى واستهلاك صفر ذاكرة كائنية. في المقابل، `java.lang.Integer` هو "
            "كائن مرجعي كامل (Object) يغلف الرقم الأولي، مما يسمح له بتمثيل غياب القيمة (`null`) والمشاركة في المجموعات العامة (Generics). في Kotlin، تم توحيد "
            "المفهومين برمجياً تحت اسم `Int`، حيث يترجمه المترجم إلى `int` إذا كان غير قابل للـ null، وإلى `Integer` إذا كان يقبل الـ null (`Int?`) أو ضمن Generics. "
            "تكمن الخطورة الكبرى عند استدعاء دوال Java تفتقر إلى توصيفات الأمان (JSR-305 Annotations)، حيث يعتبرها Kotlin نوعاً حراً (`Int!`)، مما قد يفجر التطبيق بـ NPE عند فك التغليف التلقائي."
        ),
        "worked_example_ar": (
            "فخ الـ Platform Type عند التعامل مع مكتبة Java قديمة:\n"
            "```kotlin\n"
            "// تعريف في ملف Java بدون Annotations:\n"
            "// public class LegacyAnalytics {\n"
            "//     public static Integer getScoreOrNull() { return null; }\n"
            "// }\n"
            "\n"
            "// ❌ استدعاء من كود Kotlin يسبب كراش لحظي:\n"
            "fun processAnalytics() {\n"
            "    // المترجم يرى النوع كـ Integer! فلو فرضنا أنه Int غير قابل للـ null:\n"
            "    val score: Int = LegacyAnalytics.getScoreOrNull() // 💥 يرمي NullPointerException عند محاولة عمل unboxing لـ null!\n"
            "}\n"
            "\n"
            "// ✅ الاستدعاء الآمن بتحديد القابلية للـ null صراحة:\n"
            "fun processAnalyticsSafe() {\n"
            "    val score: Int? = LegacyAnalytics.getScoreOrNull() // آمن ومحمي\n"
            "    if (score != null) {\n"
            "        println(\"User score: $score\")\n"
            "    }\n"
            "}\n"
            "```\n"
            "بتحديد النوع كـ `Int?`، يجبرنا المترجم على فحص القيمة ضد `null` قبل استخراج الرقم الأولي واستخدامه، مما يمنع سقوط التطبيق."
        ),
        "trade_offs_ar": (
            "استخدام `int` الأولي يوفر أقصى سرعة تنفيذ وأقل استهلاك لذاكرة الـ Heap، ولكنه يعجز عن تمثيل الحالات التي تكون فيها القيمة غير متوفرة أو اختيارية. "
            "استخدام `Integer` يتيح تمثيل القيمة الفارغة (`null`) والتوافق مع الـ Generics وواجهات برمجة التطبيقات القديمة، لكنه يدفع ضريبة حجز الكائنات وتكاليف فك "
            "التغليف وإمكانية وقوع أخطاء مطابقة المراجع. الخيار الأمثل دائماً هو تفضيل `Int` غير القابل للـ null إلا إذا كانت القيمة اختيارية فعلياً."
        ),
        "failure_modes_ar": (
            "الاستدعاء التلقائي لـ `intValue()` على كائن `Integer` يحمل القيمة `null` يؤدي فوراً إلى `NullPointerException`. مقارنة كائنين من نوع `Integer` باستخدام "
            "معامل مطابقة المراجع `==` في Java (أو `===` في Kotlin) قد تعطي نتائج صحيحة للأرقام بين -128 و 127 بسبب كاش النظام وتفشل تماماً مع الأرقام الأكبر مسببة "
            "أخطاء منطقية كارثية. تمرير مصفوفات `Integer[]` إلى دوال C++ عبر JNI يخلق عبء تحويل هائل ويفقد ميزة التثبيت المباشر للذاكرة."
        ),
        "production_perspective_ar": (
            "في المشاريع الضخمة التي تحتوي على كود مشترك بين Java و Kotlin، نفرض تطبيق أدوات التحليل الثابت والـ Linter للتأكد من وجود توصيفات `@NonNull` و `@Nullable` "
            "على كافة دوال Java العامة. هذا يمنع ظهور الـ Platform Types (`Int!`) في طبقة الـ Kotlin، ويجعل المترجم قادراً على فرض الأمان التام للأنواع أثناء الترجمة، "
            "مما يحمي طبقة الإنتاج من استثناءات الـ NPE الخفية."
        ),
        "how_to_answer_ar": (
            "- **الأساس الكائني:** اشرح الفارق الجوهري في Java بين الـ Primitive Value والـ Reference Object، مع ذكر قيود الـ null والـ Generics.\n"
            "- **معالجة Kotlin للمفهوم:** وضّح كيف دمجت Kotlin المفهومين في `Int`، وكيف يتحول في الـ Bytecode بحسب القابلية للـ null (`Int` مقابل `Int?`).\n"
            "- **فخ التوافقية (Interop Trap):** اشرح مفهوم الـ Platform Type ومصيدة الـ NullPointerException عند استدعاء كود Java قديم."
        ),
        "talking_points_ar": (
            "ناقش توليد تعليمات الـ Bytecode مثل `INVOKESTATIC Integer.valueOf` و `INVOKEVIRTUAL Integer.intValue`، وتفاصيل كاش الأرقام في `IntegerCache`، "
            "وكيفية تمرير المصفوفات الأولية عبر JNI باستخدام `GetPrimitiveArrayCritical` لتمكين المعالجة بدون نسخ (Zero-Copy)."
        ),
        "follow_ups_ar": (
            "- **المحاور:** \"لو قارنا كائنين `Integer` بيحتووا على الرقم 100 باستخدام `==` في Java، إيه النتيجة؟ ولو الرقم 200؟\"\n"
            "  **المرشح:** \"مع الرقم 100 المقارنة هترجع `true`، لكن مع الرقم 200 هترجع `false`! والسبب هو إن Java بتعمل Caching لكائنات الـ Integer في النطاق من -128 إلى 127 عبر `IntegerCache`، فالمؤشرين بيشاوروا على نفس الكائن في الذاكرة. أما 200 فبيتم إنشاء كائنين منفصلين، ومقارنة `==` في Java بتقارن المراجع مش القيم، وده فخ شهير جداً.\"\n\n"
            "- **المحاور:** \"إزاي مترجم Kotlin بيحمينا من الفخ ده؟\"\n"
            "  **المرشح:** \"في Kotlin، معامل `==` بيترجم دائماً لـ `.equals()` اللي بتقارن القيمة الرقمية الفعلية مش المرجع، ولو محتاجين نقارن المراجع صراحة بنستخدم معامل `===`.\""
        ),
        "self_check_ar": (
            "فرّق بين تمثيل `Int` و `Int?` في الـ Bytecode؛ اشرح سلوك الـ IntegerCache؛ ووضح خطورة الـ Platform Type عند التعامل مع كود Java."
        ),
        "references_ar": (
            "- [التوافق بين Java و Kotlin](https://kotlinlang.org/docs/java-to-kotlin-interop.html) — التعامل مع الأنواع والـ Platform Types.\n"
            "- [توثيق فئة Integer في Java](https://docs.oracle.com/javase/8/docs/api/java/lang/Integer.html) — تفاصيل التغليف وكاش الأرقام.\n\n"
            "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."
        ),
        "quick_answer_ar": (
            "في Java، الـ `int` هو نوع أولي بسيط بحجم 32-bit ولا يقبل الـ null إطلاقاً ومفيش عليه أي overhead، بينما `Integer` هو كائن مغلف على الـ Heap بيقبل الـ null "
            "وبيدعم الـ Generics. في Kotlin، الاتنين مدمجين تحت اسم `Int`؛ فلو كان غير قابل للـ null بيترجم لـ `int` أولي، ولو كان `Int?` أو في قائمة بيترجم لـ `Integer`. "
            "الخطورة في التوافقية بتظهر لما Java ترجع `Integer!` بدون توثيق ويتم استخدامه كـ `Int` فيحصل كراش NPE."
        ),
        "best_answer_ar": (
            "التفرقة بين `int` و `Integer` في عالم أندرويد بتمثل الفارق بين الأداء الخام للعتاد والمرونة الكائنية للغة Java.\n\n"
            "في Java الصريحة، `int` ده Primitive بيعيش قيمته مباشرة على الـ Stack أو جوه الكائن، استهلاكه 4 بايت ومستحيل يكون `null`. أما `java.lang.Integer` فده كائن كامل "
            "على الـ Heap شايل الرقم جواه، وده بيسمح له يمثل غياب القيمة كـ `null`، ويدخل في الحاويات العامة زي `List<Integer>` لأن Java بتمنع وضع Primitives جوه الـ Generics.\n\n"
            "لما جينا لكوتلن، مصممي اللغة وحدوا الموضوع تحت نوع واحد وهو `Int`. المترجم بذكاء بيبص على السياق: لو كتبت `val x: Int = 10`، هيولد في الـ Bytecode نوع `int` أولي. "
            "لكن لو كتبته يقبل الفراغ `val x: Int? = null` أو حطيته جوه `List<Int>`، بيترجمه فوراً لـ `java.lang.Integer`.\n\n"
            "نقطة الخطورة في بيئة الإنتاج بتظهر عند التوافقية مع كود Java قديم بدون Annotations. كوتلن بيعتبر النوع العائد Platform Type (`Int!`)، ولو المطور استقبله كـ `Int` "
            "وكانت القيمة الحقيقية `null`، التطبيق هيرمي `NullPointerException` لحظي بسبب محاولة فك التغليف التلقائي. عشان كده لازم دايماً نحدد النوع بـ `Int?` لتأمين الكود."
        ),
        "deep_answer_ar": (
            "لو فحصنا كود الـ Bytecode المترجم، هنلاقي إن استخدام `Int` العادي بيولد أوامر معالج مباشرة وسريعة جداً زي `ILOAD` و `ISTORE` و `IADD`. أول ما نحط علامة الاستفهام "
            "`Int?`، المترجم بيولد استدعاءات ميثود صريحة لـ `INVOKESTATIC java/lang/Integer.valueOf` عند التخزين، و `INVOKEVIRTUAL java/lang/Integer.intValue` عند القراءة. "
            "ده مش بس بيزود حجم كود الـ DEX، بل بيضاعف استهلاك الذاكرة 4 مرات على الأقل على أنظمة ART 64-bit.\n\n"
            "فخ التوافقية التاني هو مقارنة الهوية (Identity Comparison). في Java، فئة `Integer` فيها كاش داخلي ثابت اسمه `IntegerCache` بيحتفظ بكائنات الأرقام من -128 لحد 127. "
            "لو استلمت كائنين `Integer` من Java وحاولت تقارنهم بالـ Reference، هيدوك `true` لو الرقم 50، وهيدوك `false` لو الرقم 500 حتى لو القيمتين متطابقتين! كوتلن بتنقذنا من "
            "الفخ ده بأن معامل `==` بيفك المقارنة لـ `equals()` تلقائياً، بينما بيحتفظ بمعامل `===` لمقارنة المراجع.\n\n"
            "وعلى مستوى الـ JNI والـ C++ Interop، تمرير مصفوفة `int[]` بيسمح لنا نستخدم `GetPrimitiveArrayCritical`، وده بيعمل Pinning للذاكرة في بيئة ART وبيدي كود C++ مؤشر "
            "مباشر للـ Raw Buffer بدون نسخ وبدون تدخل مجمع النفايات. أما لو مررت مصفوفة `Integer[]`، الـ Runtime هيضطر يفك كل مؤشر كائن على حدة، وده بيخلق JNI Overhead عنيف "
            "وبيمنع الـ Vectorization. كـ Staff Engineers، بنلزم الفرق بوضع `@NonNull` و `@Nullable` على كل واجهات الـ Java وبنعتمد على مصفوفات الـ Primitives في معالجة البيانات."
        ),
    },
}

def main():
    print("=== Elevating MEM-01 to MEM-07 ===")
    out_meta = {}

    for qid in ["MEM-01", "MEM-02", "MEM-03", "MEM-04", "MEM-05", "MEM-06", "MEM-07"]:
        print(f"Updating canonical question {qid}...")
        en = EN_DATA[qid]
        ee.update_canonical_question(
            qid=qid,
            concept_en=en["concept_en"],
            walkthrough_en=en["walkthrough_en"],
            structured_en=en["structured_en"],
            deep_senior_en=en["deep_senior_en"],
            short_en=en["short_en"],
        )
        out_meta[qid] = AR_DATA[qid]

    meta_path = ee.DATA_DIR / "metadata_mem_01_07.json"
    meta_path.write_text(json.dumps(out_meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(out_meta)} metadata records to {meta_path}")

    ee.merge_all_metadata()

    has_err = False
    for qid in ["MEM-01", "MEM-02", "MEM-03", "MEM-04", "MEM-05", "MEM-06", "MEM-07"]:
        errs = ee.validate_question(qid)
        if errs:
            has_err = True
            print(f"ERRORS in {qid}:")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"PASS: {qid} (0 errors)")

    if has_err:
        sys.exit(1)
    print("Batch 1 (MEM-01 to MEM-07) completed successfully!")

if __name__ == "__main__":
    main()
