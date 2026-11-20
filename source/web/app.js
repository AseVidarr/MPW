/* MPW im Browser – Stufe 1 (Songs & Suno, Bands). Daten kommen von mpw_web.py auf 127.0.0.1.
   Alle Inhalte werden als Text gesetzt (textContent), nie als HTML. */
'use strict';

const I18N = {
  de: {
    app_sub: 'im Browser', tab_songs: 'Songs & Suno', tab_bands: 'Bands', all_bands: 'Alle Bands',
    search_placeholder: 'Song suchen …', songs_count: '{n} Songs', no_song: 'Bitte links einen Song auswählen.',
    status: 'Status', distributor: 'Distributor', platforms: 'Plattformen', style: 'Style', lyrics: 'Lyrics',
    save: 'Song speichern', revert: 'Änderungen verwerfen', unsaved: 'Ungespeicherte Änderungen',
    saved: 'Song gespeichert.', saved_archived: 'Song gespeichert. Der vorherige Prompt wurde in der Versionshistorie gesichert.',
    conflict: 'Der Song wurde inzwischen geändert (z. B. in der Desktop-App). Deine Eingaben wurden nicht gespeichert.\n„Änderungen verwerfen“ lädt den aktuellen Stand.',
    too_long: 'Style maximal 1.000, Lyrics maximal 5.000 Zeichen.', error: 'Fehler: {detail}',
    connection: 'Keine Verbindung zu MPW-Web. Läuft das MPW-Web-Fenster noch?',
    token: 'Zugriff verweigert. Bitte MPW-Web neu starten und die angezeigte Adresse öffnen.',
    versions: 'Gespeicherte Prompt-Versionen', no_versions: 'Noch keine gespeicherten Versionen.',
    version_load: 'In den Editor übernehmen', version_load_hint: 'Gespeichert wird erst mit „Song speichern“.',
    version_loaded: 'Version #{id} in den Editor übernommen – noch nicht gespeichert.',
    confirm_discard: 'Ungespeicherte Änderungen verwerfen?', no_band: 'Bitte links eine Band auswählen.',
    genres: 'Genres', persona: 'Persona', hardware: 'Instrumente / Hardware', group: 'Gruppe', projects: 'Song/Projekte',
    none: '–', bands_readonly: 'Bands werden in dieser Stufe nur angezeigt; bearbeiten in der Desktop-App.',
    no_projects: 'Keine Song/Projekte.', footer: 'Lokal auf diesem PC · dieselben Daten wie die installierte MPW',
    chars: '{n}/{max}', st_0: 'In Bearbeitung', st_1: 'Fertig', st_2: 'Veröffentlicht',
    genre_main: "Hauptgenre",
    genre_second: "Zweitgenre",
    band_save: "Bandprofil speichern",
    band_name_hint: "Der Bandname wird in der Desktop-App geändert (daran hängt der Band-Ordner).",
    band_saved: "Bandprofil gespeichert.",
    hw_add: "Instrument hinzufügen",
    hw_save: "Änderung speichern",
    cancel: "Abbrechen",
    edit: "Bearbeiten",
    delete: "Löschen",
    confirm_delete_hw: "Diesen Hardware-Eintrag löschen?\n{entry}",
    no_hardware: "Noch keine Instrumente / Hardware.",
    presets: "Hardware-Presets",
    no_presets: "Keine Presets gespeichert.",
    preset_add: "Preset zur Band hinzufügen",
    preset_replace: "Preset auf Band anwenden (ersetzen)",
    preset_save: "Band-Hardware als Preset speichern",
    preset_name_prompt: "Name des Studio-Setups:",
    preset_overwrite: "Das Preset „{name}“ existiert bereits. Überschreiben?",
    preset_saved: "Preset mit {count} Einträgen gespeichert.",
    preset_added: "{added} Einträge hinzugefügt, {skipped} waren schon vorhanden.",
    confirm_replace: "Preset „{name}“ auf „{band}“ anwenden?\n\nDie vorhandene Hardware dieser Band wird ERSETZT.",
    preset_replaced: "Hardware ersetzt: {added} Einträge aus dem Preset.",
    err_empty_field: "Gruppe und Instrument / Hardware dürfen nicht leer sein.",
    err_too_long: "Eingabe ist zu lang.",
    err_no_hardware: "Diese Band hat noch keine Hardware-Einträge.",
    err_preset_damaged: "Das Preset ist beschädigt und kann nicht verwendet werden.",
    err_missing: "Der Eintrag existiert nicht mehr. Bitte neu laden.",
    band_new: "+ Neue Band",
    band_new_title: "Neue Band anlegen",
    band_name: "Bandname",
    band_create: "Band anlegen",
    band_new_hint: "Legt den Band-Ordner und den Prompt-Ordner an. Projekt-Unterordner entstehen erst beim Anlegen eines Projekts.",
    err_band_name_empty: "Bitte einen Bandnamen eingeben.",
    err_band_name: "Der Name ist als Ordnername nicht zulässig (keine Zeichen wie < > : \" / \\ | ? *, nicht mit Punkt oder Leerzeichen enden).",
    err_band_folder: "Der Band-Ordner konnte nicht angelegt werden: {detail}",
    confirm_import_folder: "Ein Ordner „{folder}“ ist bereits vorhanden, aber noch keine Band dazu.\n\nOrdner als Band übernehmen? Vorhandene Dateien und Ordner werden nicht verändert.",
    band_exists: "Die Band „{name}“ gibt es bereits – sie wurde ausgewählt.",
    band_exists_plain: "Die Band „{name}“ gibt es bereits.",
    band_created: "Band „{name}“ angelegt. Verzeichnis: {folder}",
    band_imported: "Band „{name}“ übernommen. Vorhandenes Verzeichnis: {folder} (nichts verändert).",
    band_prompt_warning: "Der Prompt-Ordner konnte nicht angelegt werden: {detail}",
    tab_media: "Medien & Releases",
    media_links: "Verlinkte Plattform-Medien",
    media_files: "Mediendateien",
    media_label: "Bezeichnung (optional)",
    media_add_link: "Link speichern",
    media_import_hint: "Dateien importieren, Audioanalyse und Medien-Explorer: in der Desktop-App.",
    media_no_links: "Noch keine Links gespeichert.",
    media_no_files: "Keine Mediendateien im Projektordner gefunden.",
    media_no_preview: "keine Vorschau im Browser",
    media_open: "In neuem Tab öffnen",
    media_link_added: "Link gespeichert.",
    release_title: "Releases",
    release_distributor: "Distributor",
    release_date: "Release-Datum (optional)",
    release_check: "Release-Checkliste prüfen (ohne Speichern)",
    release_save: "Release speichern / ISRC abgleichen",
    release_none: "Noch keine Veröffentlichungen.",
    release_platform_save: "Plattform speichern",
    release_platform_saved: "Plattform „{platform}“ gespeichert.",
    release_saved: "Release #{id} gespeichert.",
    err_invalid_url: "Bitte einen gültigen HTTP(S)-Link eingeben.",
    err_link_exists: "Dieser Link ist bereits gespeichert.",
    err_invalid_isrc: "Ungültige ISRC.",
    err_invalid_date: "Ungültiges Datum.",
    err_release_required: "Song und Distributor sind erforderlich.",
    err_media_unavailable: "Medienordner konnten nicht gelesen werden: {detail}",
    tab_conn: "KI-Verbindungen",
    conn_manual: "Auf diesem System kann MPW kein Fenster dafür öffnen. Bitte in einem Terminal ausführen:\n{command}",
    conn_copy_failed: "Kopieren in die Zwischenablage nicht möglich. Bitte diesen Text selbst kopieren:",
    suno_button: "An Suno senden (MCP) …",
    tab_ai: "AI Prompt Launcher",
    band: "Band",
    ai_target: "Ziel-Song / Projekt",
    ai_create_song: "Song-Eintrag anlegen",
    ai_platform: "KI-Plattform",
    ai_hardware: "Hardware für diesen Prompt",
    ai_hw_band: "Hardware des Bandprofils",
    ai_model: "API-Modell",
    ai_key: "API-Schlüssel (optional)",
    ai_cli_command: "CLI-Befehl",
    ai_cli_model: "CLI-Modell",
    ai_cli_model_hint: "leer = Standard der CLI",
    ai_cli_check: "CLI prüfen",
    ai_brief: "Songidee / Anweisung",
    ai_brief_hint: "Beispiel: British Blues trifft Industrial Folk Metal, Geschichte über …",
    ai_generate_api: "Prompt erstellen (API)",
    ai_generate_cli: "Prompt erstellen (CLI)",
    ai_copy_open: "Anfrage kopieren & Plattform öffnen",
    ai_import_file: "Antwort aus Datei",
    ai_paste: "Antwort aus dem Chat einfügen",
    ai_paste_hint: "Antwort der KI hier einfügen (STYLE- und LYRICS-Abschnitt oder JSON) …",
    ai_paste_apply: "In Style und Lyrics aufteilen",
    ai_style_hint: "Nur den Musikstil – ohne [STYLE]-Markierungen.",
    ai_lyrics_hint: "Songtext und Produktionsanweisungen – ohne [LYRICS]-Markierungen.",
    ai_save: "Als neue Version speichern",
    ai_save_hint: "Der aktive Song-Prompt bleibt unverändert; zusätzlich wird eine Textdatei im Prompt-Ordner der Band abgelegt.",
    ai_load_version: "In Style und Lyrics laden",
    ai_no_bands: "Noch keine Band vorhanden. Bitte zuerst im Reiter „Bands“ eine Band anlegen.",
    ai_no_projects: "Diese Band hat noch kein Song-Projekt. Projekte werden in der Desktop-App angelegt.",
    ai_no_song_entry: "kein Song-Eintrag",
    ai_key_env_found: "Leer lassen: Schlüssel aus {env} wird verwendet.",
    ai_key_env_missing: "Kein Schlüssel in {env} gefunden – Schlüssel eingeben (wird nur für diese Anfrage verwendet, nicht gespeichert).",
    ai_err_split: "Die KI-Antwort konnte nicht in Style und Lyrics aufgeteilt werden. Bitte eine Antwort mit STYLE- und LYRICS-Abschnitt (oder JSON) verwenden.",
    ai_err_key: "API-Schlüssel fehlt. Schlüssel eingeben oder die Umgebungsvariable {env} setzen.",
    ai_err_model: "Ungültiger Modellname.",
    ai_err_busy: "Es läuft bereits eine KI-Anfrage. Bitte warten, bis sie fertig ist.",
    ai_err_no_song: "Bitte einen Ziel-Song auswählen oder über „Song-Eintrag anlegen“ zuerst einen Song zum Projekt erstellen.",
    ai_err_job: "Die KI-Anfrage ist nicht mehr bekannt (wurde MPW im Browser neu gestartet?). Bitte erneut starten.",
    ai_err_empty: "Style und Lyrics dürfen nicht leer sein.",
    ai_err_prompt: "Die Anfrage konnte nicht erstellt werden: {detail}",
    ai_err_file_size: "Die Importdatei darf maximal 2 MB groß sein.",
    ai_running_api: "API-Anfrage läuft … {s} s",
    ai_running_cli: "CLI-Anfrage läuft … {s} s (kann einige Minuten dauern)",
    ai_received: "Antwort empfangen. Bitte prüfen; gespeichert wird erst mit „Als neue Version speichern“.",
    ai_cli_found: "{provider}-CLI gefunden: {path}\nFalls noch nicht geschehen, die CLI einmal in einem Terminal starten und anmelden.",
    ai_copy_failed: "Die Anfrage konnte nicht in die Zwischenablage kopiert werden.",
    ai_copied: "Anfrage kopiert und {url} geöffnet. Dort mit Strg+V einfügen; die Antwort anschließend unten einfügen oder als Datei importieren.",
    ai_copied_no_window: "Anfrage kopiert. Der Browser hat das neue Fenster blockiert – bitte {url} selbst öffnen und mit Strg+V einfügen.",
    ai_imported: "Antwort übernommen (Quelle: {source}). Bitte prüfen und dann als Version speichern.",
    ai_source_paste: "eingefügter Text",
    ai_confirm_replace: "Style und Lyrics enthalten bereits Text. Durch den neuen Inhalt ersetzen?",
    ai_saved: "Version #{id} gespeichert und als Textdatei archiviert:\n{file}\nDer aktive Song-Prompt bleibt unverändert.",
    ai_saved_no_file: "Version #{id} wurde gespeichert, aber die Textdatei konnte nicht erstellt werden: {detail}",
    ai_confirm_song: "Für das Projekt „{project}“ einen Song-Eintrag anlegen?\n\nEs werden keine Dateien verändert.",
    ai_song_created: "Der Ziel-Song „{project}“ wurde dem Projekt zugeordnet.",
    ai_version_loaded: "Version #{id} in Style und Lyrics geladen. Noch nicht gespeichert.",
  },
  en: {
    app_sub: 'in the browser', tab_songs: 'Songs & Suno', tab_bands: 'Bands', all_bands: 'All Bands',
    search_placeholder: 'Search songs…', songs_count: '{n} Songs', no_song: 'Please select a song on the left.',
    status: 'Status', distributor: 'Distributor', platforms: 'Platforms', style: 'Style', lyrics: 'Lyrics',
    save: 'Save song', revert: 'Discard changes', unsaved: 'Unsaved changes',
    saved: 'Song saved.', saved_archived: 'Song saved. The previous prompt was kept in the version history.',
    conflict: 'The song was changed meanwhile (e.g. in the desktop app). Your input was not saved.\n“Discard changes” loads the current version.',
    too_long: 'Style max. 1,000, lyrics max. 5,000 characters.', error: 'Error: {detail}',
    connection: 'No connection to MPW-Web. Is the MPW-Web window still open?',
    token: 'Access denied. Please restart MPW-Web and open the address it shows.',
    versions: 'Saved prompt versions', no_versions: 'No saved versions yet.',
    version_load: 'Load into editor', version_load_hint: 'It is only saved with “Save song”.',
    version_loaded: 'Version #{id} loaded into the editor – not saved yet.',
    confirm_discard: 'Discard unsaved changes?', no_band: 'Please select a band on the left.',
    genres: 'Genres', persona: 'Persona', hardware: 'Instruments / Hardware', group: 'Group', projects: 'Songs/Projects',
    none: '–', bands_readonly: 'Bands are view-only in this stage; edit them in the desktop app.',
    no_projects: 'No songs/projects.', footer: 'Local on this PC · same data as the installed MPW',
    chars: '{n}/{max}', st_0: 'In Progress', st_1: 'Completed', st_2: 'Published',
    genre_main: "Primary genre",
    genre_second: "Secondary genre",
    band_save: "Save band profile",
    band_name_hint: "The band name is changed in the desktop app (the band folder depends on it).",
    band_saved: "Band profile saved.",
    hw_add: "Add instrument",
    hw_save: "Save change",
    cancel: "Cancel",
    edit: "Edit",
    delete: "Delete",
    confirm_delete_hw: "Delete this hardware entry?\n{entry}",
    no_hardware: "No instruments / hardware yet.",
    presets: "Hardware presets",
    no_presets: "No presets saved.",
    preset_add: "Add preset to band",
    preset_replace: "Apply preset to band (replace)",
    preset_save: "Save band hardware as preset",
    preset_name_prompt: "Name of the studio setup:",
    preset_overwrite: "Preset “{name}” already exists. Overwrite it?",
    preset_saved: "Preset with {count} entries saved.",
    preset_added: "{added} entries added, {skipped} already existed.",
    confirm_replace: "Apply preset “{name}” to “{band}”?\n\nThe band’s existing hardware will be REPLACED.",
    preset_replaced: "Hardware replaced: {added} entries from the preset.",
    err_empty_field: "Group and instrument / hardware must not be empty.",
    err_too_long: "Input is too long.",
    err_no_hardware: "This band has no hardware entries yet.",
    err_preset_damaged: "The preset is damaged and cannot be used.",
    err_missing: "The entry no longer exists. Please reload.",
    band_new: "+ New band",
    band_new_title: "Create new band",
    band_name: "Band name",
    band_create: "Create band",
    band_new_hint: "Creates the band folder and the prompt folder. Project subfolders are created only when a project is added.",
    err_band_name_empty: "Please enter a band name.",
    err_band_name: "This name is not allowed as a folder name (no characters like < > : \" / \\ | ? *, must not end with a dot or space).",
    err_band_folder: "The band folder could not be created: {detail}",
    confirm_import_folder: "A folder “{folder}” already exists, but there is no band for it yet.\n\nTake the folder over as a band? Existing files and folders are not changed.",
    band_exists: "The band “{name}” already exists – it has been selected.",
    band_exists_plain: "The band “{name}” already exists.",
    band_created: "Band “{name}” created. Directory: {folder}",
    band_imported: "Band “{name}” imported. Existing directory: {folder} (nothing changed).",
    band_prompt_warning: "The prompt folder could not be created: {detail}",
    tab_media: "Media & Releases",
    media_links: "Linked platform media",
    media_files: "Media files",
    media_label: "Label (optional)",
    media_add_link: "Save link",
    media_import_hint: "Importing files, audio analysis and media explorer: in the desktop app.",
    media_no_links: "No links saved yet.",
    media_no_files: "No media files found in the project folder.",
    media_no_preview: "no preview in the browser",
    media_open: "Open in new tab",
    media_link_added: "Link saved.",
    release_title: "Releases",
    release_distributor: "Distributor",
    release_date: "Release date (optional)",
    release_check: "Check release checklist (without saving)",
    release_save: "Save release / match ISRC",
    release_none: "No releases yet.",
    release_platform_save: "Save platform",
    release_platform_saved: "Platform “{platform}” saved.",
    release_saved: "Release #{id} saved.",
    err_invalid_url: "Please enter a valid HTTP(S) link.",
    err_link_exists: "This link is already saved.",
    err_invalid_isrc: "Invalid ISRC.",
    err_invalid_date: "Invalid date.",
    err_release_required: "Song and distributor are required.",
    err_media_unavailable: "Media folders could not be read: {detail}",
    tab_conn: "AI connections",
    conn_manual: "MPW cannot open a window for this on this system. Please run in a terminal:\n{command}",
    conn_copy_failed: "Copying to the clipboard is not possible. Please copy this text yourself:",
    suno_button: "Send to Suno (MCP) …",
    tab_ai: "AI Prompt Launcher",
    band: "Band",
    ai_target: "Target song / project",
    ai_create_song: "Create song entry",
    ai_platform: "AI platform",
    ai_hardware: "Hardware for this prompt",
    ai_hw_band: "Band profile hardware",
    ai_model: "API model",
    ai_key: "API key (optional)",
    ai_cli_command: "CLI command",
    ai_cli_model: "CLI model",
    ai_cli_model_hint: "empty = CLI default",
    ai_cli_check: "Check CLI",
    ai_brief: "Song idea / instruction",
    ai_brief_hint: "Example: British blues meets industrial folk metal, a story about …",
    ai_generate_api: "Create prompt (API)",
    ai_generate_cli: "Create prompt (CLI)",
    ai_copy_open: "Copy request & open platform",
    ai_import_file: "Answer from file",
    ai_paste: "Paste answer from the chat",
    ai_paste_hint: "Paste the AI answer here (STYLE and LYRICS sections or JSON) …",
    ai_paste_apply: "Split into style and lyrics",
    ai_style_hint: "Music style only – without [STYLE] markers.",
    ai_lyrics_hint: "Lyrics and production notes – without [LYRICS] markers.",
    ai_save: "Save as new version",
    ai_save_hint: "The active song prompt stays unchanged; a text file is also stored in the band’s prompt folder.",
    ai_load_version: "Load into style and lyrics",
    ai_no_bands: "No band yet. Please create a band in the “Bands” tab first.",
    ai_no_projects: "This band has no song project yet. Projects are created in the desktop app.",
    ai_no_song_entry: "no song entry",
    ai_key_env_found: "Leave empty: the key from {env} is used.",
    ai_key_env_missing: "No key found in {env} – enter a key (used for this request only, never stored).",
    ai_err_split: "The AI answer could not be split into style and lyrics. Please use an answer with STYLE and LYRICS sections (or JSON).",
    ai_err_key: "API key missing. Enter a key or set the environment variable {env}.",
    ai_err_model: "Invalid model name.",
    ai_err_busy: "An AI request is already running. Please wait until it has finished.",
    ai_err_no_song: "Please choose a target song, or first create a song for the project with “Create song entry”.",
    ai_err_job: "The AI request is no longer known (was MPW in the browser restarted?). Please start it again.",
    ai_err_empty: "Style and lyrics must not be empty.",
    ai_err_prompt: "The request could not be created: {detail}",
    ai_err_file_size: "The import file must not be larger than 2 MB.",
    ai_running_api: "API request running … {s} s",
    ai_running_cli: "CLI request running … {s} s (may take a few minutes)",
    ai_received: "Answer received. Please review; it is saved only with “Save as new version”.",
    ai_cli_found: "{provider} CLI found: {path}\nIf not done yet, start the CLI once in a terminal and sign in.",
    ai_copy_failed: "The request could not be copied to the clipboard.",
    ai_copied: "Request copied and {url} opened. Paste it there with Ctrl+V; then paste the answer below or import it as a file.",
    ai_copied_no_window: "Request copied. The browser blocked the new window – please open {url} yourself and paste with Ctrl+V.",
    ai_imported: "Answer applied (source: {source}). Please review, then save it as a version.",
    ai_source_paste: "pasted text",
    ai_confirm_replace: "Style and lyrics already contain text. Replace it with the new content?",
    ai_saved: "Version #{id} saved and archived as a text file:\n{file}\nThe active song prompt stays unchanged.",
    ai_saved_no_file: "Version #{id} was saved, but the text file could not be created: {detail}",
    ai_confirm_song: "Create a song entry for the project “{project}”?\n\nNo files are changed.",
    ai_song_created: "The target song “{project}” was assigned to the project.",
    ai_version_loaded: "Version #{id} loaded into style and lyrics. Not saved yet.",
  },
  fr: {
    app_sub: 'dans le navigateur', tab_songs: 'Songs & Suno', tab_bands: 'Groupes', all_bands: 'Tous les groupes',
    search_placeholder: 'Rechercher des titres…', songs_count: '{n} titres', no_song: 'Sélectionnez un morceau à gauche.',
    status: 'Statut', distributor: 'Distributeur', platforms: 'Plateformes', style: 'Style', lyrics: 'Paroles',
    save: 'Enregistrer le morceau', revert: 'Annuler les modifications', unsaved: 'Modifications non enregistrées',
    saved: 'Morceau enregistré.', saved_archived: 'Morceau enregistré. Le prompt précédent a été conservé dans l’historique.',
    conflict: 'Le morceau a été modifié entre-temps (p. ex. dans l’application de bureau). Vos saisies n’ont pas été enregistrées.\n« Annuler les modifications » charge la version actuelle.',
    too_long: 'Style 1 000 caractères max., paroles 5 000 max.', error: 'Erreur : {detail}',
    connection: 'Pas de connexion à MPW-Web. La fenêtre MPW-Web est-elle encore ouverte ?',
    token: 'Accès refusé. Redémarrez MPW-Web et ouvrez l’adresse affichée.',
    versions: 'Versions de prompt enregistrées', no_versions: 'Aucune version enregistrée.',
    version_load: 'Charger dans l’éditeur', version_load_hint: 'L’enregistrement se fait avec « Enregistrer le morceau ».',
    version_loaded: 'Version n° {id} chargée dans l’éditeur – pas encore enregistrée.',
    confirm_discard: 'Abandonner les modifications non enregistrées ?', no_band: 'Sélectionnez un groupe à gauche.',
    genres: 'Genres', persona: 'Persona', hardware: 'Instruments / Matériel', group: 'Catégorie', projects: 'Titres/Projets',
    none: '–', bands_readonly: 'Les groupes sont en lecture seule à cette étape ; modifiez-les dans l’application de bureau.',
    no_projects: 'Aucun titre/projet.', footer: 'En local sur ce PC · mêmes données que MPW installé',
    chars: '{n}/{max}', st_0: 'En cours', st_1: 'Terminé', st_2: 'Publié',
    genre_main: "Genre principal",
    genre_second: "Genre secondaire",
    band_save: "Enregistrer le profil",
    band_name_hint: "Le nom du groupe se modifie dans l’application de bureau (le dossier du groupe en dépend).",
    band_saved: "Profil du groupe enregistré.",
    hw_add: "Ajouter un instrument",
    hw_save: "Enregistrer la modification",
    cancel: "Annuler",
    edit: "Modifier",
    delete: "Supprimer",
    confirm_delete_hw: "Supprimer cet équipement ?\n{entry}",
    no_hardware: "Aucun instrument / matériel.",
    presets: "Préréglages de matériel",
    no_presets: "Aucun préréglage enregistré.",
    preset_add: "Ajouter le préréglage au groupe",
    preset_replace: "Appliquer au groupe (remplacer)",
    preset_save: "Enregistrer le matériel comme préréglage",
    preset_name_prompt: "Nom de la configuration studio :",
    preset_overwrite: "Le préréglage « {name} » existe déjà. Le remplacer ?",
    preset_saved: "Préréglage de {count} éléments enregistré.",
    preset_added: "{added} éléments ajoutés, {skipped} existaient déjà.",
    confirm_replace: "Appliquer le préréglage « {name} » à « {band} » ?\n\nLe matériel existant du groupe sera REMPLACÉ.",
    preset_replaced: "Matériel remplacé : {added} éléments du préréglage.",
    err_empty_field: "Catégorie et instrument / matériel ne doivent pas être vides.",
    err_too_long: "Saisie trop longue.",
    err_no_hardware: "Ce groupe n’a pas encore de matériel.",
    err_preset_damaged: "Le préréglage est endommagé et inutilisable.",
    err_missing: "L’élément n’existe plus. Veuillez recharger.",
    band_new: "+ Nouveau groupe",
    band_new_title: "Créer un groupe",
    band_name: "Nom du groupe",
    band_create: "Créer le groupe",
    band_new_hint: "Crée le dossier du groupe et le dossier des prompts. Les sous-dossiers de projet sont créés lors de la création d’un projet.",
    err_band_name_empty: "Veuillez saisir un nom de groupe.",
    err_band_name: "Ce nom n’est pas autorisé comme nom de dossier (pas de caractères < > : \" / \\ | ? *, ni de point ou d’espace final).",
    err_band_folder: "Le dossier du groupe n’a pas pu être créé : {detail}",
    confirm_import_folder: "Un dossier « {folder} » existe déjà, mais aucun groupe ne lui correspond.\n\nReprendre ce dossier comme groupe ? Les fichiers et dossiers existants ne sont pas modifiés.",
    band_exists: "Le groupe « {name} » existe déjà – il a été sélectionné.",
    band_exists_plain: "Le groupe « {name} » existe déjà.",
    band_created: "Groupe « {name} » créé. Dossier : {folder}",
    band_imported: "Groupe « {name} » importé. Dossier existant : {folder} (rien modifié).",
    band_prompt_warning: "Le dossier des prompts n’a pas pu être créé : {detail}",
    tab_media: "Médias & sorties",
    media_links: "Médias de plateforme liés",
    media_files: "Fichiers médias",
    media_label: "Libellé (facultatif)",
    media_add_link: "Enregistrer le lien",
    media_import_hint: "Import de fichiers, analyse audio et explorateur de médias : dans l’application de bureau.",
    media_no_links: "Aucun lien enregistré.",
    media_no_files: "Aucun fichier média dans le dossier du projet.",
    media_no_preview: "pas d’aperçu dans le navigateur",
    media_open: "Ouvrir dans un nouvel onglet",
    media_link_added: "Lien enregistré.",
    release_title: "Sorties",
    release_distributor: "Distributeur",
    release_date: "Date de sortie (facultative)",
    release_check: "Vérifier la liste de contrôle (sans enregistrer)",
    release_save: "Enregistrer la sortie / comparer l’ISRC",
    release_none: "Aucune sortie.",
    release_platform_save: "Enregistrer la plateforme",
    release_platform_saved: "Plateforme « {platform} » enregistrée.",
    release_saved: "Sortie n°{id} enregistrée.",
    err_invalid_url: "Saisissez un lien HTTP(S) valide.",
    err_link_exists: "Ce lien est déjà enregistré.",
    err_invalid_isrc: "ISRC invalide.",
    err_invalid_date: "Date invalide.",
    err_release_required: "Le titre et le distributeur sont obligatoires.",
    err_media_unavailable: "Impossible de lire les dossiers médias : {detail}",
    tab_conn: "Connexions IA",
    conn_manual: "Sur ce système, MPW ne peut pas ouvrir de fenêtre pour cela. Exécutez dans un terminal :\n{command}",
    conn_copy_failed: "Impossible de copier dans le presse-papiers. Copiez ce texte vous-même :",
    suno_button: "Envoyer à Suno (MCP) …",
    tab_ai: "AI Prompt Launcher",
    band: "Groupe",
    ai_target: "Chanson / projet cible",
    ai_create_song: "Créer l’entrée de chanson",
    ai_platform: "Plateforme IA",
    ai_hardware: "Matériel pour ce prompt",
    ai_hw_band: "Matériel du profil du groupe",
    ai_model: "Modèle API",
    ai_key: "Clé API (facultative)",
    ai_cli_command: "Commande CLI",
    ai_cli_model: "Modèle CLI",
    ai_cli_model_hint: "vide = valeur par défaut de la CLI",
    ai_cli_check: "Vérifier la CLI",
    ai_brief: "Idée de chanson / consigne",
    ai_brief_hint: "Exemple : blues britannique et folk metal industriel, une histoire sur …",
    ai_generate_api: "Créer le prompt (API)",
    ai_generate_cli: "Créer le prompt (CLI)",
    ai_copy_open: "Copier la demande et ouvrir la plateforme",
    ai_import_file: "Réponse depuis un fichier",
    ai_paste: "Coller la réponse du chat",
    ai_paste_hint: "Collez ici la réponse de l’IA (sections STYLE et LYRICS ou JSON) …",
    ai_paste_apply: "Répartir en style et paroles",
    ai_style_hint: "Uniquement le style musical – sans balises [STYLE].",
    ai_lyrics_hint: "Paroles et consignes de production – sans balises [LYRICS].",
    ai_save: "Enregistrer comme nouvelle version",
    ai_save_hint: "Le prompt actif de la chanson reste inchangé ; un fichier texte est aussi enregistré dans le dossier des prompts du groupe.",
    ai_load_version: "Charger dans style et paroles",
    ai_no_bands: "Aucun groupe. Créez d’abord un groupe dans l’onglet « Bands ».",
    ai_no_projects: "Ce groupe n’a pas encore de projet de chanson. Les projets se créent dans l’application de bureau.",
    ai_no_song_entry: "pas d’entrée de chanson",
    ai_key_env_found: "Laisser vide : la clé de {env} est utilisée.",
    ai_key_env_missing: "Aucune clé trouvée dans {env} – saisissez une clé (utilisée pour cette demande uniquement, jamais enregistrée).",
    ai_err_split: "La réponse de l’IA n’a pas pu être répartie en style et paroles. Utilisez une réponse avec sections STYLE et LYRICS (ou JSON).",
    ai_err_key: "Clé API manquante. Saisissez une clé ou définissez la variable d’environnement {env}.",
    ai_err_model: "Nom de modèle non valide.",
    ai_err_busy: "Une demande IA est déjà en cours. Veuillez attendre qu’elle se termine.",
    ai_err_no_song: "Choisissez une chanson cible ou créez d’abord une chanson pour le projet avec « Créer l’entrée de chanson ».",
    ai_err_job: "La demande IA n’est plus connue (MPW dans le navigateur a-t-il été redémarré ?). Veuillez la relancer.",
    ai_err_empty: "Le style et les paroles ne doivent pas être vides.",
    ai_err_prompt: "La demande n’a pas pu être créée : {detail}",
    ai_err_file_size: "Le fichier d’import ne doit pas dépasser 2 Mo.",
    ai_running_api: "Demande API en cours … {s} s",
    ai_running_cli: "Demande CLI en cours … {s} s (peut prendre quelques minutes)",
    ai_received: "Réponse reçue. Vérifiez-la ; elle n’est enregistrée qu’avec « Enregistrer comme nouvelle version ».",
    ai_cli_found: "CLI {provider} trouvée : {path}\nSi ce n’est pas encore fait, lancez la CLI une fois dans un terminal et connectez-vous.",
    ai_copy_failed: "La demande n’a pas pu être copiée dans le presse-papiers.",
    ai_copied: "Demande copiée et {url} ouvert. Collez-la avec Ctrl+V ; collez ensuite la réponse ci-dessous ou importez-la comme fichier.",
    ai_copied_no_window: "Demande copiée. Le navigateur a bloqué la nouvelle fenêtre – ouvrez {url} vous-même et collez avec Ctrl+V.",
    ai_imported: "Réponse reprise (source : {source}). Vérifiez-la, puis enregistrez-la comme version.",
    ai_source_paste: "texte collé",
    ai_confirm_replace: "Le style et les paroles contiennent déjà du texte. Le remplacer par le nouveau contenu ?",
    ai_saved: "Version #{id} enregistrée et archivée comme fichier texte :\n{file}\nLe prompt actif de la chanson reste inchangé.",
    ai_saved_no_file: "La version #{id} a été enregistrée, mais le fichier texte n’a pas pu être créé : {detail}",
    ai_confirm_song: "Créer une entrée de chanson pour le projet « {project} » ?\n\nAucun fichier n’est modifié.",
    ai_song_created: "La chanson cible « {project} » a été associée au projet.",
    ai_version_loaded: "Version #{id} chargée dans style et paroles. Pas encore enregistrée.",
  },
  es: {
    app_sub: 'en el navegador', tab_songs: 'Songs & Suno', tab_bands: 'Bandas', all_bands: 'Todas las bandas',
    search_placeholder: 'Buscar canciones…', songs_count: '{n} canciones', no_song: 'Seleccione una canción a la izquierda.',
    status: 'Estado', distributor: 'Distribuidor', platforms: 'Plataformas', style: 'Style', lyrics: 'Letra',
    save: 'Guardar canción', revert: 'Descartar cambios', unsaved: 'Cambios sin guardar',
    saved: 'Canción guardada.', saved_archived: 'Canción guardada. El prompt anterior se conservó en el historial.',
    conflict: 'La canción se modificó entretanto (p. ej. en la aplicación de escritorio). Sus datos no se guardaron.\n«Descartar cambios» carga la versión actual.',
    too_long: 'Style máx. 1.000, letra máx. 5.000 caracteres.', error: 'Error: {detail}',
    connection: 'Sin conexión con MPW-Web. ¿Sigue abierta la ventana de MPW-Web?',
    token: 'Acceso denegado. Reinicie MPW-Web y abra la dirección que muestra.',
    versions: 'Versiones de prompt guardadas', no_versions: 'Aún no hay versiones guardadas.',
    version_load: 'Cargar en el editor', version_load_hint: 'Se guarda solo con «Guardar canción».',
    version_loaded: 'Versión n.º {id} cargada en el editor; aún no guardada.',
    confirm_discard: '¿Descartar los cambios sin guardar?', no_band: 'Seleccione una banda a la izquierda.',
    genres: 'Géneros', persona: 'Persona', hardware: 'Instrumentos / Equipo', group: 'Grupo', projects: 'Canciones/Proyectos',
    none: '–', bands_readonly: 'En esta etapa las bandas solo se muestran; edítelas en la aplicación de escritorio.',
    no_projects: 'Sin canciones/proyectos.', footer: 'Local en este PC · los mismos datos que MPW instalado',
    chars: '{n}/{max}', st_0: 'En progreso', st_1: 'Terminado', st_2: 'Publicado',
    genre_main: "Género principal",
    genre_second: "Género secundario",
    band_save: "Guardar perfil",
    band_name_hint: "El nombre de la banda se cambia en la aplicación de escritorio (de él depende la carpeta).",
    band_saved: "Perfil de la banda guardado.",
    hw_add: "Añadir instrumento",
    hw_save: "Guardar cambio",
    cancel: "Cancelar",
    edit: "Editar",
    delete: "Eliminar",
    confirm_delete_hw: "¿Eliminar este equipo?\n{entry}",
    no_hardware: "Aún no hay instrumentos / equipo.",
    presets: "Ajustes de equipo",
    no_presets: "No hay ajustes guardados.",
    preset_add: "Añadir ajuste a la banda",
    preset_replace: "Aplicar ajuste a la banda (reemplazar)",
    preset_save: "Guardar equipo como ajuste",
    preset_name_prompt: "Nombre de la configuración de estudio:",
    preset_overwrite: "El ajuste «{name}» ya existe. ¿Sobrescribirlo?",
    preset_saved: "Ajuste con {count} elementos guardado.",
    preset_added: "{added} elementos añadidos, {skipped} ya existían.",
    confirm_replace: "¿Aplicar el ajuste «{name}» a «{band}»?\n\nSe REEMPLAZARÁ el equipo existente de la banda.",
    preset_replaced: "Equipo reemplazado: {added} elementos del ajuste.",
    err_empty_field: "Grupo e instrumento / equipo no pueden estar vacíos.",
    err_too_long: "La entrada es demasiado larga.",
    err_no_hardware: "Esta banda aún no tiene equipo.",
    err_preset_damaged: "El ajuste está dañado y no se puede usar.",
    err_missing: "La entrada ya no existe. Vuelva a cargar.",
    band_new: "+ Nueva banda",
    band_new_title: "Crear banda",
    band_name: "Nombre de la banda",
    band_create: "Crear banda",
    band_new_hint: "Crea la carpeta de la banda y la carpeta de prompts. Las subcarpetas se crean al añadir un proyecto.",
    err_band_name_empty: "Introduzca un nombre de banda.",
    err_band_name: "El nombre no es válido como nombre de carpeta (sin caracteres como < > : \" / \\ | ? *, sin punto ni espacio final).",
    err_band_folder: "No se pudo crear la carpeta de la banda: {detail}",
    confirm_import_folder: "Ya existe una carpeta «{folder}», pero aún no hay banda para ella.\n\n¿Usar la carpeta como banda? Los archivos y carpetas existentes no se modifican.",
    band_exists: "La banda «{name}» ya existe; se ha seleccionado.",
    band_exists_plain: "La banda «{name}» ya existe.",
    band_created: "Banda «{name}» creada. Carpeta: {folder}",
    band_imported: "Banda «{name}» importada. Carpeta existente: {folder} (sin cambios).",
    band_prompt_warning: "No se pudo crear la carpeta de prompts: {detail}",
    tab_media: "Medios y lanzamientos",
    media_links: "Medios de plataforma enlazados",
    media_files: "Archivos multimedia",
    media_label: "Etiqueta (opcional)",
    media_add_link: "Guardar enlace",
    media_import_hint: "Importar archivos, análisis de audio y explorador de medios: en la aplicación de escritorio.",
    media_no_links: "Aún no hay enlaces guardados.",
    media_no_files: "No hay archivos multimedia en la carpeta del proyecto.",
    media_no_preview: "sin vista previa en el navegador",
    media_open: "Abrir en una pestaña nueva",
    media_link_added: "Enlace guardado.",
    release_title: "Lanzamientos",
    release_distributor: "Distribuidor",
    release_date: "Fecha de lanzamiento (opcional)",
    release_check: "Comprobar lista de lanzamiento (sin guardar)",
    release_save: "Guardar lanzamiento / comparar ISRC",
    release_none: "Aún no hay lanzamientos.",
    release_platform_save: "Guardar plataforma",
    release_platform_saved: "Plataforma «{platform}» guardada.",
    release_saved: "Lanzamiento #{id} guardado.",
    err_invalid_url: "Introduzca un enlace HTTP(S) válido.",
    err_link_exists: "Este enlace ya está guardado.",
    err_invalid_isrc: "ISRC no válido.",
    err_invalid_date: "Fecha no válida.",
    err_release_required: "La canción y el distribuidor son obligatorios.",
    err_media_unavailable: "No se pudieron leer las carpetas multimedia: {detail}",
    tab_conn: "Conexiones de IA",
    conn_manual: "En este sistema MPW no puede abrir una ventana para esto. Ejecute en un terminal:\n{command}",
    conn_copy_failed: "No se puede copiar al portapapeles. Copie usted mismo este texto:",
    suno_button: "Enviar a Suno (MCP) …",
    tab_ai: "AI Prompt Launcher",
    band: "Banda",
    ai_target: "Canción / proyecto de destino",
    ai_create_song: "Crear entrada de canción",
    ai_platform: "Plataforma de IA",
    ai_hardware: "Equipo para este prompt",
    ai_hw_band: "Equipo del perfil de la banda",
    ai_model: "Modelo API",
    ai_key: "Clave API (opcional)",
    ai_cli_command: "Comando CLI",
    ai_cli_model: "Modelo CLI",
    ai_cli_model_hint: "vacío = predeterminado de la CLI",
    ai_cli_check: "Comprobar CLI",
    ai_brief: "Idea de canción / instrucción",
    ai_brief_hint: "Ejemplo: blues británico con folk metal industrial, una historia sobre …",
    ai_generate_api: "Crear prompt (API)",
    ai_generate_cli: "Crear prompt (CLI)",
    ai_copy_open: "Copiar solicitud y abrir plataforma",
    ai_import_file: "Respuesta desde archivo",
    ai_paste: "Pegar respuesta del chat",
    ai_paste_hint: "Pegue aquí la respuesta de la IA (secciones STYLE y LYRICS o JSON) …",
    ai_paste_apply: "Dividir en estilo y letra",
    ai_style_hint: "Solo el estilo musical, sin marcas [STYLE].",
    ai_lyrics_hint: "Letra e indicaciones de producción, sin marcas [LYRICS].",
    ai_save: "Guardar como nueva versión",
    ai_save_hint: "El prompt activo de la canción no cambia; además se guarda un archivo de texto en la carpeta de prompts de la banda.",
    ai_load_version: "Cargar en estilo y letra",
    ai_no_bands: "Aún no hay ninguna banda. Cree primero una banda en la pestaña «Bands».",
    ai_no_projects: "Esta banda aún no tiene proyectos de canción. Los proyectos se crean en la aplicación de escritorio.",
    ai_no_song_entry: "sin entrada de canción",
    ai_key_env_found: "Dejar vacío: se usa la clave de {env}.",
    ai_key_env_missing: "No se encontró clave en {env}; introduzca una clave (solo para esta solicitud, no se guarda).",
    ai_err_split: "La respuesta de la IA no se pudo dividir en estilo y letra. Use una respuesta con secciones STYLE y LYRICS (o JSON).",
    ai_err_key: "Falta la clave API. Introduzca una clave o defina la variable de entorno {env}.",
    ai_err_model: "Nombre de modelo no válido.",
    ai_err_busy: "Ya hay una solicitud de IA en curso. Espere a que termine.",
    ai_err_no_song: "Elija una canción de destino o cree primero una canción para el proyecto con «Crear entrada de canción».",
    ai_err_job: "La solicitud de IA ya no se conoce (¿se reinició MPW en el navegador?). Iníciela de nuevo.",
    ai_err_empty: "El estilo y la letra no pueden estar vacíos.",
    ai_err_prompt: "No se pudo crear la solicitud: {detail}",
    ai_err_file_size: "El archivo de importación no puede superar 2 MB.",
    ai_running_api: "Solicitud API en curso … {s} s",
    ai_running_cli: "Solicitud CLI en curso … {s} s (puede tardar unos minutos)",
    ai_received: "Respuesta recibida. Revísela; solo se guarda con «Guardar como nueva versión».",
    ai_cli_found: "CLI de {provider} encontrada: {path}\nSi aún no lo ha hecho, inicie la CLI una vez en un terminal e inicie sesión.",
    ai_copy_failed: "No se pudo copiar la solicitud al portapapeles.",
    ai_copied: "Solicitud copiada y {url} abierto. Péguela allí con Ctrl+V; después pegue la respuesta abajo o impórtela como archivo.",
    ai_copied_no_window: "Solicitud copiada. El navegador bloqueó la nueva ventana; abra {url} usted mismo y pegue con Ctrl+V.",
    ai_imported: "Respuesta aplicada (origen: {source}). Revísela y guárdela como versión.",
    ai_source_paste: "texto pegado",
    ai_confirm_replace: "El estilo y la letra ya contienen texto. ¿Reemplazarlo por el nuevo contenido?",
    ai_saved: "Versión #{id} guardada y archivada como archivo de texto:\n{file}\nEl prompt activo de la canción no cambia.",
    ai_saved_no_file: "La versión #{id} se guardó, pero no se pudo crear el archivo de texto: {detail}",
    ai_confirm_song: "¿Crear una entrada de canción para el proyecto «{project}»?\n\nNo se modifica ningún archivo.",
    ai_song_created: "La canción de destino «{project}» se asignó al proyecto.",
    ai_version_loaded: "Versión #{id} cargada en estilo y letra. Aún no se ha guardado.",
  },
  it: {
    app_sub: 'nel browser', tab_songs: 'Songs & Suno', tab_bands: 'Band', all_bands: 'Tutte le band',
    search_placeholder: 'Cerca brani…', songs_count: '{n} brani', no_song: 'Seleziona un brano a sinistra.',
    status: 'Stato', distributor: 'Distributore', platforms: 'Piattaforme', style: 'Style', lyrics: 'Testo',
    save: 'Salva brano', revert: 'Annulla modifiche', unsaved: 'Modifiche non salvate',
    saved: 'Brano salvato.', saved_archived: 'Brano salvato. Il prompt precedente è stato conservato nella cronologia.',
    conflict: 'Il brano è stato modificato nel frattempo (ad es. nell’app desktop). I tuoi dati non sono stati salvati.\n«Annulla modifiche» carica la versione attuale.',
    too_long: 'Style max 1.000, testo max 5.000 caratteri.', error: 'Errore: {detail}',
    connection: 'Nessuna connessione a MPW-Web. La finestra di MPW-Web è ancora aperta?',
    token: 'Accesso negato. Riavvia MPW-Web e apri l’indirizzo indicato.',
    versions: 'Versioni dei prompt salvate', no_versions: 'Nessuna versione salvata.',
    version_load: 'Carica nell’editor', version_load_hint: 'Viene salvato solo con «Salva brano».',
    version_loaded: 'Versione n. {id} caricata nell’editor – non ancora salvata.',
    confirm_discard: 'Scartare le modifiche non salvate?', no_band: 'Seleziona una band a sinistra.',
    genres: 'Generi', persona: 'Persona', hardware: 'Strumenti / Hardware', group: 'Gruppo', projects: 'Brani/Progetti',
    none: '–', bands_readonly: 'In questa fase le band sono solo visualizzate; modificale nell’app desktop.',
    no_projects: 'Nessun brano/progetto.', footer: 'In locale su questo PC · stessi dati di MPW installato',
    chars: '{n}/{max}', st_0: 'In corso', st_1: 'Completato', st_2: 'Pubblicato',
    genre_main: "Genere principale",
    genre_second: "Genere secondario",
    band_save: "Salva profilo",
    band_name_hint: "Il nome del gruppo si cambia nell’app desktop (da esso dipende la cartella).",
    band_saved: "Profilo del gruppo salvato.",
    hw_add: "Aggiungi strumento",
    hw_save: "Salva modifica",
    cancel: "Annulla",
    edit: "Modifica",
    delete: "Elimina",
    confirm_delete_hw: "Eliminare questo elemento hardware?\n{entry}",
    no_hardware: "Nessuno strumento / hardware.",
    presets: "Preset hardware",
    no_presets: "Nessun preset salvato.",
    preset_add: "Aggiungi preset al gruppo",
    preset_replace: "Applica preset al gruppo (sostituisci)",
    preset_save: "Salva hardware come preset",
    preset_name_prompt: "Nome della configurazione studio:",
    preset_overwrite: "Il preset «{name}» esiste già. Sovrascriverlo?",
    preset_saved: "Preset con {count} elementi salvato.",
    preset_added: "{added} elementi aggiunti, {skipped} esistevano già.",
    confirm_replace: "Applicare il preset «{name}» a «{band}»?\n\nL’hardware esistente del gruppo verrà SOSTITUITO.",
    preset_replaced: "Hardware sostituito: {added} elementi dal preset.",
    err_empty_field: "Gruppo e strumento / hardware non possono essere vuoti.",
    err_too_long: "Testo troppo lungo.",
    err_no_hardware: "Questo gruppo non ha ancora hardware.",
    err_preset_damaged: "Il preset è danneggiato e non può essere usato.",
    err_missing: "L’elemento non esiste più. Ricarica.",
    band_new: "+ Nuovo gruppo",
    band_new_title: "Crea gruppo",
    band_name: "Nome del gruppo",
    band_create: "Crea gruppo",
    band_new_hint: "Crea la cartella del gruppo e la cartella dei prompt. Le sottocartelle vengono create quando si aggiunge un progetto.",
    err_band_name_empty: "Inserisci il nome del gruppo.",
    err_band_name: "Il nome non è valido come nome di cartella (niente caratteri come < > : \" / \\ | ? *, non terminare con punto o spazio).",
    err_band_folder: "Impossibile creare la cartella del gruppo: {detail}",
    confirm_import_folder: "Esiste già una cartella «{folder}», ma non ancora un gruppo.\n\nUsare la cartella come gruppo? File e cartelle esistenti non vengono modificati.",
    band_exists: "Il gruppo «{name}» esiste già ed è stato selezionato.",
    band_exists_plain: "Il gruppo «{name}» esiste già.",
    band_created: "Gruppo «{name}» creato. Cartella: {folder}",
    band_imported: "Gruppo «{name}» importato. Cartella esistente: {folder} (nessuna modifica).",
    band_prompt_warning: "Impossibile creare la cartella dei prompt: {detail}",
    tab_media: "Media & pubblicazioni",
    media_links: "Media collegati alle piattaforme",
    media_files: "File multimediali",
    media_label: "Etichetta (facoltativa)",
    media_add_link: "Salva link",
    media_import_hint: "Importazione file, analisi audio ed esplora media: nell’app desktop.",
    media_no_links: "Nessun link salvato.",
    media_no_files: "Nessun file multimediale nella cartella del progetto.",
    media_no_preview: "nessuna anteprima nel browser",
    media_open: "Apri in una nuova scheda",
    media_link_added: "Link salvato.",
    release_title: "Pubblicazioni",
    release_distributor: "Distributore",
    release_date: "Data di uscita (facoltativa)",
    release_check: "Verifica lista di controllo (senza salvare)",
    release_save: "Salva pubblicazione / confronta ISRC",
    release_none: "Nessuna pubblicazione.",
    release_platform_save: "Salva piattaforma",
    release_platform_saved: "Piattaforma «{platform}» salvata.",
    release_saved: "Pubblicazione #{id} salvata.",
    err_invalid_url: "Inserisci un link HTTP(S) valido.",
    err_link_exists: "Questo link è già salvato.",
    err_invalid_isrc: "ISRC non valido.",
    err_invalid_date: "Data non valida.",
    err_release_required: "Brano e distributore sono obbligatori.",
    err_media_unavailable: "Impossibile leggere le cartelle multimediali: {detail}",
    tab_conn: "Connessioni IA",
    conn_manual: "Su questo sistema MPW non può aprire una finestra per questo. Esegui in un terminale:\n{command}",
    conn_copy_failed: "Impossibile copiare negli appunti. Copia tu stesso questo testo:",
    suno_button: "Invia a Suno (MCP) …",
    tab_ai: "AI Prompt Launcher",
    band: "Gruppo",
    ai_target: "Brano / progetto di destinazione",
    ai_create_song: "Crea voce del brano",
    ai_platform: "Piattaforma IA",
    ai_hardware: "Hardware per questo prompt",
    ai_hw_band: "Hardware del profilo del gruppo",
    ai_model: "Modello API",
    ai_key: "Chiave API (facoltativa)",
    ai_cli_command: "Comando CLI",
    ai_cli_model: "Modello CLI",
    ai_cli_model_hint: "vuoto = predefinito della CLI",
    ai_cli_check: "Verifica CLI",
    ai_brief: "Idea del brano / istruzione",
    ai_brief_hint: "Esempio: blues britannico incontra folk metal industriale, una storia su …",
    ai_generate_api: "Crea prompt (API)",
    ai_generate_cli: "Crea prompt (CLI)",
    ai_copy_open: "Copia richiesta e apri piattaforma",
    ai_import_file: "Risposta da file",
    ai_paste: "Incolla la risposta della chat",
    ai_paste_hint: "Incolla qui la risposta dell’IA (sezioni STYLE e LYRICS o JSON) …",
    ai_paste_apply: "Dividi in stile e testo",
    ai_style_hint: "Solo lo stile musicale, senza marcatori [STYLE].",
    ai_lyrics_hint: "Testo e indicazioni di produzione, senza marcatori [LYRICS].",
    ai_save: "Salva come nuova versione",
    ai_save_hint: "Il prompt attivo del brano resta invariato; viene inoltre salvato un file di testo nella cartella dei prompt del gruppo.",
    ai_load_version: "Carica in stile e testo",
    ai_no_bands: "Nessun gruppo. Crea prima un gruppo nella scheda «Bands».",
    ai_no_projects: "Questo gruppo non ha ancora progetti di brani. I progetti si creano nell’app desktop.",
    ai_no_song_entry: "nessuna voce del brano",
    ai_key_env_found: "Lascia vuoto: viene usata la chiave di {env}.",
    ai_key_env_missing: "Nessuna chiave trovata in {env}: inserisci una chiave (usata solo per questa richiesta, non salvata).",
    ai_err_split: "Impossibile dividere la risposta dell’IA in stile e testo. Usa una risposta con sezioni STYLE e LYRICS (o JSON).",
    ai_err_key: "Chiave API mancante. Inserisci una chiave o imposta la variabile d’ambiente {env}.",
    ai_err_model: "Nome del modello non valido.",
    ai_err_busy: "Una richiesta IA è già in corso. Attendi che termini.",
    ai_err_no_song: "Scegli un brano di destinazione o crea prima un brano per il progetto con «Crea voce del brano».",
    ai_err_job: "La richiesta IA non è più nota (MPW nel browser è stato riavviato?). Avviala di nuovo.",
    ai_err_empty: "Stile e testo non possono essere vuoti.",
    ai_err_prompt: "Impossibile creare la richiesta: {detail}",
    ai_err_file_size: "Il file da importare non può superare 2 MB.",
    ai_running_api: "Richiesta API in corso … {s} s",
    ai_running_cli: "Richiesta CLI in corso … {s} s (può richiedere alcuni minuti)",
    ai_received: "Risposta ricevuta. Controllala; viene salvata solo con «Salva come nuova versione».",
    ai_cli_found: "CLI di {provider} trovata: {path}\nSe non l’hai ancora fatto, avvia la CLI una volta in un terminale ed effettua l’accesso.",
    ai_copy_failed: "Impossibile copiare la richiesta negli appunti.",
    ai_copied: "Richiesta copiata e {url} aperto. Incollala lì con Ctrl+V; poi incolla la risposta qui sotto o importala come file.",
    ai_copied_no_window: "Richiesta copiata. Il browser ha bloccato la nuova finestra: apri {url} e incolla con Ctrl+V.",
    ai_imported: "Risposta acquisita (fonte: {source}). Controllala e salvala come versione.",
    ai_source_paste: "testo incollato",
    ai_confirm_replace: "Stile e testo contengono già del testo. Sostituirlo con il nuovo contenuto?",
    ai_saved: "Versione #{id} salvata e archiviata come file di testo:\n{file}\nIl prompt attivo del brano resta invariato.",
    ai_saved_no_file: "La versione #{id} è stata salvata, ma non è stato possibile creare il file di testo: {detail}",
    ai_confirm_song: "Creare una voce del brano per il progetto «{project}»?\n\nNessun file viene modificato.",
    ai_song_created: "Il brano di destinazione «{project}» è stato assegnato al progetto.",
    ai_version_loaded: "Versione #{id} caricata in stile e testo. Non ancora salvata.",
  },
};

const state = { lang: 'de', info: null, songs: [], song: null, loaded: null, versions: [], version: null, bands: [] };
const $ = (id) => document.getElementById(id);

function t(key, values) {
  const table = I18N[state.lang] || I18N.en;
  let text = table[key] !== undefined ? table[key] : (I18N.de[key] || key);
  for (const [k, v] of Object.entries(values || {})) text = text.split('{' + k + '}').join(String(v));
  return text;
}

// Token from the URL fragment once, then kept for this browser tab only.
const TOKEN = (() => {
  const match = location.hash.match(/t=([A-Za-z0-9_-]+)/);
  if (match) {
    try { sessionStorage.setItem('mpw-token', match[1]); } catch (e) { /* storage blocked */ }
    history.replaceState(null, '', location.pathname);
    return match[1];
  }
  try { return sessionStorage.getItem('mpw-token') || ''; } catch (e) { return ''; }
})();

async function api(path, options = {}) {
  const init = { method: options.method || 'GET', headers: { 'X-MPW-Token': TOKEN } };
  if (options.body !== undefined) {
    init.headers['Content-Type'] = 'application/json';
    init.body = JSON.stringify(options.body);
  }
  let response;
  try {
    response = await fetch(path, init);
  } catch (e) {
    throw Object.assign(new Error(t('connection')), { kind: 'connection' });
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error === 'token' ? t('token') : (data.detail || data.error || response.status));
    Object.assign(error, { status: response.status, data });
    throw error;
  }
  return data;
}

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function showMessage(text, kind) {
  const box = $('message');
  box.textContent = text;
  box.className = 'message' + (kind ? ' ' + kind : '');
  box.hidden = !text;
}

function applyLanguage() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll('[data-i18n]').forEach((node) => { node.textContent = t(node.dataset.i18n); });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => { node.placeholder = t(node.dataset.i18nPlaceholder); });
  const status = $('f-status');
  const current = status.value;
  status.replaceChildren(...(state.info ? state.info.statuses : []).map((key, i) => {
    const option = el('option', t('st_' + i)); option.value = key; return option;
  }));
  if (current) status.value = current;
  if (state.info) {
    $('meta').textContent = 'v' + state.info.version;
    $('meta').title = state.info.database;
  }
}

/* ------------------------------------------------------------------ Songs & Suno */

function editorValues() {
  return { status: $('f-status').value, distributor: $('f-distributor').value, platforms: $('f-platforms').value,
           style: $('f-style').value, lyrics: $('f-lyrics').value };
}

function isDirty() {
  if (!state.loaded) return false;
  const now = editorValues();
  return Object.keys(now).some((k) => now[k] !== state.loaded[k]);
}

function updateCounters() {
  const limits = state.info ? state.info.limits : { style: 1000, lyrics: 5000 };
  let over = false;
  for (const field of ['style', 'lyrics']) {
    const n = $('f-' + field).value.length;
    const counter = $('c-' + field);
    counter.textContent = t('chars', { n, max: limits[field] });
    counter.classList.toggle('over', n > limits[field]);
    over = over || n > limits[field];
  }
  const dirty = isDirty();
  $('dirty').hidden = !dirty;
  $('btn-save').disabled = !dirty || over;
  $('btn-revert').disabled = !dirty;
}

async function loadBandsFilter() {
  state.bands = await api('/api/bands');
  const select = $('band-filter');
  const selected = select.value;
  select.replaceChildren(el('option', t('all_bands')));
  select.firstChild.value = '';
  for (const band of state.bands) {
    const option = el('option', band.name); option.value = band.id; select.append(option);
  }
  select.value = selected;
}

async function loadSongs() {
  const params = new URLSearchParams();
  if ($('band-filter').value) params.set('band_id', $('band-filter').value);
  if ($('song-search').value.trim()) params.set('q', $('song-search').value.trim());
  state.songs = await api('/api/songs?' + params.toString());
  renderSongList();
}

function renderSongList() {
  const list = $('song-list');
  list.replaceChildren(...state.songs.map((song) => {
    const item = el('li');
    item.append(el('span', song.title));
    const index = state.info ? state.info.statuses.indexOf(song.status) : -1;
    if (song.status) item.append(el('span', index >= 0 ? t('st_' + index) : song.status, 'badge'));
    item.append(el('span', song.band + ' · ' + song.project, 'sub'));
    item.classList.toggle('active', !!state.song && state.song.id === song.id);
    item.addEventListener('click', () => selectSong(song.id));
    return item;
  }));
  $('song-count').textContent = t('songs_count', { n: state.songs.length });
}

async function selectSong(id) {
  if (isDirty() && !confirm(t('confirm_discard'))) return;
  const song = await api('/api/songs/' + id);
  state.song = song;
  state.loaded = { status: song.status || state.info.statuses[0], distributor: song.distributor || '',
                   platforms: song.platforms || '', style: song.style || '', lyrics: song.lyrics || '' };
  fillEditor(state.loaded);
  $('song-title').textContent = song.title;
  $('song-path').textContent = song.band + ' / ' + song.project;
  $('editor-empty').hidden = true;
  $('editor-body').hidden = false;
  showMessage('');
  renderSongList();
  await loadVersions();
}

function fillEditor(values) {
  $('f-status').value = values.status;
  $('f-distributor').value = values.distributor;
  $('f-platforms').value = values.platforms;
  $('f-style').value = values.style;
  $('f-lyrics').value = values.lyrics;
  updateCounters();
}

async function saveSong() {
  const values = editorValues();
  try {
    const result = await api('/api/songs/' + state.song.id, { method: 'POST', body: { ...values, expected: state.loaded } });
    state.loaded = values;
    state.song = result.song;
    updateCounters();
    showMessage(result.archived ? t('saved_archived') : t('saved'));
    await Promise.all([loadVersions(), loadSongs()]);
  } catch (error) {
    if (error.status === 409) showMessage(t('conflict'), 'warn');
    else if (error.data && error.data.error === 'too_long') showMessage(t('too_long'), 'error');
    else showMessage(error.kind === 'connection' ? error.message : t('error', { detail: error.message }), 'error');
  }
}

async function revertSong() {
  if (!state.song) return;
  state.loaded = null;  // reload without the discard question
  await selectSong(state.song.id);
}

async function loadVersions() {
  state.versions = state.song ? await api('/api/songs/' + state.song.id + '/versions') : [];
  state.version = null;
  $('version-preview').hidden = true;
  const list = $('version-list');
  if (!state.versions.length) {
    list.replaceChildren(el('li', t('no_versions'), 'hint'));
    return;
  }
  list.replaceChildren(...state.versions.map((version) => {
    const item = el('li');
    item.append(el('span', '#' + version.id + ' · ' + version.provider));
    item.append(el('span', version.model + ' · ' + version.created_at, 'sub'));
    item.addEventListener('click', () => showVersion(version.id, item));
    return item;
  }));
}

async function showVersion(id, item) {
  state.version = await api('/api/versions/' + id);
  document.querySelectorAll('#version-list li').forEach((li) => li.classList.toggle('active', li === item));
  $('version-head').textContent = '#' + state.version.id + ' · ' + state.version.provider + ' · ' + state.version.created_at;
  $('v-style').textContent = state.version.style;
  $('v-lyrics').textContent = state.version.lyrics;
  $('version-preview').hidden = false;
}

function loadVersionIntoEditor() {
  if (!state.version) return;
  $('f-style').value = state.version.style;
  $('f-lyrics').value = state.version.lyrics;
  updateCounters();
  showMessage(t('version_loaded', { id: state.version.id }), 'warn');
}

/* ------------------------------------------------------------------ Bands (stage 2: edit) */

const bandState = { band: null, item: null, editing: null, presets: [], busy: false };

// One band action at a time: further clicks are ignored until the running one has finished.
async function bandAction(fn) {
  if (bandState.busy) return;
  bandState.busy = true;
  try { await fn(); } finally { bandState.busy = false; }
}

function bandMessage(text, kind) {
  const box = $('band-message');
  box.textContent = text;
  box.className = 'message' + (kind ? ' ' + kind : '');
  box.hidden = !text;
}

function bandError(error) {
  const code = error.data && error.data.error;
  const map = { empty_field: 'err_empty_field', too_long: 'err_too_long', no_hardware: 'err_no_hardware',
                preset_damaged: 'err_preset_damaged', band_missing: 'err_missing', instrument_missing: 'err_missing',
                preset_missing: 'err_missing' };
  bandMessage(map[code] ? t(map[code]) : (error.kind === 'connection' ? error.message : t('error', { detail: error.message })), 'error');
}

function fillOptions(list, values) {
  list.replaceChildren(...values.map((value) => { const o = el('option'); o.value = value; return o; }));
}

async function loadBandList() {
  state.bands = await api('/api/bands');
  $('band-list').replaceChildren(...state.bands.map((band) => {
    const item = el('li');
    item.append(el('span', band.name));
    item.append(el('span', [band.genre, band.second_genre].filter(Boolean).join(' / ') || t('none'), 'sub'));
    item.addEventListener('click', () => bandAction(async () => { bandMessage(''); await selectBand(band.id, item); }).catch(bandError));
    return item;
  }));
}

async function refreshHardwareChoices() {
  const group = $('hw-group').value.trim();
  const choices = await api('/api/hardware/choices?category=' + encodeURIComponent(group));
  fillOptions($('hw-groups'), choices.groups);
  fillOptions($('hw-details-list'), choices.details);
}

async function loadPresets() {
  const presets = await api('/api/presets');
  bandState.presets = Array.isArray(presets) ? presets : [];
  const select = $('preset-select');
  select.replaceChildren(...bandState.presets.map((p) => {
    const o = el('option', p.name + ' (' + p.items.length + ')'); o.value = p.id; return o;
  }));
  if (!bandState.presets.length) { const o = el('option', t('no_presets')); o.value = ''; select.append(o); }
  for (const id of ['btn-preset-add', 'btn-preset-replace']) $(id).disabled = !bandState.presets.length;
}

async function selectBand(id, item) {
  const band = await api('/api/bands/' + id + '/full');
  bandState.band = band;
  if (item) bandState.item = item;
  document.querySelectorAll('#band-list li').forEach((li) => li.classList.toggle('active', li === bandState.item));
  $('band-name').textContent = band.name;
  $('b-genre').value = band.genre || '';
  $('b-second').value = band.second_genre || '';
  fillOptions($('genre-options'), band.genre_catalog);
  $('b-persona').replaceChildren(...band.personas.map((p) => { const o = el('option', p); o.value = p; return o; }));
  $('b-persona').value = band.personas.includes(band.persona) ? band.persona : band.personas[0];
  renderHardware();
  resetHardwareForm();
  renderProjects(id, band.projects);
  $('band-empty').hidden = true;
  $('band-new').hidden = true;
  $('band-body').hidden = false;
  await Promise.all([refreshHardwareChoices(), loadPresets()]);
}

/* „Neue Band“: same rules as the desktop app (folder + database + prompt folder). */

function newBandMessage(text, kind) {
  const box = $('band-new-message');
  box.textContent = text;
  box.className = 'message' + (kind ? ' ' + kind : '');
  box.hidden = !text;
}

async function showNewBandForm() {
  const options = await api('/api/band-options');
  fillOptions($('genre-options'), options.genres);
  $('n-persona').replaceChildren(...options.personas.map((p) => { const o = el('option', p); o.value = p; return o; }));
  for (const id of ['n-name', 'n-genre', 'n-second']) $(id).value = '';
  newBandMessage('');
  document.querySelectorAll('#band-list li').forEach((li) => li.classList.remove('active'));
  $('band-empty').hidden = true;
  $('band-body').hidden = true;
  $('band-new').hidden = false;
  $('n-name').focus();
}

function hideNewBandForm() {
  $('band-new').hidden = true;
  if (bandState.band && bandState.item && bandState.item.isConnected) {  // back to the band shown before
    bandState.item.classList.add('active');
    $('band-body').hidden = false;
  } else $('band-empty').hidden = false;
}

async function createBand() {
  const body = { name: $('n-name').value.trim(), genre: $('n-genre').value,
                 second_genre: $('n-second').value, persona: $('n-persona').value };
  if (!body.name) { newBandMessage(t('err_band_name_empty'), 'error'); return; }
  let result;
  try {
    try {
      result = await api('/api/bands', { method: 'POST', body });
    } catch (error) {
      const code = error.data && error.data.error;
      if (code !== 'folder_exists') throw error;
      // A folder with this name exists but no band profile: take it over unchanged only on a clear yes.
      if (!confirm(t('confirm_import_folder', { folder: error.data.folder || body.name }))) return;
      result = await api('/api/bands', { method: 'POST', body: { ...body, import_existing: true } });
    }
  } catch (error) {
    const code = error.data && error.data.error;
    if (code === 'band_exists' && error.data.id) {
      bandState.band = { id: error.data.id };
      await reloadBand();
      bandMessage(t('band_exists', { name: bandState.band.name }));
      return;
    }
    const map = { invalid_name: 'err_band_name', too_long: 'err_too_long', empty_field: 'err_band_name_empty',
                  band_exists: 'band_exists_plain' };
    if (code === 'folder_error') newBandMessage(t('err_band_folder', { detail: error.data.detail || '' }), 'error');
    else newBandMessage(map[code] ? t(map[code], { name: body.name })
      : (error.kind === 'connection' ? error.message : t('error', { detail: error.message })), 'error');
    return;
  }
  bandState.band = { id: result.id };
  let text = t(result.created ? 'band_created' : 'band_imported', { name: result.name, folder: result.folder });
  if (result.prompt_warning) text += ' ' + t('band_prompt_warning', { detail: result.prompt_warning });
  await reloadBand(text);
  await loadBandsFilter();  // the new band also appears in the Songs filter
}

function renderHardware() {
  const rows = bandState.band.instruments.map((row) => {
    const tr = el('tr');
    tr.classList.toggle('editing', bandState.editing === row.id);
    const actions = el('td', null, 'row-actions');
    const edit = el('button', t('edit'));
    edit.addEventListener('click', () => startEditHardware(row));
    const del = el('button', t('delete'), 'danger');
    del.addEventListener('click', () => bandAction(() => deleteHardware(row)));
    actions.append(edit, del);
    tr.append(el('td', row.category), el('td', row.details), actions);
    return tr;
  });
  if (!rows.length) { const tr = el('tr'); const td = el('td', t('no_hardware'), 'hint'); td.colSpan = 3; tr.append(td); rows.push(tr); }
  $('band-hardware').replaceChildren(...rows);
}

function resetHardwareForm() {
  bandState.editing = null;
  $('hw-group').value = '';
  $('hw-details').value = '';
  $('btn-hw-save').textContent = t('hw_add');
  $('btn-hw-cancel').hidden = true;
}

function startEditHardware(row) {
  bandState.editing = row.id;
  $('hw-group').value = row.category;
  $('hw-details').value = row.details;
  $('btn-hw-save').textContent = t('hw_save');
  $('btn-hw-cancel').hidden = false;
  renderHardware();
  refreshHardwareChoices().catch(bandError);
}

async function reloadBand(message) {
  await selectBand(bandState.band.id);
  await loadBandList();
  document.querySelectorAll('#band-list li').forEach((li, i) => {
    if (state.bands[i] && state.bands[i].id === bandState.band.id) { li.classList.add('active'); bandState.item = li; }
  });
  if (message) bandMessage(message);
}

async function saveBandProfile() {
  try {
    await api('/api/bands/' + bandState.band.id, { method: 'POST',
      body: { genre: $('b-genre').value, second_genre: $('b-second').value, persona: $('b-persona').value } });
    await reloadBand(t('band_saved'));
  } catch (error) { bandError(error); }
}

async function saveHardware() {
  const body = { category: $('hw-group').value, details: $('hw-details').value };
  try {
    if (bandState.editing) await api('/api/instruments/' + bandState.editing, { method: 'POST', body });
    else await api('/api/bands/' + bandState.band.id + '/instruments', { method: 'POST', body });
    bandMessage('');
    await selectBand(bandState.band.id);
  } catch (error) { bandError(error); }
}

async function deleteHardware(row) {
  if (!confirm(t('confirm_delete_hw', { entry: row.category + ': ' + row.details }))) return;
  try {
    await api('/api/instruments/' + row.id + '/delete', { method: 'POST', body: {} });
    bandMessage('');
    await selectBand(bandState.band.id);
  } catch (error) { bandError(error); }
}

async function transferPreset(mode) {
  const id = Number($('preset-select').value);
  const preset = bandState.presets.find((p) => p.id === id);
  if (!preset) return;
  if (mode === 'replace' && !confirm(t('confirm_replace', { name: preset.name, band: bandState.band.name }))) return;
  try {
    const result = await api('/api/presets/' + id + '/transfer', { method: 'POST',
      body: { band_id: bandState.band.id, mode, confirm: mode === 'replace' } });
    await selectBand(bandState.band.id);
    bandMessage(mode === 'add' ? t('preset_added', result) : t('preset_replaced', result));
  } catch (error) { bandError(error); }
}

async function saveAsPreset() {
  const name = (prompt(t('preset_name_prompt')) || '').trim();
  if (!name) return;
  const url = '/api/bands/' + bandState.band.id + '/presets';
  try {
    let result;
    try {
      result = await api(url, { method: 'POST', body: { name } });
    } catch (error) {
      if (error.status !== 409 || !confirm(t('preset_overwrite', { name }))) throw error;
      result = await api(url, { method: 'POST', body: { name, overwrite: true } });
    }
    await loadPresets();
    bandMessage(t('preset_saved', result));
  } catch (error) { if (error.status !== 409) bandError(error); }
}

function renderProjects(bandId, rows) {
  const projects = new Map();
  for (const row of rows) {
    if (!projects.has(row.id)) projects.set(row.id, { name: row.name, songs: [] });
    if (row.song_id) projects.get(row.id).songs.push(row);
  }
  const list = $('band-projects');
  list.replaceChildren(...[...projects.values()].map((project) => {
    const item = el('li');
    item.append(el('span', project.name));
    for (const song of project.songs) {
      const link = el('span', '♪ ' + song.song_title, 'sub');
      link.addEventListener('click', (event) => { event.stopPropagation(); openSongFromBand(bandId, song.song_id); });
      item.append(link);
    }
    return item;
  }));
  if (!projects.size) list.replaceChildren(el('li', t('no_projects'), 'hint'));
}

async function openSongFromBand(bandId, songId) {
  switchView('songs');
  $('band-filter').value = String(bandId);
  $('song-search').value = '';
  await loadSongs();
  await selectSong(songId);
}

let hwTimer;
$('hw-group').addEventListener('input', () => { clearTimeout(hwTimer); hwTimer = setTimeout(() => refreshHardwareChoices().catch(bandError), 250); });
$('btn-band-save').addEventListener('click', () => bandAction(saveBandProfile));
$('btn-hw-save').addEventListener('click', () => bandAction(saveHardware));
$('btn-hw-cancel').addEventListener('click', () => { resetHardwareForm(); renderHardware(); });
$('btn-preset-add').addEventListener('click', () => bandAction(() => transferPreset('add')));
$('btn-preset-replace').addEventListener('click', () => bandAction(() => transferPreset('replace')));
$('btn-preset-save').addEventListener('click', () => bandAction(saveAsPreset));
$('btn-band-new').addEventListener('click', () => bandAction(showNewBandForm).catch(bandError));
$('btn-band-new-cancel').addEventListener('click', hideNewBandForm);
$('btn-band-create').addEventListener('click', () => bandAction(createBand).catch((error) => newBandMessage(error.message, 'error')));
$('n-name').addEventListener('keydown', (event) => { if (event.key === 'Enter') $('btn-band-create').click(); });

/* ------------------------------------------------------------------ Medien & Releases (stage 7) */

const mrState = { songs: [], song: null, media: null, rel: null, busy: false };

function fmt(text, values) {
  for (const [k, v] of Object.entries(values || {})) text = text.split('{' + k + '}').join(String(v));
  return text;
}

function mrMessage(id, text, kind) {
  const box = $(id);
  box.textContent = text;
  box.className = 'message' + (kind ? ' ' + kind : '');
  box.hidden = !text;
}

// Texts shared with the desktop tabs (served by the core): release edit texts, checklist, status labels.
function relEdit(index, values) {
  const all = mrState.rel.edit_texts;
  return fmt((all[state.lang] || all.de)[index], values);
}

function relPreflight(key, values) {
  const table = mrState.rel.preflight_texts[state.lang] || {};
  return fmt(table[key] || key, values);
}

function relStatusLabel(status) {
  const labels = mrState.rel.status_labels[state.lang];
  const index = mrState.rel.states.indexOf(status);
  return labels && index >= 0 ? labels[index] : status;
}

function mrErrorText(error) {
  const code = error.data && error.data.error;
  const map = { invalid_url: 'err_invalid_url', link_exists: 'err_link_exists', invalid_isrc: 'err_invalid_isrc',
                invalid_date: 'err_invalid_date', empty_field: 'err_release_required', too_long: 'err_too_long',
                song_missing: 'err_missing', link_missing: 'err_missing', release_missing: 'err_missing',
                media_unavailable: 'err_media_unavailable' };
  if (code === 'empty_field' && mrState.rel) return relEdit(0);
  if (code === 'invalid_isrc' && mrState.rel) return relEdit(1);
  if (map[code]) return t(map[code], { detail: (error.data && error.data.detail) || '' });
  return error.kind === 'connection' ? error.message : t('error', { detail: error.message });
}

async function mrAction(fn, messageBox) {
  if (mrState.busy) return;
  mrState.busy = true;
  try { await fn(); } catch (error) { mrMessage(messageBox || 'rl-message', mrErrorText(error), 'error'); }
  finally { mrState.busy = false; }
}

async function mrInit() {
  const bands = await api('/api/bands');
  const select = $('mr-band');
  select.replaceChildren(el('option', t('all_bands')));
  select.firstChild.value = '';
  for (const band of bands) { const o = el('option', band.name); o.value = band.id; select.append(o); }
  await mrLoadSongs();
}

async function mrLoadSongs() {
  const params = new URLSearchParams();
  if ($('mr-band').value) params.set('band_id', $('mr-band').value);
  if ($('mr-search').value.trim()) params.set('q', $('mr-search').value.trim());
  mrState.songs = await api('/api/songs?' + params.toString());
  $('mr-song-list').replaceChildren(...mrState.songs.map((song) => {
    const item = el('li');
    item.append(el('span', song.title), el('span', song.band + ' · ' + song.project, 'sub'));
    item.classList.toggle('active', !!mrState.song && mrState.song.id === song.id);
    item.addEventListener('click', () => mrAction(() => mrSelectSong(song), 'rl-message'));
    return item;
  }));
}

async function mrSelectSong(song) {
  mrState.song = song;
  document.querySelectorAll('#mr-song-list li').forEach((li, i) => li.classList.toggle('active', mrState.songs[i] === song));
  $('mr-title').textContent = song.title;
  $('mr-path').textContent = song.band + ' / ' + song.project;
  $('mr-empty').hidden = true;
  $('mr-body').hidden = false;
  mrMessage('rl-message', '');
  $('rl-choices').hidden = true;
  for (const id of ['rl-dist', 'rl-date', 'rl-isrc', 'rl-upc', 'mr-link-url', 'mr-link-label']) $(id).value = '';
  $('mr-preview').hidden = true;
  $('mr-preview').replaceChildren();
  await Promise.all([mrLoadMedia(), mrLoadReleases()]);
}

async function mrLoadMedia() {
  const media = await api('/api/songs/' + mrState.song.id + '/media');
  mrState.media = media;
  const platform = $('mr-link-platform');
  if (!platform.options.length) {
    platform.replaceChildren(...media.platforms.map((p) => { const o = el('option', p); o.value = p; return o; }));
  }
  const links = media.links.map((link) => {
    const row = el('li', null, 'link-row');
    const text = el('div', null, 'grow');
    text.append(el('div', link.platform + (link.label ? ' · ' + link.label : '')));
    const a = el('a', link.url);
    a.href = link.url; a.target = '_blank'; a.rel = 'noopener noreferrer';
    text.append(a);
    const del = el('button', t('delete'), 'danger');
    del.addEventListener('click', () => mrAction(() => mrDeleteLink(link), 'rl-message'));
    row.append(text, del);
    return row;
  });
  $('mr-links').replaceChildren(...(links.length ? links : [el('li', t('media_no_links'), 'hint')]));
  const files = media.files.map((file) => {
    const item = el('li');
    item.append(el('span', file.kind + ' · ' + file.name), el('span', (file.bytes / 1048576).toFixed(1) + ' MB'
      + (file.preview ? '' : ' · ' + t('media_no_preview')), 'sub'));
    item.addEventListener('click', () => mrPreview(file, item));
    return item;
  });
  $('mr-files').replaceChildren(...(files.length ? files : [el('li', t('media_no_files'), 'hint')]));
}

async function mrPreview(file, item) {
  document.querySelectorAll('#mr-files li').forEach((li) => li.classList.toggle('active', li === item));
  const box = $('mr-preview');
  box.replaceChildren(el('div', file.name + ' · ' + (file.bytes / 1048576).toFixed(2) + ' MB', 'hint'));
  box.hidden = false;
  if (!file.url) { box.append(el('div', t('media_no_preview'), 'hint')); return; }
  if (file.preview === 'image') { const img = el('img'); img.src = file.url; img.alt = file.name; box.append(img); }
  else if (file.preview === 'audio' || file.preview === 'video') {
    const player = el(file.preview); player.controls = true; player.preload = 'metadata'; player.src = file.url; box.append(player);
  } else if (file.preview === 'text') {
    const response = await fetch(file.url, { headers: { Range: 'bytes=0-200000' } });
    box.append(el('pre', response.ok ? await response.text() : t('media_no_preview')));
  }
  if (file.preview === 'pdf' || file.preview === 'video' || file.preview === 'image') {
    const open = el('a', t('media_open'));
    open.href = file.url; open.target = '_blank'; open.rel = 'noopener noreferrer';
    box.append(open);
  }
}

async function mrAddLink() {
  await api('/api/songs/' + mrState.song.id + '/media-links', { method: 'POST',
    body: { platform: $('mr-link-platform').value, url: $('mr-link-url').value.trim(), label: $('mr-link-label').value } });
  $('mr-link-url').value = '';
  $('mr-link-label').value = '';
  mrMessage('rl-message', t('media_link_added'));
  await mrLoadMedia();
}

async function mrDeleteLink(link) {
  const texts = mrState.media.confirm_texts;
  if (!confirm((texts[state.lang] || texts.de).delete + '\n\n' + link.url)) return;
  await api('/api/songs/' + mrState.song.id + '/media-links/' + link.id + '/delete', { method: 'POST', body: { confirm: true } });
  await mrLoadMedia();
}

function releaseBody() {
  return { distributor: $('rl-dist').value, release_date: $('rl-date').value || null,
           isrc: $('rl-isrc').value, upc: $('rl-upc').value };
}

async function mrLoadReleases() {
  const rel = await api('/api/songs/' + mrState.song.id + '/releases');
  mrState.rel = rel;
  fillOptions($('rl-dists'), rel.distributors);
  const items = rel.releases.map((r) => {
    const item = el('li');
    item.append(el('div', '#' + r.id + ' · ' + r.distributor + ' · ' + (r.release_date || relEdit(2)) + ' · ISRC: ' + (r.isrc || '–')
      + (r.upc ? ' · UPC: ' + r.upc : ''), 'release-head'));
    if (r.platforms.length) {
      const list = el('ul', null, 'release-platforms');
      for (const p of r.platforms) {
        const line = el('li', p.platform + ' · ' + relStatusLabel(p.status) + ' · ');
        if (p.url) { const a = el('a', p.url); a.href = p.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; line.append(a); }
        else line.append(relEdit(11));
        list.append(line);
      }
      item.append(list);
    }
    const form = el('div', null, 'hw-form release-form');
    const platform = el('select');
    for (const name of rel.platforms) { const o = el('option', name); o.value = name; platform.append(o); }
    const status = el('select');
    for (const s of rel.states) { const o = el('option', relStatusLabel(s)); o.value = s; status.append(o); }
    const url = el('input'); url.placeholder = 'https://…'; url.maxLength = 2000;
    const fill = () => {  // show the stored values of an already listed platform
      const known = r.platforms.find((p) => p.platform === platform.value);
      status.value = known ? known.status : rel.states[0];
      url.value = known ? known.url : '';
    };
    platform.addEventListener('change', fill);
    fill();
    const save = el('button', t('release_platform_save'));
    save.addEventListener('click', () => mrAction(async () => {
      await api('/api/releases/' + r.id + '/platforms', { method: 'POST',
        body: { platform: platform.value, status: status.value, url: url.value.trim() } });
      mrMessage('rl-message', t('release_platform_saved', { platform: platform.value }));
      await mrLoadReleases();
    }));
    form.append(platform, status, url, save);
    item.append(form);
    return item;
  });
  $('rl-list').replaceChildren(...(items.length ? items : [el('li', t('release_none'), 'hint')]));
}

async function mrCheckRelease() {
  const result = await api('/api/songs/' + mrState.song.id + '/releases/check', { method: 'POST', body: releaseBody() });
  const lines = [relPreflight('RELEASE-CHECKLISTE (nur Hinweis, keine Speicherung)'), ''];
  for (const [kind, key, values] of result.items) {
    const date = values.date || '';
    const rest = Object.fromEntries(Object.entries(values).filter(([k]) => k !== 'date'));
    lines.push((kind === 'ok' ? '✓ ' : '! ') + relPreflight(key, rest) + date);
  }
  lines.push('', relPreflight('Zusätzlich vor Veröffentlichung prüfen: finale Audiodatei, Cover, Rechte, Credits, Metadaten und Distributor-Vorgaben.'),
             relPreflight('MPW führt keine Veröffentlichung und keine externe Kennungsprüfung durch.'));
  mrMessage('rl-message', lines.join('\n'), result.items.some((i) => i[0] === 'issue') ? 'warn' : '');
}

async function mrSaveRelease(updateId) {
  $('rl-choices').hidden = true;
  const body = releaseBody();
  if (updateId) Object.assign(body, { update_id: updateId, confirm: true });
  try {
    const result = await api('/api/songs/' + mrState.song.id + '/releases', { method: 'POST', body });
    mrMessage('rl-message', result.created ? t('release_saved', { id: result.id }) : relEdit(10, { rid: result.id }));
    await mrLoadReleases();
  } catch (error) {
    if (!(error.data && error.data.error === 'isrc_exists')) throw error;
    // Same ISRC already stored: the user picks the record to change and confirms (like the desktop dialog).
    const matches = error.data.matches || [];
    mrMessage('rl-message', matches.length > 1 ? relEdit(4) : relEdit(5), 'warn');
    $('rl-choices').replaceChildren(...matches.map((m) => {
      const button = el('button', '#' + m.id + ' | ' + m.title + ' | ' + m.distributor + ' | ' + (m.release_date || relEdit(2)));
      button.addEventListener('click', () => {
        const text = relEdit(6) + '\n\nISRC: ' + body.isrc + '\n#' + m.id + ' · ' + m.title + ' · ' + m.distributor
          + '\n\n' + relEdit(7) + '\n' + relEdit(8);
        if (confirm(text)) mrAction(() => mrSaveRelease(m.id));
      });
      return button;
    }));
    $('rl-choices').hidden = false;
  }
}

$('mr-band').addEventListener('change', () => mrLoadSongs().catch(fatal));
let mrSearchTimer;
$('mr-search').addEventListener('input', () => { clearTimeout(mrSearchTimer); mrSearchTimer = setTimeout(() => mrLoadSongs().catch(fatal), 200); });
$('btn-mr-link').addEventListener('click', () => mrAction(mrAddLink));
$('btn-rl-check').addEventListener('click', () => mrAction(mrCheckRelease));
$('btn-rl-save').addEventListener('click', () => mrAction(() => mrSaveRelease(null)));

/* ------------------------------------------------------------------ KI-Verbindungen (stage 6) */

// Same groups, texts and status rules as the desktop window (texts and rules come from the core).
const connState = { info: null, lines: {}, running: false, busy: false, targets: {} };

function connTexts() { const all = connState.info.texts; return all[state.lang] || all.en; }

function connText(key, values) {
  let text = connTexts()[key] || key;
  for (const [k, v] of Object.entries(values || {})) text = text.split('{' + k + '}').join(String(v));
  return text;
}

function renderConnLine(line) {  // [key, values]; a value may itself be [key, values]
  const [key, values] = line;
  const done = {};
  for (const [k, v] of Object.entries(values || {})) done[k] = Array.isArray(v) ? renderConnLine(v) : v;
  return connText(key, done);
}

function connMessage(text, kind) {
  const box = $('conn-message');
  box.textContent = text;
  box.className = 'message' + (kind ? ' ' + kind : '');
  box.hidden = !text;
}

function connGroups() {
  const info = connState.info;
  const link = (key, name) => ({ key, link: info.links[name] });
  const clients = info.clients.map((c) => c.id);
  return [
    { key: 'grp_claude', lines: ['claude_path', 'claude_login'],
      buttons: [link('btn_install', 'claude_install'), { key: 'btn_login', run: () => connLogin('claude') }] },
    { key: 'grp_cli', lines: ['gemini_path', 'codex_path', 'node'],
      buttons: [link('btn_gemini', 'gemini_install'), link('btn_codex', 'codex_install'), link('btn_node', 'node_install')] },
    { key: 'grp_keys', lines: info.providers.map((p) => 'key_' + p), note: 'keys_note',
      buttons: [link('btn_key_claude', 'anthropic_keys'), link('btn_key_openai', 'openai_keys'), link('btn_key_gemini', 'gemini_keys')] },
    { key: 'grp_mpw', section: 'mpw', lines: clients.map((c) => 'mcp_mpw_' + c), note: 'mpw_note',
      buttons: [{ key: 'btn_connect', run: () => connSetup('mpw', 'add', 'confirm_connect') },
                { key: 'btn_disconnect', run: () => connSetup('mpw', 'remove', 'confirm_disconnect') },
                { key: 'btn_desktop', run: connCopyDesktop }] },
    { key: 'grp_suno', section: 'suno', lines: clients.map((c) => 'mcp_suno_' + c), note: 'suno_note',
      buttons: [{ key: 'btn_suno_add', run: () => connSetup('suno', 'add', 'confirm_suno') },
                { key: 'btn_suno_login', run: () => connLogin('suno') },
                { key: 'btn_suno_remove', run: () => connSetup('suno', 'remove', 'confirm_suno_remove') },
                link('btn_suno_access', 'suno_access')] },
    { key: 'grp_net', lines: info.hosts.map((h) => 'tls_' + h), hint: 'tls_hint' },
  ];
}

function renderConnPage() {
  $('conn-intro').textContent = connText('intro');
  $('btn-conn-recheck').textContent = connText('btn_recheck');
  $('btn-conn-recheck').disabled = connState.running;
  const groups = connGroups().map((group) => {
    const box = el('fieldset', null, 'conn-group');
    box.append(el('legend', connText(group.key)));
    for (const line of group.lines) {
      const value = connState.lines[line];
      box.append(el('div', value ? renderConnLine(value) : (connState.running ? connText('checking') : ''), 'conn-line'));
    }
    if (group.hint && connState.intercepted) box.append(el('div', connText(group.hint), 'message warn'));
    if (group.note) box.append(el('div', connText(group.note), 'hint'));
    if (group.section) {  // which AI CLI the buttons of this section act on
      const row = el('label', null, 'conn-target');
      row.append(el('span', connText('target_label')));
      const select = el('select');
      for (const client of connState.info.clients) { const o = el('option', client.name); o.value = client.id; select.append(o); }
      select.value = connState.targets[group.section] || 'claude';
      select.addEventListener('change', () => { connState.targets[group.section] = select.value; });
      row.append(select);
      box.append(row);
    }
    if (group.buttons) {
      const actions = el('div', null, 'actions');
      for (const b of group.buttons) {
        const button = el('button', connText(b.key));
        if (b.link) button.addEventListener('click', () => window.open(b.link, '_blank', 'noopener'));
        else button.addEventListener('click', () => connAction(b.run));
        button.disabled = connState.busy && !b.link;
        actions.append(button);
      }
      box.append(actions);
    }
    return box;
  });
  $('conn-groups').replaceChildren(...groups);
}

async function connAction(fn) {
  if (connState.busy) return;
  connState.busy = true;
  renderConnPage();
  try { await fn(); } catch (error) { connMessage(connErrorText(error), 'error'); }
  finally { connState.busy = false; renderConnPage(); }
}

function connErrorText(error) {
  const data = error.data || {};
  if (data.error === 'need_cli') return connText('need_cli', { name: data.name });
  if (data.error === 'need_claude') return connText('need_claude');
  if (data.error === 'mcp_exe_missing') return connText('mcp_exe_missing', { path: data.path });
  if (data.error === 'ai_busy') return connText('checking');
  return error.kind === 'connection' ? error.message : t('error', { detail: error.message });
}

async function connInit() {
  connState.info = await api('/api/connections');
  renderConnPage();
  await connCheck();
}

async function connCheck() {
  if (connState.running) return;
  connState.running = true;
  connState.lines = {};
  connState.intercepted = false;
  renderConnPage();
  try {
    const started = await api('/api/connections/check', { method: 'POST', body: {} });
    for (;;) {
      await sleep(1500);
      const job = await api('/api/connections/jobs/' + started.job);
      if (job.status === 'running') continue;
      if (job.status === 'done') { connState.lines = job.lines; connState.intercepted = job.intercepted; }
      else connMessage(connText('check_failed', { error: (job.error && job.error.detail) || '?' }), 'error');
      break;
    }
  } catch (error) {
    connMessage(connErrorText(error), 'error');
  } finally {
    connState.running = false;
    renderConnPage();
  }
}

function connClient(section) {
  const id = connState.targets[section] || 'claude';
  return connState.info.clients.find((c) => c.id === id);
}

async function connSetup(server, action, confirmKey) {
  const client = connClient(server);
  if (!confirm(connText(confirmKey, { name: client.name }))) return;
  const result = await api('/api/connections/setup', { method: 'POST',
    body: { server, action, client: client.id, confirm: true } });
  connMessage(result.ok ? connText('done') : connText('failed', { detail: result.detail }), result.ok ? '' : 'error');
  connState.busy = false;
  await connCheck();
}

async function connLogin(target) {
  const body = { target };
  if (target === 'suno') body.client = connClient('suno').id;
  const result = await api('/api/connections/login', { method: 'POST', body });
  if (result.started) connMessage(connText(result.message));
  else if (result.command) connMessage(t('conn_manual', { command: result.command }) + '\n\n' + connText(result.message), 'warn');
  else connMessage(connText('failed', { detail: result.error || '?' }), 'error');
}

async function connCopyDesktop() {
  const result = await api('/api/connections/desktop-config');
  try {
    await navigator.clipboard.writeText(result.text);
    connMessage(connText('desktop_copied'));
  } catch (e) {
    connMessage(t('conn_copy_failed') + '\n\n' + result.text, 'warn');
  }
}

$('btn-conn-recheck').addEventListener('click', () => connCheck());

/* ------------------------------------------------------------------ An Suno senden (stage 5) */

// Only saved prompts are sent: the server reads the chosen prompt from the database itself.
const sunoState = { info: null, songId: null, job: null, running: false, linksSaved: false };

function sunoText(key, values) {
  const all = sunoState.info.texts;
  let text = (all[state.lang] || all.en)[key] || key;
  for (const [k, v] of Object.entries(values || {})) text = text.split('{' + k + '}').join(String(v));
  return text;
}

function sunoStatus(text, kind) {
  const box = $('suno-status');
  box.textContent = text;
  box.className = 'message' + (kind ? ' ' + kind : '');
  box.hidden = !text;
}

function sunoChoice() {
  const index = Number($('suno-choice').value);
  return sunoState.info.choices[index] || null;
}

function showSunoChoice() {
  const choice = sunoChoice();
  const style = choice ? choice.style : '';
  const lyrics = choice ? choice.lyrics : '';
  $('suno-style').textContent = style;
  $('suno-lyrics').textContent = lyrics;
  $('suno-l-style').textContent = sunoText('style_label', { count: style.trim().length });
  $('suno-l-lyrics').textContent = sunoText('lyrics_label', { count: lyrics.trim().length });
}

function updateSunoButtons() {
  $('btn-suno-send').disabled = sunoState.running;
  $('suno-choice').disabled = sunoState.running;
  $('suno-song-title').disabled = sunoState.running;
}

async function openSunoDialog() {
  if (!state.song) return;
  const songId = state.song.id;
  const sameRunning = sunoState.running && sunoState.songId === songId;
  if (!sameRunning) {
    const info = await api('/api/songs/' + songId + '/suno');
    Object.assign(sunoState, { info, songId, job: null, linksSaved: false });
    $('suno-head').textContent = sunoText('title', { song: info.title });
    $('suno-l-prompt').textContent = sunoText('prompt_label');
    $('suno-l-title').textContent = sunoText('title_label');
    $('suno-info').textContent = sunoText('info');
    $('btn-suno-send').textContent = sunoText('btn_send');
    $('btn-suno-links').textContent = sunoText('btn_save_links');
    $('btn-suno-close').textContent = sunoText('btn_close');
    $('suno-choice').replaceChildren(...info.choices.map((c, i) => {
      const label = c.version_id === null ? sunoText('active')
        : sunoText('version', { id: c.version_id, provider: c.provider, created: c.created });
      const option = el('option', label); option.value = i; return option;
    }));
    $('suno-song-title').value = info.title;
    sunoStatus('');
    $('suno-results').hidden = true;
    $('btn-suno-links').hidden = true;
    showSunoChoice();
  }
  // the editor may differ from what is saved: only the saved state is sent
  $('suno-unsaved').textContent = sunoText('unsaved');
  $('suno-unsaved').hidden = !isDirty();
  updateSunoButtons();
  $('suno-dialog').showModal();
}

function sunoProviderError(values) {
  const all = sunoState.info.error_texts;
  const texts = all[state.lang] || all.en;
  let text = (texts[values.kind] || texts.unexpected).split('{provider}').join('Claude')
    .split('{code}').join(values.code || '?').split('{model}').join('');
  if (values.detail && !['timeout', 'truncated', 'empty', 'cli_timeout'].includes(values.kind)) text += '\n\n' + texts.detail + ' ' + values.detail;
  return text;
}

function showSunoResult(job) {
  const values = job.values || {};
  let text;
  if (job.outcome === 'provider_error') text = sunoText('error', { detail: sunoProviderError(values) });
  else if (job.outcome === 'done') text = sunoText('done', { count: values.count });
  else text = sunoText(job.outcome, values);
  text = [text, ...(job.notes || []).map((note) => sunoText(note))].join('\n');
  const ok = job.outcome === 'done' || job.outcome === 'no_clips';
  sunoStatus(text, ok ? ((job.notes || []).length || job.outcome === 'no_clips' ? 'warn' : '') : 'error');
  const clips = job.clips || [];
  $('suno-results').replaceChildren(...clips.map((clip) => {
    const item = el('li', (clip.title || $('suno-song-title').value || clip.id) + ' (' + clip.status + ')');
    if (clip.url && /^https:\/\//.test(clip.url)) {  // server only passes real Suno https links
      const link = el('a', clip.url);
      link.href = clip.url; link.target = '_blank'; link.rel = 'noopener noreferrer';
      item.append(' – ', link);
    }
    return item;
  }));
  $('suno-results').hidden = !clips.length;
  $('btn-suno-links').hidden = !clips.some((clip) => clip.url);
  $('btn-suno-links').disabled = sunoState.linksSaved;
}

async function sendToSuno() {
  const choice = sunoChoice();
  if (!choice) return;
  const title = $('suno-song-title').value.trim();
  const lyrics = choice.lyrics.trim();
  const style = choice.style.trim();
  if (!lyrics) { sunoStatus(sunoText('empty'), 'error'); return; }
  const limits = sunoState.info.limits;
  if (title.length > limits.title || style.length > limits.style || lyrics.length > limits.lyrics) {
    sunoStatus(sunoText('too_long'), 'error'); return;
  }
  // Suno creates 2 songs and spends credits: only after an explicit yes
  if (!confirm(sunoText('confirm', { title: title || '–', style: style.length, lyrics: lyrics.length }))) return;
  sunoState.running = true;
  sunoState.linksSaved = false;
  updateSunoButtons();
  $('suno-results').hidden = true;
  $('btn-suno-links').hidden = true;
  const songId = sunoState.songId;
  try {
    const started = await api('/api/songs/' + songId + '/suno/send', { method: 'POST',
      body: { version_id: choice.version_id, title, confirm: true } });
    sunoState.job = started.job;
    const began = Date.now();
    let failures = 0;
    for (;;) {
      sunoStatus(sunoText('sending') + ' (' + Math.round((Date.now() - began) / 1000) + ' s)', 'warn');
      await sleep(2000);
      let job;
      try {
        job = await api('/api/ai/jobs/' + started.job);
        failures = 0;
      } catch (error) {
        if (error.kind !== 'connection' || ++failures > 5) throw error;
        continue;
      }
      if (job.status === 'running') continue;
      if (job.status === 'failed') sunoStatus(sunoText('error', { detail: sunoProviderError(job.error) }), 'error');
      else showSunoResult(job);
      return;
    }
  } catch (error) {
    const data = error.data || {};
    if (data.error === 'provider') sunoStatus(sunoText('error', { detail: sunoProviderError(data) }), 'error');
    else if (data.error === 'ai_busy') sunoStatus(t('ai_err_busy'), 'error');
    else if (data.error === 'suno_empty') sunoStatus(sunoText('empty'), 'error');
    else if (data.error === 'suno_too_long') sunoStatus(sunoText('too_long'), 'error');
    else sunoStatus(error.kind === 'connection' ? error.message : t('error', { detail: error.message }), 'error');
  } finally {
    sunoState.running = false;
    updateSunoButtons();
  }
}

async function saveSunoLinks() {
  if (!sunoState.job || sunoState.linksSaved) return;
  try {
    const result = await api('/api/songs/' + sunoState.songId + '/suno/links', { method: 'POST',
      body: { job: sunoState.job, lang: state.lang } });
    sunoState.linksSaved = true;
    $('btn-suno-links').disabled = true;
    sunoStatus($('suno-status').textContent + '\n' + sunoText('links_saved', { count: result.added }), $('suno-status').className.replace('message', '').trim());
  } catch (error) {
    sunoStatus(t('error', { detail: error.message }), 'error');
  }
}

$('btn-suno').addEventListener('click', () => openSunoDialog().catch((error) => showMessage(t('error', { detail: error.message }), 'error')));
$('suno-choice').addEventListener('change', showSunoChoice);
$('btn-suno-send').addEventListener('click', () => { if (!sunoState.running) sendToSuno(); });
$('btn-suno-links').addEventListener('click', saveSunoLinks);
$('btn-suno-close').addEventListener('click', () => $('suno-dialog').close());

/* ------------------------------------------------------------------ AI Prompt Launcher (stage 4) */

const IMPORT_MODEL = 'Import (manuell)';
const aiState = { options: null, targets: [], songId: null, busy: false, originModel: null, version: null, unsaved: false };

function aiMessage(text, kind) {
  const box = $('ai-message');
  box.textContent = text;
  box.className = 'message' + (kind ? ' ' + kind : '');
  box.hidden = !text;
}

function aiProvider() { return $('ai-provider').value; }

// Same provider/CLI messages as the desktop tab (served by the core in all five languages).
function providerErrorText(kind, code, detail) {
  if (kind === 'split') return t('ai_err_split');
  const all = aiState.options.error_texts;
  const texts = all[state.lang] || all.en;
  let text = (texts[kind] || texts.unexpected).split('{provider}').join(aiProvider())
    .split('{code}').join(code || '?').split('{model}').join($('ai-model').value.trim());
  if (detail && !['timeout', 'truncated', 'empty', 'cli_timeout'].includes(kind)) text += '\n\n' + texts.detail + ' ' + detail;
  return text;
}

function aiErrorText(error) {
  const data = error.data || {};
  if (data.error === 'provider') return providerErrorText(data.kind, data.code, data.detail);
  const map = { key_missing: 'ai_err_key', invalid_model: 'ai_err_model', ai_busy: 'ai_err_busy', no_song: 'ai_err_no_song',
                song_missing: 'err_missing', project_missing: 'err_missing', job_missing: 'ai_err_job',
                no_structure: 'ai_err_split', too_long: 'err_too_long', empty_field: 'ai_err_empty',
                prompt_error: 'ai_err_prompt' };
  if (map[data.error]) return t(map[data.error], { env: data.env || '', detail: data.detail || '' });
  return error.kind === 'connection' ? error.message : t('error', { detail: error.message });
}

async function aiAction(fn) {
  if (aiState.busy) return;
  aiState.busy = true;
  updateAiState();
  try { await fn(); } catch (error) { aiMessage(aiErrorText(error), 'error'); } finally { aiState.busy = false; updateAiState(); }
}

async function aiInit() {
  aiState.options = await api('/api/ai/options');
  const o = aiState.options;
  $('ai-provider').replaceChildren(...o.providers.map((p) => { const opt = el('option', p); opt.value = p; return opt; }));
  const presets = [el('option', t('ai_hw_band'))];
  presets[0].value = '';
  for (const p of o.presets) { const opt = el('option', p.name + ' (' + p.count + ')'); opt.value = p.id; presets.push(opt); }
  $('ai-preset').replaceChildren(...presets);
  const bands = await api('/api/bands');
  $('ai-band').replaceChildren(...bands.map((b) => { const opt = el('option', b.name); opt.value = b.id; return opt; }));
  if (!bands.length) aiMessage(t('ai_no_bands'), 'warn');
  aiProviderChanged();
  await loadAiTargets();
}

function aiProviderChanged() {
  const o = aiState.options;
  const provider = aiProvider();
  $('ai-model').value = o.models[provider] || '';
  const cli = $('ai-cli').value.trim();
  if (!cli || Object.values(o.cli_commands).includes(cli)) $('ai-cli').value = o.cli_commands[provider] || '';
  const env = o.key_env[provider];
  $('ai-key-hint').textContent = t(o.key_in_env[provider] ? 'ai_key_env_found' : 'ai_key_env_missing', { env });
}

async function loadAiTargets() {
  const bandId = $('ai-band').value;
  const previous = $('ai-project').value;
  aiState.targets = bandId ? await api('/api/ai/targets?band_id=' + encodeURIComponent(bandId)) : [];
  $('ai-project').replaceChildren(...aiState.targets.map((p) => {
    const opt = el('option', p.song_id ? p.name : p.name + ' – ' + t('ai_no_song_entry'));
    opt.value = p.project_id;
    return opt;
  }));
  if (aiState.targets.some((p) => String(p.project_id) === previous)) $('ai-project').value = previous;
  else {  // prefer a project that already has a song entry
    const ready = aiState.targets.find((p) => p.song_id);
    if (ready) $('ai-project').value = String(ready.project_id);
  }
  if (bandId && !aiState.targets.length) aiMessage(t('ai_no_projects'), 'warn');
  await aiTargetChanged();
}

function aiTarget() {
  return aiState.targets.find((p) => String(p.project_id) === $('ai-project').value) || null;
}

async function aiTargetChanged() {
  const target = aiTarget();
  aiState.songId = target ? target.song_id : null;
  $('btn-ai-song').hidden = !target || !!target.song_id;
  updateAiState();
  await loadAiVersions();
}

function aiValues() { return { style: $('ai-style').value.trim(), lyrics: $('ai-lyrics').value.trim() }; }

function updateAiState() {
  const limits = aiState.options ? aiState.options.limits : { style: 1000, lyrics: 5000 };
  let valid = true;
  for (const field of ['style', 'lyrics']) {
    const n = $('ai-' + field).value.trim().length;
    const counter = $('ai-c-' + field);
    counter.textContent = t('chars', { n, max: limits[field] });
    counter.classList.toggle('over', n > limits[field]);
    valid = valid && n > 0 && n <= limits[field];
  }
  const ready = !!aiState.songId && !aiState.busy;
  for (const id of ['btn-ai-api', 'btn-ai-cli', 'btn-ai-copy']) $(id).disabled = !ready;
  $('btn-ai-save').disabled = !(ready && valid);
  $('btn-ai-song').disabled = aiState.busy;
}

function aiRequestBody() {
  const preset = $('ai-preset').value;
  return { song_id: aiState.songId, provider: aiProvider(), brief: $('ai-brief').value,
           preset_id: preset ? Number(preset) : null };
}

function setAiEditors(style, lyrics, originModel) {
  $('ai-style').value = style;
  $('ai-lyrics').value = lyrics;
  aiState.originModel = originModel;
  aiState.unsaved = true;
  updateAiState();
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function generateAi(mode) {
  if (!aiState.songId) { aiMessage(t('ai_err_no_song'), 'error'); return; }
  const body = aiRequestBody();
  body.mode = mode;
  const model = mode === 'api' ? $('ai-model').value.trim() : $('ai-cli-model').value.trim();
  body.model = model;
  if (mode === 'api') body.api_key = $('ai-key').value;
  else body.cli_command = $('ai-cli').value;
  let started;
  try {
    started = await api('/api/ai/generate', { method: 'POST', body });
  } finally {
    $('ai-key').value = '';  // the key is only used for this one request
  }
  const began = Date.now();
  let failures = 0;
  for (;;) {
    aiMessage(t(mode === 'api' ? 'ai_running_api' : 'ai_running_cli', { s: Math.round((Date.now() - began) / 1000) }), 'warn');
    await sleep(1500);
    let job;
    try {
      job = await api('/api/ai/jobs/' + started.job);
      failures = 0;
    } catch (error) {
      if (error.kind !== 'connection' || ++failures > 5) throw error;
      continue;
    }
    if (job.status === 'running') continue;
    if (job.status === 'failed') {
      aiMessage(providerErrorText(job.error.kind, job.error.code, job.error.detail), 'error');
      return;
    }
    setAiEditors(job.style, job.lyrics, mode === 'api' ? model : (model || 'CLI'));
    aiMessage(t('ai_received'));
    return;
  }
}

async function checkAiCli() {
  const result = await api('/api/ai/check-cli', { method: 'POST', body: { provider: aiProvider(), cli_command: $('ai-cli').value } });
  aiMessage(t('ai_cli_found', { provider: aiProvider(), path: result.path }));
}

async function copyAiRequest() {
  if (!aiState.songId) { aiMessage(t('ai_err_no_song'), 'error'); return; }
  const result = await api('/api/ai/request-text', { method: 'POST', body: aiRequestBody() });
  try {
    await navigator.clipboard.writeText(result.text);
  } catch (e) {
    aiMessage(t('ai_copy_failed'), 'error');
    return;
  }
  const opened = window.open(result.url, '_blank', 'noopener');
  aiMessage(t(opened === null ? 'ai_copied_no_window' : 'ai_copied', { url: result.url }));
  $('ai-paste-box').open = true;
}

async function parseAiAnswer(text, source) {
  const result = await api('/api/ai/parse', { method: 'POST', body: { text } });
  if (!confirmReplaceAi(result.style, result.lyrics)) return false;
  setAiEditors(result.style, result.lyrics, IMPORT_MODEL);
  aiMessage(t('ai_imported', { source }));
  return true;
}

function confirmReplaceAi(style, lyrics) {
  const now = aiValues();
  if (!now.style && !now.lyrics) return true;
  if (now.style === style.trim() && now.lyrics === lyrics.trim()) return true;
  return confirm(t('ai_confirm_replace'));
}

async function importAiFile(file) {
  if (file.size > 2 * 1024 * 1024) { aiMessage(t('ai_err_file_size'), 'error'); return; }
  const text = await file.text();
  await parseAiAnswer(text, file.name);
}

async function saveAiVersion() {
  const values = aiValues();
  const body = { provider: aiProvider(), model: aiState.originModel || $('ai-model').value.trim(),
                 style: values.style, lyrics: values.lyrics, brief: $('ai-brief').value };
  const result = await api('/api/songs/' + aiState.songId + '/prompt-versions', { method: 'POST', body });
  aiState.unsaved = false;
  if (result.file_error) aiMessage(t('ai_saved_no_file', { id: result.id, detail: result.file_error }), 'warn');
  else aiMessage(t('ai_saved', { id: result.id, file: result.file }));
  await loadAiVersions();
}

async function createAiSong() {
  const target = aiTarget();
  if (!target || target.song_id) return;
  if (!confirm(t('ai_confirm_song', { project: target.name }))) return;
  await api('/api/projects/' + target.project_id + '/song', { method: 'POST', body: { confirm: true } });
  await loadAiTargets();
  aiMessage(t('ai_song_created', { project: target.name }));
}

async function loadAiVersions() {
  const versions = aiState.songId ? await api('/api/songs/' + aiState.songId + '/versions') : [];
  aiState.version = null;
  $('ai-version-preview').hidden = true;
  const list = $('ai-version-list');
  if (!versions.length) { list.replaceChildren(el('li', t('no_versions'), 'hint')); return; }
  list.replaceChildren(...versions.map((version) => {
    const item = el('li');
    item.append(el('span', '#' + version.id + ' · ' + version.provider));
    item.append(el('span', version.model + ' · ' + version.created_at, 'sub'));
    item.addEventListener('click', () => showAiVersion(version.id, item).catch((error) => aiMessage(aiErrorText(error), 'error')));
    return item;
  }));
}

async function showAiVersion(id, item) {
  aiState.version = await api('/api/versions/' + id);
  document.querySelectorAll('#ai-version-list li').forEach((li) => li.classList.toggle('active', li === item));
  $('ai-version-head').textContent = '#' + aiState.version.id + ' · ' + aiState.version.provider + ' · ' + aiState.version.created_at;
  $('ai-v-style').textContent = aiState.version.style;
  $('ai-v-lyrics').textContent = aiState.version.lyrics;
  $('ai-version-preview').hidden = false;
}

function loadAiVersion() {
  const v = aiState.version;
  if (!v || !confirmReplaceAi(v.style, v.lyrics)) return;
  setAiEditors(v.style, v.lyrics, IMPORT_MODEL);
  aiState.unsaved = false;  // identical to a saved version
  aiMessage(t('ai_version_loaded', { id: v.id }), 'warn');
}

const aiRun = (fn) => () => aiAction(fn);
$('ai-band').addEventListener('change', aiRun(loadAiTargets));
$('ai-project').addEventListener('change', aiRun(aiTargetChanged));
$('ai-provider').addEventListener('change', aiProviderChanged);
$('btn-ai-song').addEventListener('click', aiRun(createAiSong));
$('btn-ai-check').addEventListener('click', aiRun(checkAiCli));
$('btn-ai-api').addEventListener('click', aiRun(() => generateAi('api')));
$('btn-ai-cli').addEventListener('click', aiRun(() => generateAi('cli')));
$('btn-ai-copy').addEventListener('click', aiRun(copyAiRequest));
$('btn-ai-file').addEventListener('click', () => $('ai-file').click());
$('ai-file').addEventListener('change', () => {
  const file = $('ai-file').files[0];
  $('ai-file').value = '';
  if (file) aiAction(() => importAiFile(file));
});
$('btn-ai-paste').addEventListener('click', aiRun(async () => {
  const text = $('ai-paste').value;
  if (!text.trim()) return;
  if (await parseAiAnswer(text, t('ai_source_paste'))) $('ai-paste').value = '';
}));
$('btn-ai-save').addEventListener('click', aiRun(saveAiVersion));
$('btn-ai-load').addEventListener('click', loadAiVersion);
['ai-style', 'ai-lyrics'].forEach((id) => $(id).addEventListener('input', () => { aiState.unsaved = true; updateAiState(); }));

/* ------------------------------------------------------------------ start */

function switchView(name) {
  document.querySelectorAll('.tab').forEach((tab) => tab.classList.toggle('active', tab.dataset.view === name));
  $('view-songs').hidden = name !== 'songs';
  $('view-bands').hidden = name !== 'bands';
  $('view-ai').hidden = name !== 'ai';
  $('view-conn').hidden = name !== 'conn';
  $('view-media').hidden = name !== 'media';
  if (name === 'media' && !$('mr-band').options.length) mrInit().catch((error) => mrMessage('rl-message', mrErrorText(error), 'error'));
  if (name === 'conn' && !connState.info) connInit().catch((error) => connMessage(connErrorText(error), 'error'));
  if (name === 'bands' && !$('band-list').children.length) loadBandList().catch(fatal);
  if (name === 'ai' && !aiState.options) aiAction(aiInit);
}

function fatal(error) {
  const box = $('editor-empty');
  box.textContent = error.message;
  box.hidden = false;
  $('editor-body').hidden = true;
}

async function start() {
  try {
    state.info = await api('/api/info');
    const browser = (navigator.language || 'en').slice(0, 2);
    state.lang = state.info.language !== 'auto' ? state.info.language : (I18N[browser] ? browser : 'en');
    applyLanguage();
    await loadBandsFilter();
    await loadSongs();
  } catch (error) {
    applyLanguage();
    fatal(error);
  }
}

document.querySelectorAll('.tab').forEach((tab) => tab.addEventListener('click', () => switchView(tab.dataset.view)));
$('band-filter').addEventListener('change', () => loadSongs().catch(fatal));
let searchTimer;
$('song-search').addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(() => loadSongs().catch(fatal), 200); });
['f-status', 'f-distributor', 'f-platforms', 'f-style', 'f-lyrics'].forEach((id) => $(id).addEventListener('input', updateCounters));
$('f-status').addEventListener('change', updateCounters);
$('btn-save').addEventListener('click', saveSong);
$('btn-revert').addEventListener('click', revertSong);
$('btn-load-version').addEventListener('click', loadVersionIntoEditor);
window.addEventListener('beforeunload', (event) => {
  // unsaved song changes, or an AI result that was not saved as a version yet
  const aiUnsaved = aiState.unsaved && (aiValues().style || aiValues().lyrics);
  if (isDirty() || aiUnsaved) { event.preventDefault(); event.returnValue = ''; }
});
start();
