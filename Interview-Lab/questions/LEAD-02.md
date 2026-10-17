---
id: "LEAD-02"
question: "How do you review code for correctness, security, readability, and testability?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "A"
phase: 5
priority: "P2"
order: 457
editorial_status: "reviewed"
---

# LEAD-02

## Original interview question

How do you review code for correctness, security, readability, and testability?

## What the interviewer evaluates

- Risk-ranked code review with constructive, verifiable feedback.
- Correctness/security before style and testability.

## Concept and technical explanation

A disciplined code review methodology elevates team engineering standards by automating mechanical checks and focusing human review on architectural invariants, security, and edge cases:
- The Senior Review Philosophy:
  - Automate the Trivial: Formatting, naming conventions, import ordering, and static linting must be enforced automatically in CI via ktlint, Detekt, and Android Lint. Human reviewers should never waste time debating indentation.
  - Review for Depth: Focus cognitive effort on system correctness, security vectors, concurrency hazards, lifecycle boundaries, and testability.
- The 4-Pillar Review Rubric:
  1. Correctness & Concurrency:
     - Are race conditions, deadlocks, or coroutine leaks possible? Is cancellation handled gracefully? Are state mutations atomic? Are edge cases (nulls, empty collections, boundary numbers) tested?
  2. Security & Compliance:
     - Is user input sanitized? Are credentials, tokens, or PII exposed to Logcat or SharedPreferences? Are Intent extras and exported components secured?
  3. Readability & Maintainability:
     - Does the code reveal its intent clearly? Are domain abstractions intuitive? Are public functions self-documenting without misleading comments?
  4. Testability & Modularity:
     - Is the logic decoupled from Android framework lifecycles? Can external dependencies be substituted with deterministic fakes? Are tests asserting behaviors rather than implementation details?
- The Empathetic Review Culture:
  - Frame critiques as collaborative questions ("What happens if the network drops here?" instead of "You forgot timeout handling").
  - Distinguish blocking blockers from non-blocking suggestions using explicit prefixes (e.g., `nit:`, `suggestion:`, `blocking:`).

## Practical walkthrough (English)

Structured Code Review checklist and PR feedback model in Kotlin:
```kotlin
// Example Pull Request under Review: User Profile Updater
class UserProfileViewModel(
    private val repository: UserRepository,
    private val analytics: AnalyticsTracker
) : ViewModel() {

    // CODE REVIEW DEFECT 1 (Correctness): Non-atomic state mutation and missing cancellation
    // CODE REVIEW DEFECT 2 (Security): Logging raw PII (email) into production analytics
    fun updateEmail(newEmail: String) {
        viewModelScope.launch {
            analytics.logEvent("email_change_attempt", mapOf("email" to newEmail)) // SECURITY HAZARD
            val result = repository.updateEmail(newEmail)
            // Lacks error handling or loading state management
        }
    }
}

// Senior Reviewer Constructive Feedback Format:
// [Blocking / Security]: Under GDPR and PCI rules, we cannot log cleartext email addresses.
//   Please mask the email or log an anonymized userId instead: `hashSha256(email)`.
// [Blocking / Correctness]: If the user navigates away or taps twice rapidly, duplicate requests fire.
//   Suggestion: Use an in-flight UI state check or throttle via flatMapLatest.
// [Nit / Readability]: Could we extract the validation regex into a domain value object `EmailAddress`?
```

## Explanation in Arabic

كيف تدير عملية مراجعة الكود (Code Review) بشكل منهجي يغطي الصحة البرمجية (Correctness)، والأمان (Security)، وسهولة القراءة، وقابلية الاختبار؟

1. فلسفة مراجعة الكود للـ Senior Engineer:
   - مراجعة الكود ليست تصيداً للأخطاء الشخصية، بل هي **بوابة جودة هندسية (Quality Gate) وأداة لنشر المعرفة داخل الفريق**.
   - **أتمتة ما يمكن أتمتته**: لا تضيع وقتك البشري في مراجعة المسافات والتنسيق؛ دع Spotless و ktlint و Detekt يرفضون الـ PR آلياً.

2. المحاور الأربعة للمراجعة العميقة:
   - **1. الصحة البرمجية ومنطق العمل (Correctness)**: هل الكود يلبي متطلبات الـ User Story؟ هل تم التعامل مع الحالات الحدية (Empty states, Network timeout, Screen rotation, Process Death)؟ هل هناك تسريبات ذاكرة أو Coroutine leaks؟
   - **2. الأمان والخصوصية (Security)**: هل تم تشفير البيانات الحساسة؟ هل تم منع كشف الـ Tokens في الـ Logs؟ هل يوجد فحص لمدخلات الـ Deep Links؟ هل تم تعيين `android:exported="false"` للمكونات غير العامة؟
   - **3. سهولة القراءة والمعمارية (Readability & Architecture)**: هل الكود يتبع النمط المعتمد (MVI/MVVM)؟ هل التسميات تعبر عن نية الكود (Intent-revealing names)؟ هل تم احترام Single Responsibility Principle؟
   - **4. قابلية الاختبار وجودة الفحص (Testability)**: هل الكود الجديد مغطى بـ Unit Tests حقيقية تفحص منطق العمل وليس مجرد رفع نسبة التغطية (Code Coverage) بسطور وهمية؟

## Practical walkthrough

قائمة مراجعة عملية (Code Review Checklist) ونموذج للتعليقات البناءة:
```markdown
### ❌ نموذج تعليق سيئ وغير بناء:
"This is wrong. Change it to Coroutines and fix your architecture."

### ✅ نموذج تعليق Senior بناء وتعليمي:
"[Blocking - Correctness]: I noticed we're collecting this Flow directly inside `onCreate`:
`viewModel.state.collect { ... }`
On Android, if the app goes to the background, this coroutine continues emitting,
which can trigger UI updates and waste battery or crash if accessing views.
Could we wrap this in `repeatOnLifecycle(Lifecycle.State.STARTED)`?
Here's the official Android guide for reference: [link]"

### مستويات تصنيف الملاحظات (Conventional Comments):
- **[Blocking]**: خطأ منطقي، تسريب ذاكرة، ثغرة أمنية (يمنع الدمج).
- **[Non-blocking / Suggestion]**: تحسين أداء طفيف أو إعادة صياغة بديلة.
- **[Question]**: طلب توضيح حول قرار معين.
- **[Nitpick]**: تفصيلة جمالية غير مؤثرة (لا تمنع الدمج إطلاقاً).
- **[Praise]**: إشادة بحل هندسي ذكي ومكتوب باحترافية.
```

## Why it matters and how it works

Review is a risk filter and a knowledge-sharing process. Check source of truth, lifecycle, concurrency, security boundary, performance and test evidence. Different findings have different severity; blocking comments should identify a real defect or unmet requirement.

## Worked example

On a PR that retries a charge after timeout, ask whether the same operation ID is persisted before send and enforced server-side. Request a lost-response test. A style issue on the same PR can be nonblocking if formatter handles it.

## Trade-offs and decision criteria

Deep reviews take time; risk-based sampling focuses attention. Automated lint handles routine formatting, freeing human review for logic and threat models. Excessive nitpicks can slow delivery and discourage discussion.

## Failure modes

Approving because tests pass misses untested trust boundaries. Blocking on personal naming taste wastes attention. Separate required change from suggestion and cite the concrete failure mode.

## Production perspective

Team review checklist includes release variant, data migration, API contract, telemetry redaction and rollback for risky code. Measure defect escapes and review latency, not comment count.

## Interview answer — short

Review code by automating mechanical formatting via CI and focusing human review on correctness, security, readability, and testability. Verify concurrency safety, lifecycle boundaries, zero PII leakage, and test coverage using deterministic fakes. Communicate empathetically using explicit tags to distinguish blocking architectural defects from non-blocking suggestions.

## Interview answer — structured

A senior code review process balances rigorous technical scrutiny with a collaborative, empathetic engineering culture.
The foundation of effective code review is delegating mechanical checks like linting, code formatting, and syntax validation entirely to automated CI tools like ktlint and Detekt, freeing engineers to focus on substantive architecture.
Human review evaluates four essential dimensions.
Correctness examines concurrency hazards, race conditions, memory leaks, and boundary conditions.
Security verifies that sensitive data like PII and tokens are never logged or insecurely stored and ensures all external inputs and IPC boundaries are validated.
Readability assesses whether the code clearly expresses business intent and avoids unnecessary complexity.
Testability ensures that components are loosely coupled and that unit tests verify behavioral contracts rather than brittle internal implementation details.
Finally, senior reviewers communicate constructively, providing clear rationale and using explicit tags like blocking or nit to distinguish mandatory fixes from educational advice.

## Interview answer — deep senior

From an engineering leadership and continuous delivery perspective, code review is the primary mechanism for knowledge distribution, architectural governance, and collective code ownership.
Ineffective code review cultures suffer from two common anti-patterns: shallow bikeshedding, where reviewers bicker over variable names and curly brace placement, and rubber-stamping, where large pull requests are approved without inspection. Senior leaders eliminate bikeshedding by mandating that any rule capable of being automated must be enforced via pre-commit hooks and CI gates like Detekt and Android Lint.
This elevates the review to architectural forensics. Reviewers inspect concurrency correctness: verifying that Coroutine dispatchers are injected rather than hardcoded, that shared mutable state is guarded by Mutex or atomic primitives, and that cancellation exceptions are never swallowed in catch-all blocks.
In the security domain, reviewers verify zero-trust data handling: validating that PII is masked, that sensitive flags prevent screenshot capture in banking flows via FLAG_SECURE, and that exported Android components enforce custom signature permissions.
For testability, reviewers check that ViewModels interact with domain interfaces, ensuring that test suites utilize fast, deterministic fakes rather than fragile mocks that mirror private methods.
Equally important is the human delivery. High-performing engineering teams adopt conventional comments, labeling feedback as blocking, suggestion, or praise. Reviewers explain the underlying mechanical rationale, transforming every pull request into an uplifting mentorship opportunity that levels up the entire team.

## How to answer in the interview

- **Why:** review prevents escaped behavior and boundary errors.
- **How:** follow contract, security, clarity and test evidence.
- **Trade-off:** review depth versus release speed.
- **Failure case:** style nit hides an unsafe retry.
- **Production solution:** block on demonstrated risk and verify fix.

## Deep-dive talking points

Prompt for severity, trust boundary, targeted test, respectful feedback and rollback.

## Follow-up questions

- **Interviewer:** "Why should formatting and linting checks be completely removed from human code reviews?"
  **Answer:** "Because automated CI linters execute them instantaneously and objectively, freeing human reviewers to focus on architectural correctness and security."

- **Interviewer:** "What is the benefit of using prefixes like `[Blocking]` and `[Nitpick]` in review comments?"
  **Answer:** "It provides unambiguous clarity to the PR author on which comments require resolution before merge versus which are purely optional suggestions."

## Self-check rubric

Review correctness, security boundaries, readability and testability with one concrete PR example; distinguish a blocking invariant from a style preference and propose a verifiable fix.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — design boundaries.
- [Google code review guidance](https://google.github.io/eng-practices/review/reviewer/) — primary review process guidance.

Technically reviewed against primary documentation on 2026-10-13.
