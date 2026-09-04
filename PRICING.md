# Pricing

FED-LINk itself is **free software under the MIT license** — no tiers, no
paid features, no API keys, no rate limits. The only costs in play are the
hosting and domain you already control. This page exists because the
honest question for any shortener is "what does this cost versus Bitly or
Dub.co?" — and the answer is a comparison table.

## What FED-LINk costs to run

| Item | Cost | Notes |
|---|---|---|
| The generator | $0 | MIT-licensed, runs offline |
| Hosting (InfinityFree) | $0 | free tier handles the redirect bundle easily; no ads injected into `.htaccess`-driven 301 responses |
| Mirror (GitHub Pages) | $0 | public repo, unlimited static hosting within Pages limits |
| Domain (`fedpromptly.com`) | already owned | IONOS; the `link.` subdomain costs nothing extra |
| Build infrastructure | $0 | GitHub Actions free minutes on public repositories |
| Desktop / Android apps | $0 | PyInstaller and Buildozer run in CI on free runners |

**Total: $0/month, unlimited links, custom domain included.**

The `kofi` short link (`link.fedpromptly.com/kofi` →
`https://ko-fi.com/fedpromptly`) is a voluntary support page — nothing in
the project requires or nags for payment.

## What the same thing costs as a service

Prices as of writing, on each vendor's public pricing pages, for the
features FED-LINk gives you for free:

| Feature | Bitly | Dub.co | FED-LINk |
|---|---|---|---|
| Custom domain (`link.yourdomain.com`) | paid tier | free tier (1 domain) | free (you own the domain) |
| Unlimited short links | paid tier | free tier limited / paid for volume | unlimited |
| 301 redirect behavior | configurable | default | always 301 |
| Export your data | CSV export on paid tiers | API on paid tiers | it's a JSON file in your git repo |
| UTM / analytics | paid tier | free tier basic | none (by design — see the FAQ's privacy stance) |
| No account, no tracking of *you* | no | no | yes — nothing phones home |
| Price for the feature set | ~$35/mo+ | ~$10–40/mo | $0 |

If you need click analytics, those services earn their price. If you need
correct, permanent, ownable redirects — which is what a personal link hub
is — a static bundle is strictly better: no expiry, no account to lose, no
vendor to outlive.

## Cost knobs if you outgrow free tiers

- **InfinityFree limits** (the realistic first ceiling): free accounts cap
  concurrent connections and have inode limits. A redirect bundle is
  thousands of tiny files at most; the practical fix if you ever hit it is
  the `redirects.map` file — one Apache `RewriteMap` file instead of
  per-slug folders, which `configs/redirects.map` already models (see
  ADR-0002 for why per-slug folders won anyway, and when to switch).
- **Pages limits**: 1 GB site / 100 GB bandwidth per month soft limits. A
  redirect bundle is measured in kilobytes.
- **CI minutes**: public repositories run free; if you fork this privately,
  the desktop/Android builds are the heavy jobs — expect them to be the
  bulk of any paid minutes.

## Support tiers

There are none. Bug reports and feature requests go through GitHub Issues
and Discussions, free, for everyone (see [`SUPPORT.md`](SUPPORT.md)).
Security reports are handled per [`SECURITY.md`](SECURITY.md). If you want
to fund development anyway, that's what the ko-fi link is for.
