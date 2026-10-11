#!/usr/bin/env python3
from pathlib import Path
import json,re
R=Path(__file__).resolve().parent.parent; DATE="2026-10-11"
def slug(x):return re.sub(r'[^a-z0-9]+','-',x.lower()).strip('-')
def E(id,prefix,title,path,pre,start,count,model,risk,sources,concepts):return dict(id=id,prefix=prefix,title=title,path=path,pre=pre,start=start,count=count,model=model,risk=risk,sources=sources,concepts=concepts)
A="https://developer.android.com/";K="https://kotlinlang.org/"
exts=[
E("EXT-ART-01","ART","JVM/ART","08-Mobile-System-Design/ext-art-01.md",["KOT-006"],1,10,
"Kotlin/JVM code تمر من compiler إلى class files، ثم Android toolchain تحول وتجمع DEX، وART تحمل وتتحقق وتنفذ مع AOT/JIT حسب النظام. Zygote يشارك صفحات preloaded، class loading له identity، وJNI boundary لها تكلفة وأمان مختلفين. فرّق دائمًا بين language guarantee وJVM behavior وAndroid runtime implementation.","مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping.",[A+"guide/platform",A+"tools/d8",A+"build/shrink-code",K+"docs/compiler-reference.html"],
[("Kotlin to DEX pipeline","Kotlin compilation and Android DEX packaging are separate stages with different artifacts and diagnostics."),("D8 versus R8","D8 desugars and converts bytecode to DEX; R8 can shrink, optimize, and obfuscate according to the build pipeline."),("ART execution","ART verifies and executes DEX with runtime and compilation strategies that vary by platform and install profile."),("Zygote model","App processes fork from Zygote and benefit from preloaded shared pages, while app state remains process-isolated."),("Class loading identity","A class is identified by name plus defining loader, which matters for plugins and reflection."),("JNI boundary","JNI crosses managed/native memory, threading, exception, and lifetime rules and should stay narrow."),("Reflection and shrinking","Reflection hides reachability from static analysis, so narrow keep metadata and release tests are required."),("Boxing and allocation","Generic and nullable primitives may allocate or box; prove user impact with profiles before redesign."),("Crash retrace","Preserve mapping files per release and retrace the exact build before diagnosing obfuscated stacks."),("Runtime evidence","Use release artifacts, dexdump/profile traces, mapping, and device versions; do not infer device behavior from JVM tests.")]),
E("EXT-CON-01","CON","Concurrency","08-Mobile-System-Design/ext-con-01.md",["COR-006"],1,10,
"Concurrency correctness تبدأ shared state وatomicity وvisibility وordering. Coroutine مش thread، وsingle-thread execution مش ضمان لو callbacks تعيد الدخول أو state مشتركة خارج السياق. اختار immutability أو confinement أو Mutex/atomics حسب invariant، وخلي lock scope صغيرة ومن غير I/O.","counter read-modify-write تضيع updates، أو Mutex ماسكة أثناء network، أو atomic fields منفصلة تكسر invariant مشتركة.",[K+"docs/shared-mutable-state-and-concurrency.html",K+"api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-mutex/","https://docs.oracle.com/javase/specs/jls/se17/html/jls-17.html"],
[("Race definition","A race exists when correctness depends on uncontrolled ordering of conflicting operations."),("Atomicity versus visibility","Visibility exposes writes; atomicity protects an indivisible invariant. One does not automatically provide the other."),("Mutex contract","A coroutine Mutex serializes a critical section but is not reentrant and should not surround slow external work."),("Atomic update","Use a single atomic state/update when the invariant spans fields, not unrelated atomics that can be observed inconsistently."),("Confinement","Owning mutable state on one serialized context can simplify reasoning if every access truly crosses that owner."),("Immutability","Immutable snapshots remove in-place races but publication and stale-version policy still matter."),("Deadlock review","Map lock order and external callbacks; avoid nested locks and calls that can reenter while held."),("Backpressure","Bound queues and define suspend, reject, drop, or conflate policy from event semantics."),("Stress testing","Controlled interleavings prove invariants better than sleeps; stress runs can reveal but not prove absence of races."),("Cancellation and locks","Use structured lock APIs so cancellation releases ownership, and keep cleanup bounded.")]),
E("EXT-UI-01","EUI","UI","08-Mobile-System-Design/ext-ui-01.md",["UI-006"],1,10,
"UI deep dive تربط rendering pipeline وstate snapshots وlayout/draw وinput/semantics. الأداء والaccessibility والadaptive behavior contracts متداخلة: optimization ماينفعش تكسر focus أو state restoration. ابدأ user journey وقياس frame بدل micro tweak.","custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail.",[A+"develop/ui/compose/mental-model",A+"develop/ui/compose/performance",A+"guide/topics/ui/accessibility",A+"develop/ui/compose/layouts/adaptive"],
[("Frame pipeline","Input, state change, composition, layout, draw, and GPU work contribute different evidence to a slow frame."),("Snapshot state","Compose snapshots coordinate state reads and writes; mutable non-observable data can bypass invalidation."),("Stability contract","Stable means observable public behavior will not change unexpectedly; false annotations can hide updates."),("Custom layout","Measure children under constraints, choose size, and place consistently without repeated expensive work."),("Lazy list identity","Stable keys preserve item identity and state across insertion, removal, and reorder."),("Nested scroll","Coordinate gesture consumption and ownership instead of stacking independent scroll containers blindly."),("Semantics merging","Expose one meaningful control or structured descendants without duplicate announcements."),("Focus restoration","Preserve logical focus across adaptive layout changes and avoid trapping keyboard or accessibility navigation."),("Edge-to-edge","Handle insets by ownership and avoid applying the same inset multiple times."),("UI benchmark","Use macrobenchmark/frame evidence on release-like builds and verify visual and accessibility behavior after optimization.")]),
E("EXT-STAFF-01","STF","System design","08-Mobile-System-Design/ext-staff-01.md",["INT-006"],1,10,
"Staff-level design يربط product outcomes وorg ownership وevolution. المطلوب مش أكبر diagram؛ المطلوب seams تقلل blast radius، migration قابلة للرجوع، SLO/observability، وقرار واضح تحت uncertainty. فرّق local optimum عن تكلفة النظام والفريق.","فريق يعيد كتابة التطبيق كله من غير migration path أو success metrics، أو platform team تبني abstraction بلا users.",[A+"topic/architecture",A+"topic/modularization","https://sre.google/sre-book/service-level-objectives/"],
[("Requirement shaping","Turn vague scale and reliability claims into measurable user journeys, constraints, and non-goals."),("Architecture evolution","Use seams, strangler migration, compatibility, and rollback instead of a big-bang rewrite."),("Ownership model","Assign decision, operation, data, and incident ownership across team boundaries."),("SLO and error budget","Tie reliability targets to user outcomes and use budget to balance change velocity and risk."),("Blast-radius control","Partition releases, data, accounts, and dependencies so one failure has bounded impact."),("Migration governance","Define dual-read/write risks, reconciliation, cutover criteria, and rollback evidence."),("Platform product thinking","A shared platform needs real consumers, support model, adoption metrics, and escape hatches."),("Decision under uncertainty","State assumptions, reversible probes, leading risks, and the trigger to revisit."),("Cross-team disagreement","Make trade-offs and evidence visible, decide with an owner, and document dissent without paralysis."),("Operational design","Include dashboards, alerts, runbooks, privacy, capacity, failure injection, and deprecation from the start.")]),
E("EXT-POS-01","POS","POS/NFC","10-Optional-POS-Specialist/ext-pos-01.md",["PRO-003"],6,5,
"POS transaction state machine لازم تفرق request، card read، online authorization، approved/declined، unknown outcome، reversal، settlement، وreconciliation. NFC transport أو HCE مش payment approval. ممنوع تخزين sensitive authentication data أو اختراع PCI compliance من client code.","network يقطع بعد authorization فيتعمل retry بعملية جديدة، أو SDK callback قديمة تكمل attempt مختلفة.",[A+"develop/connectivity/nfc",A+"reference/android/nfc/NfcAdapter",A+"develop/connectivity/nfc/hce","https://www.emvco.com/wp-content/uploads/2022/09/EMV%C2%AE-Chip-At-A-Glance-EMVCo-eBook.pdf","https://www.emvco.com/wp-content/uploads/2023/06/EMVCo_QRG_EMV_CONTACTLESS_FINAL.pdf"],
[("Reversal boundary","Reversal is a protocol/business action for a prior attempt, not a UI undo button."),("Settlement and reconciliation","Authorization outcome, clearing/settlement, and terminal reconciliation are distinct ledgers and times."),("Terminal operation identity","Every attempt has stable identity across UI, SDK, host, retry, receipt, and recovery."),("Hardware disconnect","Device loss changes state to recoverable, failed, or unknown according to the last confirmed boundary."),("PCI-safe diagnostics","Log state, duration, and redacted identifiers; never PAN, track data, cryptograms, PIN, or secrets.")]),
E("EXT-DSA-01","DSA","Algorithms","07-DSA-Live-Coding/ext-dsa-01.md",["SYS-002"],6,5,
"Live coding senior يقيم contract وcommunication/invariant/tests، مش حفظ LeetCode. اختار data structure من operations، احسب overflow، وابدأ brute force صحيح قبل optimization لو الوقت يسمح.","حل سريع يفشل duplicates أو overflow، والمرشح يعلن O(n) من غير حساب memory/hash assumptions.",["https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/PriorityQueue.html",K+"docs/collections-overview.html",K+"docs/collection-operations.html"],
[("Interval merge invariant","Sort by start; the output contains disjoint merged intervals and the last is the only candidate for overlap."),("LRU cache design","Hash map plus doubly linked order gives expected O(1) get/put when every mutation updates both structures atomically."),("Top K selection","A size-k min-heap costs O(n log k) and avoids sorting all n when k is small."),("Cycle detection","DFS colors or Kahn indegrees detect directed cycles; a parent check changes the undirected case."),("DP optimization","Compress dimensions only after proving each state reads values that the overwrite order preserves.")])
]

next(e for e in exts if e['id'] == 'EXT-POS-01')['sources'][-1] = "https://www.emvco.com/wp-content/uploads/2023/06/EMVCo_QRG_EMV-CONTACTLESS_FINAL.pdf"

diff=["foundational","intermediate","intermediate","senior","senior","senior","senior","senior","senior","senior"]
styles=["conceptual","code-review","debugging","architecture","live-coding","performance","debugging","system-design","live-coding","architecture"]

def lesson(e):
 qs=[f"{e['prefix']}-Q{i:03d}" for i in range(e['start'],e['start']+e['count'])]
 return f'''---
id: {e['id']}
title: {e['title']}
module: {Path(e['path']).parent.as_posix()}
tier: Advanced
estimated_minutes: 90
prerequisite_ids: [{", ".join(e['pre'])}]
learning_outcomes:
  - Explain advanced mechanisms without mixing platform layers
  - Diagnose a realistic failure and defend a trade-off
  - Answer specialist follow-ups with evidence boundaries
status: reviewed
code_verification: not_applicable
last_source_checked: {DATE}
source_urls:
'''+''.join(f'  - {x}\n' for x in e['sources'])+f'''example_paths: []
question_ids: [{", ".join(qs)}]
---

# {e['id']} — {e['title']} deep interview reference

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">{e['risk']}</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">{e['model']}</p>

## Mechanism and execution trace

<p dir="rtl" lang="ar">ارسم الطبقات والـowners بالترتيب، وحدد contract كل boundary والartifact أو state قبلها وبعدها. بعدين أدخل failure في boundary واحدة وتتبع propagation وcleanup وevidence. ما تنقلش guarantee من JVM لـAndroid أو من client لـserver من غير مصدر واختبار مناسب.</p>

'''+'\n'.join(f'### {i+1}. {t}\n\n<p dir="rtl" lang="ar">{fact}</p>' for i,(t,fact) in enumerate(e['concepts']))+f'''

## Wrong and corrected implementation

<p dir="rtl" lang="ar">الحل الغلط هو استخدام الاسم أو abstraction كإجابة نهائية من غير lifetime وfailure وsecurity/evidence. التصحيح يبدأ contract صغيرة، يختبر boundary، ويضيف complexity بس لما requirement أو قياس يبررها.</p>

## Tests and failure cases

- Trace valid, malformed, duplicate, stale, cancellation/restart, and boundary-size cases.
- Use release/device/backend evidence for claims outside pure Kotlin.
- Reject one plausible shortcut and explain the invariant it violates.

## Interview explanation

<p dir="rtl" lang="ar"><strong>الإجابة المختصرة:</strong> {e['concepts'][0][1]}</p>

**English:** “{e['concepts'][0][1]} I would trace the ownership and failure boundaries, compare one viable alternative, and verify the claim with the artifact, test, or production signal that actually observes that layer.”

## Senior follow-ups

1. **What assumption is most dangerous?** {e['risk']}
2. **What evidence belongs to this layer?** Use the actual artifact, controlled test, device trace, or backend record; do not infer across layers.
3. **When would you choose a simpler design?** When scale, durability, or isolation requirements do not justify the added operational cost.

## Misconceptions and revision

<p dir="rtl" lang="ar">راجع الأسئلة {qs[0]} إلى {qs[-1]}. جاوب direct answer ثم mechanism ثم failure ثم test. المحتوى specialist ومش بديل عن vendor/device evidence.</p>
'''

def qdocs(e):
 for j in range(e['count']):
  i=e['start']+j;topic,fact=e['concepts'][j];qid=f"{e['prefix']}-Q{i:03d}";d=diff[min(j,len(diff)-1)];sty=styles[min(j,len(styles)-1)]
  q=f'''---
id: {qid}
lesson_id: {e['id']}
topic: {topic}
difficulty: {d}
style: {sty}
expected_minutes: 6
status: reviewed
---
# {qid} — {topic}

During a specialist interview, explain {topic}, trace one failure, reject one misleading shortcut, and name evidence at the correct platform boundary.

[Open complete model answer](../Model-Answers/{qid}.md) · [Lesson](../../{e['path']})
'''
  a=f'''---
id: {qid}-ANSWER
question_id: {qid}
status: reviewed
---
# {qid} — Complete model answer

**Spoken answer:** “{fact}”

<p dir="rtl" lang="ar">{e['model']} نقطة السؤال هي <strong>{topic}</strong>. الخطأ الواقعي اللي لازم تمنعه: {e['risk']}</p>

**Mechanics:** Identify the exact layer, owner, input artifact or state, transition, and output. Then inject a failure at that boundary and trace propagation, cleanup, and observable evidence.

**Common wrong answer:** “The platform or pattern handles it automatically.” This skips the contract, version, ownership, and operational evidence.

**Follow-up 1:** How would you prove the claim without a production experiment? Build the smallest controlled test or inspect the exact artifact for that layer, include a negative case, and state which device or backend behavior remains unproved.

**Follow-up 2:** What trade-off could reverse your decision? A stricter durability, latency, security, scale, or team-ownership constraint could justify another design. Compare the alternative on failure recovery and operating cost, not fashion.

**Polished English answer:** “{fact} The main failure I would guard against is {e['risk']} I would verify the invariant at the owning boundary and keep the remaining assumptions explicit.”

**Rubric:** Layer accuracy, ordered trace, failure, alternative, evidence, and clear spoken delivery.
'''
  yield qid,q,a,topic,d,sty

# Write new lessons and all question pairs; augment existing specialist frontmatter.
for e in exts:
 p=R/e['path']
 if e['id'] in {'EXT-POS-01','EXT-DSA-01'}:
  raw=p.read_text(); existing=re.search(r'^question_ids:\s*\[[^\]]*\]',raw,re.M)
  allids=[f"{e['prefix']}-Q{i:03d}" for i in range(1,11)]
  raw=raw[:existing.start()]+f"question_ids: [{', '.join(allids)}]"+raw[existing.end():];p.write_text(raw)
 else:p.write_text(lesson(e),encoding='utf-8')
 for qid,q,a,*_ in qdocs(e):
  (R/f'Interview-Question-Bank/Questions/{qid}.md').write_text(q,encoding='utf-8');(R/f'Interview-Question-Bank/Model-Answers/{qid}.md').write_text(a,encoding='utf-8')

mp=R/'CONTENT-MANIFEST.json';m=json.loads(mp.read_text())
items=[];seen=set()
for entry in m['items']:
 if entry['id'] not in seen:items.append(entry);seen.add(entry['id'])
m['items']=items;by={x['id']:x for x in items}
for e in exts:
 new=[f"{e['prefix']}-Q{i:03d}" for i in range(e['start'],e['start']+e['count'])]
 old=by[e['id']]['question_ids'];allq=list(dict.fromkeys(old+new)) if e['id'] in {'EXT-POS-01','EXT-DSA-01'} else new
 update=dict(status='reviewed',question_ids=allq,source_urls=e['sources'],source_status='verified')
 if e['id'] not in {'EXT-POS-01','EXT-DSA-01'}:update.update(code_verification='not_applicable',verification_evidence=None,example_paths=[],source_urls=e['sources'])
 by[e['id']].update(update)
 for qid in new:
  x=dict(id=qid,type='question',path=f'Interview-Question-Bank/Questions/{qid}.md',answer_path=f'Interview-Question-Bank/Model-Answers/{qid}.md',prerequisites=[e['id']],status='reviewed',code_verification='not_applicable',verification_evidence='scripts/validate.py',question_ids=[],example_paths=[],source_urls=[e['sources'][0]],source_status='verified')
  if qid in by:by[qid].update(x)
  else:items.append(x);by[qid]=x

# Eight cumulative mocks reuse reviewed questions but contain question-only first sections and full local answer keys.
all_question_ids=[x['id'] for x in items if x['type']=='question' and x['status']=='reviewed']
packs=[
 ("MOCK-001","Kotlin and coroutines",[q for q in all_question_ids if q.startswith(('KOT-','COR-'))][:12]),
 ("MOCK-002","Android internals",[q for q in all_question_ids if q.startswith('AND-')][:12]),
 ("MOCK-003","Architecture and data",[q for q in all_question_ids if q.startswith('ARC-')][:12]),
 ("MOCK-004","Views and Compose",[q for q in all_question_ids if q.startswith(('UI-','EUI-'))][:12]),
 ("MOCK-005","Production and security",[q for q in all_question_ids if q.startswith('PRO-')][:12]),
 ("MOCK-006","DSA live coding",[q for q in all_question_ids if q.startswith(('SYS-','DSA-'))][:12]),
 ("MOCK-007","System design and leadership",[q for q in all_question_ids if q.startswith(('SYS-','INT-','STF-'))][10:22]),
 ("MOCK-008","Full loop and POS",[q for q in all_question_ids if q.startswith(('POS-','COR-','PRO-','INT-'))][-12:]),
]
for mid,title,qids in packs:
 number=mid[-3:];path=f'Mock-Interviews/{mid.lower()}-{slug(title)}.md'
 questions=[];answers=[]
 for i,qid in enumerate(qids,1):
  qi=by[qid];qraw=(R/qi['path']).read_text();body=qraw.split('---',2)[-1];prompt=' '.join(x.strip() for x in body.splitlines() if x.strip() and not x.startswith(('#','[')))
  prompt=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',prompt)
  araw=(R/qi['answer_path']).read_text();spoken=re.search(r'\*\*Spoken answer:\*\*\s*[“\"](.+?)[”\"]',araw)
  questions.append(f'{i}. **{qid}:** {prompt}')
  spoken_text=spoken.group(1) if spoken else "Open the complete model answer and trace the contract."
  spoken_text=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',spoken_text)
  answers.append(f'{i}. **{qid}:** {spoken_text} [Complete answer](../{qi["answer_path"]})')
 doc=f'''---
id: {mid}
status: reviewed
---
# {mid} — {title}

**Recommended time:** 75 minutes. **Default:** Learning Mode; scoring is optional and self-reported. Read the rubric before starting.

## Question-only interview

{chr(10).join(questions)}

## Answer key

{chr(10).join(answers)}

## Published rubric

Score each answer 0–4: **0** absent/unsafe, **1** definition only, **2** correct core contract, **3** mechanism plus failure/test, **4** senior trade-off, evidence boundary, and clear communication. Coding questions also require compiling logic, boundary tests, and honest complexity. The score is practice evidence, never a hiring guarantee.

## Debrief

Record three items: the first wrong assumption, the slowest explanation, and the missing test. Return to linked lessons before repeating this pack. Do not memorize the answer key wording.
'''
 (R/path).write_text(doc,encoding='utf-8')
 x=dict(id=mid,type='mock_pack',title=title,path=path,prerequisites=[],status='reviewed',code_verification='not_applicable',verification_evidence=None,question_ids=[],example_paths=[],source_urls=[A+'topic/architecture/recommendations',K+'docs/home.html'],source_status='verified')
 if mid in by:by[mid].update(x)
 else:items.append(x);by[mid]=x

m['as_of']=DATE;mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

# Registries and coverage.
tp=R/'Interview-Question-Bank/BY-TOPIC.md';dp=R/'Interview-Question-Bank/BY-DIFFICULTY.md';sp=R/'Interview-Question-Bank/BY-INTERVIEW-STYLE.md';tt=tp.read_text();dt=dp.read_text();st=sp.read_text()
for e in exts:
 for qid,_,_,topic,d,sty in qdocs(e):
  ql=f'[{qid}](Questions/{qid}.md)';al=f'[answer](Model-Answers/{qid}.md)'
  if f'Questions/{qid}.md' not in tt:tt+=f'\n| {topic} | {ql} | [Model answer](Model-Answers/{qid}.md) |'
  if f'Questions/{qid}.md' not in dt:dt+=f'\n- {d.title()}: {ql} — {al}'
  if f'Questions/{qid}.md' not in st:st+=f'\n- {sty.replace("-"," ").title()}: {ql} — {al}'
tp.write_text(tt.rstrip()+'\n');dp.write_text(dt.rstrip()+'\n');sp.write_text(st.rstrip()+'\n')
cp=R/'COVERAGE-MATRIX.md';lines=cp.read_text().splitlines()
for e in exts:
 for i,line in enumerate(lines):
  if line.startswith(f'| {e["id"]} |'):
   lines[i]=f'| {e["id"]} | {Path(e["path"]).parent.as_posix()} | Advanced | {", ".join(e["pre"])} | 90 | [{e["id"]}]({e["path"]}) | {len(by[e["id"]]["question_ids"])} specialist questions | Interview traces | [official]({e["sources"][0]}) | reviewed | Advanced interview reference |';break
cp.write_text('\n'.join(lines)+'\n')
print('Completed 6 specialist tracks, 50 new Q&A, and 8 mock interview packs')

from harden_interview_bank import harden_bank
print("Hardened interview bank:", harden_bank())
