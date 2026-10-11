---
id: COR-Q007-ANSWER
question_id: COR-Q007
status: reviewed
---
# COR-Q007 — Complete model answer

**Spoken answer:** “CoroutineExceptionHandler observes uncaught exceptions at an appropriate root boundary; it is not a recovery mechanism for an ordinary child. A child failure is delegated to its parent. I recover with try/catch around the operation whose failure I understand, or use supervision when independent sibling failure is part of the contract.”

<p dir="rtl" lang="ar">الـhandler مش زي try/catch حوالين business operation. لما child يفشل جوه structured scope، الـparent هو اللي يدير الفشل ويلغي الشجرة حسب نوع الـJob. تركيب handler على child ما يغيرش العلاقة دي. حط recovery قريب من call تعرف تصنّف فشلها، أو غيّر topology لـsupervision بعد قرار product واضح.</p>

**Mechanics:** The handler is invoked for uncaught failures when the coroutine has already completed and cannot resume. `async` normally exposes its failure through `await`. Logging in a handler must avoid PII and must not imply the operation recovered.

**Common wrong answer:** “Add a handler and the ViewModel scope cannot be cancelled.” A handler observes; it does not override structured propagation.

**Follow-up 1:** Where can a handler be useful? At a root application-owned scope to report an otherwise uncaught programming failure, with a documented lifetime and privacy-safe metadata.

**Follow-up 2:** Would `SupervisorJob` solve every ViewModel error? No. It isolates direct child failures, but each child still needs explicit error state and cancellation-safe code.

**Rubric for self-review:** Separate observation from recovery and explain child, root, launch, and async behavior.
