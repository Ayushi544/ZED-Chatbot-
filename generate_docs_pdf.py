"""
Generate ZED Mitra Interview Documentation PDF
Uses fpdf2 for pure-Python PDF generation with Unicode support.
"""
import subprocess, sys

# Ensure fpdf2 is installed
try:
    from fpdf import FPDF
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2", "-q"])
    from fpdf import FPDF

import os

# ── OUTPUT PATH ──
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "ZED_Mitra_Interview_Documentation.pdf")


class DocPDF(FPDF):
    """Custom PDF class with header/footer and helper methods."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        # Use built-in Helvetica (supports latin chars well)
        self.set_auto_page_break(auto=True, margin=20)

    # Store colors as class-level constants (plain tuples, never mutated)
    C_PRIMARY = (26, 171, 138)
    C_DARK = (19, 140, 112)
    C_ACCENT = (46, 125, 50)
    C_TEXT = (30, 30, 30)
    C_MID = (80, 80, 80)
    C_LIGHT_BG = (245, 249, 245)

    def header(self):
        if self.page_no() == 1:
            return  # Cover page has custom header
        # Tricolor stripe
        self.set_fill_color(255, 153, 51)
        self.rect(0, 0, 70, 2, "F")
        self.set_fill_color(255, 255, 255)
        self.rect(70, 0, 70, 2, "F")
        self.set_fill_color(19, 136, 8)
        self.rect(140, 0, 70, 2, "F")
        # Header bar
        self.set_fill_color(*self.C_PRIMARY)
        self.rect(0, 2, 210, 10, "F")
        self.set_y(3)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, "ZED Mitra  |  Interview Documentation  |  Ministry of MSME", align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    # ── Helper methods ──

    def cover_page(self):
        self.add_page()
        # Tricolor top
        self.set_fill_color(255, 153, 51)
        self.rect(0, 0, 70, 4, "F")
        self.set_fill_color(255, 255, 255)
        self.rect(70, 0, 70, 4, "F")
        self.set_fill_color(19, 136, 8)
        self.rect(140, 0, 70, 4, "F")
        # Teal banner
        self.set_fill_color(*self.C_PRIMARY)
        self.rect(0, 4, 210, 60, "F")
        self.set_y(18)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(255, 255, 255)
        self.cell(0, 14, "ZED Mitra", align="C")
        self.ln(14)
        self.set_font("Helvetica", "", 13)
        self.cell(0, 8, "AI-Powered Advisor for MSME ZED Certification", align="C")
        self.ln(8)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(220, 255, 240)
        self.cell(0, 7, "Ministry of MSME  |  Government of India", align="C")
        # Subtitle box
        self.set_y(80)
        self.set_text_color(*self.C_TEXT)
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Complete Interview Documentation", align="C")
        self.ln(14)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(*self.C_MID)
        self.set_x(30)
        self.multi_cell(150, 6,
            "End-to-end technical documentation covering architecture, "
            "code walkthrough, RAG pipeline, design decisions, "
            "pros & cons, scalability, security, future roadmap, "
            "and 15+ expected interview questions with detailed answers.",
            align="C")
        # Tech stack badges
        self.ln(10)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.C_PRIMARY)
        self.cell(0, 8, "Tech Stack", align="C")
        self.ln(8)
        badges = ["Python", "FastAPI", "FAISS", "Sentence Transformers", "Groq / LLaMA 3.1", "Vanilla JS"]
        self.set_font("Helvetica", "", 9)
        badge_w = 30
        total_w = len(badges) * badge_w + (len(badges) - 1) * 3
        x_start = (210 - total_w) / 2
        for i, b in enumerate(badges):
            x = x_start + i * (badge_w + 3)
            self.set_fill_color(*self.C_LIGHT_BG)
            self.set_draw_color(*self.C_PRIMARY)
            self.set_text_color(*self.C_DARK)
            self.rounded_rect(x, self.get_y(), badge_w, 8, 2, style="DF")
            self.set_xy(x, self.get_y())
            self.cell(badge_w, 8, b, align="C")
        self.ln(20)
        # Stats
        self.set_text_color(*self.C_TEXT)
        stats = [
            ("3,277+", "Lines of Code"),
            ("3", "Core Modules"),
            ("29", "PDF Documents Indexed"),
            ("12", "Indian Languages"),
        ]
        stat_w = 40
        x_start = (210 - len(stats) * stat_w) / 2
        for i, (num, label) in enumerate(stats):
            x = x_start + i * stat_w
            self.set_xy(x, self.get_y())
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(*self.C_PRIMARY)
            self.cell(stat_w, 10, num, align="C")
            self.set_xy(x, self.get_y() + 10)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(*self.C_MID)
            self.cell(stat_w, 5, label, align="C")
        self.ln(25)
        # Divider
        self.set_draw_color(*self.C_PRIMARY)
        self.line(40, self.get_y(), 170, self.get_y())
        self.ln(8)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(*self.C_MID)
        self.cell(0, 6, "Prepared by: Ayushi", align="C")
        self.ln(6)
        self.cell(0, 6, "Project: ZED Mitra v2 - Full Stack AI Chatbot", align="C")

    def rounded_rect(self, x, y, w, h, r, style=""):
        """Draw a rectangle with rounded corners."""
        # Simplified: just draw a regular rect
        if "F" in style:
            self.rect(x, y, w, h, style)
        else:
            self.rect(x, y, w, h, style)

    def section_title(self, num, title):
        """Major section heading with teal accent bar."""
        self.ln(4)
        # Accent bar
        self.set_fill_color(*self.C_PRIMARY)
        self.rect(15, self.get_y(), 3, 9, "F")
        self.set_x(22)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*self.C_DARK)
        self.cell(0, 9, f"{num}. {title}")
        self.ln(12)

    def sub_heading(self, text):
        """Sub-section heading."""
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*self.C_ACCENT)
        self.cell(0, 8, text)
        self.ln(8)

    def sub_sub_heading(self, text):
        """Sub-sub-section heading."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.C_DARK)
        self.cell(0, 7, text)
        self.ln(7)

    def body_text(self, text):
        """Normal paragraph text."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.C_TEXT)
        self.multi_cell(0, 5.5, text)
        self.ln(3)

    def italic_text(self, text):
        """Italic/quote text."""
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(*self.C_MID)
        self.set_x(20)
        self.multi_cell(170, 5.5, text)
        self.ln(3)

    def bold_text(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.C_TEXT)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=20):
        """Bullet point."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.C_TEXT)
        x = self.get_x()
        self.set_x(indent)
        self.cell(5, 5.5, "-")  # bullet char
        self.multi_cell(170 - indent, 5.5, text)
        self.ln(1)

    def numbered_item(self, num, text, indent=20):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.C_TEXT)
        self.set_x(indent)
        self.set_font("Helvetica", "B", 10)
        self.cell(8, 5.5, f"{num}.")
        self.set_font("Helvetica", "", 10)
        self.multi_cell(162 - indent, 5.5, text)
        self.ln(1)

    def code_block(self, text):
        """Monospace code block with gray background."""
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(50, 50, 50)
        lines = text.strip().split("\n")
        h = len(lines) * 4.5 + 6
        y_start = self.get_y()
        if y_start + h > 277:
            self.add_page()
            y_start = self.get_y()
        self.rect(15, y_start, 180, h, "DF")
        self.set_xy(18, y_start + 3)
        for line in lines:
            self.cell(0, 4.5, line[:95])
            self.ln(4.5)
            self.set_x(18)
        self.ln(4)

    def table_header(self, cols, widths):
        """Table header row."""
        self.set_fill_color(*self.C_PRIMARY)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, col, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, cols, widths, fill=False):
        """Table data row."""
        if fill:
            self.set_fill_color(*self.C_LIGHT_BG)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_text_color(*self.C_TEXT)
        self.set_font("Helvetica", "", 8.5)
        max_lines = 1
        # Calculate max lines needed
        for i, col in enumerate(cols):
            lines_needed = max(1, len(col) * self.get_string_width("a") / (widths[i] - 2) + 1)
            max_lines = max(max_lines, int(lines_needed))
        row_h = max(7, max_lines * 4.5)
        # Check page break
        if self.get_y() + row_h > 277:
            self.add_page()
        y_start = self.get_y()
        x_start = self.get_x()
        for i, col in enumerate(cols):
            self.set_xy(x_start + sum(widths[:i]), y_start)
            self.multi_cell(widths[i], 4.5, col, border=1, fill=fill, align="L")
        self.set_y(max(self.get_y(), y_start + row_h))

    def simple_table_row(self, cols, widths, fill=False):
        """Simple single-line table row."""
        if fill:
            self.set_fill_color(*self.C_LIGHT_BG)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_text_color(*self.C_TEXT)
        self.set_font("Helvetica", "", 8.5)
        if self.get_y() + 7 > 277:
            self.add_page()
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, col[:50], border=1, fill=fill)
        self.ln()

    def info_box(self, text, box_type="info"):
        """Colored info/warning box."""
        if box_type == "info":
            bg = (230, 249, 245)
            border_c = self.C_PRIMARY
        elif box_type == "warning":
            bg = (255, 243, 224)
            border_c = (230, 126, 34)
        elif box_type == "tip":
            bg = (232, 245, 233)
            border_c = self.C_ACCENT
        else:
            bg = (245, 245, 245)
            border_c = (150, 150, 150)
        self.set_fill_color(*bg)
        self.set_draw_color(*border_c)
        y_start = self.get_y()
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(60, 60, 60)
        # Estimate height
        lines = len(text) / 80 + 1
        h = max(12, lines * 5 + 6)
        if y_start + h > 277:
            self.add_page()
            y_start = self.get_y()
        self.rect(15, y_start, 180, h, "DF")
        self.set_xy(18, y_start + 3)
        self.multi_cell(174, 5, text)
        self.set_y(y_start + h + 3)

    def page_break_check(self, needed=40):
        if self.get_y() + needed > 270:
            self.add_page()

    def separator(self):
        self.ln(3)
        self.set_draw_color(200, 220, 200)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(5)


def build_pdf():
    pdf = DocPDF()
    pdf.alias_nb_pages()

    # ═══════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════
    pdf.cover_page()

    # ═══════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*pdf.C_DARK)
    pdf.cell(0, 12, "Table of Contents", align="C")
    pdf.ln(15)

    toc = [
        ("1", "Project Overview & Problem Statement"),
        ("2", "System Architecture"),
        ("3", "Tech Stack & Justification"),
        ("4", "Folder Structure & File Walkthrough"),
        ("5", "Backend Deep Dive"),
        ("6", "RAG Pipeline Deep Dive"),
        ("7", "Frontend Deep Dive"),
        ("8", "Data Flow - End to End"),
        ("9", "API Endpoints Reference"),
        ("10", "Design Patterns & Engineering Decisions"),
        ("11", "Pros (Strengths)"),
        ("12", "Cons (Limitations & Technical Debt)"),
        ("13", "Scalability Analysis"),
        ("14", "Security Considerations"),
        ("15", "Future Roadmap"),
        ("16", "Interview Q&A - Expected Questions"),
        ("17", "How to Demo This Project"),
    ]
    for num, title in toc:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*pdf.C_PRIMARY)
        pdf.set_x(25)
        pdf.cell(10, 8, num + ".")
        pdf.set_text_color(*pdf.C_TEXT)
        pdf.cell(0, 8, title)
        pdf.ln(8)

    # ═══════════════════════════════════════════
    # ELEVATOR PITCH
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*pdf.C_DARK)
    pdf.cell(0, 10, "Elevator Pitch (30 seconds)")
    pdf.ln(12)
    pdf.info_box(
        '"I built ZED Mitra, a full-stack AI-powered chatbot for the Ministry of MSME\'s Zero Defect Zero Effect '
        'certification scheme. It uses RAG (Retrieval-Augmented Generation) over 29 official government PDFs, '
        'a FAISS vector database for semantic search, and Groq\'s LLM API to give MSME owners personalised '
        'certification guidance in 12 Indian languages. It includes a readiness assessment tool that scores '
        'enterprises against ZED parameters and generates AI-powered 30-day action plans. The entire system '
        'runs on a Python/FastAPI backend with a single-page HTML frontend - designed for simplicity so '
        'government officers can deploy it."',
        "tip"
    )
    pdf.ln(5)

    # ═══════════════════════════════════════════
    # SECTION 1: PROJECT OVERVIEW
    # ═══════════════════════════════════════════
    pdf.section_title("1", "Project Overview & Problem Statement")

    pdf.sub_heading("The Problem")
    pdf.body_text(
        "India has 63+ million MSMEs (Micro, Small & Medium Enterprises). The Government's ZED Certification "
        "Scheme (Zero Defect Zero Effect) helps MSMEs improve quality and sustainability. However:"
    )
    pdf.bullet("The certification process is complex - 3 levels (Bronze, Silver, Gold), 10 assessment parameters, different subsidies")
    pdf.bullet("Official documentation is spread across 29+ PDF guidance documents, each 30-50 pages")
    pdf.bullet("MSME owners (often non-technical) don't know where to start or what level they qualify for")
    pdf.bullet("Information is only available in English - most MSME owners speak regional languages")
    pdf.bullet("No interactive tool exists to assess readiness before applying")

    pdf.sub_heading("The Solution: ZED Mitra")
    pdf.body_text("An AI advisor chatbot with 3 core modules:")
    pdf.ln(2)

    w = [60, 60, 60]
    pdf.table_header(["Module", "What it Does", "Tech Used"], w)
    pdf.simple_table_row(["Ask ZED (Chat)", "General Q&A chatbot", "LLM + System Prompt"], w, True)
    pdf.simple_table_row(["Readiness Assessment", "20-Q self-assessment + roadmap", "Scoring Engine + LLM"], w)
    pdf.simple_table_row(["Sector Guidance", "RAG search over 29 PDFs", "FAISS + Embeddings + LLM"], w, True)
    pdf.ln(5)

    pdf.sub_heading("Target Users")
    pdf.bullet("MSME owners wanting to understand ZED certification")
    pdf.bullet("Government officers (JS-level) evaluating the chatbot for national deployment")
    pdf.bullet("ZED consultants needing quick reference to certification parameters")

    # ═══════════════════════════════════════════
    # SECTION 2: ARCHITECTURE
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("2", "System Architecture")

    pdf.body_text("The system follows a monolithic architecture where a single FastAPI application serves both the API and the static frontend:")
    pdf.ln(2)
    pdf.code_block(
        "USER (Browser)\n"
        "  |-- Tab 1: Ask ZED ------> POST /chat ---------> System Prompt + Groq LLM\n"
        "  |-- Tab 2: Assessment ---> POST /assessment ----> Scoring Engine + Groq LLM\n"
        "  |-- Tab 3: Sector -------> POST /sector-chat ---> FAISS Retrieval + Groq LLM\n"
        "                                                         |\n"
        "                                                    FAISS Index\n"
        "                                                    (zed.index)\n"
        "                                                    + chunks.pkl\n"
        "\n"
        "FALLBACK CHAIN: Groq LLM -> Keyword Fallback -> Hardcoded Response\n"
        "                (Demo NEVER crashes)"
    )

    pdf.sub_heading("Key Architectural Decisions")
    pdf.numbered_item(1, "Monolith - Single FastAPI app serves both API and static files. No NGINX/reverse proxy needed.")
    pdf.numbered_item(2, "Graceful Degradation - If FAISS fails -> keyword fallback. If Groq fails -> hardcoded responses.")
    pdf.numbered_item(3, "No Database - State is entirely client-side (chat history in JS arrays). Zero-config deployment.")
    pdf.numbered_item(4, "Single-file Frontend - All HTML/CSS/JS in one index.html (~1,950 lines). No build step needed.")

    # ═══════════════════════════════════════════
    # SECTION 3: TECH STACK
    # ═══════════════════════════════════════════
    pdf.page_break_check(60)
    pdf.section_title("3", "Tech Stack & Justification")

    pdf.sub_heading("Backend")
    w = [35, 25, 120]
    pdf.table_header(["Technology", "Version", "Why This Choice"], w)
    rows = [
        ("Python", "3.11+", "Standard for ML/AI; government teams know it"),
        ("FastAPI", "0.111.0", "Async-ready, auto-docs, Pydantic validation"),
        ("Groq API", "0.9.0", "Free tier LLM, fastest inference (LPU hardware)"),
        ("LLaMA 3.1 8B", "--", "Open-source, fast inference, good multilingual"),
        ("FAISS (faiss-cpu)", "1.8.0", "Facebook's vector search, runs on CPU"),
        ("Sentence Trans.", "2.7.0", "all-MiniLM-L6-v2: only 80MB, fast embeddings"),
        ("PyMuPDF (fitz)", "1.24.3", "Fastest PDF text extractor in Python"),
        ("python-dotenv", "1.0.1", "Secure API key management via .env"),
        ("Pydantic", "2.0+", "Request/response validation with FastAPI"),
        ("NumPy", "1.24+", "Array operations for FAISS embeddings"),
    ]
    for i, (tech, ver, why) in enumerate(rows):
        pdf.simple_table_row([tech, ver, why], w, i % 2 == 0)

    pdf.ln(5)
    pdf.sub_heading("Frontend")
    w2 = [50, 130]
    pdf.table_header(["Technology", "Why"], w2)
    pdf.simple_table_row(["Vanilla HTML/CSS/JS", "Zero build step, works on any browser, no npm install"], w2, True)
    pdf.simple_table_row(["CSS Custom Properties", "Government branding (teal palette from ZED portal)"], w2)
    pdf.simple_table_row(["Web Speech API", "Browser-native voice input in 12 Indian languages"], w2, True)
    pdf.simple_table_row(["Fetch API", "Async HTTP calls to backend"], w2)

    pdf.ln(5)
    pdf.sub_heading("Why NOT React/Vue/Next.js?")
    pdf.info_box(
        "Government officers need to deploy this with minimal technical knowledge. A single HTML file that "
        "'just works' eliminates the need for Node.js, webpack, or any build toolchain. The tradeoff is code "
        "organization, but for a POC, simplicity wins.",
        "info"
    )

    pdf.sub_heading("Why Groq Instead of OpenAI/Claude?")
    pdf.numbered_item(1, "Free tier - no budget needed for POC")
    pdf.numbered_item(2, "Fastest inference - Groq uses custom LPU (Language Processing Units)")
    pdf.numbered_item(3, "Open models - LLaMA 3.1 is open-source, avoids vendor lock-in")
    pdf.numbered_item(4, "Drop-in replaceable - When Ministry provides its own API, just change model name")

    # ═══════════════════════════════════════════
    # SECTION 4: FOLDER STRUCTURE
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("4", "Folder Structure & File Walkthrough")

    pdf.code_block(
        "zed_chatbot/\n"
        "|\n"
        "|-- .gitignore                    Excludes .env, __pycache__, venv\n"
        "|-- README.md                     Setup guide for non-technical users\n"
        "|-- test_imports.py               Quick sanity check for all deps\n"
        "|\n"
        "|-- backend/\n"
        "|   |-- .env                      Secret API key (NOT in git)\n"
        "|   |-- .env.example              Template for .env\n"
        "|   |-- main.py                   Core application (351 lines)\n"
        "|   |-- rag.py                    RAG retrieval engine (214 lines)\n"
        "|   |-- build_index.py            Index builder from Excel (492 lines)\n"
        "|   |-- extract_docs.py           Index builder from PDFs (269 lines)\n"
        "|   |-- requirements.txt          Python deps (9 packages)\n"
        "|   |-- ZED_Upload.xlsx           Excel with document URLs\n"
        "|   |-- docs/                     29 official ZED PDF documents\n"
        "|   |-- vectorstore/\n"
        "|       |-- zed.index             FAISS index (~1.4 MB)\n"
        "|       |-- chunks.pkl            Text chunks + metadata (~960 KB)\n"
        "|\n"
        "|-- frontend/\n"
        "|   |-- index.html                Complete frontend (1,951 lines)\n"
        "|\n"
        "|-- data/\n"
        "|   |-- assessment_questions.json  20 weighted assessment questions\n"
        "|   |-- sector_docs.json          Extracted text from all PDFs\n"
        "|\n"
        "|-- docs/\n"
        "    |-- question_bank.json        50 test questions by category"
    )

    # ═══════════════════════════════════════════
    # SECTION 5: BACKEND DEEP DIVE
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("5", "Backend Deep Dive")

    pdf.sub_heading("main.py - The Brain (351 lines)")

    pdf.sub_sub_heading("Initialization Flow")
    pdf.code_block(
        "1. load_dotenv()                  # Load .env\n"
        "2. groq_client = Groq(api_key=...) # Init LLM client\n"
        "3. from rag import retrieve        # Load FAISS index\n"
        "4. ASSESSMENT_QUESTIONS = json.load(...)  # Load questions\n"
        "5. app = FastAPI(...)              # Configure with CORS\n"
        "6. app.mount('/static', ...)       # Serve frontend"
    )

    pdf.sub_sub_heading("Endpoint 1: POST /chat - General Q&A")
    pdf.body_text(
        "Flow: User Question -> System Prompt (ZED_KNOWLEDGE, ~78 lines of compressed ZED facts) "
        "+ Chat History (last 6 messages) + Language Instruction -> Groq LLM -> Response. "
        "If Groq fails -> keyword-based chat_fallback()."
    )

    pdf.sub_sub_heading("Endpoint 2: POST /assessment - Readiness Scoring")
    pdf.body_text("Uses SET THEORY for clean certification logic:")
    pdf.code_block(
        "BRONZE_QIDS = {1,2,3,4,5,6,7,8,9,10,15,16}\n"
        "SILVER_QIDS = {1,2,3,4,5,6,7,8,9,10,13,14,15,16,19}\n"
        "GOLD_QIDS   = {1,2,...,20}  # All 20 questions\n"
        "\n"
        "has_bronze = BRONZE_QIDS.issubset(yes_qids)  # Set theory!\n"
        "has_silver = SILVER_QIDS.issubset(yes_qids)\n"
        "has_gold   = GOLD_QIDS.issubset(yes_qids)"
    )
    pdf.body_text("Subsidy: Micro=80%, Small=60%, Medium=50%. +10% for Women-Owned/SC-ST/NER/JK. Capped at 90%.")

    pdf.sub_sub_heading("Endpoint 3: POST /sector-chat - RAG Sector Guidance")
    pdf.body_text(
        "Flow: Prepend sector name to query -> retrieve() from rag.py (FAISS top-5) "
        "-> System prompt: 'Answer only from context below' + context -> Groq LLM -> "
        "Response with source PDF name."
    )

    pdf.sub_sub_heading("The call_groq() Function")
    pdf.code_block(
        "def call_groq(messages, max_tokens=700):\n"
        "    res = groq_client.chat.completions.create(\n"
        "        model='llama-3.1-8b-instant',  # Fast, multilingual\n"
        "        messages=messages,\n"
        "        max_tokens=max_tokens,\n"
        "        temperature=0.4,  # Low = factual, consistent\n"
        "    )\n"
        "    return res.choices[0].message.content.strip()"
    )
    pdf.info_box(
        "Why temperature=0.4? ZED certification has specific rules and numbers. We want factual "
        "accuracy, not creative answers. 0.4 allows slight variation in phrasing without hallucination risk.",
        "tip"
    )

    # ═══════════════════════════════════════════
    # SECTION 6: RAG PIPELINE
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("6", "RAG Pipeline Deep Dive")

    pdf.sub_heading("What is RAG?")
    pdf.info_box(
        "Retrieval-Augmented Generation = Instead of relying solely on the LLM's training data, we first "
        "RETRIEVE relevant text from our own documents, then feed that text as CONTEXT to the LLM. "
        "This grounds the LLM's answers in official documents.",
        "info"
    )

    pdf.sub_heading("rag.py - Retrieval Engine (214 lines)")
    pdf.code_block(
        'User Query: "What parameters matter for textiles?"\n'
        "     |\n"
        "     v\n"
        "SentenceTransformer (all-MiniLM-L6-v2)\n"
        "  Encode query -> 384-dimensional vector\n"
        "     |\n"
        "     v\n"
        "FAISS Index (IndexFlatL2)\n"
        "  Brute-force L2 distance search\n"
        "  Return top-5 nearest neighbours\n"
        "     |\n"
        "     v\n"
        "Retrieve chunk text + source PDF metadata\n"
        "  -> Passed to LLM as system context"
    )

    pdf.sub_heading("Three Fallback Levels")
    pdf.numbered_item(1, "FAISS + Embeddings (if index exists and sentence-transformers loaded)")
    pdf.numbered_item(2, "Keyword Fallback (if FAISS unavailable - matches keywords to predefined knowledge)")
    pdf.numbered_item(3, "Raw context return (if Groq API also fails - returns retrieved text directly)")
    pdf.ln(3)
    pdf.info_box("This means the demo NEVER crashes, even if FAISS, sentence-transformers, or Groq API are unavailable.", "tip")

    pdf.sub_heading("Index Building: extract_docs.py (269 lines)")
    pdf.code_block(
        "Local docs/ folder (29 PDFs)\n"
        "  -> Extract text using extract_text_from_file()\n"
        "  -> Save as data/sector_docs.json\n"
        "  -> Chunk with sliding window (size=800, overlap=100)\n"
        "  -> Embed with all-MiniLM-L6-v2\n"
        "  -> Build FAISS IndexFlatL2\n"
        "  -> Save vectorstore/zed.index + chunks.pkl"
    )
    pdf.body_text(
        "Key: Uses overlapping chunks (100-char overlap) to prevent losing context at chunk boundaries. "
        "Supports 7+ file formats: PDF, DOCX, XLSX, CSV, TXT, Markdown, and even CorelDRAW (.cdr)."
    )

    pdf.sub_heading("Embedding Model: all-MiniLM-L6-v2")
    w = [45, 135]
    pdf.table_header(["Property", "Value"], w)
    pdf.simple_table_row(["Dimensions", "384"], w, True)
    pdf.simple_table_row(["Model Size", "~80 MB"], w)
    pdf.simple_table_row(["Speed", "~14,000 sentences/sec on GPU"], w, True)
    pdf.simple_table_row(["Languages", "English-focused, handles romanized Hindi"], w)

    # ═══════════════════════════════════════════
    # SECTION 7: FRONTEND
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("7", "Frontend Deep Dive")

    pdf.sub_heading("index.html - Single-Page Application (1,951 lines)")
    pdf.body_text("Layout: Indian Tricolor Stripe -> Teal Top Bar (Language + Status) -> White Header (Logos) -> Tabs -> Active Panel -> Input Area")
    pdf.ln(2)

    pdf.sub_sub_heading("Tab 1: Ask ZED (Chat)")
    pdf.bullet("Welcome Screen with 3 feature cards + quick suggestion chips")
    pdf.bullet("Chat messages with user/bot avatars, typing animation (CSS keyframes)")
    pdf.bullet("Source tags showing whether response came from AI, RAG, or fallback")

    pdf.sub_sub_heading("Tab 2: Readiness Assessment")
    pdf.bullet("Enterprise Details Form: Name, Sector (17 NIC divisions), Type, Target Cert, Special Category")
    pdf.bullet("20-Question Checklist with Yes/No toggle buttons")
    pdf.bullet("Result Card: Score circle, readiness label, subsidy pill, strengths/gaps tags, AI roadmap")

    pdf.sub_sub_heading("Tab 3: Sector Guidance")
    pdf.bullet("Sector Selector with 13 industry sectors (NIC codes)")
    pdf.bullet("RAG-powered chat with source attribution showing PDF document name")

    pdf.sub_heading("Key Frontend Features")
    pdf.numbered_item(1, "Multilingual Support: 12 Indian languages with auto-detection from script (Devanagari -> Hindi, etc.) + RTL for Urdu")
    pdf.numbered_item(2, "Voice Input: Web Speech API with locale codes (hi-IN, ta-IN, etc.) + recording animation + toast notification")
    pdf.numbered_item(3, "File Attachment: Supports PDF, DOC, DOCX, XLS, XLSX, CSV, TXT, CDR, PNG, JPG with badge UI")
    pdf.numbered_item(4, "Auto-growing TextArea: Dynamically resizes up to 108px max height")
    pdf.numbered_item(5, "Health Check: Status dot shows 'AI + RAG connected' / 'AI connected' / 'fallback mode' / 'offline'")
    pdf.numbered_item(6, "Smart API URL Detection: Works both locally and on Render without code changes")

    # ═══════════════════════════════════════════
    # SECTION 8: DATA FLOW
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("8", "Data Flow - End to End")

    pdf.sub_heading("Flow 1: Chat Question")
    pdf.code_block(
        'User types: "How to get Bronze?"\n'
        "  1. Frontend: chatSendText(q) - hide welcome, show user bubble, push history\n"
        "  2. POST /chat { message, history[last 8], language }\n"
        "  3. Backend: build messages = [system_prompt, ...history, user_msg]\n"
        "  4. call_groq(messages, 700) -> Groq API -> LLaMA 3.1 -> response\n"
        '  5. Return: { reply: "...", source: "groq" }\n'
        "     (If Groq fails -> chat_fallback() -> source: 'fallback')\n"
        "  6. Frontend: remove typing, show bot bubble + source tag"
    )

    pdf.sub_heading("Flow 2: Assessment")
    pdf.code_block(
        "User fills form + answers 20 questions -> clicks Submit\n"
        '  1. Frontend: validate name, sector, all Qs answered\n'
        '  2. POST /assessment { name, sector, type, answers, target, category }\n'
        "  3. Backend:\n"
        "     a. score = sum(weight where answer=true) / total_weights\n"
        "     b. Check Bronze/Silver/Gold via QID set operations\n"
        "     c. Calculate subsidy (base + bonus, cap 90%)\n"
        "     d. Generate AI roadmap via call_groq()\n"
        "  4. Return: { score, readiness, strengths, gaps, subsidy, roadmap }\n"
        "  5. Frontend: animate score circle, show tags, render roadmap"
    )

    pdf.sub_heading("Flow 3: Sector RAG Query")
    pdf.code_block(
        'User selects "Textiles" + asks: "What documents?"\n'
        '  1. POST /sector-chat { message, sector, history, language }\n'
        '  2. Backend: prepend sector -> "Textiles sector: What documents?"\n'
        "  3. retrieve(query): encode -> FAISS top-5 -> return chunks + sources\n"
        '  4. System prompt: "Answer from context only" + context\n'
        "  5. call_groq() -> AI response grounded in documents\n"
        '  6. Return: { reply, source: "RAG - NIC_Division_13.pdf" }'
    )

    # ═══════════════════════════════════════════
    # SECTION 9: API ENDPOINTS
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("9", "API Endpoints Reference")

    pdf.sub_heading("GET / - Serve Frontend")
    pdf.body_text("Returns frontend/index.html if it exists, otherwise returns JSON status.")

    pdf.sub_heading("GET /health - Health Check")
    pdf.code_block(
        '{\n'
        '    "status": "ok",\n'
        '    "groq_connected": true,\n'
        '    "rag_loaded": true,\n'
        '    "assessment_questions": 20\n'
        '}'
    )

    pdf.sub_heading("POST /chat - General ZED Q&A")
    pdf.sub_sub_heading("Request:")
    pdf.code_block(
        '{\n'
        '    "message": "How to apply for Bronze?",\n'
        '    "history": [{"role":"user","content":"..."}, ...],\n'
        '    "language": "English"\n'
        '}'
    )
    pdf.sub_sub_heading("Response:")
    pdf.code_block('{ "reply": "To apply for Bronze...", "source": "groq" }')

    pdf.sub_heading("POST /assessment - Readiness Assessment")
    pdf.sub_sub_heading("Request:")
    pdf.code_block(
        '{\n'
        '    "enterprise_name": "Sharma Textiles",\n'
        '    "sector": "Textiles (NIC 13)",\n'
        '    "enterprise_type": "Micro",\n'
        '    "answers": {"1": true, "2": false, ...},\n'
        '    "target_cert": "Bronze",\n'
        '    "special_category": "Women-Owned"\n'
        '}'
    )
    pdf.sub_sub_heading("Response:")
    pdf.code_block(
        '{\n'
        '    "score": 72,\n'
        '    "readiness": "Ready for Bronze!",\n'
        '    "strengths": ["Leadership", "5S Workplace"],\n'
        '    "gaps": ["Lean & Waste", "IT Adoption"],\n'
        '    "subsidy_eligible": "up to 90% (+10% Women Owned)",\n'
        '    "roadmap": "**Summary** Your enterprise is Bronze-ready..."\n'
        '}'
    )

    pdf.sub_heading("POST /sector-chat - RAG Sector Guidance")
    pdf.sub_sub_heading("Response includes source PDF:")
    pdf.code_block('{ "reply": "For textiles...", "source": "RAG - NIC_Division_13.pdf" }')

    # ═══════════════════════════════════════════
    # SECTION 10: DESIGN PATTERNS
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("10", "Design Patterns & Engineering Decisions")

    pdf.sub_heading("1. Graceful Degradation Pattern")
    pdf.code_block(
        "Level 1: FAISS + Embeddings + Groq LLM     <- Best quality\n"
        "Level 2: Keyword Fallback + Groq LLM        <- If FAISS fails\n"
        "Level 3: Keyword Fallback only               <- If Groq API fails\n"
        "Level 4: Hardcoded default response           <- If everything fails"
    )
    pdf.info_box("Why? Government demos cannot crash. Even if internet is down, the chatbot responds.", "tip")

    pdf.sub_heading("2. Prompt Engineering")
    pdf.bullet("System prompt contains compressed ZED knowledge (~78 lines)")
    pdf.bullet("Language instruction appended dynamically based on user's language selection")
    pdf.bullet("Assessment roadmap uses structured prompt with specific output format (Summary/Missing/Plan)")

    pdf.sub_heading("3. Client-Side State Management")
    pdf.bullet("Chat history in JavaScript arrays - no server-side sessions")
    pdf.bullet("Stateless backend -> easy to scale horizontally")
    pdf.bullet("History window limited to last 6-8 messages to control token usage")

    pdf.sub_heading("4. Set Theory for Certification Logic")
    pdf.body_text("Instead of complex if/else chains, uses Python set operations (issubset) for clean, correct, readable certification level determination.")

    pdf.sub_heading("5. Monolithic Deployment")
    pdf.body_text("FastAPI serves API + static files. Single 'uvicorn main:app' command starts everything. Works on Render.com free tier.")

    # ═══════════════════════════════════════════
    # SECTION 11: PROS
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("11", "Pros (Strengths)")

    pdf.sub_heading("Technical Strengths")
    w = [8, 55, 117]
    pdf.table_header(["#", "Strength", "Impact"], w)
    pros = [
        ("1", "RAG over 29 real govt PDFs", "Answers grounded in official documents, not hallucinations"),
        ("2", "Graceful degradation (4 lvls)", "Demo never crashes, even without internet"),
        ("3", "12 Indian language support", "Accessible to non-English MSMEs (90%+ of target)"),
        ("4", "Voice input (Web Speech)", "Critical for users with limited literacy"),
        ("5", "Sub-second FAISS retrieval", "Vector search is near-instant with 1000+ chunks"),
        ("6", "Zero-config deployment", "No database, no Redis, no Docker - pip install and run"),
        ("7", "Free infrastructure", "Groq free tier + Render free tier = Rs.0 cost"),
        ("8", "Multi-format ingestion", "PDF, DOCX, XLSX, CSV, CDR - handles govt file chaos"),
        ("9", "Auto-detect language", "Detects Devanagari/Tamil/etc. and auto-switches"),
        ("10", "Assessment + AI roadmap", "Not just chatbot - actionable business intelligence"),
    ]
    for i, (n, s, imp) in enumerate(pros):
        pdf.simple_table_row([n, s, imp], w, i % 2 == 0)

    pdf.ln(5)
    pdf.sub_heading("Product Strengths")
    w2 = [8, 50, 122]
    pdf.table_header(["#", "Strength", "Impact"], w2)
    pprods = [
        ("1", "Solves real problem", "63M MSMEs need ZED guidance"),
        ("2", "Government-branded UI", "Indian tricolor, official logos, ZED colour scheme"),
        ("3", "3-tab design", "Clear separation of use cases"),
        ("4", "50-question test bank", "QA is built into the project"),
        ("5", "Source attribution", "User sees which PDF the answer came from"),
    ]
    for i, (n, s, imp) in enumerate(pprods):
        pdf.simple_table_row([n, s, imp], w2, i % 2 == 0)

    # ═══════════════════════════════════════════
    # SECTION 12: CONS
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("12", "Cons (Limitations & Technical Debt)")

    pdf.sub_heading("Technical Limitations")
    w = [8, 45, 15, 112]
    pdf.table_header(["#", "Limitation", "Sev.", "Mitigation"], w)
    cons = [
        ("1", "No authentication", "High", "Add JWT or API key auth"),
        ("2", "No rate limiting", "High", "Add slowapi middleware"),
        ("3", "No conversation persistence", "Med", "Add Redis/SQLite for sessions"),
        ("4", "Single-file frontend (1951 ln)", "Med", "Refactor to React or componentize"),
        ("5", "Hardcoded assessment Qs", "Med", "Load from API dynamically"),
        ("6", "No input validation (FE)", "Med", "Sanitize with DOMPurify"),
        ("7", "FAISS brute-force", "Low", "Switch to IndexIVFFlat for millions"),
        ("8", "English-centric embeddings", "Med", "Use multilingual-e5-large"),
        ("9", "No streaming responses", "Low", "Use SSE/WebSocket streaming"),
        ("10", "API key in .env.example", "High", "Remove real key from template"),
        ("11", "File upload UI exists", "Low", "Backend doesn't process files yet"),
        ("12", "No prompt injection guard", "Med", "Add input screening + guard prompt"),
    ]
    for i, (n, lim, sev, mit) in enumerate(cons):
        pdf.simple_table_row([n, lim, sev, mit], w, i % 2 == 0)

    pdf.ln(5)
    pdf.sub_heading("Product Limitations")
    pdf.bullet("No user feedback collection - can't measure accuracy")
    pdf.bullet("No analytics dashboard - officers can't see usage patterns")
    pdf.bullet("No admin panel - can't update knowledge base without code changes")
    pdf.bullet("Assessment questions are self-reported - no verification of actual compliance")

    # ═══════════════════════════════════════════
    # SECTION 13: SCALABILITY
    # ═══════════════════════════════════════════
    pdf.page_break_check(80)
    pdf.section_title("13", "Scalability Analysis")

    pdf.sub_heading("Current Capacity")
    w = [50, 50, 80]
    pdf.table_header(["Component", "Limit", "Bottleneck"], w)
    pdf.simple_table_row(["FastAPI (1 worker)", "~100 concurrent users", "CPU-bound embedding"], w, True)
    pdf.simple_table_row(["Groq free tier", "30 req/min, 14.4K/day", "API rate limit"], w)
    pdf.simple_table_row(["FAISS (in-memory)", "~500K chunks on 4GB", "Memory"], w, True)
    pdf.simple_table_row(["Render free tier", "512 MB RAM", "Cold starts after 15 min"], w)

    pdf.ln(5)
    pdf.sub_heading("Scaling Path")
    pdf.code_block(
        "Current (POC):     1 server, 1 worker, in-memory FAISS\n"
        "                          |\n"
        "Phase 2 (Pilot):   Gunicorn 4 workers, Redis for sessions\n"
        "                          |\n"
        "Phase 3 (Prod):    Kubernetes, Milvus/Pinecone, GPU, LB"
    )

    # ═══════════════════════════════════════════
    # SECTION 14: SECURITY
    # ═══════════════════════════════════════════
    pdf.page_break_check(60)
    pdf.section_title("14", "Security Considerations")

    w = [45, 55, 80]
    pdf.table_header(["Aspect", "Current Status", "Risk / Action"], w)
    sec = [
        ("API key mgmt", ".env file, excluded from git", "Good - keep it"),
        ("CORS", 'allow_origins=["*"]', "Too permissive - restrict for prod"),
        ("Input sanitization", "Basic HTML escaping (FE)", "Needs server-side sanitization"),
        ("Rate limiting", "None", "DoS vulnerability - add slowapi"),
        ("Authentication", "None", "Open to all - add JWT"),
        ("HTTPS", "Via Render deployment", "Automatic - good"),
        ("Prompt injection", "No guard rails", "Add screening + guard prompt"),
    ]
    for i, (a, s, r) in enumerate(sec):
        pdf.simple_table_row([a, s, r], w, i % 2 == 0)

    # ═══════════════════════════════════════════
    # SECTION 15: FUTURE ROADMAP
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("15", "Future Roadmap")

    pdf.sub_heading("Phase 1: Immediate Improvements (1-2 weeks)")
    pdf.bullet("Add rate limiting with slowapi")
    pdf.bullet("Remove hardcoded API key from .env.example")
    pdf.bullet("Add server-side input validation and sanitization")
    pdf.bullet("Implement basic analytics (query count, top questions, error rate)")
    pdf.bullet("Add response streaming (SSE) for better UX")
    pdf.bullet("Load assessment questions dynamically from API")

    pdf.sub_heading("Phase 2: Enhanced Intelligence (1-2 months)")
    pdf.bullet("Multilingual embeddings - switch to multilingual-e5-large for better Hindi/regional RAG")
    pdf.bullet("Hybrid search - combine FAISS vector search with BM25 keyword search")
    pdf.bullet("Re-ranking - use cross-encoder to re-rank FAISS results before LLM")
    pdf.bullet("Document versioning - auto-update index when new ZED circulars published")
    pdf.bullet("Conversation memory - store sessions in Redis for multi-turn context")
    pdf.bullet("File processing - actually extract and use uploaded documents in responses")

    pdf.sub_heading("Phase 3: Platform Expansion (3-6 months)")
    pdf.bullet("WhatsApp Bot - same backend, new channel (80%+ MSMEs use WhatsApp)")
    pdf.bullet("IVR Phone Line - text-to-speech for 40% MSMEs without smartphones")
    pdf.bullet("Admin Dashboard - officers view analytics, update knowledge, review queries")
    pdf.bullet("Fine-tuned Model - fine-tune LLaMA on ZED-specific Q&A pairs")
    pdf.bullet("Automated PDF Ingestion - watch govt website, auto-index new documents")

    pdf.sub_heading("Phase 4: Production Scale (6-12 months)")
    pdf.bullet("Migrate to Milvus/Pinecone for managed vector DB")
    pdf.bullet("Kubernetes deployment with auto-scaling")
    pdf.bullet("Government SSO integration (Parichay/DigiLocker)")
    pdf.bullet("Feedback loop - user ratings -> fine-tuning dataset")
    pdf.bullet("Offline mode - PWA with cached responses for poor connectivity areas")
    pdf.bullet("Integration with ZED Portal - auto-fill application forms from assessment")

    # ═══════════════════════════════════════════
    # SECTION 16: INTERVIEW Q&A
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("16", "Interview Q&A - Expected Questions")

    pdf.sub_heading("Architecture & Design Questions")
    pdf.ln(2)

    qa_arch = [
        ("Why did you choose FastAPI over Flask/Django?",
         "FastAPI gives automatic request validation via Pydantic, async support, and built-in OpenAPI docs - "
         "all with minimal boilerplate. Flask would need marshmallow for validation and is synchronous by default. "
         "Django is overkill for an API-only service. FastAPI is the modern standard for Python APIs."),

        ("Why a single HTML file instead of React?",
         "This is a government POC. The target deployers are JS-level officers who may not have Node.js installed. "
         "A single HTML file eliminates the entire build toolchain - no npm, no webpack, no 'npm run build'. "
         "The tradeoff is code organization, but for a POC with 3 tabs, it's manageable. "
         "For production, I'd refactor to React or Vue."),

        ("Why FAISS and not Pinecone/Chroma?",
         "FAISS runs locally with zero setup - no API key, no cloud account, no network dependency. "
         "For a government POC that might be demo'd on a laptop without internet, local FAISS is critical. "
         "Pinecone/Weaviate are better for production (managed, scalable), but they add complexity and cost."),

        ("Explain the RAG pipeline in simple terms.",
         "Imagine you have 29 textbooks. When someone asks a question, you don't read all 29 - "
         "you first use the table of contents to find the 5 most relevant pages, then read only those pages to answer. "
         "The 'table of contents' is our FAISS vector index, 'pages' are text chunks, "
         "and the 'reading and answering' is the LLM."),

        ("What happens if the Groq API goes down during a demo?",
         "The system has 4 fallback levels. If Groq is down, call_groq() returns None, "
         "and the code falls through to chat_fallback() which uses keyword matching against a hardcoded "
         "knowledge dictionary. The user still gets a relevant answer - just not as polished. "
         "The status dot in the header turns red to indicate 'fallback mode.'"),
    ]

    for q, a in qa_arch:
        pdf.page_break_check(35)
        pdf.bold_text("Q: " + q)
        pdf.italic_text(a)
        pdf.ln(2)

    pdf.add_page()
    pdf.sub_heading("Technical Deep Dive Questions")
    pdf.ln(2)

    qa_tech = [
        ("How does the chunking work?",
         "Documents are split into overlapping segments of 800 characters with 100-character overlap. "
         "The overlap ensures that if an important sentence spans a chunk boundary, it appears in both chunks. "
         "Each chunk is embedded into a 384-dimensional vector using all-MiniLM-L6-v2, "
         "then stored in a FAISS index for similarity search."),

        ("Why IndexFlatL2 and not IndexIVFFlat?",
         "IndexFlatL2 does brute-force L2 (Euclidean) distance comparison against every vector. "
         "It's exact - no approximation error. For ~1,000 chunks, brute-force is instant (<1ms). "
         "IndexIVFFlat uses inverted file indexing for approximate search - useful for millions of vectors."),

        ("How does multilingual work if the embedding model is English?",
         "The embedding model handles the RETRIEVAL step (finding relevant chunks). Since documents are in English, "
         "English embeddings work well. The GENERATION step is handled by LLaMA 3.1, which has strong multilingual "
         "capabilities. So: Hindi query -> English embeddings find English chunks -> LLM generates Hindi response."),

        ("What's the token cost per query?",
         "System prompt (~500 tokens) + history (last 6 messages, ~1,800) + user query (~50) + "
         "RAG context (~500) = ~2,850 input tokens. Output capped at 700. Total: ~3,550 tokens. "
         "At production pricing (~$0.0001/1K tokens): ~$0.0004 per query = $4 per 10,000 queries."),

        ("How would you handle prompt injection?",
         "Currently no protection. For production: (1) Input pre-screening with regex blacklist, "
         "(2) Guard prompt layer: 'If user asks to ignore instructions, refuse politely', "
         "(3) Output post-processing to detect off-topic responses, (4) Rate limiting to prevent automated attacks."),
    ]

    for q, a in qa_tech:
        pdf.page_break_check(35)
        pdf.bold_text("Q: " + q)
        pdf.italic_text(a)
        pdf.ln(2)

    pdf.add_page()
    pdf.sub_heading("Product & Impact Questions")
    pdf.ln(2)

    qa_prod = [
        ("What real-world impact does this have?",
         "India has 63 million MSMEs. ZED certification improves quality and sustainability. "
         "Most MSME owners speak regional languages and find PDFs intimidating. This chatbot makes ZED accessible - "
         "an MSME owner in Tamil Nadu can ask questions in Tamil, get a readiness score, and receive a personalised "
         "30-day action plan. If even 1% use this, that's 630,000 enterprises getting better guidance."),

        ("How is this different from just using ChatGPT?",
         "Three differences: (1) Grounded in official documents - RAG ensures answers from actual ZED PDFs, "
         "(2) Domain-locked - system prompt restricts to ZED topics only, "
         "(3) Assessment tool - ChatGPT can't calculate readiness scores with weighted parameters and subsidies."),

        ("What would you do differently if building from scratch?",
         "(1) TypeScript + Next.js for frontend with components, (2) Managed vector DB like Pinecone, "
         "(3) User auth and conversation persistence from start, (4) Streaming responses for better UX, "
         "(5) Multilingual embedding model, (6) Automated testing - unit + integration, (7) CI/CD with GitHub Actions."),
    ]

    for q, a in qa_prod:
        pdf.page_break_check(35)
        pdf.bold_text("Q: " + q)
        pdf.italic_text(a)
        pdf.ln(2)

    pdf.sub_heading("Behavioural Questions")
    pdf.ln(2)

    qa_beh = [
        ("What was the most challenging part?",
         "Multi-format document ingestion. Government documents come in DOCX, Excel, even CorelDRAW (.cdr). "
         "I built handlers for 7+ formats. CDR files were handled by treating them as ZIP archives "
         "and extracting XML/SVG text content - a creative solution requiring reverse-engineering the format."),

        ("How did you ensure accuracy?",
         "Three layers: (1) Knowledge grounding - system prompt contains verified ZED facts from official documents, "
         "(2) RAG - sector answers retrieved from actual PDFs, not generated from training, "
         "(3) Test bank - 50 categorised test questions with expected topics, manually verified."),

        ("What did you learn from this project?",
         "(1) RAG is more engineering than ML - chunking strategy and embedding model matter more than which LLM, "
         "(2) Graceful degradation is essential for govt/enterprise - demos can't crash, "
         "(3) Simplicity beats elegance for POCs - single HTML > React app requiring Node.js, "
         "(4) Domain knowledge is half the battle - understanding ZED's parameters was as important as coding."),
    ]

    for q, a in qa_beh:
        pdf.page_break_check(35)
        pdf.bold_text("Q: " + q)
        pdf.italic_text(a)
        pdf.ln(2)

    # ═══════════════════════════════════════════
    # SECTION 17: DEMO GUIDE
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("17", "How to Demo This Project")

    pdf.sub_heading("2-Minute Quick Demo")
    pdf.numbered_item(1, 'Open the app -> Show the government-branded UI with tricolor stripe')
    pdf.numbered_item(2, 'Ask: "What is ZED certification?" -> Show AI response with source tag')
    pdf.numbered_item(3, 'Switch to Hindi -> Ask: "ZED ka kya matlab hai?" -> Show multilingual response')
    pdf.numbered_item(4, 'Switch to Assessment tab -> Fill details -> Submit -> Show score + roadmap')
    pdf.numbered_item(5, 'Switch to Sector tab -> Select Textiles -> Ask question -> Show RAG response with PDF source')

    pdf.ln(5)
    pdf.sub_heading("Technical Demo Points")
    pdf.bullet("Show terminal -> health check showing 'AI + RAG connected'")
    pdf.bullet("Show FAISS index loading logs on startup")
    pdf.bullet("Kill internet -> Show fallback mode still works")
    pdf.bullet("Show .env file -> Explain API key management")
    pdf.bullet("Show docs/ folder -> 29 official PDFs -> Explain ingestion pipeline")

    pdf.ln(5)
    pdf.sub_heading("GitHub Portfolio Pitch")
    pdf.info_box(
        '"This project demonstrates: FastAPI backend development, RAG pipeline with FAISS, '
        'LLM integration (Groq/LLaMA), multilingual NLP, government-scale product design, '
        'graceful error handling, and deployment on cloud platforms. '
        "It's not a toy project - it solves a real problem for 63 million MSMEs.\"",
        "tip"
    )

    # ═══════════════════════════════════════════
    # FINAL PAGE
    # ═══════════════════════════════════════════
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*pdf.C_DARK)
    pdf.cell(0, 14, "Good Luck with Your Interview!", align="C")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*pdf.C_MID)
    pdf.cell(0, 8, "Project: ZED Mitra v2 - Full Stack AI Chatbot", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, "By: Ayushi", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, "Stack: Python | FastAPI | FAISS | Sentence Transformers | Groq | LLaMA 3.1 | Vanilla JS", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, "Lines of Code: ~3,277 (Backend: ~1,326 + Frontend: ~1,951)", align="C")
    pdf.ln(20)
    pdf.set_draw_color(*pdf.C_PRIMARY)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 8, "This document was auto-generated from codebase analysis.", align="C")

    # ═══════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════
    pdf.output(OUTPUT_PDF)
    print(f"\nPDF generated successfully!")
    print(f"Location: {OUTPUT_PDF}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
