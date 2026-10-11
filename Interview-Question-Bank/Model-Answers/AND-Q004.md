---
id: AND-Q004-ANSWER
question_id: AND-Q004
status: reviewed
---
# AND-Q004 — Complete model answer

**Spoken answer:** “A configuration change commonly recreates an Activity and may retain a ViewModel through the owner mechanism; process death loses memory. Saved state can help reconstruct minimal UI, while durable data comes from storage. ViewSession proves only local detach/rebind behavior.”

<p dir="rtl" lang="ar">تغيير التكوين يعيد إنشاء Activity غالبًا ويمكن ViewModel الاحتفاظ بحالة في الذاكرة. قتل process يمحو الذاكرة؛ saved state تساعد في إعادة بناء UI صغيرة. اختبار JVM لا يشغل النظام.</p>

**Mechanics:** The expected callback and restoration pathways are platform concerns. The fake model tests the ownership decision that a detached renderer must not receive late values and a new renderer can attach. [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle), [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) and [process guidance](https://developer.android.com/guide/components/activities/process-lifecycle) were checked 2026-10-10.

**Common wrong answer:** “A passing JVM test verifies rotation and process recreation.” Neither platform transition ran.

**Follow-up 1:** Could the same Fragment instance survive all navigation paths? No. Back-stack, recreation and removal differ; test the paths the product supports rather than assuming a single instance.

**Follow-up 2:** What should be stored in persistent data instead of saved UI state? Durable notes, user content and records that must survive app restarts belong to a data source with explicit persistence guarantees.

**Rubric for self-review:** Name the exact owner, trace one plausible transition, distinguish configuration change from process death, and state what must be tested on Android. This is visible practice, not a scored assessment.
