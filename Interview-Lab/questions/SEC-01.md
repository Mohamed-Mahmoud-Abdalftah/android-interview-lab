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

1. معمارية الـ Application Sandbox على مستوى نواة Linux:
   - كل تطبيق أندرويد يتم تثبيته يُعامل كـ **مستخدم نظام Linux مستقل تماماً** وله معرف مستخدم فريد (Unique Linux UID مثل `u0_a145`).
   - يعمل كل تطبيق داخل عملية مستقلة (Isolated Process) ومساحة ذاكرة خاصة به، ويمتلك مجلداً خاصاً مشفراً للملفات (`/data/data/<package_name>/`) بأذونات حصرية (`rwx------`).
   - لا يستطيع أي تطبيق آخر على الهاتف قراءة ملفات تطبيقك أو التجسس على الذاكرة أو حقن كود، إلا إذا اشترك التطبيقان في نفس شهادة التوقيع (Shared User ID).
   - كل اتصال بين التطبيقات يمر عبر **Binder IPC** الذي يفحص هوية المتصل (`Binder.getCallingUid()`).

2. نظام الصلاحيات (Android Permission Model):
   - **صلاحيات عادية (Normal Permissions)**: تُمنح تلقائياً عند التثبيت (مثل الوصول للإنترنت `android.permission.INTERNET`).
   - **صلاحيات خطرة (Dangerous / Runtime Permissions)**: تتطلب موافقة المستخدم الصريحة أثناء التشغيل (الموقع، الكاميرا، الميكروفون، الإشعارات).
   - **صلاحيات خاصة (Special Permissions)**: تتطلب توجيه المستخدم لصفحة إعدادات النظام (مثل ظهور فوق التطبيقات `SYSTEM_ALERT_WINDOW` أو إدارة الملفات `MANAGE_EXTERNAL_STORAGE`).

3. حدود الـ Sandbox والافتراضات الخاطئة (The Sandbox Boundaries):
   - الـ Sandbox يحمي التطبيق من **التطبيقات الأخرى العادية**، ولكنه **لا يحمي التطبيق إذا كان الجهاز نفسه مخترقاً (Rooted Device)** أو إذا كان نظام التشغيل معدلاً (Compromised OS).
   - مستخدم الـ Root يمتلك UID 0، ويستطيع تجاوز صلاحيات Linux وقراءة مجلد `/data/data/` بالكامل وتفريغ الذاكرة (RAM Dump) واستخراج التوكنز غير المشفرة!

## Practical walkthrough

التحقق من هوية المتصل عبر Binder IPC ومنع الثغرات الأمنية في المكونات المصدرة:
```kotlin
// ❌ ثغرة أمنية: تصدير Service أو ContentProvider بدون فحص UID المتصل:
class VulnerablePaymentService : Service() {
    override fun onBind(intent: Intent): IBinder = object : IPaymentService.Stub() {
        override fun transferMoney(amount: Long, toAccount: String) {
            // أي تطبيق خبيث على الهاتف يستطيع استدعاء هذه الدالة وسرقة الأموال!
            executeTransfer(amount, toAccount)
        }
    }
}

// ✅ تأمين Binder IPC بفحص UID والتحقق من التوقيع الرقمي للمتصل (Signature Permission):
class SecurePaymentService : Service() {
    override fun onBind(intent: Intent): IBinder = object : IPaymentService.Stub() {
        override fun transferMoney(amount: Long, toAccount: String) {
            val callingUid = Binder.getCallingUid()
            val callingPackage = packageManager.getNameForUid(callingUid)
            
            // 1. فحص الصلاحية عبر Signature-level permission:
            if (checkCallingOrSelfPermission("com.example.permission.TRUSTED_PAYMENT") != PackageManager.PERMISSION_GRANTED) {
                throw SecurityException("Unauthorized caller: UID $callingUid ($callingPackage)")
            }
            
            executeTransfer(amount, toAccount)
        }
    }
}
```

## Why it matters and how it works

Android assigns an app identity and enforces file/process isolation through the kernel and framework. A manifest declaration states a requested capability; dangerous permissions also need runtime grant on supported versions. A system service checks the caller identity. Content providers, intents, URI grants, and shared storage create deliberate crossings of that boundary.

## Worked example

A photo upload flow requests only media access needed by its implementation, or uses the system photo picker when appropriate. It checks permission at use time and handles denial or later revocation. A private database stays in internal app storage; an exported provider needs its own authorization. This is a design example, not a tested program.

## Trade-offs and decision criteria

Least privilege reduces blast radius and review burden. Runtime prompts add friction, so prefer scoped platform pickers when possible. Permissions grant access to platform resources; they do not prove a user is allowed to read a server account.

## Failure modes

An app checks permission once during onboarding, then assumes it remains granted forever. Revocation can cause failure later. Recheck before use and handle denial. A mistakenly exported provider can leak data even though the database file itself is sandboxed.

## Production perspective

For a fintech app, keep customer data in app-private storage, request only necessary permissions, audit manifest exports and SDK permissions, and enforce account ownership on every backend request. Test denied and revoked permissions plus malicious intents.

## Interview answer — short

Android's application sandbox enforces process and storage isolation at the Linux kernel level by assigning each app a unique Linux UID and private directory. The permission model gates device capabilities across install-time, runtime, and special tiers. However, the sandbox only protects against peer apps; on rooted devices, root access bypasses UID isolation completely.

## Interview answer — structured

The Android security sandbox is built on multi-user Linux kernel primitives rather than JVM boundaries:

1. **Linux UID Isolation**: During installation, Android assigns each application a unique, non-privileged Linux User ID (e.g. `u0_a145`). The process runs with this UID, and its internal storage directory (`/data/data/<package>/`) is restricted with file permissions `0700`. Other apps running under different UIDs are blocked by the kernel from reading memory, inspecting files, or intercepting threads.

2. **Binder IPC Mediation**: Inter-process communication across components (Activities, Services, Providers) is brokered by the Linux Binder driver. Binder guarantees the cryptographic authenticity of `Binder.getCallingUid()`, allowing services to enforce permission checks before executing sensitive methods.

3. **Permission Hierarchy**: Access to hardware and sensitive user data is gated by permissions: Normal (granted at install), Dangerous/Runtime (biometrics, camera, location required explicit user prompt), and Special App Access (exact alarms, all-files access).

The critical boundary to understand: **The sandbox assumes the underlying kernel and hardware are uncompromised**. On rooted devices or emulators with UID 0 (root), kernel boundaries dissolve: an attacker can dump app RAM, attach debuggers, and read private files directly.

## Interview answer — deep senior

From an OS security architecture perspective, Android adds multiple layers beyond pure UID isolation:

1. **SELinux (Security-Enhanced Linux)**: Enforces Mandatory Access Control (MAC) in enforcing mode. Even if an attacker finds an exploit giving them UID 0 inside a sandboxed daemon, SELinux domain policies restrict what files, device nodes, and system calls that domain can access, preventing privilege escalation into the core kernel.

2. **Seccomp Filters**: Restricts available system calls for app processes. Zygote installs a restrictive BPF filter blocking dangerous syscalls (like raw socket creation or kernel module loading) before forking an application process.

Despite these defenses, senior engineers adopt a **Zero Trust Client Model**: never treat client-side validation as authoritative. A modified APK on a rooted device can hook Binder, patch Dalvik bytecode, or alter memory variables. All business authorization, price checks, and security invariants must be verified on the server.

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
  **Answer:** "Historically yes, using `sharedUserId` in the Manifest if signed with the exact same developer certificate; however, Google deprecated `sharedUserId` in API 29 due to security and update risks."

- **Interviewer:** "What is the difference between `checkCallingPermission` and `enforceCallingPermission`?"
  **Answer:** "`checkCallingPermission` returns `PERMISSION_GRANTED` or `PERMISSION_DENIED` as an integer; `enforceCallingPermission` immediately throws a `SecurityException` if the caller lacks the permission."

## Self-check rubric

Can I explain UID isolation, runtime permission denial, a cross-app entry point, least privilege, and why backend authorization remains separate?

## References and reviewed-on date

- [Android app sandbox](https://source.android.com/docs/security/app-sandbox) — UID-based isolation.
- [Android permissions overview](https://developer.android.com/guide/topics/permissions/overview) — declarations and runtime access.

Technically reviewed against primary documentation on 2026-10-13.
