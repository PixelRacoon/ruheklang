# Ruheklang 🌿

Eine kostenlose, datensparsame **Offline-Web-App** für iPhone, Android und Desktop.

**13 Klänge:** Regen, starker Regen, Gewitter, Meer, Bach, Wind, Wald, Kamin, Sommernacht, braunes / rosa / weißes Rauschen und Ventilator.

**Funktionen:** Dropdown für Klangwahl, Play/Pause/Stopp, Lautstärke und Einschlaf-Timer (5 bis 120 Minuten oder unbegrenzt).

- Kein Benutzerkonto, keine Werbung, keine Analytics, keine Cookies und keine externen Skripte
- Originale, algorithmisch generierte MP3-Tonspuren
- Offline-Betrieb via Service Worker, nachdem alle Dateien einmal geladen wurden

## Installation

Nach Aktivierung von **Settings → Pages → Deploy from a branch → main → /(root)**:

https://pixelracoon.github.io/ruheklang/

iPhone: Mit **Safari** öffnen → Teilen → Zum Home-Bildschirm → Hinzufügen.

Android: Mit **Chrome** öffnen → Menü → App installieren.

## Technisches

- `index.html`: Benutzeroberfläche und Player
- `manifest.webmanifest`: Installationsdaten
- `service-worker.js`: Cache für Offline-Verwendung und Unterstützung für Audio-Ranges
- `assets/*.mp3`: vollständig lokale Sounds
- `icons/*.png`: App-Symbole
- `generate_audio.py` / `make_icons.py`: Quellen der selbst generierten Medien
- `.github/workflows/build-assets.yml`: erzeugt fehlende Medien einmalig und schreibt sie ins Repo

**Wichtig für iOS:** MP3 über einen HTML-Audioplayer ist tendenziell besser für Bildschirm-Sperre als reines Web Audio; zuverlässige Hintergrundwiedergabe und sekundengenaue Timer sind jedoch von iOS abhängig und nicht garantiert.

Alle Dateien für die Website werden direkt von GitHub Pages bereitgestellt. Es werden keine privaten Inhalte erfasst. GitHub als Hosting-Dienst kann technisch notwendige Zugriffsprotokolle verarbeiten.
