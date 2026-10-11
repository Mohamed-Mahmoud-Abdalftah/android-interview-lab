<!-- Copy the YAML block below to the top of a new lesson, without the fences. -->

```yaml
---
id: SAMPLE-ARABIC-LESSON
title: Replace with the lesson title
module: Replace with the module directory
tier: Core
estimated_minutes: 55
prerequisite_ids: []
learning_outcomes:
  - Replace with one observable outcome
status: draft
code_verification: not_run
last_source_checked: 2026-10-10
source_urls: []
example_paths: []
question_ids: []
---
```

# SAMPLE-ARABIC-LESSON — Replace with the lesson title

<!-- Replace sample content and metadata when copying. Keep each Arabic block self-contained. -->

<h2 dir="rtl" lang="ar" id="mental-model">الفكرة الأساسية</h2>

<p dir="rtl" lang="ar">لما تستخدم <code dir="ltr">StateFlow</code> مع <code dir="ltr">ViewModel</code>، لازم تفهم إزاي الـ <span dir="ltr">Coroutine</span> بتتعامل مع الـ <code dir="ltr">Lifecycle</code>.</p>

<h2 dir="rtl" lang="ar" id="trace">تتبّع السلوك</h2>

<ol dir="rtl" lang="ar">
<li>حدّد قيمة <code dir="ltr">StateFlow</code> قبل التغيير.</li>
<li>اتبع الفرع اللي بيشغّله <code dir="ltr">ViewModel</code>.</li>
</ol>

```kotlin
val current: String? = null
val label = current ?: "Guest"
```

<table dir="rtl" lang="ar">
<thead><tr><th>الخطوة</th><th>القيمة</th><th>السبب</th></tr></thead>
<tbody><tr><td>القراءة</td><td dir="ltr"><code dir="ltr">null</code></td><td>القيمة ممكن تغيب.</td></tr></tbody>
</table>

<p dir="rtl" lang="ar">راجع <a dir="ltr" href="https://kotlinlang.org/docs/null-safety.html">Kotlin null safety</a>، وافتح المسار <code dir="ltr">src/main/kotlin</code> في المشروع.</p>

## English interview answer

Describe the boundary, the failure mode, and the test in clear English.
