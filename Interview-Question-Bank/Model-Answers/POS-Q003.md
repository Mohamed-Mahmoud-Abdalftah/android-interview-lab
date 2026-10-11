---
id: POS-Q003-ANSWER
question_id: POS-Q003
status: reviewed
---
# POS-Q003 — Complete model answer

<p dir="rtl" lang="ar">Reader mode تخلي الجهاز يقرأ tags/cards أثناء Activity foreground وتحتاج تفعيل/تعطيل مع lifecycle وفحص hardware. HCE تخلي الجهاز endpoint كارت، والنظام يوجه APDUs لـ <code dir="ltr">HostApduService</code> حسب AID. الاتنين يحتاجوا validation وتقليل logs؛ HCE payment تضيف provisioning/keys/scheme ومتطلبات اعتماد.</p>

**Spoken answer:** “Reader mode makes the foreground device a reader. HCE makes the device emulate a card endpoint through an AID-selected service. Their lifecycle, protocol, and security responsibilities differ.”

**Common wrong answer:** Assuming reader mode and HCE are interchangeable ways to receive the same callback.

**Follow-up 1:** What does `onDeactivated` prove in HCE? It proves the NFC link or service selection ended, not that a payment was declined.

**Follow-up 2:** How do you test device variability? Use a supported hardware matrix with lifecycle, screen, lock, removal, and timing cases, then record exact models and versions.

**Rubric:** Cover direction, component/lifecycle, routing, deactivation semantics, and payment requirements.
