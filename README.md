# hostfiles

Cached mirror of M17 host files, served via GitHub Pages.

## What this does

A scheduled GitHub Action runs hourly, fetches the upstream host file, and
commits it to this repo if the contents changed. GitHub Pages serves the
committed copy over a Fastly-backed CDN.

## Mirrored files

| File | Upstream source |
| --- | --- |
| `M17Hosts.txt`  | https://hostfiles.refcheck.radio/M17Hosts.txt |
| `M17Hosts.json` | https://hostfiles.refcheck.radio/M17Hosts.json |

The upstream requires a specific `User-Agent` for access; the sync action
sends it from the `REFCHECK_USER_AGENT` repository secret.

## Client URLs

Clients fetch from:

```
https://m17-project.github.io/hostfiles/M17Hosts.txt
https://m17-project.github.io/hostfiles/M17Hosts.json
```

## Setup checklist

1. Push this repo to `M17-Project/hostfiles` on GitHub.
2. In **Settings → Pages**, set source to **Deploy from a branch**, branch
   `main`, folder `/ (root)`.
3. In **Settings → Actions → General**, set workflow permissions to
   **Read and write**.
4. In **Settings → Secrets and variables → Actions**, add a repository
   secret named `REFCHECK_USER_AGENT` containing the User-Agent string
   provided by refcheck.radio.
5. Run the **Sync hostfiles** workflow once manually (Actions tab →
   *Run workflow*) to seed the files.

## Operations

- The workflow runs at `:17` past every hour and commits only when the file
  changes.
- GitHub cron can be delayed or skipped under load &mdash; expect updates
  within an hour or two of upstream changes, not to the minute.
- To force a refresh, trigger the workflow manually from the Actions tab.
- To add a new mirrored file, add its filename to the `for f in ...` loops
  in `.github/workflows/sync.yml`, extend the `tracked` and `git add` lines,
  and add a link in `index.html`.
