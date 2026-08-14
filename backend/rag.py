"""
rag.py — FAISS-based retrieval for ZED sector documents

For tonight's demo:
- If vectorstore/zed.index exists → use real FAISS retrieval
- If not → falls back to keyword search over ZED_KNOWLEDGE
  so your demo NEVER breaks even without PDFs

To build the index later (after downloading PDFs):
  python extract_docs.py
"""

import os
import pickle
import numpy as np
from pathlib import Path

# ── Try loading FAISS (graceful if not installed yet) ──
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[WARN] faiss-cpu not installed. Using fallback retrieval.")

# ── Try loading sentence-transformers ──
try:
    from sentence_transformers import SentenceTransformer
    _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    EMBEDDER_AVAILABLE = True
except Exception:
    EMBEDDER_AVAILABLE = False
    print("[WARN] sentence-transformers not available. Using keyword fallback.")

VECTORSTORE = Path(__file__).parent / "vectorstore"
INDEX_PATH  = VECTORSTORE / "zed.index"
CHUNKS_PATH = VECTORSTORE / "chunks.pkl"

# ── Load index if it exists ──
_index  = None
_chunks = []
_meta   = []

def load_index():
    global _index, _chunks, _meta
    if not FAISS_AVAILABLE:
        return False
    if not INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        return False
    try:
        _index = faiss.read_index(str(INDEX_PATH))
        with open(CHUNKS_PATH, "rb") as f:
            saved = pickle.load(f)
            _chunks = saved["chunks"]
            _meta   = saved["meta"]
        print(f"[OK] FAISS index loaded - {len(_chunks)} chunks")
        return True
    except Exception as e:
        print(f"[WARN] Could not load FAISS index: {e}")
        return False

INDEX_LOADED = load_index()

# ── ZED knowledge for keyword fallback ──
ZED_FALLBACK = {
    "bronze": """Bronze Certification (Entry Level):
- Assessment type: Desktop / self-declaration, no site visit required
- Timeline: 1 to 3 months
- Subsidy: Up to 80% for Micro, 60% for Small, 50% for Medium enterprises
- Documents needed: Udyam certificate, PAN card, factory photos (min 3), quality policy draft, GST certificate
- Steps: UDYAM → ZED Pledge → Apply Bronze → Upload docs → Desktop assessment → Certificate
- Best for: First-time MSMEs, micro enterprises""",

    "silver": """Silver Certification (Intermediate Level):
- Assessment type: Remote / document verification
- Timeline: 3 to 6 months
- Focus: Fully documented QMS, complete 5S implementation, energy tracking
- Recommended: MSMEs targeting government procurement preference
- Can apply directly without Bronze""",

    "gold": """Gold Certification (Advanced Level):
- Assessment type: Onsite physical inspection
- Timeline: 6 to 12 months
- Focus: Full lean systems, ISO-equivalent QMS, sustainability reporting
- Best for: Export-ready MSMEs, OEM component suppliers""",

    "subsidy": """ZED Subsidy Structure:
- Micro enterprise: Up to 80% of certification cost
- Small enterprise: Up to 60% of certification cost
- Medium enterprise: Up to 50% of certification cost
- Extra 10% bonus for: Women-owned, SC/ST-owned, North-East Region, J&K/Ladakh enterprises
- Subsidy is reimbursed AFTER certification is awarded
- Example: Micro + Women-owned = up to 90% subsidy""",

    "document": """Documents Required for Bronze:
Mandatory:
- Udyam Registration Certificate (from udyamregistration.gov.in)
- PAN Card of enterprise
- GST Certificate (if registered)
- Workplace photographs (minimum 3, showing production area)
- Organisational chart
- Draft quality policy (even 1 page is acceptable for Bronze)
Optional but helpful:
- Existing ISO certificates (waive relevant parameters)
- Monthly electricity bills
- Customer list""",

    "parameter": """10 ZED Assessment Parameters:
1. Leadership & Management Commitment — 10% weight
2. 5S Workplace Organisation — 15% weight
3. Quality Management System (QMS) — 20% weight (highest)
4. Customer Satisfaction — 10% weight
5. Lean Manufacturing & Waste Reduction — 10% weight
6. Energy Conservation & Environment — 15% weight
7. Occupational Health & Safety — 10% weight
8. IT Adoption — 5% weight
9. Product & Process Benchmarking — 3% weight
10. Social Responsibility — 2% weight""",

    "iso": """ISO Certification Waivers in ZED:
- ISO 9001  → Quality Management System (QMS, 20%) waived
- ISO 14001 → Environmental management parameters waived
- ISO 45001 → Occupational Health & Safety (10%) waived
- ISO 50001 → Energy management parameters waived
- BIS/ISI   → Product quality in QMS waived
- IATF 16949 → QMS (20%) + Lean (10%) both waived — best waiver
- FSSAI     → Food safety / QMS parameters waived
- SA 8000   → Social Responsibility (2%) waived""",

    "pledge": """ZED Pledge and KAWACH:
- ZED Pledge is a mandatory 5-minute commitment on zed.msme.gov.in
- Must be taken BEFORE applying for any certification level
- After pledge: FREE WASH/KAWACH certification available immediately
- WASH = Workplace Assessment for Safety and Hygiene
- KAWACH = Knowledge Acquisition through WASH for COVID-19 Handling
- No cost for pledge or KAWACH certification""",

    "udyam": """UDYAM Registration:
- Mandatory before applying for ZED
- Register free at: udyamregistration.gov.in
- Needs: Aadhaar number, PAN card, bank account details
- Takes 15-20 minutes
- You receive a UDYAM Registration Number (URN)
- Enterprise size (Micro/Small/Medium) is determined by UDYAM data""",

    "textile": """ZED Guidance for Textiles (NIC Division 13 & 14):
- Sector-specific guidance document available at zed.msme.gov.in
- Key parameters for textiles: QMS for fabric quality, 5S in weaving/dyeing units
- Environment focus: Effluent treatment for dyeing units
- Energy: Loom energy consumption tracking
- Common ISO certs in textile sector: ISO 9001, OEKO-TEX (ask assessor)
- Download: ZED_Guidance_Document_NIC_Division_13.pdf""",

    "food": """ZED Guidance for Food Products (NIC Division 10):
- FSSAI certificate holders get QMS parameters automatically waived
- Key focus: Hygiene, food safety, contamination prevention
- 5S is critical in food processing units
- Energy: Cold chain and processing energy
- Download: ZED_Guidance_Document_NIC_Division_10.pdf""",

    "default": """ZED Mitra — I can answer questions on:
- Bronze, Silver, Gold certification process
- Documents required for application
- Subsidy amounts and eligibility
- ZED parameters and scoring
- ISO certificate waivers
- Sector-specific guidance (textiles, food, pharma, auto, etc.)
- UDYAM registration
- ZED Pledge and KAWACH

Please ask your specific question and I will help."""
}

def keyword_fallback(query: str) -> str:
    """Simple keyword match over ZED_FALLBACK dict."""
    q = query.lower()
    if "bronze" in q:           return ZED_FALLBACK["bronze"]
    if "silver" in q:           return ZED_FALLBACK["silver"]
    if "gold" in q:             return ZED_FALLBACK["gold"]
    if any(w in q for w in ["subsidy","money","cost","incentive","reimburs"]): return ZED_FALLBACK["subsidy"]
    if any(w in q for w in ["document","upload","file","paper","attach"]):     return ZED_FALLBACK["document"]
    if any(w in q for w in ["parameter","param","score","weight"]):            return ZED_FALLBACK["parameter"]
    if "iso" in q or "waive" in q or "exempt" in q:                           return ZED_FALLBACK["iso"]
    if any(w in q for w in ["pledge","kawach","wash"]):                        return ZED_FALLBACK["pledge"]
    if "udyam" in q:            return ZED_FALLBACK["udyam"]
    if any(w in q for w in ["textile","fabric","garment","apparel","weav"]):   return ZED_FALLBACK["textile"]
    if any(w in q for w in ["food","beverage","fssai","process"]):             return ZED_FALLBACK["food"]
    return ZED_FALLBACK["default"]

# ── Retrieval config ──
DISTANCE_THRESHOLD = 1.2   # L2 distance — lower = stricter (tune after testing)
CONFIDENCE_HIGH    = 0.7   # below this = high confidence
CONFIDENCE_MEDIUM  = 1.0   # below this = medium confidence


def _get_confidence(best_distance: float) -> str:
    """Map best L2 distance to a confidence label."""
    if best_distance < CONFIDENCE_HIGH:
        return "high"
    if best_distance < CONFIDENCE_MEDIUM:
        return "medium"
    if best_distance < DISTANCE_THRESHOLD:
        return "low"
    return "none"


def retrieve(query: str, top_k: int = 5) -> tuple[str, str]:
    """
    Returns (context_string, source_label)

    Improvements over v1:
    - Filters out chunks with L2 distance > DISTANCE_THRESHOLD
    - Adds confidence scoring (high / medium / low)
    - Logs distances for debugging
    - Falls back to keyword search if no good FAISS matches
    """
    # ── Real FAISS retrieval ──
    if INDEX_LOADED and EMBEDDER_AVAILABLE and _index is not None:
        try:
            q_vec = _embedder.encode([query])
            D, I  = _index.search(np.array(q_vec, dtype="float32"), top_k)

            # Debug log — distances for each retrieved chunk
            print(f"[RAG] Query: {query[:80]}...")
            for rank, (dist, idx) in enumerate(zip(D[0], I[0])):
                src = _meta[idx].get("source", "?") if idx < len(_meta) else "?"
                status = "✓" if dist < DISTANCE_THRESHOLD else "✗ (filtered)"
                print(f"  #{rank+1}  dist={dist:.4f}  {status}  src={src}")

            # Filter by distance threshold — reject irrelevant chunks
            results = []
            sources = set()
            for dist, idx in zip(D[0], I[0]):
                if dist >= DISTANCE_THRESHOLD:
                    continue  # too far = irrelevant
                if idx < len(_chunks):
                    results.append(_chunks[idx])
                    if idx < len(_meta):
                        sources.add(_meta[idx].get("source", "ZED Docs"))

            if not results:
                print(f"[RAG] No chunks passed threshold ({DISTANCE_THRESHOLD}), using keyword fallback")
                return keyword_fallback(query), "ZED Knowledge Base (fallback)"

            confidence = _get_confidence(D[0][0])  # best match distance
            context    = "\n\n---\n\n".join(results)
            source     = ", ".join(sources) if sources else "ZED Sector Documents"
            source     = f"{confidence} confidence — {source}"
            print(f"[RAG] Returning {len(results)} chunks, confidence={confidence}")
            return context, source

        except Exception as e:
            print(f"FAISS retrieval error: {e}, falling back")

    # ── Keyword fallback ──
    return keyword_fallback(query), "ZED Knowledge Base"
