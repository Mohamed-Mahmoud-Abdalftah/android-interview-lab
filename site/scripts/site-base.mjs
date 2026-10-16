export function siteBase() {
  const explicit = process.env.PUBLIC_SITE_BASE;
  const repository = process.env.GITHUB_REPOSITORY?.split('/').at(-1);
  const inferred = repository ? (repository.endsWith('.github.io') ? '/' : `/${repository}/`) : '/android-interview-lab/';
  const value = explicit ?? inferred;
  return value === '/' ? '/' : `/${value.replace(/^\/+|\/+$/g, '')}/`;
}

export function href(route) {
  return `${siteBase()}${route.replace(/^\//, '')}`;
}
