---
id: AND-Q003-ANSWER
question_id: AND-Q003
status: reviewed
---
# AND-Q003 — Complete model answer

**Spoken answer:** “onDestroy is not guaranteed on system process kill, so this is not a reliable persistence hook. I would keep a small restoration key or draft metadata in saved state as appropriate and persist durable draft content through the data layer.”

<p dir="rtl" lang="ar">النظام ممكن يقتل process من غير onDestroy. ViewModel تفيد عبر بعض configuration changes لكنها لا تضمن بقاء البيانات بعد process death. احتفظ بـ saved state صغيرة وdata دائمة في storage مناسبة.</p>

**Mechanics:** The Android process lifecycle documentation explicitly warns that onDestroy may not be called for system kill. Saved UI state is a backup for reconstruction, distinct from durable app data. [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle), [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) and [process guidance](https://developer.android.com/guide/components/activities/process-lifecycle) were checked 2026-10-10.

**Common wrong answer:** “ViewModel survives process death, so no persistence is needed.” A new process creates new in-memory objects.

**Follow-up 1:** Is SavedStateHandle a database replacement? No. It is for small UI restoration state; substantial durable app data belongs in persistent storage.

**Follow-up 2:** How would you verify recovery? Use a platform test that recreates the process or state owner and confirms the draft reloads from the intended durable source.

**Rubric for self-review:** Name the exact owner, trace one plausible transition, distinguish configuration change from process death, and state what must be tested on Android. This is visible practice, not a scored assessment.
