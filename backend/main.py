"""
ZED AI Advisor — Backend
=========================
5 endpoints:
  POST /chat          → Tab 1: Ask ZED (general chatbot)
  POST /assessment    → Tab 2: Score + AI roadmap
  POST /sector-chat   → Tab 3: RAG over sector documents
  POST /translate     → Full-page UI translation
  POST /whatsapp      → WhatsApp webhook (Twilio)

Run: uvicorn main:app --reload --port 8000
"""

import os
import re
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict
from groq import Groq
from dotenv import load_dotenv


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
groq_client  = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not set - fallback mode active")

# ── Twilio WhatsApp config ──
TWILIO_ACCOUNT_SID    = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN      = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

from rag import retrieve

DATA_DIR     = Path(__file__).parent.parent / "data"
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

ASSESSMENT_QUESTIONS = []
aq_path = DATA_DIR / "assessment_questions.json"
if aq_path.exists():
    with open(aq_path, encoding="utf-8") as f:
        ASSESSMENT_QUESTIONS = json.load(f)
    print(f"Loaded {len(ASSESSMENT_QUESTIONS)} assessment questions")

app = FastAPI(title="ZED AI Advisor", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

ZED_KNOWLEDGE = """
You are ZED Mitra, a helpful assistant for the MSME Sustainable (ZED) Certification Scheme
by the Ministry of MSME, Government of India. Only answer ZED-related questions.

BRONZE: Desktop assessment, 1-3 months, 80% subsidy for Micro
SILVER: Remote verification, 3-6 months
GOLD: Onsite inspection, 6-12 months

STEPS: UDYAM registration → ZED Pledge → WASH cert (free) → Apply → Upload docs → Assessment → Certificate

DOCUMENTS FOR BRONZE: Udyam cert, PAN, GST cert, 3 workplace photos, org chart, quality policy draft

SUBSIDY: Micro 80%, Small 60%, Medium 50%. Extra 10% for women-owned, SC/ST, NER, J&K

10 PARAMETERS:
1. Leadership (10%) 2. 5S Workplace (15%) 3. QMS Quality (20%) 4. Customer Satisfaction (10%)
5. Lean & Waste (10%) 6. Energy & Environment (15%) 7. OHS Safety (10%)
8. IT Adoption (5%) 9. Benchmarking (3%) 10. Social Responsibility (2%)

ISO WAIVERS: ISO 9001 waivers QMS(20%), ISO 45001 waivers OHS(10%), IATF 16949 waivers QMS+Lean(30%), FSSAI waivers food QMS
LANGUAGE RULE: Always reply in the SAME language the user writes in. Hindi to Hindi. English to English. Hinglish to Hinglish.
"""


class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    language: str = "English"

class ChatResponse(BaseModel):
    reply: str
    source: str

class AssessmentRequest(BaseModel):
    enterprise_name: str
    sector: str
    enterprise_type: str
    answers: Dict[str, Dict[str, int]]
    target_cert: Optional[str] = "Advise"
    special_category: Optional[str] = "None"
    iso_certifications: List[str] = []
    language: str = "English"

class SectorChatRequest(BaseModel):
    message: str
    sector: Optional[str] = None
    history: List[Message] = []
    language: str = "English"

class TranslateRequest(BaseModel):
    texts: List[str]
    target_language: str


def call_groq(messages: list, max_tokens: int = 700) -> str:
    if not groq_client:
        return None
    try:
        res = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.4,
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq error: {e}")
        return None

FALLBACK = {
    "bronze":   "Bronze: Desktop assessment, 1-3 months, up to 80% subsidy. Documents: Udyam cert, PAN, factory photos, quality policy draft. Apply at zed.msme.gov.in",
    "silver":   "Silver: Remote assessment, 3-6 months. Focus: documented QMS, full 5S, energy tracking.",
    "gold":     "Gold: Onsite inspection, 6-12 months. For export-ready MSMEs.",
    "subsidy":  "Subsidy: Micro 80%, Small 60%, Medium 50%. Extra 10% for women-owned, SC/ST, NER, J&K.",
    "document": "Bronze documents: Udyam cert, PAN, GST cert, 3 workplace photos, org chart, quality policy draft.",
    "pledge":   "ZED Pledge: Free 5-minute commitment on zed.msme.gov.in. Mandatory before applying. Free WASH cert given immediately.",
    "iso":      "ISO waivers: ISO 9001 waivers QMS, ISO 45001 waivers OHS, IATF 16949 waivers QMS+Lean, FSSAI waivers food QMS.",
    "default":  "I can help with: Bronze/Silver/Gold process, documents, subsidy, parameters, ISO waivers. What would you like to know?"
}

def chat_fallback(msg: str) -> str:
    ml = msg.lower()
    if "bronze" in ml: return FALLBACK["bronze"]
    if "silver" in ml: return FALLBACK["silver"]
    if "gold" in ml:   return FALLBACK["gold"]
    if any(w in ml for w in ["subsidy","money","cost","incentive"]): return FALLBACK["subsidy"]
    if any(w in ml for w in ["document","upload","file","paper"]):   return FALLBACK["document"]
    if any(w in ml for w in ["pledge","kawach","wash"]):             return FALLBACK["pledge"]
    if "iso" in ml or "waive" in ml:                                 return FALLBACK["iso"]
    return FALLBACK["default"]


@app.get("/")
def root():
    idx = FRONTEND_DIR / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    return {"status": "ZED AI Advisor running"}

@app.get("/health")
def health():
    from rag import INDEX_LOADED
    return {
        "status": "ok",
        "groq_connected": groq_client is not None,
        "rag_loaded": INDEX_LOADED,
        "assessment_questions": len(ASSESSMENT_QUESTIONS),
    }

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    lang_note = f"\n\nLanguage Instruction: The user's selected language is {req.language}. However, you MUST reply in the same language and script in which the user asked their query. If the user writes in Hindi (Devanagari script like 'नमस्ते' or Hinglish like 'kaise apply kare'), reply in Hindi or Hinglish accordingly. If the user writes in English, reply in English. Match the user's language and script exactly."
    messages = [{"role": "system", "content": ZED_KNOWLEDGE + lang_note}]
    for m in req.history[-6:]:
        messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": req.message})
    reply = call_groq(messages)
    if reply:
        return ChatResponse(reply=reply, source="groq")
    return ChatResponse(reply=chat_fallback(req.message), source="fallback")


PARAM_NAMES = {
    "p1": "Leadership", "p2": "Swachh Workplace", "p3": "Occupational Safety", "p4": "Measurement of Timely Delivery",
    "p5": "Quality Management", "p6": "Human Resource Management", "p7": "Daily Works Management",
    "p8": "Planned Maintenance & Calibration", "p9": "Process Control", "p10": "Product Quality & Safety",
    "p11": "Material Management", "p12": "Energy Management", "p13": "Environment Management",
    "p14": "Measurement & Analysis", "p15": "Supply Chain Management", "p16": "Risk Management",
    "p17": "Waste Management (Muda/Mura/Muri)", "p18": "Technology Selection & Upgradation",
    "p19": "Natural Resource Conservation", "p20": "Corporate Social Responsibility"
}

@app.post("/assessment")
def assessment(req: AssessmentRequest):
    target = req.target_cert or "Advise"
    
    bronze_ids = [f"p{i}" for i in range(1, 6)]
    silver_ids = [f"p{i}" for i in range(1, 15)]
    gold_ids = [f"p{i}" for i in range(1, 21)]

    # Limit evaluation to target cert
    if target == "Bronze":
        eval_ids = bronze_ids
    elif target == "Silver":
        eval_ids = silver_ids
    else:
        eval_ids = gold_ids

    total_raw = 0
    total_max = 0
    gaps = []
    strengths = []
    pScores = {}

    for pid in eval_ids:
        ans_dict = req.answers.get(pid, {})
        if not ans_dict:
            continue
        raw = sum(ans_dict.values())
        mx = len(ans_dict) * 5
        pct = round(raw / mx * 100) if mx > 0 else 0
        pScores[pid] = pct
        total_raw += raw
        total_max += mx

        param_name = PARAM_NAMES.get(pid, pid)
        if pct < 50:
            gaps.append(param_name)
        elif pct >= 70:
            strengths.append(param_name)

    overall_pct = round((total_raw / total_max) * 100) if total_max > 0 else 0

    def get_level_score(ids):
        r = 0
        m = 0
        for pid in ids:
            ans_dict = req.answers.get(pid, {})
            if ans_dict:
                r += sum(ans_dict.values())
                m += len(ans_dict) * 5
        return round(r / m * 100) if m > 0 else 0

    bScore = get_level_score(bronze_ids)
    sScore = get_level_score(silver_ids)
    gScore = get_level_score(gold_ids)

    bE = bScore >= 50
    sE = sScore >= 55 and bE
    gE = gScore >= 60 and sE

    # Determine readiness strictly based on target
    if target == "Bronze":
        readiness = "Bronze Level Ready 🥉" if bE else "Building Foundations"
        readiness_note = f"Bronze score: {bScore}%." + (" Ready to apply!" if bE else " Focus on the 5 core parameters.")
        gE = False
        sE = False
    elif target == "Silver":
        readiness = "Silver Level Ready 🥈" if sE else ("Bronze Level Ready 🥉" if bE else "Building Foundations")
        readiness_note = f"Silver score: {sScore}%." + (" Ready to apply!" if sE else " Needs improvement for Silver.")
        gE = False
    elif target == "Gold" or target == "Advise":
        if gE:
            readiness = "Gold Level Ready 🥇"
            readiness_note = f"Outstanding! Gold score: {gScore}%."
        elif sE:
            readiness = "Silver Level Ready 🥈"
            readiness_note = f"Strong foundation. Silver score: {sScore}%."
        elif bE:
            readiness = "Bronze Level Ready 🥉"
            readiness_note = f"Good start. Bronze score: {bScore}%."
        else:
            readiness = "Building Foundations"
            readiness_note = f"Focus on Bronze parameters first. Bronze score: {bScore}%."

    roadmap = generate_roadmap(overall_pct, gaps, req.enterprise_name, req.sector, req.enterprise_type, target, readiness)

    base_subsidy = {"Micro": 80, "Small": 60, "Medium": 50}.get(req.enterprise_type, 80)
    special = req.special_category or "None"
    has_bonus = special in ["Women-Owned", "SC-ST", "NER", "JK-Ladakh"]
    total_subsidy = min(base_subsidy + 10 if has_bonus else base_subsidy, 90)
    subsidy_str = f"up to {total_subsidy}%"
    if has_bonus:
        subsidy_str += f" (includes +10% for {special.replace('-', ' ')})"

    return {
        "score": overall_pct,
        "bronze_score": bScore,
        "silver_score": sScore,
        "gold_score": gScore,
        "bronze_eligible": bE,
        "silver_eligible": sE,
        "gold_eligible": gE,
        "readiness": readiness,
        "readiness_note": readiness_note,
        "strengths": strengths,
        "gaps": gaps,
        "subsidy_eligible": subsidy_str,
        "roadmap": roadmap,
    }

def generate_roadmap(score, gaps, name, sector, size, target_cert, qualified_level):
    gaps_text = ", ".join(gaps) if gaps else "None"
    prompt = f"""You are a ZED certification consultant.

Enterprise: {name} | Sector: {sector} | Size: {size}
Target Certification Level: {target_cert}
Current Assessment Score: {score}%
Current Qualified Level: {qualified_level}
Missing areas: {gaps_text}

Write in this format:

**Summary**
One sentence on readiness and suitability for the target certification.

**Missing Requirements (Specific to {sector} sector)**
Bullet list of what to fix to achieve the {target_cert} level. Provide SPECIFIC advice tailored to the {sector} industry on how to address these gaps (e.g. specific processes, tools, or documents). Do NOT give generic advice.

**30-Day Action Plan**
Week 1: (Specific actions targeting missing requirements)
Week 2: (Specific actions targeting missing requirements)
Week 3: (Actions)
Week 4: Apply for {target_cert if target_cert != 'Advise' else 'the advised level'} on zed.msme.gov.in

Keep it practical, highly specific to the {sector} sector, and focused on {target_cert} certification."""

    result = call_groq([{"role": "user", "content": prompt}], max_tokens=500)
    if result:
        return result

    if not gaps:
        return f"**Summary**\nReady to apply for {target_cert}.\n\n**30-Day Plan**\nWeek 1-2: Gather documents\nWeek 3: Take ZED Pledge\nWeek 4: Submit application"

    return f"**Summary**\nScore: {score}%. Target: {target_cert}. Current: {qualified_level}. Address {len(gaps)} area(s) before applying.\n\n**Missing:**\n" + \
           "\n".join(f"- {g}" for g in gaps[:5]) + \
           "\n\n**Plan:**\nWeek 1: Quality policy + complaint register\nWeek 2: 5S + workplace photos\nWeek 3: Energy records + PPE\nWeek 4: ZED Pledge + application"


@app.post("/sector-chat", response_model=ChatResponse)
def sector_chat(req: SectorChatRequest):
    query = f"{req.sector} sector: {req.message}" if req.sector else req.message
    context, source = retrieve(query)
    lang_note = f"\n\nLanguage Instruction: The user's selected language is {req.language}. However, you MUST reply in the same language and script in which the user asked their query. If the user writes in Hindi, reply in Hindi. If the user writes in Hinglish, reply in Hinglish. Match the user's language and script exactly."
    system = f"""You are a ZED sector expert. You MUST follow these rules strictly:

1. Answer ONLY using information found in the CONTEXT below.
2. If the context does not contain the answer, say: "This information is not available in the ZED sector documents. Please try the general Ask ZED tab or rephrase your question."
3. Do NOT add any information from your own training data.
4. When possible, mention which document or section your answer comes from.
5. Keep answers concise and practical for MSME owners.{lang_note}

CONTEXT:
{context}"""
    messages = [{"role": "system", "content": system}]
    for m in req.history[-4:]:
        messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": req.message})
    reply = call_groq(messages, max_tokens=600)
    if reply:
        return ChatResponse(reply=reply, source=f"RAG — {source}")
    return ChatResponse(reply=context[:800], source=source)


TRANSLATE_BATCH_SIZE = 20
LINE_RE = re.compile(r"^\s*(\d+)\s*[.)]\s*(.*)$")

def translate_batch(texts: List[str], target_language: str) -> List[str]:
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    prompt = (
        f"Translate each numbered line below into {target_language}. "
        f"Reply with exactly {len(texts)} numbered lines in the same order, same numbering, "
        "one translation per line, and nothing else. "
        "Keep placeholders, symbols and punctuation such as →, %, …, and numbers unchanged.\n\n"
        f"{numbered}"
    )
    result = call_groq(
        [{"role": "user", "content": prompt}],
        max_tokens=min(4096, max(700, len(numbered) * 2)),
    )
    if not result:
        return texts

    parsed: Dict[int, str] = {}
    for line in result.splitlines():
        m = LINE_RE.match(line)
        if m:
            idx = int(m.group(1)) - 1
            if 0 <= idx < len(texts):
                parsed[idx] = m.group(2).strip()

    if len(parsed) != len(texts):
        return texts

    return [parsed[i] for i in range(len(texts))]


@app.post("/translate")
def translate(req: TranslateRequest):
    if not req.texts:
        return {"translated": True, "translations": []}
    if not groq_client:
        raise HTTPException(503, "Translation service unavailable")

    translations: List[str] = []
    for i in range(0, len(req.texts), TRANSLATE_BATCH_SIZE):
        batch = req.texts[i:i + TRANSLATE_BATCH_SIZE]
        translations.extend(translate_batch(batch, req.target_language))

    return {"translated": True, "translations": translations}


# ═══════════════════════════════════════
#  WHATSAPP INTEGRATION (Twilio webhook)
# ═══════════════════════════════════════

# In-memory session store for WhatsApp conversations
# Key: phone number, Value: list of recent messages
_wa_sessions: Dict[str, List[Dict]] = {}
WA_MAX_HISTORY = 6  # keep last 6 messages per user


def _wa_get_history(phone: str) -> List[Dict]:
    """Get conversation history for a WhatsApp user."""
    return _wa_sessions.get(phone, [])


def _wa_add_message(phone: str, role: str, content: str):
    """Add a message to the WhatsApp user's history."""
    if phone not in _wa_sessions:
        _wa_sessions[phone] = []
    _wa_sessions[phone].append({"role": role, "content": content})
    # Keep only last N messages
    if len(_wa_sessions[phone]) > WA_MAX_HISTORY:
        _wa_sessions[phone] = _wa_sessions[phone][-WA_MAX_HISTORY:]


def _wa_clean_for_whatsapp(text: str) -> str:
    """
    Clean LLM response for WhatsApp:
    - WhatsApp supports *bold* and _italic_ but not **markdown bold**
    - Limit to 1600 chars (WhatsApp message limit)
    """
    # Convert **bold** to *bold* (WhatsApp format)
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
    # Convert ### headers to *bold* lines
    text = re.sub(r'^#{1,3}\s+(.+)$', r'*\1*', text, flags=re.MULTILINE)
    # Truncate if too long
    if len(text) > 1500:
        text = text[:1497] + "..."
    return text


def _wa_process_message(phone: str, body: str) -> str:
    """
    Process a WhatsApp message and return the reply.
    Routes to general chat or sector RAG based on prefix.

    Usage:
    - Normal message  → general ZED chat
    - "sector: <msg>" → sector-specific RAG search
    - "help"          → show available commands
    - "reset"         → clear conversation history
    """
    body_stripped = body.strip()
    body_lower = body_stripped.lower()

    # Handle special commands
    if body_lower in ["help", "menu", "hi", "hello", "start"]:
        return (
            "🏭 *ZED Mitra — WhatsApp Bot*\n\n"
            "I can help with ZED Certification queries!\n\n"
            "Just type your question, for example:\n"
            "• What is Bronze certification?\n"
            "• How much subsidy for micro enterprise?\n"
            "• Documents needed for ZED?\n\n"
            "For sector-specific guidance, type:\n"
            "  *sector:* textile how to prepare for ZED\n\n"
            "Type *reset* to clear chat history."
        )

    if body_lower == "reset":
        _wa_sessions.pop(phone, None)
        return "✅ Chat history cleared. Ask me anything about ZED!"

    # Route: sector RAG
    if body_lower.startswith("sector:"):
        query = body_stripped[7:].strip()
        if not query:
            return "Please add your question after 'sector:'. Example: sector: textile Bronze preparation"
        from rag import retrieve
        context, source = retrieve(query)
        system = f"""You are a ZED sector expert on WhatsApp. Answer ONLY from the context below.
If the context doesn't have the answer, say so honestly.
Keep answers short and practical (max 3-4 points). Use simple language.

Context:
{context}"""
        messages = [{"role": "system", "content": system}]
        messages.append({"role": "user", "content": query})
        reply = call_groq(messages, max_tokens=500)
        if reply:
            return _wa_clean_for_whatsapp(reply) + f"\n\n📄 _Source: {source}_"
        return _wa_clean_for_whatsapp(context[:600]) + f"\n\n📄 _Source: {source}_"

    # Route: general chat
    lang_note = "\nReply in the same language the user writes in. Hindi to Hindi. English to English. Hinglish to Hinglish. Keep answers concise for WhatsApp (max 3-4 short points)."
    messages = [{"role": "system", "content": ZED_KNOWLEDGE + lang_note}]

    # Add conversation history
    for m in _wa_get_history(phone):
        messages.append(m)

    messages.append({"role": "user", "content": body_stripped})

    reply = call_groq(messages, max_tokens=500)
    if reply:
        # Save to history
        _wa_add_message(phone, "user", body_stripped)
        _wa_add_message(phone, "assistant", reply)
        return _wa_clean_for_whatsapp(reply)

    # Fallback
    return _wa_clean_for_whatsapp(chat_fallback(body_stripped))


@app.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(default=""),
    Body: str = Form(default=""),
):
    """
    Twilio WhatsApp webhook endpoint.

    Twilio sends POST with form data:
    - From: "whatsapp:+91XXXXXXXXXX"
    - Body: the user's message text

    We return TwiML XML to reply.

    Setup:
    1. Sign up at twilio.com (free)
    2. Go to Messaging > Try it out > WhatsApp Sandbox
    3. Set webhook URL to: https://your-domain.com/whatsapp
    4. Send the join code from your WhatsApp to the sandbox number
    """
    phone = From or "unknown"
    message = Body or ""

    if not message.strip():
        reply = "Hi! I'm ZED Mitra. Ask me anything about ZED Certification. Type *help* for options."
    else:
        try:
            reply = _wa_process_message(phone, message)
        except Exception as e:
            print(f"[WhatsApp] Error processing message from {phone}: {e}")
            reply = "Sorry, I encountered an error. Please try again or type *help*."

    print(f"[WhatsApp] {phone}: {message[:80]}... → {reply[:80]}...")

    # Return TwiML XML response
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>"""
    return Response(content=twiml, media_type="application/xml")
