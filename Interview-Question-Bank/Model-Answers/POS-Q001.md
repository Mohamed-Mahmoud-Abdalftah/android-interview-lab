---
id: POS-Q001-ANSWER
question_id: POS-Q001
status: reviewed
---
# POS-Q001 — Complete model answer

<p dir="rtl" lang="ar">NFC تنقل bytes على مسافة قصيرة. protocol/kernel تفسر الرسائل وترتيبها. authorization جهة مالية تقرر approve أو decline. capture/settlement تحرك وتسوي الأموال بعد القرار حسب النظام. نجاح طبقة لا يثبت نجاح اللي بعدها؛ قراءة tag لا تعني دفع.</p>

**Spoken answer:** “NFC is the transport. The card and terminal protocol interpret the exchange, the issuer or provider authorizes the transaction, and later capture and settlement complete the financial lifecycle.”

**Common wrong answer:** Treating the NFC callback as an approved transaction and updating the receipt immediately.

**Follow-up 1:** Where does the Android UI belong? It presents state and sends actions; it is never the financial source of truth.

**Follow-up 2:** What does HCE change? It routes supported card-emulation protocol traffic to a host service; authorization and scheme requirements still remain.

**Rubric:** Separate all four layers and state that evidence does not automatically cross a boundary.
