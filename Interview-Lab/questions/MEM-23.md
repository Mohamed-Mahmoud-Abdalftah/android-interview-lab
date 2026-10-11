---
id: "MEM-23"
question: "An app freezes only when decoding a large image. How do you diagnose it?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "C"
phase: 1
priority: "P1"
order: 78
editorial_status: "reviewed"
---

# MEM-23

## Original interview question

An app freezes only when decoding a large image. How do you diagnose it?

## What the interviewer evaluates

- Separate main-thread decode latency from OOM, GC pressure, and GPU upload/render cost.
- Reproduce with original dimensions, pixel format, target view size, and device memory.
- Fix decode sizing/thread ownership and validate both responsiveness and image quality.

## Explanation in Arabic

أولًا حدد “freeze” يعني dropped frames ولا ANR ولا OOM crash. سجل حجم الصورة الحقيقي وأبعادها، لأن ملف مضغوط صغير قد يفك إلى عشرات MB. خذ trace وقت فتح الصورة: هل Main thread تنادي decoder أو تنتظر bitmap allocation/GC؟ هل الـdecode على worker لكن Main تنتظر `join` أو lock؟ هل التأخير في upload للـGPU أو layout؟ راقب Java/native/graphics memory. بعدها اطلب حجم يناسب الشاشة، decode خارج Main عبر image loader، وألغِ طلبات الواجهة المغلقة. لصورة zoom استخدم tiles أو rendition مناسب بدل ضغط كل الأصل في thumbnail. اختبر الجودة والوقت والذاكرة على جهاز ضعيف.

## Why it matters and how it works

Image decompression expands pixels according to dimensions and format; 4000×3000 ARGB_8888 needs about 48 MB of pixel storage before temporary buffers. Decode and transform work can block Main if called synchronously, while a background decode may still trigger memory pressure or an expensive handoff/upload. An ANR requires a blocked responsiveness path, not merely a high allocation. Trace frame and thread timelines, plus memory categories, to find the actual phase.

## Worked example

On a low-memory device, opening a 6000×4000 JPEG in a 300×200 preview blocks Main for hundreds of milliseconds. Capture a Perfetto trace and Android Studio memory profile; if `BitmapFactory.decodeStream` appears on Main, route through a lifecycle-aware loader with 300×200 target size. If the feature supports zoom, request a separate high-resolution path with tiling. This is a hypothetical diagnosis and timing, not a measured project result.

## Trade-offs and decision criteria

Downsampling reduces memory and latency but may blur zoom; use different image sizes for thumbnail and detail. Background decode protects Main, yet unrestricted parallel decodes can OOM, so bound concurrency. Hardware bitmaps can help drawing in some paths but have restrictions for pixel access and memory accounting. Caching reduces repeat decode but must be bounded and account-scoped.

## Failure modes

Moving decode to `Dispatchers.IO` while immediately calling `runBlocking` on Main leaves the freeze. Decoding full resolution off Main avoids one stall but still OOMs. A stale request binds an old bitmap into a recycled list row. Repeated retries of a malformed image waste CPU. Catch decode failure, validate source dimensions and limits, cancel obsolete requests, and test low-RAM devices.

## Production perspective

Capture input metadata, trace slice, frame metric, and memory categories without storing private image contents. Fix target sizing and lifecycle request ownership; cap in-flight decodes. Compare time to first preview, slow-frame percentile, peak native/graphics footprint, and visual quality before/after across representative devices and image types. Monitor image-related ANR/OOM cohorts after staged rollout.

## Interview answer — short

“I trace the freeze to distinguish synchronous decode, GC/OOM pressure, and rendering cost. Then I request an image near the view size, decode off Main with bounded concurrency, and measure frame time and memory on a constrained device.”

## Interview answer — structured

“I reproduce with the original image and device, record dimensions and target size, and clarify whether the symptom is jank, ANR, or OOM. A compressed file can expand to tens of megabytes. I capture a system trace and memory profile to see whether Main decodes synchronously, waits on a worker, or stalls during allocation and upload. I use a lifecycle-aware image loader to downsample for the preview and cancel stale work. If users need zoom, I provide a separate larger or tiled strategy. I compare responsiveness, peak process memory, and visual quality after the change.”

## Interview answer — deep senior

“The phrase ‘freezes on a large image’ hides several mechanisms. I first classify the failure with an ANR trace, frame timeline, and OOM evidence. I calculate the decoded footprint from pixel dimensions and format, then capture a Perfetto trace and memory categories while opening the exact image on a representative low-memory device. If decode executes on Main, I move it to a loader-managed worker path and request dimensions close to the target. If Main is blocked waiting on a worker, I remove the synchronous join or lock; if native bitmap memory or GPU upload dominates, I reduce size, cap parallel decodes, or use tiling for zoom. I guard malformed input and cancel requests when the view ends so old results cannot bind to recycled rows. I verify slow frames, first-preview latency, peak footprint, OOM rate, and acceptable image quality, then watch staged rollout cohorts.”

## Deep-dive talking points

Discuss decoded footprint, Main wait versus worker decode, GPU upload, bounded concurrency, target sizing, and zoom quality.

## Follow-up questions

- Does `withContext(IO)` always solve the freeze? **Answer:** no; Main could still wait synchronously, allocation/GC or GPU work may dominate, and full-size decode may OOM.
- Why separate thumbnail and zoom strategies? **Answer:** the preview needs few pixels, while zoom requires detail without loading every image at full resolution.
- What evidence distinguishes ANR from OOM? **Answer:** ANR traces show unresponsive execution; OOM crash and memory profiles show allocation failure and footprint.

## Self-check rubric

Classify the symptom, calculate decoded size, inspect trace and memory, propose a bounded decode path, and verify image quality.

## References and reviewed-on date

- [Load large bitmaps efficiently](https://developer.android.com/topic/performance/graphics/load-bitmap) — downsampling.
- [Bitmaps and memory](https://developer.android.com/topic/performance/memory/guide/bitmaps) — footprint and pixel storage.
- [System tracing](https://developer.android.com/topic/performance/tracing) — thread and frame timeline.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. No image decode benchmark was performed.
