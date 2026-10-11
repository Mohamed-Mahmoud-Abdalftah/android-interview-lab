---
id: "AND-10"
question: "What are Intent and PendingIntent? Explain explicit versus implicit intents."
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 40
editorial_status: "reviewed"
---

# AND-10

## Original interview question

What are Intent and PendingIntent? Explain explicit versus implicit intents.

## What the interviewer evaluates

- Distinguish a message used now from a token another actor can invoke later.
- Explain component-targeted explicit versus action/data-based implicit resolution.
- Choose safe `PendingIntent` target, mutability, identity, and validation for notifications.

## Explanation in Arabic

`Intent` رسالة تصف action وdata وextras لبدء Activity أو Service أو إرسال broadcast. الـexplicit Intent يحدد component معيّن، غالبًا داخل تطبيقك؛ الـimplicit Intent يحدد المطلوب والنظام يختار app مناسبة من intent filters. `PendingIntent` مختلف: token بتسلمه للنظام أو app تانية عشان تنفّذ Intent لاحقًا بصلاحية التطبيق اللي أنشأه. عشان كده لازم target واضح، بيانات قليلة، و`FLAG_IMMUTABLE` افتراضيًا؛ mutable فقط لو ميزة زي inline reply محتاجة الطرف الآخر يملأ حقول محددة. وصول notification tap لا يساوي authorization؛ افحص session وresource بعد الفتح.

## Why it matters and how it works

Android resolves an explicit Intent to its named component. An implicit Intent describes an action/data type and is matched against exported filters, potentially showing a chooser. A PendingIntent is a system-managed capability that wraps an Intent for later invocation by a holder such as the notification manager. Its identity and update flags affect whether old extras are reused or replaced. Mutability must be explicit for apps targeting Android 12+, and modern target-SDK restrictions make mutable implicit PendingIntents especially unsafe. The receiver still validates every input and current account state.

## Worked example

For a receipt notification, build an explicit Intent to `ReceiptActivity` with an opaque receipt ID and create `PendingIntent.getActivity` with a stable request code plus `FLAG_UPDATE_CURRENT or FLAG_IMMUTABLE`. The Activity does not trust the extra as proof of ownership: it authenticates and fetches the receipt from the backend. For sharing text to another app, use an implicit `ACTION_SEND` Intent and a chooser instead of naming an unknown package. Exact notification/task-stack behavior should be tested against the app's navigation graph and target SDK.

## Trade-offs and decision criteria

Explicit Intents are predictable for internal navigation and services; implicit Intents enable user choice for external capabilities but can have no handler or resolve to an untrusted handler. Immutable PendingIntents limit what a holder can change, but a mutable one may be required for a documented inline-reply flow. `FLAG_UPDATE_CURRENT` can update creator-supplied extras even for an immutable PendingIntent, so carefully choose identity and avoid mixing users or receipt IDs in one token.

## Failure modes

An implicit Intent used for a private Service can resolve unexpectedly or be rejected. A mutable PendingIntent with broad fields can let its holder redirect an operation. Reusing the same request code for multiple notifications can show the wrong receipt if identity is not designed. A notification tap after logout can reveal stale private data if the Activity trusts extras. Test multiple simultaneous notifications, account switching, process recreation, absent handlers, and malicious extras.

## Production perspective

An order app creates a distinct explicit immutable PendingIntent per notification identity, with only an opaque order ID. The destination reconstructs navigation and checks authentication and backend ownership. Its CI inspects target-SDK behavior and tests tap flows after process death. External share flows use a chooser and temporary URI grants rather than placing private file paths in unrestricted extras.

## Interview answer — short

“An Intent requests an action now; an explicit Intent names a component, while an implicit Intent lets Android resolve a capable handler. A PendingIntent is a token allowing another actor to invoke a chosen Intent later with the creator's identity. I prefer explicit immutable PendingIntents and validate data on delivery.”

## Interview answer — structured

“I use explicit Intents for known internal components and implicit Intents for actions like sharing where the user may choose another app. A PendingIntent packages an Intent for later execution by something like a notification. Because the token conveys authority, I choose a narrow target, stable identity, immutable flag by default, and only use mutability when a feature genuinely needs fill-in data. The launched screen still checks session and server authorization; the Intent extra is just input. A PendingIntent delegates a future action under the creating app’s identity, so it is more than a delayed Intent. I use an explicit target and immutable flag by default, choose stable identity/request codes deliberately, and treat extras received after a notification tap as untrusted navigation hints. The screen reloads authorized data.”
## Interview answer — deep senior

“I distinguish resolution from delegated capability. An explicit Intent routes to a named component; an implicit one asks the system to match action/data against filters and may reach an untrusted handler. PendingIntent grants a holder the ability to perform a specific later action as its creator, so I design its component, data, request-code identity, update policy, and mutability deliberately. Immutable is the default; an inline reply may justify a narrowly mutable token. For receipt notifications I pass only an opaque ID, handle multiple concurrent notifications correctly, and re-authenticate and authorize the order after a tap, including after process recreation or account switch. Explicit Intents name the component; implicit Intents ask Android to resolve an action and data type. That is useful for sharing to another app, but it is not appropriate for private privileged service calls. A PendingIntent lets a system component or another holder trigger an action later, often after process death, with the creator’s privileges. I decide whether mutability is genuinely required and constrain the target; otherwise a holder could fill in or redirect fields. Multiple notifications need distinct PendingIntent identity or they may open the wrong receipt. On tap I verify current session and backend ownership of the referenced order instead of trusting old extras.”
## Deep-dive talking points

Explain Intent resolution, exported component boundaries, PendingIntent capability semantics, mutability rules, request-code identity, stale extras, notification back stack, and resource authorization after tap.

## Follow-up questions

- [AND-16](../and-16/): Can an intent filter stop explicit external calls? **Answer:** no; exported components still need input and caller authorization checks.
- [AND-25](../and-25/): How should a notification restore navigation? **Answer:** use a stable destination/ID, reconstruct a valid back stack, then check session and resource access.
- [SEC-18](../sec-18/): When is mutable PendingIntent justified? **Answer:** only when the receiving feature needs controlled fill-in fields, such as inline reply, with a narrow explicit target.

## Self-check rubric

Define Intent and PendingIntent separately; contrast explicit and implicit resolution; choose mutability for a receipt tap; explain one identity collision; and place authorization after delivery.

## References and reviewed-on date

- [Intents and intent filters](https://developer.android.com/guide/components/intents-filters) — resolution and PendingIntent usage.
- [PendingIntent security](https://developer.android.com/privacy-and-security/risks/pending-intent) — mutability and capability risks.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The notification example is illustrative and was not device-tested.
