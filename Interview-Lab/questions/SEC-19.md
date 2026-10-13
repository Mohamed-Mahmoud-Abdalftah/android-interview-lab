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

## Practical walkthrough

WebView بتعرض صفحة دعم، ولو فتحت URL خارجي ومعاها JavaScript bridge فيها `getToken()`، أي content محمّل ممكن يناديها. قصر navigation على origins موثوقة، وما تعرضش secrets في bridge، وعطّل file access غير المطلوب. `content://` URI برضه ممكن ترجع ملف كبير أو محتوى غير متوقع؛ اقرأ بحد حجم وتحقق من MIME والـauthority بدل الثقة في الاسم.

## Why it matters and how it works

JavaScript interfaces can be invoked by frames loaded into the WebView, so origin assumptions must be explicit. WebView settings and navigation callbacks govern JavaScript, mixed content, file access and URL transitions. `WebViewAssetLoader` provides a safer way to serve bundled assets over an HTTPS-like origin.

## Worked example

Android example for a controlled, read-only receipt origin. This screen has no JavaScript bridge and no need for file/content access. A feature needing JavaScript must be reviewed separately for origin and message validation.

```kotlin
import android.net.Uri
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient

fun configureReceipt(webView: WebView) {
    webView.settings.javaScriptEnabled = false
    webView.settings.allowFileAccess = false
    webView.settings.allowContentAccess = false
    webView.webViewClient = object : WebViewClient() {
        private fun blocked(uri: Uri): Boolean =
            uri.scheme != "https" || uri.host != "receipts.example.com"

        override fun shouldOverrideUrlLoading(
            view: WebView, request: WebResourceRequest,
        ): Boolean = blocked(request.url)

        @Suppress("DEPRECATION")
        override fun shouldOverrideUrlLoading(view: WebView, url: String): Boolean =
            blocked(Uri.parse(url)) // older Android versions
    }
    webView.loadUrl("https://receipts.example.com/")
}
```

Returning `true` blocks navigation outside the allowed origin; production code also needs a policy for redirects, external links and embedded subresources.

## Trade-offs and decision criteria

A WebView can speed integration of hosted checkout, but its JS bridge and navigation enlarge attack surface. Native screens avoid some browser risks; hosted checkout may reduce direct card-data handling if the provider’s documented flow is followed.

## Failure modes

Loading a user-supplied URL then exposing a bridge allows injected content to invoke native methods. A permissive file URL setting can expose local resources. Validate origin, restrict settings and test redirects, iframes and compromised content.

## Production perspective

Security tests enumerate loaded domains, redirects, bridge methods and URI grants. A payment success page is treated as presentation; backend state determines completion. Release configs disable WebView debugging where appropriate.

## Interview answer — short

“I treat WebView content as untrusted unless tightly controlled. I restrict origins and file access, minimize JavaScript bridges, validate navigation, and never let a web callback alone authorize a payment.”

## Interview answer — structured

“The risk is crossing from web content into native capabilities. I allow only known HTTPS origins, turn on only needed settings, route external URLs to the browser, and avoid addJavascriptInterface where possible. If a bridge is required, it exposes a narrow method with server-side authorization and no secret output. I review file and content URI access and test redirects and frames. The backend independently confirms checkout status. ”

## Interview answer — deep senior

“I map every origin and URI scheme the WebView can load, including redirects, iframes and local assets. A JavaScript bridge can be callable from unexpected frames, so a trusted top-level URL alone is not enough. I remove broad file access, consider WebViewAssetLoader for bundled content, and avoid placing bearer tokens in URLs or injected JavaScript. I test a hostile page and malicious redirect against each bridge method. For fintech, card entry should follow a provider-approved hosted or native SDK flow, and the server settles financial truth after provider confirmation. The origin policy must cover redirects and frames, not only the first URL passed to `loadUrl`. A JavaScript bridge is especially risky because frame-level trust is hard to infer from a top-level address; I prefer no bridge for receipts. I would use an HTTPS asset loader for bundled content when needed and test malicious file and content URIs, oversized uploads, and mixed content on the release WebView configuration. Payment completion comes from the backend state.”

## How to answer in the interview

- **Why:** WebView bridges and URIs cross trust boundaries.
- **How:** allowlist origins, minimize JavaScript exposure, disable unnecessary file access, and validate content reads.
- **Trade-off:** strict loading rules can constrain third-party content.
- **Failure case:** untrusted page invokes a privileged bridge.
- **Production solution:** isolated WebView design and hostile-content tests.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
