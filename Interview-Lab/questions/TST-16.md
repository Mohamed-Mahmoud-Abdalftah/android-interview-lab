---
id: "TST-16"
question: "What should be unit-tested versus verified with an emulator/device?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 411
editorial_status: "reviewed"
---

# TST-16

## Original interview question

What should be unit-tested versus verified with an emulator/device?

## What the interviewer evaluates

- JVM versus platform fidelity boundary.
- Emulator/device matrix driven by OS and hardware risks.

## Explanation in Arabic

Pure Kotlin business rules، formatting وretry policy ممكن unit-test على JVM بسرعة. Android framework behavior مثل runtime permissions، Room migration على SQLite/device، lifecycle/process death، UI semantics وhardware SDK لازم emulator أو جهاز حقيقي حسب الحالة. Emulator ممتاز للـAPI matrix، لكن NFC/EMV/biometric/hardware quirks تحتاج أجهزة فعلية.

## Why it matters and how it works

JVM tests execute without Android runtime and cannot prove manifest, Binder, file backup or device UI behavior. Instrumentation executes on Android. Some local Robolectric-style tests approximate framework behavior but are not a substitute for hardware or OS-specific validation.

## Worked example

Test a payment amount rounding function on JVM; test Room migration on emulator; test POS reader disconnect on actual terminal hardware with provider sandbox. A fake terminal callback test covers app state logic but not firmware timing.

## Trade-offs and decision criteria

Device tests cost time and infrastructure; prioritize platform-sensitive risks. JVM-only coverage is fast but can provide false assurance about security, process death and SDK behavior.

## Failure modes

A mocked permission manager test passes while the manifest lacks a permission. A simulated NFC SDK test passes while one ABI cannot load its `.so`. Use release-like device smoke tests for those boundaries.

## Production perspective

Build a supported API/device/ABI matrix. Run fast JVM PR checks, targeted emulator suites, and hardware release gates for payment-critical flows. Record which claims were device-verified.

## Interview answer — short

“JVM tests cover deterministic Kotlin logic. Emulator/device tests cover Android framework behavior, and real hardware is needed for vendor SDK and physical peripheral risks.”

## Interview answer — structured

“I choose environment based on what could fail. A use case or algorithm runs in JVM tests; permissions, lifecycle, Room migration and Compose UI need Android execution. Emulators cover API levels and screen sizes efficiently, while a POS SDK and reader disconnect require actual terminal hardware. I do not call a fake SDK test proof that certified hardware behaves correctly. Instrumentation executes on Android.”

## Interview answer — deep senior

“I maintain a risk matrix with OS version, API, ABI, device class and vendor firmware. Critical business invariants get abundant fast JVM tests, but platform contracts get instrumentation and hardware-specific bugs get real-device drills. Release-like packaging matters: minification and split APKs can expose issues absent in debug. If a test uses a simulator, I state exactly what it proves and keep an authoritative integration or operational verification for the financial boundary. Build a supported API/device/ABI matrix. Record which claims were device-verified.”

## Deep-dive talking points

Prompt for JVM boundary, emulator API matrix, real hardware, release variant and claim scope.

## Follow-up questions

- [TST-11](../tst-11/): Why real Room? **Answer:** SQL and migration semantics depend on Android/SQLite.
- [TST-17](../tst-17/): What needs a device benchmark? **Answer:** frame/startup performance in realistic runtime.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android test fundamentals](https://developer.android.com/training/testing/fundamentals) — local versus instrumented tests.
- [Android device testing](https://developer.android.com/training/testing) — test environment guidance.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
