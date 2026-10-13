---
id: "BLD-16"
question: "How do you set up reproducible builds and dependency verification?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "B"
phase: 4
priority: "P1"
order: 390
editorial_status: "reviewed"
---

# BLD-16

## Original interview question

How do you set up reproducible builds and dependency verification?

## What the interviewer evaluates

- Pin toolchain and resolved dependencies, verify artifact integrity.
- Distinguish repeatable inputs from byte-for-byte reproducibility claims.
- Capture release provenance and test with controlled clean builds.

## Explanation in Arabic

ثبّت Gradle wrapper، AGP/Kotlin/JDK/NDK وAndroid SDK inputs قدر الإمكان، وتجنب dynamic/changing versions غير مضبوطة. Gradle dependency locking تثبت النسخ المحلولة بما فيها transitive؛ dependency verification تتحقق من checksums/signatures للملفات القادمة من repositories، وهما وظيفتان مختلفتان. احفظ lock/verification metadata في Git وراجع تغييراتها. اجعل tasks تعلن inputs/outputs ولا تستخدم timestamps عشوائية في artifact؛ سجل commit/variant/toolchain/hash. “نفس inputs تنتج نفس bytes” ادعاء يحتاج تجربتين نظيفتين ومقارنة hashes، ولا يكفي أن build نجحت مرتين.

## Practical walkthrough

Reproducible build تعني نفس source/dependencies/toolchain/config تنتج artifact يمكن تفسيره ومقارنته، مع مراعاة timestamps/signing وغيرها. استخدم Gradle wrapper، pinned plugin/dependency versions، dependency verification، ثابت JDK، وsource-controlled configs. قارن clean build داخل بيئة مماثلة واحفظ digest/provenance؛ cache لا تعني reproducibility. PR خبيث يغير dependency مصدرها يحتاج review وverification.

## Why it matters and how it works

Dynamic resolution can select different dependency versions over time, while compromised or changed artifacts can reuse coordinates. Locking constrains version selection; verification checks artifact identity. Reproducibility also depends on environment, generated timestamps, signing and nondeterministic tasks. Build cache correctness relies on honest inputs and outputs, but cache hits are not proof of independent reproducibility.

## Worked example

Release CI uses a pinned wrapper/JDK/AGP/NDK and committed dependency lock/verification metadata. Two clean isolated runners build the same unsigned AAB inputs and compare hashes; a mismatch leads to inspection of generated timestamp or archive ordering. Signing is then applied in a protected job and its artifact hash recorded separately.

## Trade-offs and decision criteria

Lock/verification updates add review effort but reduce surprise and supply-chain risk. Fully byte-identical Android outputs may require careful control of tool-generated metadata and signing, so report the exact reproducibility level achieved. Remote caches speed work but should not mask nondeterministic tasks during independent verification.

## Failure modes

`1.+` resolves a new transitive version unexpectedly. A lock exists but no checksum verification protects artifact substitution. A codegen task inserts current time in output. A build is called reproducible based only on same source commit while JDK/SDK differs. Verification metadata is regenerated blindly without review.

## Production perspective

Review dependency updates as changes, store build provenance/SBOM where appropriate, compare isolated outputs periodically, and investigate cache or hash mismatches. Protect release credentials independently of reproducible unsigned build inputs.

## Interview answer — short

“I pin the toolchain, lock resolved versions, verify dependency artifacts, control task inputs, and compare independent clean output hashes before claiming reproducibility.”

## Interview answer — structured

“Dependency locking answers which versions were resolved; dependency verification answers whether fetched artifacts match trusted metadata. I commit both, pin wrapper/AGP/Kotlin/JDK/SDK inputs, and avoid timestamped or undeclared task output. CI records source revision, variant and artifact hash. To claim byte-for-byte reproducibility, I build independently in controlled clean environments and compare outputs; a cache hit alone is not proof.”

## Interview answer — deep senior

“I define the claim before configuring the pipeline. A repeatable dependency graph requires pinned toolchain versions and resolved libraries; Gradle dependency locking prevents an accidental new transitive version from being chosen. Dependency verification adds integrity checks for the actual JAR, AAR and metadata files, so coordinates alone are not trusted. I commit and review the lock and verification changes instead of regenerating them automatically in every release. Reproducibility also depends on the JDK, Android SDK/NDK, AGP, environment variables, locale, generated timestamps and task input declarations. I isolate signing as a protected step and record hashes of the input and final artifact. Two clean runners with the same controlled inputs must produce the same bytes before I use the phrase ‘byte-for-byte reproducible’; if they do not, I trace archive ordering, timestamps or nondeterministic codegen. A remote build-cache hit is a performance result, not an independent reproduction test. I retain source commit, variant, toolchain, dependency state, mapping and artifact hash to make later security and crash investigations possible.”

## How to answer in the interview

- **Why:** release must be attributable.
- **How:** pin toolchain and verify dependency inputs.
- **Trade-off:** upgrade agility versus reproducibility.
- **Failure case:** dynamic dependency changes bytes silently.
- **Production solution:** record provenance and clean-build check.

## Deep-dive talking points

Discuss locking versus verification, toolchain pinning, nondeterminism, independent hash comparison and provenance.

## Follow-up questions

- Does a lockfile verify artifact integrity? **Answer:** no; dependency verification handles checksums/signatures separately.
- Does a cache hit prove reproducibility? **Answer:** no; independent clean builds are needed for that claim.
- What can cause different bytes with same source? **Answer:** toolchain/environment differences or nondeterministic timestamps/order/codegen.

## Self-check rubric

Name pinned inputs, separate lock and verification, and define a byte-comparison experiment.

## References and reviewed-on date

- [Gradle dependency locking](https://docs.gradle.org/current/userguide/dependency_locking.html) — resolved versions.
- [Gradle dependency verification](https://docs.gradle.org/current/userguide/dependency_verification.html) — artifact integrity.
- [Gradle security practices](https://docs.gradle.org/current/userguide/best_practices_security.html) — reproducibility and supply chain.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. No byte-for-byte Android artifact reproduction is claimed for this repo.
