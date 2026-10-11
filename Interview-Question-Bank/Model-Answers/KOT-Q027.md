---
id: KOT-Q027-ANSWER
question_id: KOT-Q027
status: reviewed
---
# KOT-Q027 — Complete model answer

<p dir="rtl" lang="ar">أثبت الأول إن الفرق مربوط بالـvariant: نفس input، نفس device، debug مقابل release، وstack trace retraced بالـmapping الصحيح. راجع optimization وkeep rules، reflection/serialization، generated code، resource shrinking والـdependencies. افحص APK/DEX الفعلي بدل افتراض شكل output. اعمل minimal reproduction، وبعدها غيّر عامل واحد في كل مرة. لو semantics الأساسية اختلفت فعلًا، محتاج artifact ودليل صغير يثبت ده؛ اسم ART لوحده مش root cause.</p>

**Spoken answer:** “I first reproduce with the same input and device across variants, then retrace the release stack with the matching mapping file. I inspect generated code, reflection and serialization boundaries, shrinker rules and the packaged DEX. I reduce the failure and change one build factor at a time. ART is part of execution, but a release-only failure needs artifact evidence before I claim a runtime semantic change.”

**Common wrong answer:** Disable all optimization permanently and declare the runtime unreliable.

**Follow-up 1:** Why can reflection fail after minification? Names or members used indirectly may be renamed or removed unless the framework and configuration preserve the required contract.

**Follow-up 2:** What belongs in the incident evidence? Variant identifiers, app/version, device/API, mapping checksum, inputs with sensitive data removed, retraced stack, and the minimal rule or code change that reproduces the difference.

**Rubric:** Require controlled reproduction, retracing, artifact inspection, indirect-use boundaries and a minimal causal experiment.
