# Publishing Rules (SKIE pseudonym)

**Apply when cwd matches any of:** `**/project-skie/**`, `**/*publication*/**`, `**/*manuscript*/**`.

If cwd does not match, ignore this section entirely.

## Identity hygiene
- Never insert real-name metadata, git author email, or OS username into committed files.
- Check `git config user.email` matches the pseudonym project's configured email before any commit.
- Strip notebook metadata (`kernelspec`, `metadata.authors`) before push.

## AI-assistance disclosure
- Every deliverable includes an "AI-assistance statement" in README or manuscript appendix: models used (with version), role (idea, code, prose, audit), and the reproducibility log path.
- Follow [ICMJE Recommendations (updated January 2026)](https://www.icmje.org/recommendations/): AI cannot be an author; disclose AI-assistance use.

## Venues
- Zenodo (DOI), SSRN (quant), personal Cloudflare Pages site.
- arXiv: only after endorsement lined up.

## Versioning
- Each release tagged `skie-v{MAJOR.MINOR}` with a Zenodo-minted DOI.
- Changelog entry required for every release.
