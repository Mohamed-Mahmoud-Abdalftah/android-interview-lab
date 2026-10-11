---
id: SYS-Q013-ANSWER
question_id: SYS-Q013
status: reviewed
---
# SYS-Q013 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Keystore protects key material; it does not make arbitrary stored plaintext or server trust unnecessary.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> Keystore تحمي key material وتقلل استخراجها، لكنها لا تجعل client authority ولا تمنع malware أوroot من استخدام session داخل الجهاز المفتوح؛ server تملك expiry وrevocation وauthorization.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">What security guarantee does Android Keystore provide for an auth token, what does it not provide, and how do server revocation and rooted-device risk change your design?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Secure storage:</strong> Keystore تحمي key material وتقلل استخراجها، لكنها لا تجعل client authority ولا تمنع malware أوroot من استخدام session داخل الجهاز المفتوح؛ server تملك expiry وrevocation وauthorization. خزّن أقل credential لازمة، شفّر data بمفتاح Keystore عند الحاجة، استخدم short-lived access token وrotating refresh token، وامسح account partition والwork عند logout أوrevocation.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـSecure storage: خزّن أقل credential لازمة، شفّر data بمفتاح Keystore عند الحاجة، استخدم short-lived access token وrotating refresh token، وامسح account partition والwork عند logout أوrevocation.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A token protected by Android Keystore can be trusted as final authorization without server validation.”

<p dir="rtl" lang="ar">في <strong>Secure storage</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: Keystore تحمي key material وتقلل استخراجها، لكنها لا تجعل client authority ولا تمنع malware أوroot من استخدام session داخل الجهاز المفتوح؛ server تملك expiry وrevocation وauthorization. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Secure storage: token قصيرة العمر in-memory تقلل persistence risk لو product تقبل login متكرر؛ hardware-backed key مفيدة حسب threat model وليست ضمانًا مطلقًا.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Secure storage: اختبر invalidated key، device credential change، logout، revoked refresh token، backup/restore، وaccount switch؛ تأكد إن cache القديمة لا تفتح لمستخدم جديد.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Secure storage، الـshortcut هي: <bdi dir="ltr">A token protected by Android Keystore can be trusted as final authorization without server validation.</bdi> ودي تكسر: Keystore تحمي key material وتقلل استخراجها، لكنها لا تجعل client authority ولا تمنع malware أوroot من استخدام session داخل الجهاز المفتوح؛ server تملك expiry وrevocation وauthorization.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Secure storage: اختبر invalidated key، device credential change، logout، revoked refresh token، backup/restore، وaccount switch؛ تأكد إن cache القديمة لا تفتح لمستخدم جديد.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Secure storage: token قصيرة العمر in-memory تقلل persistence risk لو product تقبل login متكرر؛ hardware-backed key مفيدة حسب threat model وليست ضمانًا مطلقًا.</span>

## English model answer

“Keystore protects key material; it does not make arbitrary stored plaintext or server trust unnecessary. I would define identities and state transitions across client and server, design for duplicate and out-of-order delivery, and prove recovery with observable end-to-end evidence. I would test duplicate, delayed, missing, and out-of-order events and observe recovery across both client and server.”
