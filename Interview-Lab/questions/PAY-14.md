---
id: "PAY-14"
question: "A release-only native dependency fails on some hardware ABIs. What is your investigation and safe rollout plan?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "C"
phase: 5
priority: "P2"
order: 484
editorial_status: "reviewed"
---

# PAY-14

## Original interview question

A release-only native dependency fails on some hardware ABIs. What is your investigation and safe rollout plan?

## What the interviewer evaluates

- ABI packaging, native load versus runtime faults and staged release.
- Safe rollback without interrupting financial state reconciliation.

## Explanation in Arabic

Release-only native SDK failure ممكن يكون missing `.so` لـABI معيّن، R8/JNI name issue، ABI split packaging، أو firmware/hardware incompatibility. نبدأ بـcrash signature وdevice/ABI matrix، نعيد المشكلة على minified release build، نفحص APK/AAB outputs والـvendor compatibility. Rollout تدريجي مع kill switch للعمليات الجديدة، لكن pending payments لازم تكمل reconciliation.

## Practical walkthrough

اعمل matrix لـABI/device/firmware/SDK version من crash reports، وبعدين شغّل نفس minified release variant على الجهاز المصاب. افتح APK splits وشوف `.so` والـtransitive dependencies، وراجع R8/JNI keep rules بس من crash evidence؛ متضيفش blanket keep rules. وقف authorizations الجديدة للجهاز المصاب مع بقاء status/reversal/reconciliation شغالين.

## Why it matters and how it works

Android loads ABI-matched native libraries; packaging filters and App Bundle splits affect delivery. R8 can also break reflected/JNI entry points. A safe investigation compares debug and release artifacts, library dependencies, vendor SDK version and device firmware.

## Worked example

If `UnsatisfiedLinkError` appears only on `arm64-v8a` terminals, inspect the generated APK split for `libvendor.so` and transitive native dependencies, reproduce on affected hardware with the exact release variant, and retrace stacks. Halt new authorization on affected cohort while preserving read/status/reversal recovery.

## Trade-offs and decision criteria

Pinning SDK version or disabling a new feature may restore availability, but payment terminal certification may constrain changes. Global rollback can strand in-flight state if old schema cannot read it; migrations must be compatible.

## Failure modes

Treating all native crashes as R8 issues wastes time. Disabling payment code abruptly while unknown operations remain can lose reconciliation. Separate initiation gate from recovery path and test rollback with real pending rows.

## Production perspective

Canary by ABI/device/firmware, monitor crash-free sessions and unknown-payment backlog, then widen rollout only after hardware smoke tests. Preserve mapping and native symbols for exact builds under restricted access.

## Interview answer — short

“I reproduce on the exact ABI and minified split, inspect the packaged native libraries and JNI entry points, and gate new authorizations for affected devices. I keep status and reversal recovery available during rollback.”

## Interview answer — structured

“I first segment crashes by ABI, model, firmware and app version. I reproduce using the shipped minified APK or split, check native library packaging and dependencies, then inspect JNI/reflection rules and vendor compatibility. A safe rollout gates new authorizations on affected devices while allowing existing unknown transactions and reversals to reconcile. I canary fixes on real hardware and keep schema/SDK rollback compatibility. I inspect the generated ABI split and retraced release stack before changing keep rules.”

## Interview answer — deep senior

“I distinguish load-time `UnsatisfiedLinkError`, JNI symbol mismatch and a runtime native crash, because each has different evidence. I inspect the AAB-generated split for every supported ABI, native dependencies, R8 mapping and symbol files, and reproduce under production signing/minification where possible. The rollout plan preserves financial obligations: a remote gate stops new transactions but never disables status lookup or reversal workers. I test rollback against persisted pending rows and provider state, then canary by hardware cohort and monitor both crash rate and reconciliation backlog before expansion. I would gate new authorizations per affected cohort while keeping already pending status and reversal paths alive. I would group crashes by device model, ABI, firmware, SDK version, app version, and split delivered by the store. Then I reproduce with the exact minified release variant on affected hardware and inspect packaged .so files and their transitive dependencies. If the error is a JNI method lookup, I inspect retraced stacks and add the narrow keep rule the vendor requires; if it is a missing ABI library, keep rules will not fix it. I use staged rollout and a cohort gate for new authorizations, but preserve status lookup and reversal recovery for pending operations. The release is safe only when the affected matrix and crash rate improve without creating stranded payments.”

## How to answer in the interview

- **Why:** debug success does not prove release native packaging works.
- **How:** compare exact split contents, ABI, JNI symbols, and minified build on affected hardware.
- **Trade-off:** a cohort kill switch reduces new risk but cannot abandon pending payments.
- **Failure case:** broad rollback disables recovery or an overbroad keep rule hides the root cause.
- **Production solution:** staged rollout, device matrix, provider escalation, and recovery monitoring.

## Deep-dive talking points

Prompt for error classification, ABI split inspection, exact release variant, cohort canary and recovery-path continuity.

## Follow-up questions

- [SEC-09](../sec-09/): Could R8 cause release-only failure? **Answer:** yes, if dynamic names need keep rules.
- [PAY-12](../pay-12/): Why retain recovery on rollback? **Answer:** in-flight issuer approvals still need reconciliation.

## Self-check rubric

Can I separate load/JNI/runtime faults and preserve recovery while blocking new transactions?

## References and reviewed-on date

- [Android app ABI management](https://developer.android.com/ndk/guides/abis) — native ABI packaging.
- [R8 shrink guide](https://developer.android.com/build/shrink-code) — release optimization behavior.
- [Android JNI keep-rule examples](https://developer.android.com/topic/performance/app-optimization/keep-rule-examples) — narrow rules for native upcalls.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
