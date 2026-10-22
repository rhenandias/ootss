/* Data-driven level audio. Media and level metadata load only on demand. */
const LevelAudio = (() => {
  let catalog = { levels: {} };
  let language = 'en';
  let active = null;
  const cache = new Map();

  function setCatalog(value) { catalog = value; }
  function hasLevel(name) { return Boolean(catalog.levels[name]); }
  function hasLog(name) { return Boolean(catalog.logs?.[name]); }
  function hasTrigger(name) { return Boolean(catalog.triggers?.[name]); }
  function close() {
    if (!active) return;
    active.audio.pause();
    active.audio.removeAttribute('src');
    active.audio.load();
    active = null;
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  async function mount(container, level, kind = 'level') {
    close();
    const state = { audio: new Audio(), clip: null, buttons: new Map(), container, sequence: false };
    state.audio.preload = 'none';
    active = state;
    container.textContent = 'Loading audio…';
    let data;
    const key = `${kind}:${level}`;
    const source = kind === 'trigger' ? catalog.triggers?.[level]
      : kind === 'log' ? catalog.logs?.[level] : catalog.levels[level];
    try {
      if (!source) throw new Error('Audio unavailable');
      if (!cache.has(key)) {
        cache.set(key, fetch(source).then(response => {
          if (!response.ok) throw new Error('Audio catalog unavailable');
          return response.json();
        }));
      }
      data = await cache.get(key);
    } catch (error) {
      cache.delete(key);
      if (active === state) container.textContent = 'Audio list could not be loaded. Reopen this popup to retry.';
      return;
    }
    if (active !== state) return;
    container.replaceChildren();
    const toolbar = element('div', 'level-audio-toolbar');
    const heading = element('strong', '', 'Audio');
    const label = element('label', 'level-audio-language');
    label.append(element('span', 'sr-only', 'Transcript language'));
    const select = element('select');
    select.setAttribute('aria-label', 'Transcript language');
    for (const [value, text] of [['en', '🇺🇸 English'], ['pt-br', '🇧🇷 Português']]) {
      const option = element('option', '', text);
      option.value = value;
      select.append(option);
    }
    select.value = language;
    label.append(select);
    const controls = element('div', 'level-audio-controls');
    const playAll = element('button', 'level-audio-play-all');
    playAll.type = 'button';
    const playAllIcon = element('i', 'fa fa-play');
    playAllIcon.setAttribute('aria-hidden', 'true');
    playAll.append(playAllIcon);
    controls.append(label, playAll);
    toolbar.append(heading, controls);
    const playlist = data.conversations.flatMap(group =>
      group.clips.map((clip, index) => ({ ...clip, occurrence: `${group.id}:${index}`,
        speakerName: (clip.speakerName || clip.speaker || '').trim().replace(/^./u, first => first.toLocaleUpperCase('en')),
        conversationTranscripts: group.transcripts })));
    const list = element('div', 'level-audio-list');
    const transcript = element('section', 'level-audio-transcript');
    transcript.setAttribute('aria-label', 'Transcript');
    const transcriptTitle = element('strong');
    const transcriptBody = element('div');
    transcript.append(transcriptTitle, transcriptBody);
    const status = element('div', 'level-audio-status');
    status.setAttribute('role', 'status');
    if (data.conversations.some(group => group.missingClips?.length)) {
      status.textContent = 'Some recordings are unavailable.';
    }
    container.append(toolbar, list, transcript, status);

    function showTranscript() {
      transcriptBody.replaceChildren();
      if (!state.clip) return;
      transcriptTitle.textContent = state.clip.speakerName;
      transcriptBody.lang = language;
      let chunks = state.clip.transcripts[language];
      if (!chunks?.length && state.clip.conversationTranscripts?.[language]?.length) {
        chunks = state.clip.conversationTranscripts[language];
        transcriptTitle.textContent = 'Conversation transcript';
      }
      if (!chunks || !chunks.length) {
        transcriptBody.append(element('p', '', 'Transcript unavailable in this language.'));
      } else {
        for (const text of chunks) transcriptBody.append(element('p', '', text));
      }
    }

    function updateButtons() {
      const playingAll = state.sequence && !state.audio.paused;
      playAllIcon.className = 'fa fa-' + (playingAll ? 'pause' : 'play');
      playAll.setAttribute('aria-label', playingAll ? 'Pause all audio' : 'Play all audio');
      playAll.setAttribute('aria-pressed', String(playingAll));
      playAll.title = playingAll ? 'Pause sequence' : state.sequence ? 'Resume sequence' : 'Play all audio in order';
      playAll.disabled = !playlist.length;
      for (const [occurrence, entry] of state.buttons) {
        const selected = state.clip && state.clip.occurrence === occurrence;
        const playing = selected && !state.audio.paused;
        entry.icon.className = 'fa fa-' + (playing ? 'pause' : 'play');
        entry.button.setAttribute('aria-label', (playing ? 'Pause ' : 'Play ') + entry.clip.speakerName + ': ' + entry.clip.id);
        entry.button.setAttribute('aria-pressed', String(playing));
        entry.row.classList.toggle('is-selected', Boolean(selected));
      }
    }

    function choose(clip) {
      if (!state.clip || state.clip.occurrence !== clip.occurrence || !state.audio.getAttribute('src')) {
        state.audio.pause();
        state.clip = clip;
        state.audio.src = clip.src;
      }
      showTranscript();
      updateButtons();
    }

    async function play(clip, sequence = false) {
      if (active !== state) return;
      state.sequence = sequence;
      const wasPlaying = state.clip && state.clip.occurrence === clip.occurrence && !state.audio.paused;
      choose(clip);
      status.textContent = '';
      if (wasPlaying) {
        state.audio.pause();
        return;
      }
      if (state.audio.ended) state.audio.currentTime = 0;
      try { await state.audio.play(); }
      catch (error) {
        if (active === state && state.clip.occurrence === clip.occurrence && error.name !== 'AbortError') {
          state.sequence = false;
          status.textContent = 'Unable to play this audio. Try again.';
        }
      }
      updateButtons();
    }

    for (const clip of playlist) {
      const row = element('div', 'level-audio-row');
      const button = element('button', 'level-audio-play');
      button.type = 'button';
      const icon = element('i', 'fa fa-play');
      icon.setAttribute('aria-hidden', 'true');
      button.append(icon);
      const name = element('button', 'level-audio-name', clip.speakerName + ' — ' + clip.transcripts.en[0]);
      name.type = 'button';
      name.title = clip.id;
      name.setAttribute('aria-label', 'Show transcript: ' + clip.id);
      const seconds = Math.round(clip.duration);
      const duration = element('span', 'level-audio-duration', Math.floor(seconds / 60) + ':' + String(seconds % 60).padStart(2, '0'));
      row.append(button, name, duration);
      list.append(row);
      state.buttons.set(clip.occurrence, { row, button, icon, clip });
      button.addEventListener('click', () => { play(clip); });
      name.addEventListener('click', () => { state.sequence = false; choose(clip); });
    }
    select.addEventListener('change', () => {
      language = select.value;
      showTranscript();
    });
    playAll.addEventListener('click', () => {
      if (state.sequence && !state.audio.paused) {
        state.audio.pause();
      } else {
        play(state.sequence ? state.clip : playlist[0], true);
      }
    });
    for (const event of ['play', 'pause', 'ended']) state.audio.addEventListener(event, updateButtons);
    state.audio.addEventListener('ended', () => {
      if (active !== state || !state.sequence) return;
      const next = playlist[playlist.findIndex(clip => clip.occurrence === state.clip.occurrence) + 1];
      if (next) {
        play(next, true);
      } else {
        state.sequence = false;
        updateButtons();
      }
    });
    state.audio.addEventListener('error', () => {
      if (active === state) {
        state.sequence = false;
        updateButtons();
        status.textContent = 'Unable to load this audio.';
      }
    });
    const first = playlist[0];
    if (first) {
      // Show a transcript initially without downloading or playing its audio.
      state.clip = first;
      showTranscript();
    }
    updateButtons();
  }

  return { setCatalog, hasLevel, hasLog, hasTrigger, mount, close };
})();
