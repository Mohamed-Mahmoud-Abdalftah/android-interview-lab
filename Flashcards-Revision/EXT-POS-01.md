# EXT-POS-01 revision cards

Use after [EXT-POS-01](../10-Optional-POS-Specialist/ext-pos-01.md).

<ol dir="rtl" lang="ar"><li><strong>NFC تثبت إيه؟</strong> transport قريب المدى؛ لا تثبت authorization.</li><li><strong>ليه Unknown outcome؟</strong> الرد ضاع وقد يكون الأثر حصل.</li><li><strong>هل نعمل retry تلقائي للدفع؟</strong> فقط بعقد idempotency/reconciliation واضح، مش network retry عام.</li><li><strong>ليه amount minor units؟</strong> تتجنب أخطاء floating point وتحدد الوحدة.</li><li><strong>هل نخزن card token في UI state؟</strong> لأ؛ قلل البيانات الحساسة واعزل adapter.</li><li><strong>إيه الدليل الناقص بعد unit tests؟</strong> hardware، Android lifecycle، provider sandbox، security، certification وsettlement.</li></ol>
