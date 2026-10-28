# Deploy

Production target is Cloudflare Pages on the belweave account, Free plan. Do not deploy from this note; the project owner runs the deploy.

## Pages project

Connect the GitHub repository. The site lives in `site/`.

| Setting | Value |
|---|---|
| Account | belweave |
| Plan | Free |
| Root directory | `site` |
| Framework preset | None |
| Build command | `npm run build` |
| Output directory | `dist` |

Pages installs from `site/package-lock.json` before the build command. There is no framework preset and no `vercel.json`.

`site/_headers` and `site/_redirects` are copied into `dist/` by the build. Pages reads those files from the output directory and does not serve them as assets. `site/functions/` stays in the project root. Pages compiles it from there; it is not part of `dist/`.

## hstack.sh

The custom domain is `hstack.sh`. DNS for that name is at Porkbun today. The registrar stays Porkbun.

Pages will not activate an apex custom domain while the DNS stays outside Cloudflare. The supported path is:

1. Add the `hstack.sh` zone on the belweave Cloudflare account (the zone itself is free).
2. At Porkbun, set the nameservers for `hstack.sh` to the pair Cloudflare shows for that zone. Do not move the registration.
3. In the Pages project, add the custom domain `hstack.sh`. Cloudflare then creates the CNAME it expects.
4. Leave Always Use HTTPS on. It is the default for an active custom domain, and it is what turns `http://hstack.sh/install` into `https://hstack.sh/install` before the script is returned.

Before the zone is on Cloudflare, the pre-DNS host is the `pages.dev` hostname. A project named `hstack` is `hstack.pages.dev`. `HSTACK_BASE_URL` can point the installer at that host.

If the records must stay at Porkbun, the record Pages documents for a hostname outside the apex is a CNAME to `<project>.pages.dev`. Porkbun can also store an ALIAS at `@` for that same target, but the Pages dashboard will not mark an external-DNS apex active until the zone is on the belweave account. Do not add an AAAA record. Add the domain in the Pages project before the record exists, or the edge answers 522.

## What the deploy serves

- `https://hstack.sh/install` and `https://hstack.sh/install/` are `install.sh`, `Content-Type: text/plain; charset=utf-8`, with or without the trailing slash.
- `https://hstack.sh/install.ps1` is the Windows installer, also `text/plain`.
- Any other path under `/install/` is a plain-text 404 (`not found`), not an HTML page. That response comes from `site/functions/install/[...path].js`. Pages does not honor a 404 status in `_redirects`.
- `curl -fsSL hstack.sh/install` follows the HTTP to HTTPS redirect and receives the script. The body is never an HTML page, including when the path under `/install/` does not exist.
- `https://hstack.sh/dl/hstack.tar.gz` is the latest archive. `hstack.tar.gz.sha256` is its digest.
- `https://hstack.sh/dl/hstack-v0.1.0.tar.gz` is that same release by version. The installer checks the digest before it extracts.

The archive has one top-level directory. Inside it are `skills/hstack/`, `scripts/apply_addons.py`, `bin/` (the addon helpers), and `VERSION`.
