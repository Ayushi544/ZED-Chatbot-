"""
extract_docs.py — Run this AFTER you download the ZED PDFs

Steps:
1. Create a folder called: docs/
2. Put all ZED PDFs inside it
3. Run: python extract_docs.py
4. It creates vectorstore/zed.index and vectorstore/chunks.pkl
5. Restart the backend — RAG will activate automatically

You don't need to run this for tonight's demo.
The chatbot works without it using the built-in knowledge base.
"""

import os
import re
import json
import pickle
import numpy as np
from pathlib import Path

# ── Check dependencies ──
try:
    import fitz
except ImportError:
    print("Install pymupdf first:  pip install pymupdf")
    exit(1)

try:
    import faiss
except ImportError:
    print("Install faiss first:  pip install faiss-cpu")
    exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Install sentence-transformers first:  pip install sentence-transformers")
    exit(1)

def extract_text_with_pages(filepath):
    """
    Extract text from PDF with page numbers.
    Returns list of (page_num, text) tuples.
    """
    pages = []
    try:
        import fitz
        pdf = fitz.open(filepath)
        for i, page in enumerate(pdf):
            page_text = page.get_text()
            if page_text and page_text.strip():
                pages.append((i + 1, page_text))
        pdf.close()
    except Exception as e:
        print(f"Error reading PDF pages {filepath}: {e}")
    return pages


def extract_text_from_file(filepath):
    """
    Extracts text content from files of various extensions.
    Supports: .pdf, .docx, .xlsx, .xls, .txt, .md, .csv, .cdr, and others.
    """
    import os
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    
    if ext == ".pdf":
        try:
            import fitz
            pdf = fitz.open(filepath)
            for page in pdf:
                page_text = page.get_text()
                if page_text:
                    text += page_text
            pdf.close()
        except Exception as e:
            print(f"Error reading PDF {filepath}: {e}")
            
    elif ext == ".docx":
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(filepath) as z:
                xml_content = z.read('word/document.xml')
            root = ET.fromstring(xml_content)
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = []
            for p in root.findall('.//w:p', namespaces):
                p_text = "".join([t.text for t in p.findall('.//w:t', namespaces) if t.text])
                if p_text:
                    paragraphs.append(p_text)
            text = "\n".join(paragraphs)
        except Exception as e:
            print(f"Error reading docx {filepath}: {e}")
            
    elif ext in [".xlsx", ".xls"]:
        try:
            import pandas as pd
            sheets = pd.read_excel(filepath, sheet_name=None)
            sheet_texts = []
            for sheet_name, df_sheet in sheets.items():
                sheet_texts.append(f"Sheet: {sheet_name}\n" + df_sheet.to_string())
            text = "\n\n".join(sheet_texts)
        except Exception as e:
            print(f"Error reading Excel {filepath}: {e}")
            
    elif ext == ".csv":
        try:
            import csv
            lines = []
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        lines.append(", ".join(row))
            text = "\n".join(lines)
        except Exception as e:
            print(f"Error reading CSV {filepath}: {e}")
            
    elif ext in [".txt", ".md"]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading text file {filepath}: {e}")
            
    elif ext == ".cdr":
        # Modern CDR formats are ZIP archives
        try:
            import zipfile
            import re
            if zipfile.is_zipfile(filepath):
                text_parts = []
                with zipfile.ZipFile(filepath) as z:
                    for name in z.namelist():
                        if name.endswith(('.xml', '.txt', '.svg')):
                            try:
                                content = z.read(name).decode('utf-8', errors='ignore')
                                clean_txt = re.sub(r'<[^>]+>', ' ', content)
                                clean_txt = re.sub(r'\s+', ' ', clean_txt).strip()
                                if len(clean_txt) > 20:
                                    text_parts.append(clean_txt)
                            except Exception:
                                pass
                if text_parts:
                    text = "\n".join(text_parts)
        except Exception:
            pass
            
        # Fallback to extracting printable ASCII strings (works on binary/older formats)
        if not text.strip():
            try:
                with open(filepath, "rb") as f:
                    data = f.read()
                import re
                ascii_strings = re.findall(br'[a-zA-Z0-9\s.,;:!?()\'"-]{6,}', data)
                text_list = []
                for s in ascii_strings:
                    try:
                        decoded = s.decode('ascii').strip()
                        if len(decoded) > 10:
                            text_list.append(decoded)
                    except Exception:
                        pass
                text = " ".join(text_list)
            except Exception as e:
                print(f"Error extracting strings from CDR {filepath}: {e}")
                
    else:
        # Fallback for generic files: text read first, then binary extraction
        try:
            with open(filepath, "r", encoding="utf-8", errors="strict") as f:
                text = f.read()
        except Exception:
            try:
                with open(filepath, "rb") as f:
                    data = f.read()
                import re
                ascii_strings = re.findall(br'[a-zA-Z0-9\s.,;:!?()\'"-]{6,}', data)
                text_list = []
                for s in ascii_strings:
                    try:
                        decoded = s.decode('ascii').strip()
                        if len(decoded) > 10:
                            text_list.append(decoded)
                    except Exception:
                        pass
                text = " ".join(text_list)
            except Exception as e:
                print(f"Error reading generic file {filepath}: {e}")
                
    return text


DOCS_DIR    = Path("docs")
DATA_DIR    = Path("data")
VECTOR_DIR  = Path("vectorstore")

DATA_DIR.mkdir(exist_ok=True)
VECTOR_DIR.mkdir(exist_ok=True)

if not DOCS_DIR.exists() or not any(f.is_file() for f in DOCS_DIR.iterdir()):
    print("[WARN] No files found in docs/ folder.")
    print("Create a docs/ folder and put your ZED files inside it.")
    exit(1)

# ── Step 1: Extract text from all documents ──
print("Step 1: Extracting text from documents...")
docs = {}
for file_path in DOCS_DIR.iterdir():
    if not file_path.is_file():
        continue
    
    # Skip temporary/hidden files
    if file_path.name.startswith("."):
        continue

    try:
        text = extract_text_from_file(str(file_path))
        if len(text.strip()) >= 50:
            docs[file_path.name] = text
            print(f"  [OK] {file_path.name} - {len(text)} characters")
        else:
            print(f"  [SKIP] {file_path.name} - text too short or empty, skipped")
    except Exception as e:
        print(f"  [ERROR] {file_path.name} - error: {e}")

with open(DATA_DIR / "sector_docs.json", "w", encoding="utf-8") as f:
    json.dump(docs, f, ensure_ascii=False, indent=2)
print(f"\nExtracted {len(docs)} documents -> data/sector_docs.json")

# ── Step 2: Chunk (sentence-aware) ──
print("\nStep 2: Chunking text (sentence-aware)...")

def chunk_text_smart(text, size=800, overlap=150):
    """
    Sentence-aware chunking — splits at sentence boundaries instead of
    mid-word. Uses period, question mark, exclamation, Hindi danda, and
    newlines as sentence delimiters.
    """
    sentences = re.split(r'(?<=[.!?।\n])\s+', text)
    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) > size and current.strip():
            chunks.append(current.strip())
            # Keep overlap by retaining last ~overlap chars worth of words
            words = current.split()
            overlap_text = ""
            while words and len(overlap_text) < overlap:
                overlap_text = words.pop() + " " + overlap_text
            current = overlap_text.strip() + " " + sent
        else:
            current = (current + " " + sent).strip()

    if current.strip() and len(current.strip()) > 60:
        chunks.append(current.strip())

    return chunks


def dedup_chunks(chunks, meta, threshold=0.9):
    """Remove near-duplicate chunks based on character overlap ratio."""
    unique_chunks = []
    unique_meta   = []
    seen_set      = set()

    for chunk, m in zip(chunks, meta):
        # Simple dedup: normalize whitespace and check exact match
        normalized = " ".join(chunk.split())
        if normalized not in seen_set:
            seen_set.add(normalized)
            unique_chunks.append(chunk)
            unique_meta.append(m)

    removed = len(chunks) - len(unique_chunks)
    if removed > 0:
        print(f"  Dedup removed {removed} duplicate chunks")
    return unique_chunks, unique_meta


all_chunks = []
all_meta   = []

for source_name, text in docs.items():
    ext = os.path.splitext(source_name)[1].lower()

    # For PDFs: chunk per page with page numbers in metadata
    if ext == ".pdf":
        pages = extract_text_with_pages(str(DOCS_DIR / source_name))
        page_chunks = 0
        for page_num, page_text in pages:
            chunks = chunk_text_smart(page_text)
            for chunk in chunks:
                all_chunks.append(chunk)
                all_meta.append({"source": source_name, "page": page_num})
                page_chunks += 1
        print(f"  {source_name} -> {page_chunks} chunks (with page numbers)")
    else:
        chunks = chunk_text_smart(text)
        for chunk in chunks:
            all_chunks.append(chunk)
            all_meta.append({"source": source_name})
        print(f"  {source_name} -> {len(chunks)} chunks")

# Deduplicate
all_chunks, all_meta = dedup_chunks(all_chunks, all_meta)
print(f"\nTotal chunks after dedup: {len(all_chunks)}")

# -- Step 3: Embed --
print("\nStep 3: Creating embeddings (this takes a few minutes)...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(all_chunks, show_progress_bar=True)
print(f"Embeddings shape: {embeddings.shape}")

# -- Step 4: Build FAISS index --
print("\nStep 4: Building FAISS index...")
dim   = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings, dtype="float32"))

faiss.write_index(index, str(VECTOR_DIR / "zed.index"))
print(f"  [OK] Saved vectorstore/zed.index")

with open(VECTOR_DIR / "chunks.pkl", "wb") as f:
    pickle.dump({"chunks": all_chunks, "meta": all_meta}, f)
print(f"  [OK] Saved vectorstore/chunks.pkl")

print(f"""
[OK] Done! FAISS index built with {len(all_chunks)} chunks from {len(docs)} files.

Now restart your backend:
  uvicorn main:app --reload --port 8000

The chatbot will automatically use real document retrieval.
""")
