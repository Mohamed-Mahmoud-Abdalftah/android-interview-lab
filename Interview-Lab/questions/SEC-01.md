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

## Concept and technical explanation

The Android application sandbox is the foundation of platform security, leveraging Linux kernel multi-user architecture to enforce strict isolation between applications. During installation, the package manager assigns each application a unique Linux User Identifier (UID), typically ranging within app-specific ranges like u0_a123. The Linux kernel enforces discretionary access control (DAC), ensuring that files created under an application's private directory (/data/data/<package_name>) are assigned permissions 0700 or 0750 owned by that specific UID. No other application can read or execute those files unless explicitly shared through ContentProviders or shared UID signing mechanisms. Layered on top of DAC is SEAndroid (Security-Enhanced Android), which enforces Mandatory Access Control (MAC) using SELinux policies. Applications execute within restricted domains (such as untrusted_app), preventing compromised processes from performing unauthorized system calls, accessing raw block devices, or escalating privileges. When applications communicate across process boundaries via Binder IPC, the kernel injects the verified calling UID and PID, allowing framework services and ContentProviders to enforce access rules at runtime.

## Practical walkthrough (English)

Enforcing permission checks at IPC and component boundaries in Android:
```kotlin
// 1. Verifying caller identity at custom Binder service boundaries
class SecurePaymentService : IPaymentService.Stub() {
    override fun processTransaction(amountCents: Long, recipientId: String): Boolean {
        // Enforce signature-level permission for sensitive inter-app IPC
        val callingUid = Binder.getCallingUid()
        val context = applicationContext
        
        context.enforceCallingPermission(
            "com.example.bank.permission.EXECUTE_PAYMENT",
            "Calling UID $callingUid lacks payment permission"
        )
        
        // 2. Validate package identity matches expected trusted signer certificate
        val callerPackages = context.packageManager.getPackagesForUid(callingUid)
        val isTrusted = callerPackages?.any { pkg ->
            context.packageManager.hasSigningCertificate(
                pkg,
                TRUSTED_FINTECH_SIGNATURE_BYTES,
                PackageManager.CERT_INPUT_SHA256
            )
        } ?: false
        
        if (!isTrusted) {
            throw SecurityException("Calling package is not signed by trusted key")
        }
        return executeTransfer(amountCents, recipientId)
    }
}
```

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

Android gives each app a sandbox, normally with its own Linux UID and private storage, and SELinux adds another layer of access control. Permissions govern access to capabilities outside that sandbox; some are granted at install time, some need a runtime decision, and some depend on the app's signing identity. For an exported component I would also check who can call it and validate the input, because a permission request alone does not secure that boundary.

## Interview answer — structured

I think of the sandbox as the default boundary between apps. Android normally runs an app under its own Linux UID, so another ordinary app cannot simply read its private files. SELinux adds restrictions on what app processes may access. That is a useful baseline, but it is not encryption of every app file and it does not make an app safe from its own bugs or a compromised device.

Permissions let an app request access beyond that baseline. Normal permissions are granted without a runtime prompt; dangerous permissions such as location need a user decision, and the user can later revoke them. Signature permissions are useful when two apps signed by the same developer need a protected IPC contract.

In practice I minimize permissions and check the current grant before a protected operation. I also review every exported Activity, Service, Receiver, and Provider. If a component is private, I keep it unexported. If another app must call it, I choose the right permission or caller check, validate incoming data, and test the denial path. The sandbox is the starting point; secure cross-app boundaries still need deliberate design.

## Interview answer — deep senior

The kernel UID and file permissions isolate ordinary app processes. SELinux policy adds mandatory rules that the process cannot opt out of. Those layers limit access, but I would avoid saying they make exploitation impossible. A vulnerable exported component, an overly broad URI grant, code running inside the app, or a compromised operating system can change the threat picture. Private internal storage is access-controlled; application-specific encryption is a separate choice based on the data and threat model.

For an IPC endpoint, I would start with whether it must be exported at all. An explicit intent does not secure an exported component by itself. If the endpoint is shared only with apps we sign, a signature-level permission can be appropriate. If third parties need access, I would define a narrower authorization policy, validate the caller and every supplied URI or extra, and avoid returning more data than the contract requires. On a Binder call, I would use a caller-oriented check, not one that can fall back to the service's own permissions. I would test with a separate app that lacks the permission.

Runtime permissions are also changing state. A grant can be denied, revoked, or limited, and the API call can still fail even after a prior check. So I check close to use and handle the failure. I would use the system Photo Picker when it meets the feature need rather than request broad media access. This is defense in depth: each layer has a specific guarantee, and I would describe those guarantees precisely instead of claiming that SELinux or a permission dialog makes the whole app secure.

## How to answer in the interview

- **Why:** sandbox boundaries reduce accidental cross-app access.
- **How:** trace UID, permission check, URI grant, and exported component.
- **Trade-off:** a scoped picker reduces access but adds URI handling.
- **Failure case:** an exported provider leaks private rows.
- **Production solution:** audit merged manifest and enforce server ownership on every request.

## Deep-dive talking points

Trace one cross-UID data path through a provider or URI grant; distinguish platform permission checks from account authorization at the backend.

## Follow-up questions

- **Interviewer:** "Are files in an app's private directory automatically encrypted by the sandbox?"
  **Answer:** "The sandbox controls which app process can access them; that is different from encryption. Device storage encryption and any app-level encryption have separate guarantees and threat models."

- **Interviewer:** "Does an explicit intent make an exported Service safe?"
  **Answer:** "No. Another app can address an exported component explicitly if it knows its name. I would restrict export or enforce an appropriate permission and validate the caller's input."

- **Interviewer:** "What if location permission is revoked while the app is running?"
  **Answer:** "I treat permission as current state, check near the operation, and handle the API failure or denial path. I would not rely on a grant cached when the screen opened."

## Self-check rubric

Can I explain UID isolation, runtime permission denial, a cross-app entry point, least privilege, and why backend authorization remains separate?

## References and reviewed-on date

- [Android app sandbox](https://source.android.com/docs/security/app-sandbox) — UID-based isolation.
- [Android permissions overview](https://developer.android.com/guide/topics/permissions/overview) — declarations and runtime access.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.
