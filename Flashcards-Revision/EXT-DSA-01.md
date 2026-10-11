# EXT-DSA-01 revision cards

Use after [EXT-DSA-01](../07-DSA-Live-Coding/ext-dsa-01.md).

<ol dir="rtl" lang="ar"><li><strong>شرط Dijkstra؟</strong> كل weights غير سالبة.</li><li><strong>ليه heap entries مكررة؟</strong> بنستخدم lazy decrease-key ونرفض stale وقت poll.</li><li><strong>متى توقف؟</strong> لما target تتعمل poll بمسافتها الحالية، مش أول discovery.</li><li><strong>كيف ترجع path؟</strong> parent عند كل improvement ثم reverse من target.</li><li><strong>overflow guard؟</strong> افحص قبل جمع <code dir="ltr">Long</code> أو استخدم domain bound.</li><li><strong>التعقيد؟</strong> محافظًا <code dir="ltr">O((V+E) log E)</code> مع lazy duplicates.</li></ol>
