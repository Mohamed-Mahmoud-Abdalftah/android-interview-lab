---
id: COR-Q003-ANSWER
question_id: COR-Q003
status: reviewed
---
# COR-Q003 — Complete model answer

**Spoken answer:** “GlobalScope detached the refresh from the screen or ViewModel owner. I would reproduce the navigation and late response, move the launch to a lifecycle-appropriate scope, and test cancellation or result ownership at that boundary.”

<p dir="rtl" lang="ar">الـ refresh مالهاش parent تابع لصاحب الشاشة. لو الشاشة اختفت، الطلب يفضل ممكن يكمل وينشر نتيجة قديمة. اجمع timeline للتنقل والطلب والنتيجة، ثم اربط job بمالك عمر واضح.</p>

**Mechanics:** Structured scopes link children to the parent job. A ViewModel-owned task can use viewModelScope if its lifetime matches the requirement; a screen-visible collector may need a narrower lifecycle. Cancellation is cooperative and a blocking call may need an adapter. [Kotlin coroutine basics](https://kotlinlang.org/docs/coroutines-basics.html) and [Android coroutine guidance](https://developer.android.com/kotlin/coroutines) were checked 2026-10-10.

**Common wrong answer:** “Add a delay before publishing.” Timing does not establish ownership and can make the race harder to reproduce.

**Follow-up 1:** Would viewModelScope always end when a Fragment view is destroyed? No. A ViewModel can outlive a particular view; choose the owner based on the specific UI work and separately guard stale results.

**Follow-up 2:** Does cancellation guarantee the remote request stopped? No. It propagates to cooperating suspending work; the underlying network or blocking API must honor cancellation for actual stop semantics.

**Rubric for self-review:** State the contract accurately, trace the owner and suspension point, identify the failure or cancellation path, and separate JVM proof from Android integration. This is visible practice, not a scored assessment.
