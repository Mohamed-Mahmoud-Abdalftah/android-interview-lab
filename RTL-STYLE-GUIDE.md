# Arabic and English direction style guide

Use this guide for Egyptian Arabic teaching prose in the academy. The direction is part of the document, so GitHub and local previews can read the same file. Local CSS refines spacing and fonts; it is not the source of truth for direction.

## Authoring rules

1. Keep YAML keys, English explanations, file paths, commands, and fenced code in their normal LTR Markdown form. Never set direction on the whole document.
2. Write each Arabic prose paragraph as a complete HTML paragraph: `<p dir="rtl" lang="ar">…</p>`. Put a blank line before and after it. Inside raw HTML, use HTML inline tags; Markdown bold, code-span, and link notation are not reliably parsed.
3. Use `<code dir="ltr">…</code>` for Kotlin identifiers, code expressions, commands, and paths inside Arabic prose. For an unformatted English phrase whose punctuation should stay together, use `<span dir="ltr">…</span>`. Use an HTML anchor with `dir="ltr"` for an English link inside an Arabic paragraph. Keep URLs and relative paths unchanged.
4. Use a complete `<h2 dir="rtl" lang="ar" id="stable-anchor">…</h2>` or corresponding heading level for an Arabic heading. Preserve existing Markdown headings when their text is predominantly English. Give a converted heading an explicit ID based on its former Markdown slug; check that fragment links work in each target renderer before publishing them.
5. Use `<ol dir="rtl" lang="ar"><li>…</li></ol>` and `<ul dir="rtl" lang="ar"><li>…</li></ul>` for Arabic lists. Put each item on its own line. This places markers and indentation on the right without depending on CSS. An English list stays Markdown.
6. Use a full HTML table with `dir="rtl" lang="ar"` when the table is Arabic. Use `<th>` and `<td>` cells; mark an English-only cell `dir="ltr"`. Keep a Markdown table when it is English. Do not mix Markdown table syntax inside raw HTML.
7. End the Arabic block before a fenced code example or English interview answer. Fenced Kotlin remains ordinary Markdown and LTR. If an Arabic callout is needed, use a complete `<blockquote dir="rtl" lang="ar"><p>…</p></blockquote>` block.

Do not use invisible bidi control characters, a global RTL stylesheet, or `markdown=1` on an HTML container. GitHub's Markdown parser does not promise to parse Markdown placed directly inside raw HTML blocks. GitHub also strips `<bdi>` in its current sanitizer, so prefer the supported `dir` attributes on block elements, `<code>`, and `<span>`.

## Copyable pattern

```html
<h2 dir="rtl" lang="ar" id="mental-model">الفكرة الأساسية</h2>

<p dir="rtl" lang="ar">لما تستخدم <code dir="ltr">StateFlow</code> مع <code dir="ltr">ViewModel</code>، لازم تفهم إزاي الـ <span dir="ltr">Coroutine</span> بتتعامل مع الـ <code dir="ltr">Lifecycle</code>.</p>

<ol dir="rtl" lang="ar">
<li>اقرأ قيمة <code dir="ltr">StateFlow</code> الحالية.</li>
<li>اتبع التغيير عند <code dir="ltr">ViewModel</code>.</li>
</ol>
```

Then write an ordinary fenced `kotlin` block and an ordinary English answer outside those HTML elements. Use [the reusable lesson template](templates/ARABIC-LESSON.md) for a new lesson and [the rendering fixture](fixtures/RTL-MIXED-LANGUAGE.md) when checking a preview.

## Local previews

- **VS Code:** Open `Android-Interview-Mastery` as the workspace root. `.vscode/settings.json` loads `.vscode/rtl-preview.css` into Markdown Preview via `markdown.styles`. This changes typography for marked Arabic blocks only.
- **Obsidian:** Open the academy as a vault. In **Settings → Appearance → CSS snippets**, reload and enable `rtl-academy.css`. The file is in `.obsidian/snippets/`. Check Reading View and Live Preview separately; Live Preview may show raw HTML around the cursor.
- **GitHub:** The semantic HTML works without either local CSS file. Inspect the rendered file after publishing. GitHub may prefix explicit HTML IDs internally, so verify any fragment links to converted headings on the published page.

The local font stack uses fonts already available on the reader's machine, including SF Arabic and Geeza Pro on macOS, then Noto Arabic families and common fallbacks. No font is bundled or downloaded.

## Review before marking content ready

Compare the rendered document with the source in each available preview. Check Arabic paragraph alignment and punctuation, technical terms and parentheses, right-side list markers, table column order, relative links and heading fragments, and LTR copy/paste of fenced Kotlin. Inspect source text for missing content after converting Markdown inline syntax to HTML. A direction attribute is a structural check, not proof of visual correctness.

References: [GitHub Flavored Markdown HTML blocks](https://github.github.com/gfm/#html-blocks), [VS Code Markdown preview styles](https://code.visualstudio.com/docs/languages/markdown#_using-your-own-css), [Obsidian CSS snippets](https://help.obsidian.md/Extending+Obsidian/CSS+snippets).
