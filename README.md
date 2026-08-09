# Tigress thread gallery (18+)

HTML gallery of all generations from the Grok tigress NSFW thread (sheets, cowgirl, doggystyle, pool table, bunny).

## Local

```
C:\Users\hebp\galleries\tigress-thread-gallery\index.html
```

## Public

GitHub Pages: see repo homepage / Actions after first push.

## Add next generation

```powershell
cd C:\Users\hebp\galleries\tigress-thread-gallery
python scripts\publish-add.py "C:\path\to\new.png" `
  --title "Pool table v6" `
  --category scene `
  --model "Seedream 5 Pro" `
  --note "smaller ass" `
  --cdn "https://tempfile.aiquickdraw.com/..." `
  --push
```

Categories: `sheet` | `scene` | `identity` | `bunny`

## Update flow (agent)

1. Generate image → save under session `assets/` + Desktop.
2. Run `publish-add.py` with `--push`.
3. Give user the GitHub Pages URL.

18+ only · noindex.
