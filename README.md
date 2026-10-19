# panagro.kz

Static site generator for panagro.kz.

- `pages.py` — page content and navigation
- `home_main.html` — home page body
- `assets/` — CSS, JS, images
- `build.py prod|preview` — builds into `../dist` or `../preview`

Push to `main` builds the site and uploads it to the hosting via FTP
(`.github/workflows/deploy.yml`). Required repository secrets:
`FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`, `FTP_DIR` (e.g. `/public_html/`).
