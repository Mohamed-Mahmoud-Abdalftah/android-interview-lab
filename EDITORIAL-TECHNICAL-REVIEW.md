# Editorial technical review checklist

Use this checklist before changing an authored item from `draft` to `reviewed`. `scripts/validate.py` checks structure and cross references; it cannot establish that an Android or Kotlin explanation is true, useful, or appropriately sourced. Record the reviewer, date, pinned tool versions, findings, and corrections in the lesson's review notes or the batch changelog.

## Technical claims

- [ ] Trace every runnable snippet and stated output against the pinned Kotlin/JDK/Gradle or Android toolchain. Mark pseudocode and intentionally unsafe examples explicitly.
- [ ] Check compiler behavior and version-sensitive claims, including platform types, smart-cast stability, data-class generated members, equality contracts, lifecycle/process behavior, and API availability.
- [ ] Check where null, blank input, exceptions, cancellation, process death, and concurrent updates cross boundaries. Ensure the proposed recovery matches the product contract.
- [ ] Separate observed local behavior from inference, hypothetical incidents, Android-device behavior, benchmarks, and production claims.
- [ ] Confirm complexity, memory, security, accessibility, and rollout claims have a stated scope and do not overgeneralize from the lab.

## Sources and learning value

- [ ] Use topic-specific primary documentation for each substantive claim. Verify the exact page, relevant section, date, and version; keep unresearched references `pending_verification`.
- [ ] Confirm conceptual prerequisites are genuinely needed, independent of `sequence_previous` study order. Look for missing concepts and unnecessary chains.
- [ ] Read the Egyptian Arabic explanation, code trace, wrong-versus-correct comparison, debugging scenario, and spoken English answer as a learner. Remove repetition and fill genuine learning gaps.
- [ ] Ensure every question asks something testable, each answer addresses that question, and follow-ups have complete reasoning rather than short yes/no claims.
- [ ] Review scenario hypotheses and evidence for alternative causes; do not present a simulated incident as observed production fact.

## Verification handoff

- [ ] Run the current tests and document exact command, date, counts, skips, failures, and environment limitations in `BUILD-VERIFICATION.md`.
- [ ] Check that linked source and test files implement the behavior described in the prose, including realistic edge cases.
- [ ] Run `python3 scripts/validate.py` after updating manifest, question registries, coverage matrix, and file inventory.
- [ ] Update `status` and `source_status` only after this review; leave incomplete future entries planned and without placeholder files.
