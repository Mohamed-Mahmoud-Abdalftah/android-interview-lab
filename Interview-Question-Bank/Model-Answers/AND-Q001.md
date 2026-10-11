---
id: AND-Q001-ANSWER
question_id: AND-Q001
status: reviewed
---
# AND-Q001 — Complete model answer

**Spoken answer:** “I choose the boundary based on whether the resource is needed while visible or only while actively interacting. onStart/onStop often models visibility, while onResume/onPause can model foreground interaction; multi-window and API behavior matter.”

<p dir="rtl" lang="ar">اختيار callbacks تابع لاحتياج المورد. لو يكفي إن الشاشة ظاهرة، STARTED/STOPPED ممكن يناسب. لو يحتاج التفاعل الفعلي، RESUMED/PAUSED قد يناسب. لازم أختبر السلوك في multi-window.</p>

**Mechanics:** Activity lifecycle callbacks indicate transitions, but their exact use for a camera, animation, location stream or player depends on product behavior and platform API. The official guide warns against treating all resources identically. [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle), [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) and [process guidance](https://developer.android.com/guide/components/activities/process-lifecycle) were checked 2026-10-10.

**Common wrong answer:** “Always release everything in onPause.” That can interrupt valid visible multi-window behavior.

**Follow-up 1:** Could onStop be too late for a camera? Possibly. If another foreground screen needs exclusive access, the device and API contract may require a RESUMED/PAUSED boundary.

**Follow-up 2:** Can I infer the exact callback sequence from one happy-path diagram? No. Navigation, configuration changes and multi-window vary; instrument the real screen and test supported transitions.

**Rubric for self-review:** Name the exact owner, trace one plausible transition, distinguish configuration change from process death, and state what must be tested on Android. This is visible practice, not a scored assessment.
