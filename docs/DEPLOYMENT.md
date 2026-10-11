# GitHub Pages deployment

The current target directory has no GitHub remote. No live Pages URL is verified. The workflow is prepared but deliberately blocks publication while canonical reviewed-answer coverage is below 485.

After completing and validating every answer, create or connect a GitHub repository, push the `main` branch, and in repository **Settings → Pages** select **GitHub Actions** as the source. `.github/workflows/deploy-pages.yml` builds with the repository's project base path and uses GitHub's official Pages upload/deploy actions. A user/organization repository named `<owner>.github.io` uses `/` as its base; another repository uses `/<repository>/`.

The workflow sets `PUBLIC_SITE_URL` to `https://<owner>.github.io` and derives `base` from `GITHUB_REPOSITORY`. For a custom domain, set `PUBLIC_SITE_URL` to that origin and `PUBLIC_SITE_BASE=/` in the build environment and add a matching `site/public/CNAME`. Do not claim a deployment until the Pages run succeeds and its actual URL is visited.

Local subpath test from `site/`:

```sh
GITHUB_REPOSITORY=example/android-interview-lab PUBLIC_SITE_URL=https://example.github.io pnpm build
GITHUB_REPOSITORY=example/android-interview-lab pnpm check:dist
```

If internal links break, inspect `PUBLIC_SITE_BASE`, `GITHUB_REPOSITORY`, and the generated `site/dist/` paths. If the release workflow stops at its content gate, run `python3 scripts/validate_interview_lab.py --require-complete`; its count is the authoritative remaining-answer total.
