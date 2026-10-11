---
id: "MEM-13"
question: "How do Bitmap allocations and image-loading libraries affect memory?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "B"
phase: 1
priority: "P1"
order: 68
editorial_status: "reviewed"
---

# MEM-13

## Original interview question

How do Bitmap allocations and image-loading libraries affect memory?

## What the interviewer evaluates

- Estimate decoded pixel memory instead of relying on compressed file size.
- Explain target-size decoding, lifecycle-aware requests, caches, and native/graphics memory.
- Avoid unsafe manual recycle or unlimited caching when using an image library.

## Explanation in Arabic

الصورة JPEG ممكن تكون 200KB على القرص لكن بعد فك الضغط 4000×3000 بكسل بـ`ARGB_8888` تحتاج تقريبًا 48MB قبل نسخ إضافية. لذلك تحميل الأصل كاملًا لـthumbnail صغير يهدر memory ويزود decode time وjank. مكتبات زي Coil أو Glide تقيس target size، تدير request cancellation والـmemory/disk cache والـbitmap pooling. لكن لازم تحدد حجم العرض وتربط الطلب بعمر الواجهة وتراقب cache budget. على Android الحديث pixel data قد تظهر في native memory، فلا تكتفي برسم Java heap فقط. لو التطبيق يستعمل library لإدارة الصور لا تعمل `recycle()` يدويًا على bitmap ما زالت مملوكة لها.

## Why it matters and how it works

Decoded bitmap size is roughly width × height × bytes per pixel for a chosen configuration, independent of compressed download size. Decoding on Main may block frames; repeated full-size decode can exhaust memory. An image loader coordinates sizing, caching, deduplication or pooling, and request lifecycle, but configuration choices and unbounded custom caches can defeat those benefits. Modern Android memory inspection must include native and graphics categories.

## Worked example

A catalog row displays a 120×120 thumbnail from a 4000×3000 photo. Request a rendition near the display dimensions and cancel the request when the item/view owner is disposed. For a zoom screen, use an appropriately larger rendition or tiled decoding rather than globally loading full resolution for every list item. A 4000×3000 ARGB_8888 decoded image is about 48 MB (`4000*3000*4` bytes), excluding overhead and temporary copies; this is a size estimate, not a measured app allocation.

## Trade-offs and decision criteria

Larger decoded images improve zoom quality but increase memory and decode latency. A bounded memory cache improves scroll reuse yet competes with other app memory; disk cache trades storage for network and CPU. RGB_565 uses fewer bytes but loses alpha and color quality. Use an established loader where feasible; manual bitmap pool management adds substantial correctness complexity.

## Failure modes

The list decodes original-size images and OOMs on low-memory devices. A singleton cache retains every image indefinitely. A View callback keeps a request and Activity alive after navigation. Manual recycling causes drawing a recycled bitmap. A heap graph looks small while native bitmap pixel buffers dominate; inspect full process memory and decode traces.

## Production perspective

Set image-size contracts per surface, request server thumbnails where available, and cap cache memory. Test long scrolling and rapid navigation on constrained devices, capture Java/native/graphics memory and frame timing, then compare after changes. Monitor image-related OOM clusters and failed decodes without logging private image content.

## Interview answer — short

“Decoded bitmaps can use far more memory than compressed files. I decode near the display size and use a lifecycle-aware image loader with bounded caches, then inspect native and graphics memory as well as the Java heap.”

## Interview answer — structured

“A 4000 by 3000 ARGB_8888 image is roughly 48 MB after decode even if the JPEG is small. Loading it for a thumbnail wastes memory and decode time. I request a size near the target view, use an image library such as Coil or Glide to manage requests and cache/pool behavior, and let the library own its bitmaps. The library is not an excuse for an unbounded custom cache or for starting work after a screen closes. I measure peak process memory, native/graphics categories, and frame timing on a low-memory device.”

## Interview answer — deep senior

“I reason in decoded pixels, not compressed bytes. The image dimensions and pixel format determine memory, and transformations may temporarily require additional buffers. For a scrolling list, I request thumbnail-sized content, ideally from the server or a loader that down-samples before display, and tie requests to the current view owner so recycled rows do not show stale results or keep screens alive. I set memory and disk cache budgets based on device constraints and use a larger or tiled strategy only for true zoom. Android's bitmap pixel storage can appear in native memory, so a Java heap-only profile can miss the dominant cost. I do not manually recycle a bitmap that an image library still owns. My regression test scrolls and navigates repeatedly on constrained devices and compares decode count, peak footprint, dropped frames, and OOM rate.”

## Deep-dive talking points

Discuss bytes per pixel, downsampling, native pixel buffers, request lifecycle, cache budget, and zoom trade-offs.

## Follow-up questions

- Why is a 200KB JPEG not a 200KB bitmap? **Answer:** decoding expands compressed pixels into an in-memory pixel buffer determined by dimensions and format.
- Why might Java heap profiling miss image pressure? **Answer:** modern bitmap pixel storage and graphics buffers can be accounted outside the managed Java heap.
- Should you call `recycle()` on a loader-owned image? **Answer:** generally no; the library may still display or pool it and manual recycling can break its ownership contract.

## Self-check rubric

Estimate a decoded image, choose a target-size strategy, explain loader ownership, and measure full process memory and frame cost.

## References and reviewed-on date

- [Bitmaps and memory](https://developer.android.com/topic/performance/memory/guide/bitmaps) — pixel formats, footprint, and pooling.
- [Load large bitmaps efficiently](https://developer.android.com/topic/performance/graphics/load-bitmap) — target-sized decode.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The memory calculation is theoretical, not a measured allocation.
