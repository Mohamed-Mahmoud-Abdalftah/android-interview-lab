---
id: "CIC-18"
question: "A malicious pull request tries to access signing secrets. How do you prevent leakage?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "C"
phase: 4
priority: "P2"
order: 437
editorial_status: "reviewed"
---

# CIC-18

## Original interview question

A malicious pull request tries to access signing secrets. How do you prevent leakage?

## What the interviewer evaluates

- Malicious PR code in build scripts/tests and privileged workflow contexts.
- Separation of untrusted validation from signing/release.

## Explanation in Arabic

PR خبيث ممكن يضيف Gradle task أو test يقرأ environment secrets ويبعتها لخارج CI. إخفاء secret في logs مش كفاية. شغّل fork/unreviewed PRs في job بدون signing keys أو Play token وبـread-only permissions؛ privileged release job يشتغل فقط من protected branch/artifact بعد review، وما ينفذش PR head code بسياق secrets.

## Why it matters and how it works

CI executes repository code, including build scripts and plugins, so PR jobs are code execution by an untrusted author. `pull_request_target`-style privileged contexts are dangerous if they check out untrusted commits. Artifact promotion must validate provenance rather than trusting attacker-produced files.

## Worked example

An attacker changes `build.gradle.kts` to POST `$PLAY_TOKEN`. In safe CI, PR job has no token and outbound restrictions where feasible. After merge/review, a separate release job retrieves scoped credentials and signs a known commit’s artifact.

## Trade-offs and decision criteria

Isolated workflows add complexity and may delay external contributions, but protect signing authority. Dependency verification and pinned actions reduce supply-chain exposure; they do not replace PR-secret isolation.

## Failure modes

A workflow uses a privileged token and then checks out `github.event.pull_request.head.sha`; malicious Gradle runs with secrets. Remove secret from that context, restrict permissions and rotate any exposed credential.

## Production perspective

Security review covers workflows, actions, Gradle plugins and artifact handoff. Audit release-trigger permissions and credential use, and alert on unexpected Play uploads.

## Interview answer — short

“I treat PR build code as untrusted. It gets no signing or Play secrets; privileged release jobs run only reviewed protected commits and verify artifact provenance.”

## Interview answer — structured

“A malicious PR can alter Gradle scripts or tests to read and exfiltrate CI secrets. Masking in logs does not stop an HTTP POST. I split PR validation from release signing, set read-only permissions for untrusted jobs and never run PR-head code inside a privileged workflow. After protected merge, a separate job uses scoped credentials to sign and publish a traceable artifact. I also pin dependencies/actions and rotate credentials if exposure is suspected. The mechanics matter. CI executes repository code, including build scripts and plugins, so PR jobs are code execution by an untrusted author. `pull_request_target`-style privileged contexts are dangerous if they check out untrusted commits. Artifact promotion must validate provenance rather than trusting attacker-produced files.”

## Interview answer — deep senior

“I threat-model CI as a code execution environment. Fork PRs, dependency updates and workflow edits are untrusted inputs. The release boundary requires branch protection, review, least-privilege tokens, isolated credentials, controlled network/artifact handoff and provenance checks. Even if a PR job uploads an artifact, a privileged job should not blindly publish it; it should verify or rebuild from reviewed source without executing attacker-controlled code with secrets. I test the policy with a benign canary PR and keep a compromise playbook for signing/upload credentials. Consider a concrete case. An attacker changes `build.gradle.kts` to POST `$PLAY_TOKEN`. In safe CI, PR job has no token and outbound restrictions where feasible. After merge/review, a separate release job retrieves scoped credentials and signs a known commit’s artifact. A failure case illustrates the risk. A workflow uses a privileged token and then checks out `github.event.pull_request.head.sha`; malicious Gradle runs with secrets. Remove secret from that context, restrict permissions and rotate any exposed credential. In production, the response is concrete. Security review covers workflows, actions, Gradle plugins and artifact handoff. Audit release-trigger permissions and credential use, and alert on unexpected Play uploads. The decision has a trade-off. Isolated workflows add complexity and may delay external contributions, but protect signing authority. Dependency verification and pinned actions reduce supply-chain exposure; they do not replace PR-secret isolation.”

## Deep-dive talking points

Prompt for build script exfiltration, privileged context danger, artifact provenance and credential rotation.

## Follow-up questions

- [CIC-09](../cic-09/): Why is masking insufficient? **Answer:** malicious code can send secret to network.
- [CIC-08](../cic-08/): What checks run on PR? **Answer:** fast validation without release credentials.

## Self-check rubric

Can you explain the mechanism, apply the example, justify a trade-off, identify a failure mode, and answer both follow-ups?

## References and reviewed-on date

- [Play App Signing](https://developer.android.com/studio/publish/app-signing) — signing roles.
- [Gradle dependency verification](https://docs.gradle.org/current/userguide/dependency_verification.html) — supply-chain integrity.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
