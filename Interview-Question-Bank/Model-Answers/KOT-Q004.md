---
id: KOT-Q004-ANSWER
question_id: KOT-Q004
status: reviewed
---
# KOT-Q004 — Model answer

**Spoken answer:** “For an optional display label, a documented `Guest` fallback is reasonable. For a required identity, I return a typed error and preserve evidence for diagnosis. I normalize at the data-to-domain boundary so downstream UI code does not repeatedly guess, and I test null, blank, valid, and malformed responses.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> لو الاسم مجرد label اختياري، <code dir="ltr">Guest</code> ممكن تبقى مناسبة. لو هوية مطلوبة، الـ fallback هيخفي مشكلة حقيقية؛ ارجع typed error. حط الـ normalization عند حد البيانات والـ domain عشان الـ UI ما تعيدش تخمين نفس القاعدة في كل شاشة.</p>

**Mechanics:** Nullability represents possible absence, not validity. The lab's `ProfileName.parse` trims and rejects blank text; `safeLabelFromLegacy` then chooses a UI fallback. A real repository could return `Result<ProfileName>` or a sealed domain outcome to distinguish missing data from SDK failure. Avoid logging personal names or sensitive SDK payloads. [Runnable example](../../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileName.kt). The choice of repository/domain boundary is an architecture decision; Android's [architecture recommendations](https://developer.android.com/topic/architecture/recommendations) are guidance, not a rigid law (checked 2026-10-10).

**Common wrong answer:** “Use Elvis everywhere and the app is robust.” It may hide broken contracts. **When not to use a typed error:** For a genuinely optional decorative label, extra error state could add complexity without user value.

**Follow-up 1:** What if blank is valid for privacy? **Then the contract must distinguish hidden name from malformed data** (for example an explicit `isHidden` flag); do not infer privacy from whitespace.

**Follow-up 2:** Where is the source of truth? **In the agreed data model/repository contract**, with a single normalization policy; UI can format for presentation but should not redefine identity validity.

**Fair rubric (10):** 3 optional/required split, 2 boundary placement, 3 test cases, 2 privacy/source-of-truth reasoning. Version caveat: no Android API version claim.
