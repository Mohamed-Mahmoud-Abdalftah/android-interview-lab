# GitHub Pages deployment

**Repository:** [Mohamed-Mahmoud-Abdalftah/android-interview-lab](https://github.com/Mohamed-Mahmoud-Abdalftah/android-interview-lab). **Published site:** [Android Interview Lab](https://mohamed-mahmoud-abdalftah.github.io/android-interview-lab/). The GitHub Actions Pages source was configured through the GitHub API. The first successful deployment completed on 2026-10-12, and both the home page and `/lab/questions/kot-01/` returned HTTP 200. Each subsequent push runs the same release gate before replacing the site.

`.github/workflows/deploy-pages.yml` runs the complete content gate, Python/JavaScript/Kotlin checks, Astro typecheck and build, internal-link checker, and Playwright browser tests before it uploads `site/dist` to GitHub Pages. It uses the official GitHub Pages configure/upload/deploy actions with `contents: read`, `pages: write`, and `id-token: write`. Publication happens only after the build job passes.

For a project repository named `android-interview-lab`, the expected base is `/android-interview-lab/`. The workflow derives this from `GITHUB_REPOSITORY` and sets the site origin to `https://<owner>.github.io`. For a user or organization repository named `<owner>.github.io`, the base is `/`. In **Settings → Pages**, set the source to **GitHub Actions**. Push `main` or dispatch the workflow, then confirm the `deploy` job succeeded and visit the actual Pages URL and a question subpath. Do not infer a live site from a green local build.

For a custom domain, set `PUBLIC_SITE_URL` to its origin and `PUBLIC_SITE_BASE=/` in the build environment, and add a matching `site/public/CNAME`. Check DNS and HTTPS in Pages settings before announcing the custom domain.

Local project-path check from `site/`:

```sh
GITHUB_REPOSITORY=example/android-interview-lab PUBLIC_SITE_URL=https://example.github.io pnpm build
GITHUB_REPOSITORY=example/android-interview-lab pnpm check:dist
pnpm test:e2e
```

The E2E suite requires an installed Google Chrome and a built `site/dist`. If links fail, check `PUBLIC_SITE_BASE`, `GITHUB_REPOSITORY`, and paths in the generated HTML. If the workflow stops at the editorial gate, run `python3 scripts/validate_interview_lab.py --require-complete` locally. Use `reports/content-coverage.json` to locate any future incomplete record.
