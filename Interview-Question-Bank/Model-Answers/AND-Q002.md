---
id: AND-Q002-ANSWER
question_id: AND-Q002
status: reviewed
---
# AND-Q002 — Complete model answer

**Spoken answer:** “The observer may outlive the view and update or retain a stale binding. For work that renders the view, I observe using viewLifecycleOwner and clear the binding at onDestroyView, then bind the new view separately.”

<p dir="rtl" lang="ar">Fragment ممكن تعيش بعد view. observer مربوطة بـ Fragment تفضل شغالة وتلمس binding انتهت أو تمنع جمعها. اربط UI observer بـ viewLifecycleOwner ونضف المرجع عند onDestroyView.</p>

**Mechanics:** The Fragment view has a separate LifecycleOwner. Official Fragment docs place view lifecycle destruction before onDestroyView and say view references should be removed then. [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle), [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) and [process guidance](https://developer.android.com/guide/components/activities/process-lifecycle) were checked 2026-10-10.

**Common wrong answer:** “The Fragment still exists, so its old view is safe.” Object lifetime and view lifetime differ.

**Follow-up 1:** What if the observer updates only a repository and never touches a view? That work may belong to a longer-lived owner; choose its scope by the resource it owns, not by one blanket rule.

**Follow-up 2:** Would a JVM detach test prove no Android memory leak? No. It proves a pure reference policy; inspect the real Fragment and run Android lifecycle/leak checks.

**Rubric for self-review:** Name the exact owner, trace one plausible transition, distinguish configuration change from process death, and state what must be tested on Android. This is visible practice, not a scored assessment.
