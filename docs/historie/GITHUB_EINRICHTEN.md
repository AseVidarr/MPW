# MPW auf GitHub bringen (mit GitHub Desktop)

Das lokale Repository ist bereits angelegt (Branch `main`, erster Commit). Es fehlt nur das Veröffentlichen auf GitHub.

## 1. Repository veröffentlichen
1. **GitHub Desktop** öffnen (angemeldet mit deinem GitHub-Konto).
2. **File › Add local repository …** und diesen Ordner wählen:
   `C:\Users\User\Downloads\MPW\MPW_v2.2.0_RC1_Prompt_Laden_Hotfix`
3. Oben auf **Publish repository** klicken.
4. Name z. B. `mpw`, **„Keep this code private“ angehakt lassen** (empfohlen), dann **Publish repository**.

## 2. Erster Build auf GitHub
Nach dem Hochladen startet automatisch **„Tests und Pakete“**:
1. Auf github.com dein Repository öffnen › Reiter **Actions**.
2. Der Lauf testet auf Windows, macOS und Linux und baut danach alle Pakete (dauert ca. 15–30 Minuten).
3. Ist alles grün: im Lauf unten unter **Artifacts** die Pakete herunterladen
   (`MPW-Windows`, `MPW-macOS`, `MPW-Linux`).
4. Ist etwas rot: den Link zum Lauf an Claude geben – die Fehlermeldung zeigt, was auf dem jeweiligen System angepasst werden muss.

Hinweis: Bei privaten Repositories verbraucht GitHub Actions Freiminuten deines Kontos; macOS-Minuten zählen dabei mehrfach. Öffentliche Repositories sind kostenlos.

## 3. Eine Version veröffentlichen (später)
1. In GitHub Desktop: **History**, Rechtsklick auf den Commit › **Create Tag …**, z. B. `v2.2.0-rc1`, dann **Push origin**.
2. GitHub baut alles neu und legt unter **Releases** einen **Entwurf** mit allen Paketen an.
3. Entwurf prüfen und erst dann selbst auf **Publish release** klicken.

## Weiterarbeiten
- Änderungen erscheinen in GitHub Desktop unter **Changes** › Commit-Text eintragen › **Commit to main** › **Push origin**.
- Die ZIP-Pakete in `Downloads\MPW` kannst du wie bisher weiterführen; `dist/`, `build/`, ZIPs und Nutzerdaten (`Data/`, `*.db`) werden von Git ignoriert.
