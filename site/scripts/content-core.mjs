import path from 'node:path';

const lessonDirectories = new Set([
  '01-Kotlin-JVM-ART',
  '02-Coroutines-Flow',
  '03-Android-Internals',
  '04-Architecture-DI',
  '05-Views-Compose',
  '06-Production-Engineering',
  '07-DSA-Live-Coding',
  '08-Mobile-System-Design',
  '09-Leadership-English',
  '10-Optional-POS-Specialist',
]);

export function stripFrontmatter(markdown) {
  const match = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!match) return { frontmatter: '', body: markdown };
  return { frontmatter: match[1], body: markdown.slice(match[0].length) };
}

function readablePrompt(markdown) {
  return markdown
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/<p[^>]*>[\s\S]*?<\/p>/gi, ' ')
    .replace(/^>\s?/gm, '')
    .replace(/\*\*(?:Interviewer:\s*)?([\s\S]*?)\*\*/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\*\*/g, '')
    .replace(/__/g, '')
    .replace(/`/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

export function extractInterviewQuestion(markdownBody) {
  const body = markdownBody.replace(/^\s*#\s+.+\r?\n+/, '');
  const labelled = body.match(/^##\s+Interview question\s*\r?\n([\s\S]*?)(?=^##\s+|(?![\s\S]))/mi);
  if (labelled) return readablePrompt(labelled[1]);

  const promptOnly = body
    .split(/^\[Open complete model answer\]/mi)[0]
    .split(/^##\s+/m)[0];
  return readablePrompt(promptOnly);
}

export function routeForCanonicalPath(inputPath) {
  const canonical = inputPath.replaceAll('\\', '/').replace(/^\.\//, '');
  const parts = canonical.split('/');
  const file = parts.at(-1) ?? '';
  const stem = file.replace(/\.md$/i, '').toLowerCase();
  if (canonical === 'projects/kotlin-jvm-labs/README.md') return '/reference/jvm-lab/';
  if (canonical === '09-Leadership-English/STAR-EVIDENCE-WORKSHEET.md') return '/reference/star-evidence-worksheet/';
  if (canonical === 'Mock-Interviews/README.md') return '/mocks/';
  if (lessonDirectories.has(parts[0])) {
    const id = file.match(/^([a-z]+(?:-[a-z]+)?-\d+)/i)?.[1]?.toLowerCase() ?? stem;
    return `/lessons/${id}/`;
  }
  if (canonical.startsWith('Interview-Question-Bank/Questions/')) return `/questions/${stem}/`;
  if (canonical.startsWith('Interview-Question-Bank/Model-Answers/')) return `/answers/${stem}/`;
  if (canonical.startsWith('Real-World-Scenarios/')) {
    const id = file.match(/^(SCN-\d+)/i)?.[1]?.toLowerCase() ?? stem;
    return `/scenarios/${id}/`;
  }
  if (canonical.startsWith('Coding-Challenges/')) {
    const id = file.match(/^(LAB-\d+)/i)?.[1]?.toLowerCase() ?? stem;
    return `/labs/${id}/`;
  }
  if (canonical.startsWith('Mock-Interviews/')) return `/mocks/${stem}/`;
  if (canonical.startsWith('Flashcards-Revision/')) return `/revision/${stem}/`;
  if (canonical.startsWith('Speaking-Shadowing/')) return `/speaking/${stem}/`;
  return `/reference/${stem}/`;
}

function splitHref(href) {
  const match = href.match(/^([^?#]*)([?#].*)?$/);
  return { pathname: match?.[1] ?? href, suffix: match?.[2] ?? '' };
}

export function rewriteCanonicalLinks(markdown, sourcePath) {
  const sourceDirectory = path.posix.dirname(sourcePath.replaceAll('\\', '/'));
  return markdown.replace(/\]\(([^)]+)\)/g, (whole, href) => {
    if (/^(?:https?:|mailto:|#|\/)/i.test(href)) return whole;
    const { pathname, suffix } = splitHref(href);
    const resolved = path.posix.normalize(path.posix.join(sourceDirectory, pathname));
    if (/\.md$/i.test(pathname)) return `](${routeForCanonicalPath(resolved)}${suffix})`;
    if (/\.(?:kt|java|kts|json|yaml|yml|txt)$/i.test(pathname)) return `](/source/${resolved}${suffix})`;
    return whole;
  }).replace(/href="(?!https?:|mailto:|#|\/)([^"]+)"/gi, (whole, href) => {
    const { pathname, suffix } = splitHref(href);
    const resolved = path.posix.normalize(path.posix.join(sourceDirectory, pathname));
    if (/\.md$/i.test(pathname)) return `href="${routeForCanonicalPath(resolved)}${suffix}"`;
    if (/\.(?:kt|java|kts|json|yaml|yml|txt)$/i.test(pathname)) return `href="/source/${resolved}${suffix}"`;
    return whole;
  });
}

export function yamlScalar(frontmatter, key) {
  const match = frontmatter.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'));
  return match?.[1]?.trim().replace(/^['"]|['"]$/g, '') ?? '';
}

export function cleanTitle(title) {
  return title.replace(/^#+\s*/, '').replaceAll('"', '\\"').trim();
}
