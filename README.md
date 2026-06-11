# hostfiles

Cached mirror of M17 host files, served via GitHub Pages.

## What this does

A scheduled GitHub Action runs hourly, fetches the upstream host file, and
commits it to this repo if the contents changed. GitHub Pages serves the
committed copy over a Fastly-backed CDN.

## Mirrored files

| File | Upstream source |
| --- | --- |
| `M17_Hosts.txt` | https://www.pistar.uk/downloads/M17_Hosts.txt |

## Client URLs

Once Pages is enabled, clients fetch from:

```
https://m17-project.github.io/hostfiles/M17_Hosts.txt
```

## Setup checklist

1. Push this repo to `M17-Project/hostfiles` on GitHub.
2. In **Settings → Pages**, set source to **Deploy from a branch**, branch
   `main`, folder `/ (root)`.
3. In **Settings → Actions → General**, set workflow permissions to
   **Read and write**.
4. Run the **Sync hostfiles** workflow once manually (Actions tab →
   *Run workflow*) to seed `M17_Hosts.txt`.

## Operations

- The workflow runs at `:17` past every hour and commits only when the file
  changes.
- GitHub cron can be delayed or skipped under load &mdash; expect updates
  within an hour or two of upstream changes, not to the minute.
- To force a refresh, trigger the workflow manually from the Actions tab.
- To add a new mirrored file, copy the `Fetch` / `Replace if changed` steps
  in `.github/workflows/sync.yml` and add a link in `index.html`.
