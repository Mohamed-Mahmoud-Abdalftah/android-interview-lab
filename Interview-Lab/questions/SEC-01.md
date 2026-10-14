---
id: "SEC-01"
question: "What is the Android application sandbox and permission model?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 298
editorial_status: "reviewed"
---

# SEC-01

## Original interview question

What is the Android application sandbox and permission model?

## What the interviewer evaluates

- Linux UID isolation, app-private files, Binder identity, and permission gates.
- The limits of permissions when the user, device, or another exported surface is hostile.

## Explanation in Arabic

ما هو نموذج العزل الأمني (Application Sandbox) ونظام الصلاحيات (Permission Model) في Android، وما هي حدوده الحقيقية؟

يعتمد أمان أندرويد على العزل المتعدد للمستخدمين في نواة Linux، حيث يُمنح كل تطبيق `UID` مستقلاً ومساحة تخزين معزولة بحماية `DAC` و `SELinux`، وتمر طلبات المكونات عبر `Binder` للتحقق من هوية المتصل وصلاحياته دون الاعتماد على مدخلات العميل.

1. معمارية الـ Application Sandbox على مستوى نواة Linux:
   - كل تطبيق أندرويد يتم تثبيته يُعامل كـ **مستخدم نظام Linux مستقل تماماً** وله معرف مستخدم فريد (Unique Linux UID مثل `u0_a145`).
   - يعمل كل تطبيق داخل عملية مستقلة (Isolated Process) ومساحة ذاكرة خاصة به، ويمتلك مجلداً خاصاً للملفات (`/data/user/0/<package_name>/` المربوط رمزياً كـ `/data/data/<package_name>/`) محمي بأذونات `DAC` حصرية (`0700` أو `rwx------` مخصصة للـ UID فقط) ومقيد بسياسات `SELinux` الإلزامية (Mandatory Access Control).
   - تشفير البيانات على القرص يتم عبر File-Based Encryption (FBE)، مع الفصل بين التخزين المشفر ببيانات الاعتماد (Credential Encrypted - CE) المتاح بعد فك قفل الشاشة، والتخزين المشفر بمفتاح الجهاز (Device Encrypted - DE) المتاح أثناء Direct Boot قبل إدخال القفل.

2. شهادات توقيع الـ APK ومفهوم الـ Shared UID:
   - **شهادة توقيع الـ APK (APK Signing)**: توقيع التطبيق (عبر APK Signature Schemes v2/v3/v4) وظيفته الأساسية إثبات أصالة المطور وضمان عدم التلاعب بالكود (Integrity & Authenticity) وحماية مسار التحديثات. **مشاركة نفس شهادة التوقيع بين تطبيقين لا تدمجهما تلقائياً ولا تمنح أحدهما حق الوصول لملفات الآخر**.
   - **خاصية `android:sharedUserId`**: كانت ميزة قديمة في Android Manifest تسمح لتطبيقين موقعين بنفس الشهادة بمشاركة نفس الـ Linux UID ومساحة التخزين، ولكنها **أُهملت رسمياً (Deprecated in API 29)** لما تسببه من ثغرات أمنية وتوسيع لمساحة الهجوم واستحالة إزالتها بعد النشر دون فقدان بيانات المستخدم.
   - **التكامل الآمن بين تطبيقات نفس المطور**: الأسلوب المعماري السليم هو استخدام **Signature-level Permissions** (`android:protectionLevel="signature"`). النظام يمنح هذه الصلاحية فقط للتطبيقات الموقعة بنفس شهادة المطور، مع بقاء كل تطبيق داخل UID وعملية ومساحة تخزين منفصلة تماماً.

3. أمان مشغل الـ Binder IPC وفحص الصلاحيات:
   - كل اتصال بين العمليات يمر عبر مشغل النواة **Binder Driver** (`/dev/binder`). النواة هي المسؤولة عن إرفاق هوية المتصل الحقيقية (`callingUid` و `callingPid`) بحزمة الـ IPC transaction، مما يجعل انتحال الهوية مستحيلاً على مستوى مساحة المستخدم (Kernel-enforced identity).
   - عند تأمين مكون مصدر (Exported Component)، يتم فحص الصلاحيات عبر `checkCallingPermission()` أو `enforceCallingPermission()`. **احذر استخدام `checkCallingOrSelfPermission()` في الخدمات المصدرة**، لأنها إذا كانت الخدمة نفسها تملك الصلاحية، فسترجع `PERMISSION_GRANTED` حتى لو كان المتصل الخارجي لا يملكها!
   - إذا احتاجت الخدمة لتنفيذ عملية خاصة بهويتها الداخلية بعد استلام الطلب، يتم استخدام `Binder.clearCallingIdentity()` ثم استعادتها بـ `Binder.restoreCallingIdentity(token)` داخل كتلة `finally`.

4. حدود الـ Sandbox والافتراضات الخاطئة (The Sandbox Boundaries):
   - الـ Sandbox يحمي التطبيق من **التطبيقات الأخرى العادية**، ولكنه **لا يحمي التطبيق إذا كان الجهاز نفسه مخترقاً (Rooted Device)** أو إذا كان نظام التشغيل معدلاً (Compromised OS).
   - مستخدم الـ Root يمتلك UID 0، ويستطيع تجاوز صلاحيات Linux DAC وقراءة مجلد `/data/data/` بالكامل وتفريغ الذاكرة (RAM Dump) واستخراج المفاتيح غير المؤمنة بالعتاد (Hardware-backed Keystore).

## Practical walkthrough

تأمين مكون مصدر (Exported Binder Service) بفحص هوية وصلاحية المتصل والتعامل السليم مع هوية التنفيذ:
```kotlin
// ❌ ثغرة أمنية: تصدير Service أو استخدام checkCallingOrSelfPermission بشكل خاطئ:
class VulnerablePaymentService : Service() {
    override fun onBind(intent: Intent): IBinder = object : IPaymentService.Stub() {
        override fun transferMoney(amount: Long, toAccount: String) {
            // ثغرة: لو الخدمة نفسها معلنة عن الصلاحية في Manifest،
            // دالة checkCallingOrSelfPermission هترجع GRANTED حتى لو المتصل غير مخول!
            if (checkCallingOrSelfPermission("com.example.permission.TRUSTED_PAYMENT") != PackageManager.PERMISSION_GRANTED) {
                throw SecurityException("Unauthorized caller")
            }
            executeTransfer(amount, toAccount)
        }
    }
}

// ✅ تأمين Binder IPC بفحص Calling Permission الصريح وإدارة هوية التنفيذ:
class SecurePaymentService : Service() {
    override fun onBind(intent: Intent): IBinder = object : IPaymentService.Stub() {
        override fun transferMoney(amount: Long, toAccount: String) {
            val callingUid = Binder.getCallingUid()
            val callingPid = Binder.getCallingPid()

            // 1. التحقق الصريح من صلاحية المتصل (وليس صلاحية الخدمة نفسها):
            if (checkCallingPermission("com.example.permission.TRUSTED_PAYMENT") != PackageManager.PERMISSION_GRANTED) {
                val callingPackage = packageManager.getNameForUid(callingUid)
                throw SecurityException("Unauthorized caller UID $callingUid ($callingPackage, PID $callingPid)")
            }

            // 2. إذا احتاجت الخدمة الوصول لبيانات داخلية تحت هويتها هي، نفصل هوية المتصل مؤقتاً:
            val token = Binder.clearCallingIdentity()
            try {
                executeInternalTransfer(amount, toAccount)
            } finally {
                Binder.restoreCallingIdentity(token)
            }
        }
    }
}
```

## Why it matters and how it works

Android assigns an app identity and enforces file and process isolation through the Linux kernel and framework. A manifest declaration states a requested capability; dangerous permissions also require runtime approval on supported versions. A system service verifies the caller identity. Content providers, intents, URI grants, and shared storage create deliberate crossings of that boundary.

## Worked example

A photo upload flow requests only media access needed by its implementation, or uses the system photo picker when appropriate. It checks permission at use time and handles denial or later revocation. A private database stays in internal app storage; an exported provider needs its own authorization. This is a design example, not a tested program.

## Trade-offs and decision criteria

Least privilege reduces blast radius and review burden. Runtime prompts add friction, so prefer scoped platform pickers when possible. Permissions grant access to platform resources; they do not prove a user is allowed to read a server account.

## Failure modes

An app checks permission once during onboarding, then assumes it remains granted forever. Revocation can cause failure later. Recheck before use and handle denial. A mistakenly exported provider can leak data even though the database file itself is sandboxed.

## Production perspective

For a fintech app, keep customer data in app-private storage, request only necessary permissions, audit manifest exports and SDK permissions, and enforce account ownership on every backend request. Test denied and revoked permissions plus malicious intents.

## Interview answer — short

Android's application sandbox enforces process and storage isolation at the Linux kernel level by assigning each app a unique Linux UID and restricted private directory protected by DAC and SELinux. The permission model gates access to system capabilities across install-time, runtime, and special tiers. Kernel-brokered Binder IPC enforces identity across boundaries, while server-side authorization remains mandatory under a Zero Trust client model.

## Interview answer — structured

The Android security sandbox is built on multi-user Linux kernel primitives rather than JVM boundaries.

First, with Linux UID Isolation, during installation, Android assigns each application a unique, non-privileged Linux User ID (e.g. `u0_a145`). The process runs under this UID, and its internal storage directory (`/data/user/0/<package>/`) is restricted with DAC file permissions `0700` and SELinux MAC policy. Apps cannot read each other's memory or files directly. Next, with Kernel-Brokered Binder IPC, inter-process communication across components is mediated by the Linux Binder driver (`/dev/binder`). The kernel attaches the caller's verified `callingUid` and `callingPid` to every transaction. Services enforce access control using `checkCallingPermission()` or `enforceCallingPermission()`. Using `checkCallingOrSelfPermission()` in an exported service is a known security vulnerability because it falls back to granting access if the service itself holds the permission.
Finally, with Permission Hierarchy & Signature Enforcement, capabilities are gated by permissions: Normal (install-time), Runtime (prompted at moment of need), and Special access. For inter-app collaboration under the same developer, signature-level permissions (`protectionLevel="signature"`) allow secure API sharing without merging UIDs; the legacy `android:sharedUserId` mechanism was deprecated in API 29 due to major security risks.

The critical boundary: **The sandbox assumes the underlying kernel and hardware are uncompromised**. On rooted devices with UID 0 (root), kernel boundaries dissolve: an attacker can dump app RAM, attach debuggers, and read private files directly.


## Interview answer — deep senior

From an OS security architecture perspective, Android adds multiple defence layers beyond basic UID isolation.

First, a SELinux (Security-Enhanced Linux) enforces Mandatory Access Control (MAC) in enforcing mode. Even if an attacker finds an exploit giving them UID 0 inside a sandboxed daemon, SELinux domain policies restrict what files, device nodes, and system calls that domain can access, preventing privilege escalation into the core kernel. Next, with Seccomp-BPF Filters, restricts available system calls for app processes. Zygote installs a restrictive BPF filter blocking dangerous syscalls (like raw socket creation or kernel module loading) before forking an application process.
Finally, with Storage Encryption (FBE), Android uses File-Based Encryption with separate cryptographic keys for Credential Encrypted (CE) storage (available only after the user enters their lockscreen credential) and Device Encrypted (DE) storage (available during Direct Boot).

Senior Android architects adopt a **Zero Trust Client Model**: never treat client-side validation as authoritative. A modified APK on a rooted device can hook Binder, patch ART bytecode, or alter memory variables. All business authorization, monetary limits, and security invariants must be verified on the server.


## How to answer in the interview

- **Why:** sandbox boundaries reduce accidental cross-app access.
- **How:** trace UID, permission check, URI grant, and exported component.
- **Trade-off:** a scoped picker reduces access but adds URI handling.
- **Failure case:** an exported provider leaks private rows.
- **Production solution:** audit merged manifest and enforce server ownership on every request.

## Deep-dive talking points

Trace one cross-UID data path through a provider or URI grant; distinguish platform permission checks from account authorization at the backend.

## Follow-up questions

- **Interviewer:** "Can two different apps share the same Linux UID?"
  **Answer:** "Historically yes, using `sharedUserId` in the Manifest if signed with the exact same certificate; however, Google deprecated `sharedUserId` in API 29 due to severe security and update risks. Modern Android applications should use custom permissions with `protectionLevel=\"signature\"` to share services while keeping distinct UIDs and isolated storage."

- **Interviewer:** "Why is `checkCallingOrSelfPermission` dangerous when securing an exported Service?"
  **Answer:** "`checkCallingOrSelfPermission` checks the caller's permission during an IPC, but if the caller doesn't have it, it falls back to checking whether the hosting service process has the permission. If your app declared that permission in its own manifest, the call will succeed even if an unauthorized third-party caller invoked it. Exported services must use `checkCallingPermission` or `enforceCallingPermission`."

## Self-check rubric

Can I explain UID isolation, runtime permission denial, a cross-app entry point, least privilege, and why backend authorization remains separate?

## References and reviewed-on date

- [Android app sandbox](https://source.android.com/docs/security/app-sandbox) — UID-based isolation.
- [Android permissions overview](https://developer.android.com/guide/topics/permissions/overview) — declarations and runtime access.

Technically reviewed against primary documentation on 2026-10-14.
