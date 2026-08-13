# Tigress thread gallery (18+)

Две версии одного сайта.

## Внешняя (GitHub Pages)

https://mrak0be5.github.io/tigress-thread-gallery/

Только галерея. Без ключей, без гайда MiniMax, без локальных путей.

## Локальная

Открыть файл с диска:

```
C:\Users\hebp\galleries\tigress-thread-gallery\index.html
```

или `local.html` в той же папке.

Показывает ключи Wan / сервисы и гайд MiniMax: [pc-video.html](pc-video.html).

`manifest.json` — полный (ключи). `manifest-public.json` — для внешней версии.

## Add next generation

```powershell
cd C:\Users\hebp\galleries\tigress-thread-gallery
python scripts\publish-add.py "C:\path\to\new.png" `
  --title "Pool table v6" `
  --category scene `
  --model "Seedream 5 Pro" `
  --note "smaller ass" `
  --cdn "https://tempfile.aiquickdraw.com/..." `
  --prompt-file "C:\path\to\prompt.txt" `
  --ref "Picture 1 scene|C:\path\to\ref.png" `
  --lora "Name|https://civitai.com/models/...|0.45" `
  --push
```

Categories: `sheet` | `scene` | `identity` | `bunny` | `video` | `story`

Story (latest version, separate gallery section):

```powershell
python scripts\publish-add.py "C:\Users\hebp\OneDrive\Desktop\TigraDeepComix\STORY-gym-4acts-v8.7.md" `
  --category story `
  --title "Ночная смена" `
  --id story-gym-night-shift `
  --note "Тигра и Винна. Ночной зал." `
  --push
```

Reader: `story.html` · nav: `#story`

## Update flow (agent)

1. Generate image → save under session `assets/` + Desktop.
2. Run `publish-add.py` with `--push`.
3. Give user the GitHub Pages URL.

18+ only · noindex.
