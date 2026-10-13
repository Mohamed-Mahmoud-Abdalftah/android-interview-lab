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

تشخيص وعلاج تجمد التطبيق (App Freeze) الذي يحدث فقط عند فك تشفير صورة كبيرة (Decoding Large Image):

1. الأسباب الجذرية لتجمد التطبيق عند فك تشفير الصور:
   - **Main Thread Decoding**: استدعاء `BitmapFactory.decode*` مباشرة على الـ UI Thread؛ فك تشفير صورة بدقة 20 ميجابكسل يستغرق 300-800ms من الحسابات الثقيلة، مما يجمد الشاشة ويسقط عشرات الفريمات.
   - **Out of Memory Heap Thrashing**: الصورة تستهلك عشرات الميجابايتات؛ قبل حدوث OOM صريح، يحاول الـ Garbage Collector القيام بـ GC Compactions متتالية في وضع Stop-The-World في محاولة يائسة لتوفير مساحة متصلة، مما يوقف التطبيق لعدة ثوانٍ.

2. التشخيص المنهجي (Diagnosis Workflow):
   - فحص الـ **Logcat**: البحث عن رسائل `Choreographer: Skipped XX frames` أو رسائل ART GC مثل `Background concurrent copying GC freed ...` متكررة.
   - فتح **CPU Profiler**: تشغيل System Trace ورؤية هل الـ `main` thread مشغول في دالة `BitmapFactory.nativeDecodeStream()`.
   - فحص **Memory Profiler**: رؤية قفزة هائلة في مساحة الذاكرة (Native أو Java Heap) بالتزامن مع لحظة الضغط على الصورة.

3. الحل الهندسي المتكامل:
   - **نقل فك التشفير إلى Background Thread**: استخدام `withContext(Dispatchers.IO)`.
   - **Subsampling (inJustDecodeBounds & inSampleSize)**: قراءة أبعاد الصورة الأصلية أولاً دون تحميل بكسلاتها، ثم حساب معامل التصغير المناسب لحجم الشاشة فقط.
   - **Bitmap Region Decoder**: للصور العملاقة والخرائط، فك تشفير الجزء المعروض على الشاشة فقط (`BitmapRegionDecoder`).

## Practical walkthrough

كود فك تشفير صورة آمن هندسياً ومحمي من التجمد والـ OOM:
```kotlin
suspend fun decodeSampledBitmapFromUri(
    context: Context,
    uri: Uri,
    reqWidth: Int,
    reqHeight: Int
): Bitmap? = withContext(Dispatchers.IO) { // 1. ضمان التنفيذ في Background Thread تماماً
    // 2. قراءة الأبعاد فقط دون حجز ذاكرة للبكسلات:
    val options = BitmapFactory.Options().apply {
        inJustDecodeBounds = true
    }
    context.contentResolver.openInputStream(uri)?.use {
        BitmapFactory.decodeStream(it, null, options)
    }

    // 3. حساب معامل التصغير المناسب (Power of 2):
    var inSampleSize = 1
    val (height: Int, width: Int) = options.outHeight to options.outWidth
    if (height > reqHeight || width > reqWidth) {
        val halfHeight = height / 2
        val halfWidth = width / 2
        while (halfHeight / inSampleSize >= reqHeight && halfWidth / inSampleSize >= reqWidth) {
            inSampleSize *= 2
        }
    }
    options.inSampleSize = inSampleSize
    options.inJustDecodeBounds = false

    // 4. فك تشفير الصورة بالمقاس المخفض المناسب للشاشة:
    context.contentResolver.openInputStream(uri)?.use {
        BitmapFactory.decodeStream(it, null, options)
    }
}
```

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

App freezes during image decoding are caused by decoding high-resolution images synchronously on the main thread, or triggering severe GC thrashing from multi-megabyte allocations. Diagnosis involves using CPU Profiler's System Trace to locate `BitmapFactory.nativeDecode` and Memory Profiler to inspect heap spikes. Resolution requires decoding on `Dispatchers.IO` using `inSampleSize` downsampling.

## Interview answer — structured

An app freeze localized to image decoding points to two culprits: executing the decode operation synchronously on the main thread, or triggering intense Garbage Collector thrashing due to severe memory pressure.

1. **Diagnosis**: I begin by reproducing the freeze with the **Android Studio CPU Profiler** recording a System Trace. If the Flame Chart reveals `BitmapFactory.nativeDecodeStream()` occupying hundreds of milliseconds on the `main` thread, the root cause is thread misplacement. Concurrently, in the Memory Profiler, I check whether memory spikes into near-OOM territory. If memory is exhausted, ART executes back-to-back compacting GCs, freezing application threads in Stop-The-World pauses.

2. **Resolution**: First, all decoding must be isolated on a background dispatcher (`Dispatchers.IO`). Second, we must avoid full-resolution decodes by implementing two-pass downsampling: using `BitmapFactory.Options.inJustDecodeBounds = true` to query the image's raw dimensions with zero pixel allocation, calculating a power-of-two `inSampleSize` matching the destination ImageView bounds, and decoding only the scaled-down bitmap.

## Interview answer — deep senior

Under the hood, `BitmapFactory` utilizes native Skia C++ decoders (`libskia.so`). When dealing with ultra-high-resolution images (such as architectural diagrams or 100-megapixel panoramas), downsampling still degrades quality if users need to zoom in. In those cases, the production standard is using `BitmapRegionDecoder`, which decodes only the visible viewport tile on demand as the user pans and zooms.

Another nuance is color depth: by default, `BitmapFactory` decodes in `ARGB_8888` (4 bytes/pixel). If alpha transparency is unnecessary, decoding using `RGB_565` (2 bytes/pixel) cuts memory consumption by 50% immediately.

In modern enterprise apps, rather than writing custom `BitmapFactory` code, we rely on established libraries like **Coil**, configuring custom `Decoder.Factory` components and enabling `Bitmap.Config.HARDWARE` to offload bitmap storage to GPU graphic buffers.

## How to answer in the interview

- **Why:** Start with pixel footprint and symptom classification.
- **How:** Trace decode, wait, and graphics stages.
- **Trade-off:** Downsampling may reduce zoom fidelity.
- **Failure case:** Main can freeze while waiting for an off-Main decoder.
- **Production solution:** Separate thumbnail and zoom requests and remeasure.

## Deep-dive talking points

Discuss decoded footprint, Main wait versus worker decode, GPU upload, bounded concurrency, target sizing, and zoom quality.

## Follow-up questions

- **Interviewer:** "Why must `inSampleSize` ideally be a power of two?"
  **Answer:** "`BitmapFactory` decoders can optimize decoding by skipping decoder passes when `inSampleSize` is a power of 2 (2, 4, 8), resulting in substantially faster native decoding compared to non-power-of-two ratios."

- **Interviewer:** "What is `BitmapRegionDecoder` and when is it preferred?"
  **Answer:** "`BitmapRegionDecoder` decodes specific rectangular sub-regions of a large image on demand, which is essential for map viewers and deep-zoom image galleries to prevent loading the full multi-hundred-megabyte image into RAM."

## Self-check rubric

Classify the symptom, calculate decoded size, inspect trace and memory, propose a bounded decode path, and verify image quality.

## References and reviewed-on date

- [Load large bitmaps efficiently](https://developer.android.com/topic/performance/graphics/load-bitmap) — downsampling.
- [Bitmaps and memory](https://developer.android.com/topic/performance/memory/guide/bitmaps) — footprint and pixel storage.
- [System tracing](https://developer.android.com/topic/performance/tracing) — thread and frame timeline.

Technically reviewed against primary documentation on 2026-10-13.
