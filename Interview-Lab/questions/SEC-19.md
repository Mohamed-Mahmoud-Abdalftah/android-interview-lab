---
id: "SEC-19"
question: "How do you secure WebView, JavaScript bridges, and file/content URIs?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 316
editorial_status: "reviewed"
---

# SEC-19

## Original interview question

How do you secure WebView, JavaScript bridges, and file/content URIs?

## What the interviewer evaluates

- WebView origin/content controls and JavaScript bridge exposure.
- File/content URI handling and external URL navigation.

## Explanation in Arabic

`WebView` بيشغّل web content جوّه app، ولو سمحت بمحتوى غير موثوق ومعاه `addJavascriptInterface` فأنت بتدي الصفحة منفذ للـnative APIs. قلّل JavaScript والـbridge، اسمح بـorigins محددة، امنع file access غير اللازم، واتعامل مع `content://` grants بحذر. WebView مش trusted UI لمجرد إنه جوّه تطبيقك.

## Why it matters and how it works

JavaScript interfaces can be invoked by frames loaded into the WebView, so origin assumptions must be explicit. WebView settings and navigation callbacks govern JavaScript, mixed content, file access and URL transitions. `WebViewAssetLoader` provides a safer way to serve bundled assets over an HTTPS-like origin.

## Worked example

A receipt screen loads only a controlled merchant origin. External links open in the browser; the app never accepts arbitrary `file://` or unvalidated `content://` input. If a bridge is unavoidable, expose one minimal method that passes an opaque ID to a server-validated operation, not a raw payment approval method.

## Trade-offs and decision criteria

A WebView can speed integration of hosted checkout, but its JS bridge and navigation enlarge attack surface. Native screens avoid some browser risks; hosted checkout may reduce direct card-data handling if the provider’s documented flow is followed.

## Failure modes

Loading a user-supplied URL then exposing a bridge allows injected content to invoke native methods. A permissive file URL setting can expose local resources. Validate origin, restrict settings and test redirects, iframes and compromised content.

## Production perspective

Security tests enumerate loaded domains, redirects, bridge methods and URI grants. A payment success page is treated as presentation; backend state determines completion. Release configs disable WebView debugging where appropriate.

## Interview answer — short

“I treat WebView content as untrusted unless tightly controlled. I restrict origins and file access, minimize JavaScript bridges, validate navigation, and never let a web callback alone authorize a payment.”

## Interview answer — structured

“The risk is crossing from web content into native capabilities. I allow only known HTTPS origins, turn on only needed settings, route external URLs to the browser, and avoid addJavascriptInterface where possible. If a bridge is required, it exposes a narrow method with server-side authorization and no secret output. I review file and content URI access and test redirects and frames. The backend independently confirms checkout status.”

## Interview answer — deep senior

“I map every origin and URI scheme the WebView can load, including redirects, iframes and local assets. A JavaScript bridge can be callable from unexpected frames, so a trusted top-level URL alone is not enough. I remove broad file access, consider WebViewAssetLoader for bundled content, and avoid placing bearer tokens in URLs or injected JavaScript. I test a hostile page and malicious redirect against each bridge method. For fintech, card entry should follow a provider-approved hosted or native SDK flow, and the server settles financial truth after provider confirmation.”

## Deep-dive talking points

Prompt for frame origin, bridge API surface, file/content URI policy, redirects, and authoritative checkout status.

## Follow-up questions

- [SEC-18](../sec-18/): Are incoming content URIs trusted? **Answer:** no; validate and limit grants.
- [PAY-08](../pay-08/): Can a WebView success URL mean approved? **Answer:** no; reconcile with backend.

## Self-check rubric

Can I outline origin allowlisting, bridge minimization, URI restrictions and server confirmation?

## References and reviewed-on date

- [WebView native bridge risks](https://developer.android.com/privacy-and-security/risks/insecure-webview-native-bridges) — interface exposure.
- [WebViewAssetLoader](https://developer.android.com/reference/androidx/webkit/WebViewAssetLoader) — local content loading.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
