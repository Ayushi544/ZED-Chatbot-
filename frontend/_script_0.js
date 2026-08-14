
    // ─── Config ───────────────────────────────────────────
    const API = window.location.hostname === 'localhost'
      ? 'http://localhost:8000'
      : window.location.origin;

    let lang = 'English';
    let chatHistory = [];
    let sectorHistory = [];
    let chatBusy = false;
    let sectorBusy = false;

    // Attached file context per tab
    const attachedFile = { chat: null, sector: null };

    // Speech recognition instances
    let chatRecognition = null;
    let sectorRecognition = null;
    let activeVoice = null; // 'chat' | 'sector' | null

    // ─── Init ──────────────────────────────────────────────
    window.addEventListener('DOMContentLoaded', () => {
      checkStatus();
      buildChatChips();
      buildQuickRow('chatQuick', CHAT_QUICK);
      buildQuickRow('sectorQuick', SECTOR_QUICK, true);
      buildQuestions();

      // Enable send as user types
      document.getElementById('chatInput').addEventListener('input', updateChatSendBtn);
      document.getElementById('sectorInput').addEventListener('input', updateSectorSendBtn);

      // Enter key default: send (Ctrl+Enter = new line)
      document.getElementById('chatInput').addEventListener('keydown', chatKey);
      document.getElementById('sectorInput').addEventListener('keydown', sectorKey);
    });

    function detectAndSetLanguage(text) {
      if (!text) return;
      const maps = [
        { lang: 'Hindi', regex: /[\u0900-\u097F]/ },     // Devanagari (Hindi/Marathi)
        { lang: 'Bengali', regex: /[\u0980-\u09FF]/ },   // Bengali
        { lang: 'Telugu', regex: /[\u0c00-\u0c7F]/ },    // Telugu
        { lang: 'Tamil', regex: /[\u0b80-\u0bff]/ },     // Tamil
        { lang: 'Gujarati', regex: /[\u0a80-\u0aff]/ },  // Gujarati
        { lang: 'Kannada', regex: /[\u0c80-\u0cff]/ },   // Kannada
        { lang: 'Malayalam', regex: /[\u0d00-\u0d7f]/ }, // Malayalam
        { lang: 'Punjabi', regex: /[\u0a00-\u0a7f]/ },   // Gurmukhi/Punjabi
        { lang: 'Odia', regex: /[\u0b00-\u0b7f]/ },      // Odia
        { lang: 'Urdu', regex: /[\u0600-\u06FF]/ }        // Arabic/Urdu
      ];
      for (const m of maps) {
        if (m.regex.test(text)) {
          if (lang !== m.lang) {
            if (m.lang === 'Hindi' && lang === 'Marathi') {
              break;
            }
            const selectEl = document.getElementById('langSel');
            if (selectEl) {
              selectEl.value = m.lang;
              setLang(m.lang);
            }
          }
          break;
        }
      }
    }

    function updateChatSendBtn() {
      const val = document.getElementById('chatInput').value;
      detectAndSetLanguage(val);
      const hasText = val.trim() !== '';
      document.getElementById('chatSend').disabled = (!hasText && !attachedFile.chat) || chatBusy;
    }

    function updateSectorSendBtn() {
      const val = document.getElementById('sectorInput').value;
      detectAndSetLanguage(val);
      const hasText = val.trim() !== '';
      document.getElementById('sectorSend').disabled = (!hasText && !attachedFile.sector) || sectorBusy;
    }

    // ─── Quick prompts ──────────────────────────────────────
    const CHAT_CHIPS = [
      "What is ZED certification?",
      "How to get Bronze?",
      "Subsidy for micro enterprise?",
      "Documents needed?",
      "ISO 9001 benefit in ZED?",
      "What is the ZED Pledge?"
    ];
    const CHAT_QUICK = [
      "How to apply for Bronze?",
      "What documents do I need?",
      "How much subsidy?",
      "ZED Pledge process?",
      "Which ISO certs waive params?"
    ];
    const SECTOR_QUICK = [
      "Key parameters for my sector?",
      "What documents does this sector need?",
      "Common gaps in this sector?",
      "Energy requirements?",
      "Quality system needed?"
    ];

    function buildChatChips() {
      document.getElementById('chatChips').innerHTML =
        CHAT_CHIPS.map(q =>
          `<button class="chip" onclick="chatSendText('${esc2(q)}')">${q}</button>`
        ).join('');
    }

    function buildQuickRow(id, items, isSector = false) {
      const fn = isSector ? 'sectorSendText' : 'chatSendText';
      document.getElementById(id).innerHTML =
        items.map(q =>
          `<button class="qchip" onclick="${fn}('${esc2(q)}')">${q}</button>`
        ).join('');
    }

    // ─── Tab switch ────────────────────────────────────────
    function switchTab(name, btn) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('panel-' + name).classList.add('active');
    }

    // ─── Language ──────────────────────────────────────────
    function setLang(val) {
      lang = val;
      document.documentElement.dir = val === 'Urdu' ? 'rtl' : 'ltr';
      // Update UI placeholders by language
      const PLACEHOLDERS = {
        Hindi: 'ZED प्रमाणन के बारे में पूछें…',
        Bengali: 'ZED সার্টিফিকেশন সম্পর্কে জিজ্ঞাসা করুন…',
        Telugu: 'ZED సర్టిఫికేషన్ గురించి అడగండి…',
        Marathi: 'ZED प्रमाणन विषयी विचारा…',
        Tamil: 'ZED சான்றிதழ் பற்றி கேளுங்கள்…',
        Gujarati: 'ZED પ્રમાણપત્ર વિશે પૂછો…',
        Kannada: 'ZED ಪ್ರಮಾಣಪತ್ರದ ಬಗ್ಗೆ ಕೇಳಿ…',
        Malayalam: 'ZED സർട്ടിഫിക്കേഷനെ കുറിച്ച് ചോദിക്കൂ…',
        Punjabi: 'ZED ਸਰਟੀਫਿਕੇਸ਼ਨ ਬਾਰੇ ਪੁੱਛੋ…',
        Odia: 'ZED ସାର୍ଟିଫିକେସନ ବିଷୟରେ ପଚାରନ୍ତୁ…',
        Urdu: 'ZED سرٹیفیکیشن کے بارے میں پوچھیں…',
        English: 'Ask about ZED certification…',
      };
      const ph = PLACEHOLDERS[val] || PLACEHOLDERS.English;
      document.getElementById('chatInput').placeholder = ph;
      document.getElementById('sectorInput').placeholder = ph;

      // Update hint
      const HINT_SEND = {
        Hindi: 'भेजने के लिए Enter दबाएं', Urdu: 'بھیجنے کے لیے Enter دبائیں',
      };
      document.getElementById('chatHint').textContent =
        (HINT_SEND[val] || 'Press Enter to send') + ' · Ctrl+Enter for new line';
    }

    // ─── Status ───────────────────────────────────────────
    async function checkStatus() {
      const dot = document.getElementById('sdot');
      const txt = document.getElementById('stext');
      try {
        const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(6000) });
        const data = await res.json();
        dot.style.background = '#4ade80';
        txt.textContent = data.groq_connected
          ? (data.rag_loaded ? 'AI + RAG connected' : 'AI connected')
          : 'fallback mode';
        // Both send buttons ready
        updateChatSendBtn();
        updateSectorSendBtn();
      } catch {
        dot.style.background = '#f87171';
        txt.textContent = 'offline — backend not reachable';
        // Still allow user to type and send (graceful degradation)
        updateChatSendBtn();
        updateSectorSendBtn();
      }
    }

    // ─── TAB 1: Chat ──────────────────────────────────────
    function chatKey(e) {
      if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        chatSend();
      }
    }

    async function chatSend() {
      const box = document.getElementById('chatInput');
      const q = box.value.trim();
      const file = attachedFile.chat;
      if ((!q && !file) || chatBusy) return;
      box.value = '';
      resize(box);
      await chatSendText(q || '(see attached file)', file);
      clearFile('chat');
    }

    async function chatSendText(q, file = null) {
      if (chatBusy) return;
      removeEl('chatWelcome');
      appendMsg('chatMsgs', 'user', q, null, false, file);
      chatHistory.push({ role: 'user', content: q });
      chatBusy = true;
      document.getElementById('chatSend').disabled = true;
      showTyping('chatMsgs');

      try {
        const body = { message: q, history: chatHistory.slice(-8), language: lang };
        if (file) body.filename = file.name;

        const res = await fetch(`${API}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
          signal: AbortSignal.timeout(30000)
        });
        if (!res.ok) throw new Error(`${res.status}`);
        const data = await res.json();
        removeTyping('chatMsgs');
        appendMsg('chatMsgs', 'bot', data.reply, data.source);
        chatHistory.push({ role: 'assistant', content: data.reply });
      } catch (e) {
        removeTyping('chatMsgs');
        appendErr('chatMsgs', e.name === 'TimeoutError'
          ? 'Response timed out. Try again.'
          : `Cannot reach server. Is the backend running?\n${e.message}`);
      }
      chatBusy = false;
      updateChatSendBtn();
      scroll('chatMsgs');
    }

    // ─── TAB 2: Assessment ───────────────────────────────
    const QUESTIONS = [];

    async function buildQuestions() {
      const qs = [
        { id: 1, parameter: "Leadership", question: "Do you have a written quality policy in your enterprise?" },
        { id: 2, parameter: "Leadership", question: "Have you appointed a quality champion or ZED coordinator?" },
        { id: 3, parameter: "5S Workplace", question: "Is your workplace free of unnecessary items and clutter?" },
        { id: 4, parameter: "5S Workplace", question: "Do tools and materials have fixed, labelled storage locations?" },
        { id: 5, parameter: "5S Workplace", question: "Is there a regular cleaning schedule followed by workers?" },
        { id: 6, parameter: "Quality Management", question: "Do you maintain inspection records for finished products?" },
        { id: 7, parameter: "Quality Management", question: "Do you have a process to record and resolve customer complaints?" },
        { id: 8, parameter: "Quality Management", question: "Are your production processes documented with work instructions?" },
        { id: 9, parameter: "Customer Satisfaction", question: "Do you track on-time delivery performance?" },
        { id: 10, parameter: "Customer Satisfaction", question: "Have you done any customer satisfaction survey in the last year?" },
        { id: 11, parameter: "Lean & Waste", question: "Have you identified the main sources of waste in your production?" },
        { id: 12, parameter: "Lean & Waste", question: "Have you taken steps to reduce material wastage or rework?" },
        { id: 13, parameter: "Energy & Environment", question: "Do you record monthly electricity and fuel consumption?" },
        { id: 14, parameter: "Energy & Environment", question: "Do you have a proper waste disposal process?" },
        { id: 15, parameter: "Occupational H&S", question: "Do workers use required Personal Protective Equipment (PPE)?" },
        { id: 16, parameter: "Occupational H&S", question: "Are fire safety equipment and emergency exits clearly marked?" },
        { id: 17, parameter: "IT Adoption", question: "Do you use any digital tool for accounts, billing, or inventory?" },
        { id: 18, parameter: "IT Adoption", question: "Do you accept digital payments (UPI, NEFT, etc.)?" },
        { id: 19, parameter: "Benchmarking", question: "Are you a member of any industry or trade association?" },
        { id: 20, parameter: "Social Responsibility", question: "Do you comply with applicable labour laws?" },
      ];
      QUESTIONS.push(...qs);

      const container = document.getElementById('qList');
      container.innerHTML = qs.map(q => `
        <div class="q-block" id="qb${q.id}">
          <div style="flex:1">
            <div class="q-text">${q.question}</div>
            <div class="q-param">${q.parameter}</div>
          </div>
          <div class="toggle">
            <button class="tog-btn yes" onclick="setAnswer(${q.id},'yes',this)">Yes</button>
            <button class="tog-btn no"  onclick="setAnswer(${q.id},'no',this)">No</button>
          </div>
        </div>`).join('');
    }

    const answers = {};
    function setAnswer(id, val, btn) {
      answers[id] = val === 'yes';
      const block = document.getElementById('qb' + id);
      block.querySelectorAll('.tog-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }

    async function submitAssess() {
      const name = document.getElementById('entName').value.trim();
      const sector = document.getElementById('entSector').value;
      const type = document.getElementById('entType').value;
      const targetCert = document.getElementById('entTargetCert').value;
      const specialCategory = document.getElementById('entSpecialCategory').value;

      if (!name) { alert('Please enter your enterprise name.'); return; }
      if (!sector) { alert('Please select your sector.'); return; }

      const unanswered = QUESTIONS.filter(q => answers[q.id] === undefined);
      if (unanswered.length > 0) {
        alert(`Please answer all questions. ${unanswered.length} remaining.`); return;
      }

      const btn = document.getElementById('assessSubmit');
      btn.disabled = true;
      btn.textContent = 'Analysing…';

      const ansObj = {};
      QUESTIONS.forEach(q => { ansObj[String(q.id)] = answers[q.id]; });

      try {
        const res = await fetch(`${API}/assessment`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            enterprise_name: name,
            sector,
            enterprise_type: type,
            answers: ansObj,
            target_cert: targetCert,
            special_category: specialCategory
          }),
          signal: AbortSignal.timeout(45000)
        });
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();
        showResult(data);
      } catch (e) {
        alert(`Error: ${e.message}. Is the backend running?`);
      }
      btn.disabled = false;
      btn.textContent = 'Get My Readiness Score & Roadmap';
    }

    function showResult(data) {
      document.getElementById('assessForm').style.display = 'none';
      const card = document.getElementById('resultCard');
      card.classList.add('show');
      document.getElementById('rScore').textContent = data.score;
      document.getElementById('rLabel').textContent = data.readiness;
      document.getElementById('rNote').textContent = data.readiness_note;
      document.getElementById('rSubsidy').textContent = data.subsidy_eligible;
      document.getElementById('rStrengths').innerHTML = data.strengths.length
        ? `<h4>✅ Strengths</h4><div class="tag-row">${data.strengths.map(s => `<span class="tag ok">${s}</span>`).join('')}</div>`
        : '';
      document.getElementById('rGaps').innerHTML = data.gaps.length
        ? `<h4>⚠️ Gaps to Address</h4><div class="tag-row">${data.gaps.map(g => `<span class="tag gap">${g}</span>`).join('')}</div>`
        : '<h4>✅ No Major Gaps</h4>';
      document.getElementById('rRoadmap').textContent = data.roadmap || 'Roadmap not available.';
      card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function resetAssess() {
      document.getElementById('resultCard').classList.remove('show');
      document.getElementById('assessForm').style.display = '';
      Object.keys(answers).forEach(k => delete answers[k]);
      document.querySelectorAll('.tog-btn').forEach(b => b.classList.remove('active'));
      document.getElementById('assessWrap').scrollTop = 0;
    }

    // ─── TAB 3: Sector Guidance ──────────────────────────
    function sectorKey(e) {
      if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
        e.preventDefault(); sectorSend();
      }
    }

    async function sectorSend() {
      const box = document.getElementById('sectorInput');
      const q = box.value.trim();
      const file = attachedFile.sector;
      if ((!q && !file) || sectorBusy) return;
      box.value = ''; resize(box);
      await sectorSendText(q || '(see attached file)', file);
      clearFile('sector');
    }

    async function sectorSendText(q, file = null) {
      if (sectorBusy) return;
      appendMsg('sectorMsgs', 'user', q, null, false, file);
      sectorHistory.push({ role: 'user', content: q });
      sectorBusy = true;
      document.getElementById('sectorSend').disabled = true;
      showTyping('sectorMsgs');

      const sector = document.getElementById('sectorSel').value;

      try {
        const res = await fetch(`${API}/sector-chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: q, sector: sector || null, history: sectorHistory.slice(-6), language: lang }),
          signal: AbortSignal.timeout(30000)
        });
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();
        removeTyping('sectorMsgs');
        appendMsg('sectorMsgs', 'bot', data.reply, data.source, true);
        sectorHistory.push({ role: 'assistant', content: data.reply });
      } catch (e) {
        removeTyping('sectorMsgs');
        appendErr('sectorMsgs', `Cannot reach server: ${e.message}`);
      }
      sectorBusy = false;
      updateSectorSendBtn();
      scroll('sectorMsgs');
    }

    // ─── File attachment ─────────────────────────────────
    function handleFile(tab, input) {
      const file = input.files[0];
      if (!file) return;
      attachedFile[tab] = file;
      document.getElementById(tab + 'FileName').textContent = file.name;
      document.getElementById(tab + 'FileBadge').style.display = 'inline-flex';
      if (tab === 'chat') updateChatSendBtn();
      if (tab === 'sector') updateSectorSendBtn();
    }

    function clearFile(tab) {
      attachedFile[tab] = null;
      document.getElementById(tab + 'FileBadge').style.display = 'none';
      document.getElementById(tab + 'FileInput').value = '';
      if (tab === 'chat') updateChatSendBtn();
      if (tab === 'sector') updateSectorSendBtn();
    }

    // ─── Voice input ──────────────────────────────────────
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

    function getLangCode(l) {
      const map = {
        English: 'en-IN', Hindi: 'hi-IN', Bengali: 'bn-IN', Telugu: 'te-IN',
        Marathi: 'mr-IN', Tamil: 'ta-IN', Gujarati: 'gu-IN', Kannada: 'kn-IN',
        Malayalam: 'ml-IN', Punjabi: 'pa-IN', Odia: 'or-IN', Urdu: 'ur-PK'
      };
      return map[l] || 'en-IN';
    }

    function toggleVoice(tab) {
      if (!SpeechRec) {
        showToast('Speech recognition not supported in this browser.');
        return;
      }
      // Stop any active recording
      if (activeVoice) {
        stopVoice(activeVoice);
        if (activeVoice === tab) return; // toggled off
      }
      startVoice(tab);
    }

    function startVoice(tab) {
      const rec = new SpeechRec();
      rec.lang = getLangCode(lang);
      rec.interimResults = true;
      rec.maxAlternatives = 1;

      const inputEl = document.getElementById(tab + 'Input');
      const voiceBtn = document.getElementById(tab + 'VoiceBtn');
      let finalT = '';

      rec.onstart = () => {
        activeVoice = tab;
        voiceBtn.classList.add('recording');
        voiceBtn.textContent = '🔴';
        showToast('🎙️ Listening…', true);
      };

      rec.onresult = (e) => {
        let interim = '';
        finalT = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {
          if (e.results[i].isFinal) finalT += e.results[i][0].transcript;
          else interim += e.results[i][0].transcript;
        }
        inputEl.value = finalT || interim;
        resize(inputEl);
        if (tab === 'chat') updateChatSendBtn();
        if (tab === 'sector') updateSectorSendBtn();
      };

      rec.onerror = (e) => {
        showToast('Voice error: ' + e.error);
        stopVoice(tab, rec);
      };

      rec.onend = () => stopVoice(tab, rec);

      if (tab === 'chat') chatRecognition = rec;
      if (tab === 'sector') sectorRecognition = rec;

      rec.start();
    }

    function stopVoice(tab, recInstance) {
      const rec = recInstance || (tab === 'chat' ? chatRecognition : sectorRecognition);
      if (rec) { try { rec.stop(); } catch (e) { } }
      const voiceBtn = document.getElementById(tab + 'VoiceBtn');
      if (voiceBtn) { voiceBtn.classList.remove('recording'); voiceBtn.textContent = '🎙️'; }
      hideToast();
      if (activeVoice === tab) activeVoice = null;
    }

    function showToast(msg, persist = false) {
      const t = document.getElementById('voiceToast');
      t.textContent = msg;
      t.classList.add('show');
      if (!persist) setTimeout(() => t.classList.remove('show'), 2500);
    }

    function hideToast() {
      document.getElementById('voiceToast').classList.remove('show');
    }

    // ─── Shared UI helpers ────────────────────────────────
    function appendMsg(containerId, role, text, source, isRag = false, file = null) {
      const c = document.getElementById(containerId);
      const row = document.createElement('div');
      row.className = `msg-row ${role}`;

      const icon = role === 'user' ? '👤' : (isRag ? '📂' : '🏭');
      let content = fmt(text);
      if (file && role === 'user') {
        content = `📎 <em style="font-size:12px;opacity:.8">${esc(file.name)}</em><br>${content}`;
      }
      row.innerHTML = `<div class="avatar">${icon}</div><div class="bubble">${content}</div>`;

      if (source && role === 'bot') {
        const wrap = document.createElement('div');
        wrap.style.cssText = 'display:flex;flex-direction:column;align-items:flex-start';
        wrap.appendChild(row);
        const src = document.createElement('div');
        src.className = `src-tag${isRag ? ' rag' : ''}`;
        src.textContent = isRag
          ? `📄 ${source}`
          : (source === 'groq' ? '✦ AI · ZED official knowledge' : '📚 Built-in knowledge');
        src.style.paddingLeft = '38px';
        wrap.appendChild(src);
        c.appendChild(wrap);
      } else {
        c.appendChild(row);
      }
      scroll(containerId);
    }

    function appendErr(containerId, msg) {
      const c = document.getElementById(containerId);
      const row = document.createElement('div');
      row.className = 'msg-row bot';
      row.innerHTML = `<div class="avatar">🏭</div><div class="err-bubble">⚠️ ${esc(msg)}</div>`;
      c.appendChild(row);
      scroll(containerId);
    }

    function showTyping(containerId) {
      const c = document.getElementById(containerId);
      const el = document.createElement('div');
      el.className = 'msg-row bot';
      el.id = containerId + '_typing';
      el.innerHTML = `<div class="avatar">🏭</div>
        <div class="typing"><div class="td"></div><div class="td"></div><div class="td"></div></div>`;
      c.appendChild(el);
      scroll(containerId);
    }

    function removeTyping(containerId) {
      document.getElementById(containerId + '_typing')?.remove();
    }

    function removeEl(id) { document.getElementById(id)?.remove(); }

    function scroll(id) {
      const el = document.getElementById(id);
      if (el) el.scrollTop = el.scrollHeight;
    }

    function resize(el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 108) + 'px';
    }

    function esc(s) {
      return String(s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function esc2(s) { return s.replace(/'/g, "\\'"); }

    function fmt(text) {
      let t = esc(text);
      t = t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      t = t.replace(/^[•\-] (.+)$/gm, '<span style="display:block;padding-left:10px;">• $1</span>');
      t = t.replace(/^(\d+)\. (.+)$/gm, '<span style="display:block;padding-left:10px;">$1. $2</span>');
      t = t.replace(/\n/g, '<br>');
      return t;
    }
  