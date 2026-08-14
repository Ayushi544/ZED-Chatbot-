import os
import re
import pickle
import requests
import fitz
import faiss
import numpy as np
import pandas as pd
import urllib3

from sentence_transformers import SentenceTransformer

# --------------------------
# CONFIG

# --------------------------

EXCEL_FILE = r"C:\Users\Ayushi\Downloads\fileszed re\zed_advisor_v2\zed_chatbot\backend\ZED_Upload.xlsx"
DOCS_DIR = "docs"
VECTORSTORE_DIR = "vectorstore"

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

urllib3.disable_warnings()

# --------------------------
# LOAD EXCEL
# --------------------------

# --------------------------
# HELPERS FOR GDRIVE & EXTENSIONS
# --------------------------

def get_gdrive_download_info(url):
    """
    Returns (download_url, default_filename) if it is a Google Drive link,
    else (None, None).
    """
    file_id = None
    if "drive.google.com" in url or "docs.google.com" in url:
        if "id=" in url:
            parts = url.split("id=")
            if len(parts) > 1:
                file_id = parts[1].split("&")[0]
        elif "/d/" in url:
            parts = url.split("/d/")
            if len(parts) > 1:
                file_id = parts[1].split("/")[0]
                
    if not file_id:
        return None, None
        
    if "document/d/" in url:
        return f"https://docs.google.com/document/d/{file_id}/export?format=pdf", f"{file_id}.pdf"
    elif "spreadsheets/d/" in url:
        return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx", f"{file_id}.xlsx"
    elif "presentation/d/" in url:
        return f"https://docs.google.com/presentation/d/{file_id}/export?format=pdf", f"{file_id}.pdf"
    else:
        return f"https://drive.google.com/uc?export=download&id={file_id}", f"gdrive_{file_id}"


def extract_text_from_file(filepath):
    """
    Extracts text content from files of various extensions.
    Supports: .pdf, .docx, .xlsx, .xls, .txt, .md, .csv, .cdr, and others.
    """
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

# --------------------------
# LOAD EXCEL
# --------------------------

print("Loading Excel...")

df = pd.read_excel(EXCEL_FILE)

if "Redirection Link" not in df.columns:
    raise Exception(
        f"Column 'Redirection Link' not found.\nAvailable columns: {list(df.columns)}"
    )

urls = []

for u in df["Redirection Link"].dropna():

    u = str(u).strip()

    if u.startswith("http"):
        urls.append(u)

print(f"Found {len(urls)} valid URLs")

# --------------------------
# DOWNLOAD DOCUMENTS
# --------------------------

print("Downloading documents...")

for url in urls:

    try:
        gdrive_url, default_filename = get_gdrive_download_info(url)
        if gdrive_url:
            download_url = gdrive_url
            filename = default_filename
        else:
            download_url = url
            filename = url.split("/")[-1].split("?")[0]

        if not filename or filename == "":
            filename = "downloaded_file"

        r = requests.get(
            download_url,
            timeout=60,
            verify=False,
            stream=True
        )

        if r.status_code != 200:
            print(
                f"Failed ({r.status_code}) : {url}"
            )
            continue

        cd = r.headers.get("content-disposition")
        if cd:
            import re
            matches = re.findall(r'filename\*?=(?:utf-8\'\')?([^;\n]+)', cd)
            if matches:
                filename = matches[0].strip('\'" ')
            else:
                matches = re.findall(r'filename="?([^;\n"]+)"?', cd)
                if matches:
                    filename = matches[0].strip()

        if "." not in filename:
            content_type = r.headers.get("content-type", "").lower()
            ext = ""
            if "pdf" in content_type:
                ext = ".pdf"
            elif "word" in content_type or "msword" in content_type:
                ext = ".docx"
            elif "sheet" in content_type or "excel" in content_type:
                ext = ".xlsx"
            elif "text" in content_type or "plain" in content_type:
                ext = ".txt"
            elif "csv" in content_type:
                ext = ".csv"
            elif "cdr" in content_type or "coreldraw" in content_type:
                ext = ".cdr"
            elif "png" in content_type:
                ext = ".png"
            elif "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            filename = filename + ext

        filepath = os.path.join(
            DOCS_DIR,
            filename
        )

        if os.path.exists(filepath):
            print(f"Already exists: {filename}")
            r.close()
            continue

        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        r.close()

        print(
            f"Downloaded: {filename}"
        )

    except Exception as e:

        print(
            f"Error downloading: {url}"
        )

        print(e)


# --------------------------
# EXTRACT TEXT
# --------------------------

print("Extracting text...")

documents = []

for file in os.listdir(DOCS_DIR):
    path = os.path.join(DOCS_DIR, file)

    if os.path.isdir(path):
        continue

    try:
        text = extract_text_from_file(path)

        if len(text.strip()) < 50:
            print(f"Skipped: {file} (Extracted text too short: {len(text.strip())} chars)")
            continue

        documents.append(
            {
                "source": file,
                "text": text
            }
        )

        print(f"Extracted: {file} ({len(text)} chars)")

    except Exception as e:
        print(f"Error reading {file}: {e}")

print(
    f"Documents extracted: {len(documents)}"
)

if len(documents) == 0:

    raise Exception(
        "No documents extracted."
    )

# --------------------------
# CHUNKING
# --------------------------

print("Chunking (sentence-aware)...")

def chunk_text_smart(text, size=800, overlap=150):
    """
    Sentence-aware chunking — splits at sentence boundaries.
    """
    sentences = re.split(r'(?<=[.!?\u0964\n])\s+', text)
    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) > size and current.strip():
            chunks.append(current.strip())
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


def extract_pages_from_pdf(filepath):
    """Extract text per page from PDF, returns list of (page_num, text)."""
    pages = []
    try:
        pdf = fitz.open(filepath)
        for i, page in enumerate(pdf):
            page_text = page.get_text()
            if page_text and page_text.strip():
                pages.append((i + 1, page_text))
        pdf.close()
    except Exception as e:
        print(f"Error reading PDF pages {filepath}: {e}")
    return pages


chunks = []
meta = []

for doc in documents:
    source = doc["source"]
    ext = os.path.splitext(source)[1].lower()

    if ext == ".pdf":
        filepath = os.path.join(DOCS_DIR, source)
        pages = extract_pages_from_pdf(filepath)
        for page_num, page_text in pages:
            page_chunks = chunk_text_smart(page_text)
            for chunk in page_chunks:
                chunks.append(chunk)
                meta.append({"source": source, "page": page_num})
    else:
        text = doc["text"]
        doc_chunks = chunk_text_smart(text)
        for chunk in doc_chunks:
            chunks.append(chunk)
            meta.append({"source": source})

print(
    f"Chunks created: {len(chunks)}"
)

if len(chunks) == 0:

    raise Exception(
        "No chunks created."
    )

# --------------------------
# EMBEDDINGS
# --------------------------

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Generating embeddings...")

embeddings = model.encode(
    chunks,
    show_progress_bar=True
)

embeddings = np.array(
    embeddings,
    dtype=np.float32
)

print(
    "Embedding shape:",
    embeddings.shape
)

# --------------------------
# FAISS
# --------------------------

print("Building FAISS index...")

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)

index.add(
    embeddings
)

faiss.write_index(
    index,
    os.path.join(
        VECTORSTORE_DIR,
        "zed.index"
    )
)

# --------------------------
# SAVE CHUNKS
# --------------------------

with open(
    os.path.join(
        VECTORSTORE_DIR,
        "chunks.pkl"
    ),
    "wb"
) as f:

    pickle.dump(
        {
            "chunks": chunks,
            "meta": meta
        },
        f
    )

print()
print("SUCCESS")
print("Index saved")

print(
    os.path.join(
        VECTORSTORE_DIR,
        "zed.index"
    )
)

print(
    os.path.join(
        VECTORSTORE_DIR,
        "chunks.pkl"
    )
)