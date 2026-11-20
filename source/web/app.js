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
  $('band-body').hidden = false;
  await Promise.all([refreshHardwareChoices(), loadPresets()]);
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

/* ------------------------------------------------------------------ start */

function switchView(name) {
  document.querySelectorAll('.tab').forEach((tab) => tab.classList.toggle('active', tab.dataset.view === name));
  $('view-songs').hidden = name !== 'songs';
  $('view-bands').hidden = name !== 'bands';
  if (name === 'bands' && !$('band-list').children.length) loadBandList().catch(fatal);
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
window.addEventListener('beforeunload', (event) => { if (isDirty()) { event.preventDefault(); event.returnValue = ''; } });
start();
