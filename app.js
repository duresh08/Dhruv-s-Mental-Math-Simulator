(() => {
  "use strict";

  // Same options and defaults as the original Streamlit app.
  const DEFAULTS = {
    ops: { add: true, sub: true, mul: true },
    mode: "audio",
    autoplay: true,
    addMax: 100,
    mul1Max: 12,
    mul2Max: 100,
  };
  const STORAGE_KEY = "mathbot.settings";

  const $ = (id) => document.getElementById(id);
  const el = {
    qnum: $("qnum"), modeLabel: $("modeLabel"), prompt: $("prompt"),
    form: $("answerForm"), input: $("answer"), submit: $("submitBtn"),
    last: $("last"), replay: $("replay"), skip: $("skip"),
    score: $("score"), answered: $("answered"), accuracy: $("accuracy"),
    streak: $("streak"), best: $("best"),
    log: $("log"), empty: $("empty"), reset: $("reset"),
    dialog: $("settings"), openSettings: $("openSettings"),
    ops: $("ops"), mode: $("mode"), autoplay: $("autoplay"),
    addMax: $("addMax"), mul1Max: $("mul1Max"), mul2Max: $("mul2Max"),
    rangeNote: $("rangeNote"),
  };

  const canSpeak = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;

  let settings = loadSettings();
  let state = freshState();

  function freshState() {
    return { score: 0, answered: 0, correct: 0, streak: 0, best: 0, n: 0, q: null, last: null, log: [], started: false, speaking: false };
  }

  function loadSettings() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (saved) return { ...DEFAULTS, ...saved, ops: { ...DEFAULTS.ops, ...saved.ops } };
    } catch (_) { /* storage unavailable */ }
    return structuredClone(DEFAULTS);
  }

  function saveSettings() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(settings)); } catch (_) { /* ignore */ }
  }

  const fmt = (n) => n.toLocaleString("en-US");
  const rand = (lo, hi) => lo + Math.floor(Math.random() * (hi - lo + 1));
  const audioMode = () => settings.mode === "audio" && canSpeak;

  // ---------------------------------------------------------------------------
  // Questions
  // ---------------------------------------------------------------------------
  function makeQuestion() {
    const ops = Object.keys(settings.ops).filter((k) => settings.ops[k]);
    const op = ops[Math.floor(Math.random() * ops.length)];
    let a, b;
    if (op === "add") {
      a = rand(2, settings.addMax); b = rand(2, settings.addMax);
      return { a, b, sym: "+", word: "plus", answer: a + b };
    }
    if (op === "sub") {
      [a, b] = [rand(2, settings.addMax), rand(2, settings.addMax)].sort((x, y) => y - x);
      return { a, b, sym: "−", word: "minus", answer: a - b };
    }
    a = rand(2, settings.mul1Max); b = rand(2, settings.mul2Max);
    if (Math.random() < 0.5) [a, b] = [b, a];
    return { a, b, sym: "×", word: "multiplied by", answer: a * b };
  }

  // ---------------------------------------------------------------------------
  // Speech
  // ---------------------------------------------------------------------------
  let voice = null;
  function pickVoice() {
    const voices = speechSynthesis.getVoices().filter((v) => /^en(-|_|$)/i.test(v.lang));
    const preferred = ["Google US English", "Samantha", "Microsoft Aria", "Microsoft Jenny", "Daniel", "Google UK English Female"];
    voice = preferred.map((name) => voices.find((v) => v.name.includes(name))).find(Boolean)
      || voices.find((v) => v.lang === "en-US") || voices[0] || null;
  }
  if (canSpeak) {
    pickVoice();
    speechSynthesis.addEventListener?.("voiceschanged", pickVoice);
  }

  function speak() {
    if (!audioMode() || !state.q) return;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(`${state.q.a} ${state.q.word} ${state.q.b}`);
    u.lang = "en-US";
    if (voice) u.voice = voice;
    u.rate = 1;
    u.onstart = () => setSpeaking(true);
    u.onend = u.onerror = () => setSpeaking(false);
    speechSynthesis.speak(u);
  }

  function setSpeaking(on) {
    state.speaking = on;
    el.prompt.classList.toggle("speaking", on);
  }

  // ---------------------------------------------------------------------------
  // Flow
  // ---------------------------------------------------------------------------
  function start() {
    state.started = true;
    el.input.disabled = false;
    el.submit.disabled = false;
    next();
  }

  function next() {
    state.q = makeQuestion();
    state.n += 1;
    el.input.value = "";
    render();
    if (settings.autoplay) speak();
    el.input.focus();
  }

  function submit() {
    if (!state.started) return start();
    const raw = el.input.value.trim();
    if (!raw || raw === "-") return;
    const given = Number(raw);
    const q = state.q;
    const ok = given === q.answer;

    state.answered += 1;
    if (ok) {
      state.score += 1; state.correct += 1; state.streak += 1;
      state.best = Math.max(state.best, state.streak);
    } else {
      state.score -= 1; state.streak = 0;
    }
    state.last = { q, given, ok };
    state.log.unshift({ n: state.n, q, given, ok });
    next();
  }

  function skip() {
    if (!state.started) return;
    state.last = null;
    next();
  }

  // ---------------------------------------------------------------------------
  // Rendering
  // ---------------------------------------------------------------------------
  function render() {
    renderPrompt();
    renderLast();
    renderStats();
    renderLog();
    el.qnum.textContent = state.started ? `Question ${state.n}` : "Ready";
    el.modeLabel.textContent = audioMode() ? "Audio" : "Visual";
    el.replay.hidden = !audioMode();
    el.replay.firstChild.textContent = settings.autoplay ? "Replay " : "Play ";
  }

  function renderPrompt() {
    if (!state.started) {
      el.prompt.innerHTML = `<button type="button" class="start" id="startBtn">Start</button><span class="start-hint">${
        audioMode() ? "Turn your sound on. Questions are read aloud." : "Questions are shown on screen."
      }</span>`;
      $("startBtn").addEventListener("click", start);
      return;
    }
    const q = state.q;
    if (audioMode()) {
      el.prompt.innerHTML = `<span class="listen"><span class="bars" aria-hidden="true"><i></i><i></i><i></i><i></i></span>Listen</span>`;
      el.prompt.classList.toggle("speaking", state.speaking);
    } else {
      el.prompt.innerHTML = `<span>${fmt(q.a)}</span><span class="op">${q.sym}</span><span>${fmt(q.b)}</span>`;
    }
  }

  function renderLast() {
    const l = state.last;
    if (!l) { el.last.innerHTML = ""; return; }
    const eq = `<span class="eq">${fmt(l.q.a)} ${l.q.sym} ${fmt(l.q.b)} = ${fmt(l.q.answer)}</span>`;
    el.last.innerHTML = l.ok
      ? `${eq}<span class="good">Correct</span>`
      : `${eq}<span class="bad">You answered ${fmt(l.given)}</span>`;
  }

  function renderStats() {
    el.score.textContent = state.score > 0 ? `+${state.score}` : String(state.score).replace("-", "−");
    el.score.className = state.score > 0 ? "good" : state.score < 0 ? "bad" : "";
    el.answered.textContent = state.answered;
    el.accuracy.textContent = state.answered ? `${Math.round((100 * state.correct) / state.answered)}%` : "–";
    el.streak.textContent = state.streak;
    el.best.textContent = state.best;
  }

  function renderLog() {
    el.empty.hidden = state.log.length > 0;
    document.querySelector(".row-head").hidden = state.log.length === 0;
    el.log.innerHTML = state.log.slice(0, 50).map((r) => `
      <li class="row">
        <span class="n">${r.n}</span>
        <span>${fmt(r.q.a)} ${r.q.sym} ${fmt(r.q.b)}</span>
        <span class="${r.ok ? "" : "wrong"}">${fmt(r.given)}</span>
        <span>${fmt(r.q.answer)}</span>
        <span class="${r.ok ? "plus" : "minus"}">${r.ok ? "+1" : "−1"}</span>
      </li>`).join("");
  }

  // ---------------------------------------------------------------------------
  // Settings dialog
  // ---------------------------------------------------------------------------
  let snapshot = "";

  function syncSettingsUI() {
    const enabled = Object.values(settings.ops).filter(Boolean).length;
    el.ops.querySelectorAll("button").forEach((b) => {
      const on = settings.ops[b.dataset.op];
      b.setAttribute("aria-pressed", on);
      b.title = on && enabled === 1 ? "At least one operation has to stay on" : "";
    });
    el.mode.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.mode === settings.mode));
    el.autoplay.checked = settings.autoplay;
    el.autoplay.disabled = settings.mode !== "audio";
    el.autoplay.parentElement.classList.toggle("disabled", settings.mode !== "audio");
    for (const k of ["addMax", "mul1Max", "mul2Max"]) {
      el[k].value = settings[k];
      $(`${k}Out`).textContent = fmt(settings[k]);
    }
    el.rangeNote.textContent =
      `(2–${fmt(settings.addMax)}) ± (2–${fmt(settings.addMax)})\n(2–${fmt(settings.mul1Max)}) × (2–${fmt(settings.mul2Max)})`;
  }

  el.ops.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-op]");
    if (!b) return;
    const op = b.dataset.op;
    const enabled = Object.values(settings.ops).filter(Boolean).length;
    if (settings.ops[op] && enabled === 1) return; // keep at least one
    settings.ops[op] = !settings.ops[op];
    syncSettingsUI();
  });

  el.mode.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-mode]");
    if (!b) return;
    settings.mode = b.dataset.mode;
    syncSettingsUI();
  });

  el.autoplay.addEventListener("change", () => { settings.autoplay = el.autoplay.checked; });

  for (const k of ["addMax", "mul1Max", "mul2Max"]) {
    el[k].addEventListener("input", () => { settings[k] = Number(el[k].value); syncSettingsUI(); });
  }

  el.openSettings.addEventListener("click", () => {
    snapshot = JSON.stringify(settings);
    syncSettingsUI();
    el.dialog.showModal();
  });

  el.dialog.addEventListener("click", (e) => { if (e.target === el.dialog) el.dialog.close(); });

  el.dialog.addEventListener("close", () => {
    const changed = JSON.stringify(settings) !== snapshot;
    saveSettings();
    if (!changed) { if (state.started) el.input.focus(); return; }
    if (canSpeak) speechSynthesis.cancel();
    if (state.started) { state.last = null; next(); } else render();
  });

  // ---------------------------------------------------------------------------
  // Input & shortcuts
  // ---------------------------------------------------------------------------
  el.form.addEventListener("submit", (e) => { e.preventDefault(); submit(); });

  el.input.addEventListener("input", () => {
    const v = el.input.value;
    const cleaned = v.replace(/[^\d-]/g, "").replace(/(?!^)-/g, "");
    if (cleaned !== v) el.input.value = cleaned;
  });

  el.input.addEventListener("keydown", (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const key = e.key.toLowerCase();
    if (key === "r") { e.preventDefault(); speak(); }
    else if (key === "s") { e.preventDefault(); skip(); }
  });

  document.addEventListener("keydown", (e) => {
    if (el.dialog.open || e.target === el.input) return;
    if (!state.started && e.key === "Enter" && e.target === document.body) { e.preventDefault(); start(); }
  });

  el.replay.addEventListener("click", () => { speak(); el.input.focus(); });
  el.skip.addEventListener("click", skip);

  el.reset.addEventListener("click", () => {
    if (canSpeak) speechSynthesis.cancel();
    const wasStarted = state.started;
    state = freshState();
    if (wasStarted) { state.started = true; next(); } else render();
  });

  render();
})();
