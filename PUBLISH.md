# Publish

Add a picture or video with `scripts/publish-add.py --push` on `master` only.

GitHub Pages builds the `gh-pages` branch, which is the HTML shell. Media stays on `master` and the site reads it from git. Pushing a new file does not rebuild the site.

Do not point Pages back at `master`, do not upload `images/` in a Pages workflow, and do not copy the media tree onto `gh-pages`. Update `gh-pages` only when `index.html`, `watch.html`, `site.js`, or a story page changes.
