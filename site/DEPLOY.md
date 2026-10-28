# Deploy

The primary host is Vercel, project `hstack`, on Preetham's Pro plan. Cloudflare Pages on the belweave account, Free plan, is the fallback. Do not deploy from this note; the project owner runs the deploy.

## Vercel

Connect the GitHub repository with the root directory set to `site`, or deploy from a checkout with `vercel deploy --prod --cwd site`. `site/vercel.json` pins the build.

| Setting | Value |
|---|---|
| Project | `hstack` |
| Account | Preetham's Pro plan |
| Root directory | `site` |
| Framework preset | Other (`framework` is `null`) |
| Build command | `npm run build` |
| Output directory | `dist` |

`cleanUrls` is on. `/install` and `/install/` rewrite to `install.sh` and are served as `text/plain; charset=utf-8` with `Cache-Control: public, max-age=60`. Any other path under `/install/` rewrites to a plain-text 404. `.tar.gz` is `application/gzip`. `.sha256` is `text/plain`. `www.hstack.sh` redirects to `https://hstack.sh` with status 308. A request that still arrives as HTTP on `hstack.sh` redirects to HTTPS with status 308.

Turn Deployment Protection off for production. A protected deploy returns an HTML login page, and `curl | sh` would not receive the installer.

## hstack.sh at Porkbun

Leave the Porkbun nameservers alone. The registrar stays Porkbun. Vercel does not need to host DNS.

1. In the Vercel project `hstack`, open Settings, then Domains. Add `hstack.sh` and `www.hstack.sh`.
2. The apex card shows an A record. For most projects the value is `76.76.21.21`. Use the address on the card if it differs.
3. At Porkbun, edit DNS for `hstack.sh`. Remove any existing apex A or AAAA record. Add one A record: host `@`, value from the apex card (usually `76.76.21.21`). Do not add an AAAA record.
4. Add a CNAME for `www`. The value is the CNAME target on the `www` domain card. For many projects that target is `cname.vercel-dns.com`. A newer project may show a specific name such as `cname.vercel-dns-0.com`. Use the card.
5. Wait until both cards say the configuration is valid. Vercel issues the certificates.

`www.hstack.sh` answers 308 to the apex. Before DNS is in place, the deployment hostname on the project card (a `*.vercel.app` host) is what `HSTACK_BASE_URL` should point at.

## What the deploy serves

- `https://hstack.sh/install` and `https://hstack.sh/install/` are `install.sh`, `Content-Type: text/plain; charset=utf-8`.
- `https://hstack.sh/install.ps1` is the Windows installer, also `text/plain`.
- Any other path under `/install/` is a plain-text 404 (`not found`), not an HTML page.
- `curl -fsSL hstack.sh/install` follows HTTP to HTTPS and receives the script. `curl -fsSL www.hstack.sh/install` follows the 308 to the apex and receives the same script.

Do not rebuild `/dl/hstack-v0.1.0.tar.gz` or `/dl/hstack-v0.2.0.tar.gz`. The site build copies both from `site/vendor/dl/` unchanged.

`hstack-v0.1.0.tar.gz` is sha256 `0c8009ee04fb31126b76e4202c91eee14e8d5be7d1cd42ac0cee551012eeda6e`, 19967 bytes. `hstack-v0.2.0.tar.gz` is the file hstack.sh served for 0.2.0, sha256 `c16dfee4cd2841939a97a5cebf816c3fc3e8d71e28f2f1874639ea539ea20810`, 30914 bytes. Each checksum line is that digest, two spaces, then the filename.

After this deploy, `/dl` is:

| Path | Bytes | Cache-Control |
|---|---|---|
| `/dl/hstack-v0.1.0.tar.gz` and `.sha256` | the vendored 0.1.0 archive | `public, max-age=31536000, immutable` |
| `/dl/hstack-v0.2.0.tar.gz` and `.sha256` | the vendored live 0.2.0 archive, not a rebuild | `public, max-age=31536000, immutable` |
| `/dl/hstack-v0.2.1.tar.gz` and `.sha256` | the vendored 0.2.1 archive | `public, max-age=31536000, immutable` |
| `/dl/hstack.tar.gz` and `.sha256` | the same bytes as `hstack-v0.2.1.tar.gz` | `public, max-age=300` |

`HSTACK_VERSION=0.1.0` and `HSTACK_VERSION=0.2.0` request those versioned files, not the alias. The alias changes on this deploy. Its five-minute cache is the existing rule. Until this build is deployed, hstack.sh still serves 0.2.0 at `/dl/hstack.tar.gz`.

The 0.2.1 archive has one top-level directory. Inside it are `skills/hstack/`, `scripts/apply_addons.py`, `scripts/apply_hooks.py`, `hooks/`, `bin/` (the addon helpers), and `VERSION`.

## Cloudflare Pages fallback

Use this only if the Vercel project is not the host. Same build: root directory `site`, build command `npm run build`, output directory `dist`, no framework preset. Account belweave, Free plan.

`site/_headers` and `site/_redirects` are copied into `dist/`. Pages reads them from the output and does not serve them as assets. `site/functions/` stays in the project root. Pages compiles it from there. `functions/install/[...path].js` returns the plain-text 404, because Pages does not honor a 404 status in `_redirects`. `functions/_middleware.js` redirects HTTP to HTTPS when the request is still http. Leave Always Use HTTPS on.

Pages will not activate the apex while DNS stays at Porkbun. The fallback path is to add the `hstack.sh` zone on the belweave account and set Porkbun's nameservers to the Cloudflare pair. That replaces the Vercel A record and the `www` CNAME. Do not point the apex at both hosts. A project named `hstack` is also reachable at `hstack.pages.dev` before that cutover.
