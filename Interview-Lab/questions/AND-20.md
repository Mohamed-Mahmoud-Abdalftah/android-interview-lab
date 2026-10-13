---
id: "AND-20"
question: "How do you share data or communicate across processes (Binder/IPC)?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 50
editorial_status: "reviewed"
---

# AND-20

## Original interview question

How do you share data or communicate across processes (Binder/IPC)?

## What the interviewer evaluates

- Explain separate address spaces and Binder as Android's IPC transport.
- Choose a ContentProvider, Intent/result, Messenger, or AIDL according to data and call pattern.
- Handle serialization, permissions, caller identity, binder death, and blocking calls.

## Explanation in Arabic

كل process له memory مستقلة؛ `singleton` أو object reference مش طريقة تشارك بها بيانات بين تطبيقين أو عمليتين. Android يستخدم Binder لنقل transaction بين العمليات، والبيانات بتتعمل لها marshaling بدل مشاركة pointer. مشاركة records أو files غالبًا تكون عبر `ContentProvider` و`content://` URI مع permissions دقيقة. لو محتاج API نداءات متعددة من service لعميل في process تانية، ممكن تستخدم `Messenger` للتسلسل البسيط أو `AIDL` لواجهة typed ومتزامنة/متوازية حسب التصميم. لازم تعتبر العميل غير موثوق، تتحقق من هويته وصلاحياته، وتتوقع موت العملية المقابلة.

## Why it matters and how it works

Binder transports calls across Linux process boundaries. AIDL generates stubs and proxies for a declared interface; arguments are copied/marshaled and calls can cross thread and process boundaries. The local Binder pattern is simpler when a service and client share a process, and does not become cross-process magic just because it implements `IBinder`. IPC calls can block, fail with `RemoteException`, or encounter a dead process. ContentProviders are the standard data-sharing interface for structured content and URI-based grants; an Intent is suitable for coarse one-way launch or result interactions.

## Worked example

A photo editor shares one exported image via a `FileProvider` URI in an `ACTION_SEND` Intent, grants temporary URI read access, and never exposes a raw file path. A separate enterprise companion app needs a remote command service, so it defines a narrow AIDL interface, enforces a signature permission, validates each request, and returns small parcelable values. Both are design examples; the exact declarations, grant flags, and AIDL code need app-specific integration and device tests.

## Practical walkthrough

لو app هتشارك صورة مع app تانية، غالبًا FileProvider + `content://` URI وgrant مؤقت كفاية؛ مش محتاج AIDL. لو companion enterprise app عايزة commands عبر process boundary، AIDL/Binder ينفع مع interface صغيرة وpermission/caller validation لكل request. Binder calls ممكن تفشل لو remote process مات، وممكن تحجز caller thread لو العمل تقيل؛ تعامل مع failure/timeout ونقل البيانات الكبيرة بURI أو file descriptor بدل Parcel ضخمة. اعمل versioning للcontract، ولا تفترض إن نفس الجهاز يعني caller موثوق. اختبر process kill والcaller غير مصرح.

## Trade-offs and decision criteria

A provider fits data queries and URI permissions better than a custom RPC. AIDL supports richer cross-process method calls but adds versioning, concurrency, and failure handling. Messenger serializes messages through a Handler and may suit simple command streams. For in-process code, direct interfaces or local Binder are simpler. Large payloads should use files or streaming interfaces instead of oversized Binder transactions.

## Failure modes

Doing a slow remote call on the main thread can trigger an ANR. Assuming remote state is always alive leaves clients stuck after process death. Trusting caller-supplied IDs without permission checks exposes data. Oversized parcels can fail with `TransactionTooLargeException`. Reusing a mutable object after marshaling does not update the remote copy. Test denial, malicious inputs, remote service kill/rebind, latency, and concurrency.

## Production perspective

Design a versioned contract with explicit error results and bounded inputs. Authorize every exported operation using manifest permissions and runtime checks where appropriate; avoid logging sensitive payloads. Perform potentially blocking IPC away from the UI thread, observe binder death where a long-lived connection matters, reconnect with backoff, and keep durable state in a repository rather than the service process alone.

## Interview answer — short

“Processes have separate memory, so Android uses Binder-backed IPC. I use ContentProvider and URI grants for shared data, and AIDL or Messenger for remote service calls, with explicit security and failure handling.”

## Interview answer — structured

Binder marshals calls between processes; it does not share ordinary object references. For records or files I prefer ContentProvider or a content URI with narrow grants. For an interactive remote service, AIDL defines a typed contract, while Messenger can fit a simpler serialized message flow. IPC adds serialization limits, caller authentication, concurrency, and remote-process failure. I avoid main-thread blocking and keep the contract small and versioned.

## Interview answer — deep senior

I start by confirming a separate process is necessary, because IPC has latency and operational cost. Binder is the underlying transport. AIDL's generated stub/proxy presents methods, but data is marshaled, calls may block, and the remote process can die. If the problem is sharing a file or structured records, I choose a provider and narrow URI grants instead of inventing RPC. For a remote service I define a versioned, minimal interface, enforce caller permissions, validate every argument, and design idempotent retry behavior where possible. I send small values, move expensive calls off Main, handle `RemoteException` and rebinding, and test service death and hostile requests.

I distinguish data sharing from remote commands. A FileProvider URI with a temporary read grant is enough for one shared photo and avoids inventing a broad Binder service. A partner application that must invoke commands may need AIDL with a small versioned interface and explicit permission and input checks. Binder calls can fail when the other process dies and should not perform blocking work on the caller’s Main thread. Large payloads are better shared by URI or descriptor than by an oversized Parcel. I would test the service with an unauthorized caller, process kill, reconnection, and malformed requests.

## How to answer in the interview

- **Why:** Process boundaries need explicit transport and authorization.
- **How:** Contrast URI sharing via provider with a narrow Binder/AIDL command API.
- **Trade-offs:** Avoid IPC complexity for ordinary in-app repositories; keep Parcels small.
- **Failure cases:** Mention remote-process death, main-thread blocking, and exported Binder abuse.
- **Production solution:** Share one image URI or secure a partner command service by caller checks.

## Deep-dive talking points

Discuss separate address spaces, marshaling, Binder limits, `RemoteException`, caller authorization, and service death recovery.

## Follow-up questions

- Does a Kotlin singleton share state across processes? **Answer:** no; each process has its own heap and singleton instance.
- When is AIDL appropriate? **Answer:** for a stable, typed cross-process service interface with multiple operations or concurrent clients.
- Why not send a bitmap in a Binder call? **Answer:** large marshaled payloads increase latency and may exceed transaction limits; use a URI or streaming mechanism.

## Self-check rubric

Explain Binder transport, choose two IPC interfaces, identify a security boundary, and describe remote death and large-payload failure.

## References and reviewed-on date

- [AIDL guide](https://developer.android.com/develop/background-work/services/aidl) — typed cross-process interfaces.
- [Bound services overview](https://developer.android.com/develop/background-work/services/bound-services) — local Binder, Messenger, and AIDL choices.
- [FileProvider](https://developer.android.com/reference/androidx/core/content/FileProvider) — URI-based file sharing.

Technically reviewed against these primary sources on 2026-10-13 by editorial review. The integration examples are illustrative.
