"""
ui_upload.py - Upload Material page for AI Study Assistant.
Handles text input, single file, and multi-file/folder uploads.
Creates Document objects (TextDocument, PDFDocument, MultiFileDocument) via polymorphism.
"""

import streamlit as st
import streamlit.components.v1 as components
import base64
import json
from document import TextDocument, PDFDocument, DocxDocument, XlsxDocument, PptxDocument, MultiFileDocument
from ui_utils import render_ai_loading

ALLOWED_EXTENSIONS = ("txt", "pdf", "docx", "xlsx", "xls", "pptx")
ICON_MAP = {
    "txt": "📝", "pdf": "📕", "docx": "📘", "doc": "📘",
    "xlsx": "📊", "xls": "📊", "pptx": "📽️", "ppt": "📽️",
    "folder": "📁"
}

# Map extension to Document class
EXT_TO_CLASS = {
    "txt": TextDocument,
    "pdf": PDFDocument,
    "docx": DocxDocument,
    "xlsx": XlsxDocument,
    "xls": XlsxDocument,
    "pptx": PptxDocument,
}

# Accept string for HTML file input
HTML_ACCEPT = ".txt,.pdf,.docx,.xlsx,.xls,.pptx"

FOLDER_PICKER_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: transparent;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100px;
    }
    #drop-zone {
        width: 100%;
        border: 2px dashed #cbd5e1;
        border-radius: 14px;
        padding: 24px 16px;
        text-align: center;
        transition: all 0.2s ease;
        cursor: pointer;
        background: #fafbfc;
    }
    #drop-zone:hover, #drop-zone.drag-over {
        border-color: #8b5cf6;
        background: #faf5ff;
    }
    #drop-zone .icon { font-size: 2.5rem; margin-bottom: 8px; }
    #drop-zone .title { font-size: 0.95rem; font-weight: 600; color: #334155; margin-bottom: 4px; }
    #drop-zone .subtitle { font-size: 0.8rem; color: #94a3b8; }
    #status {
        margin-top: 10px;
        font-size: 0.85rem;
        color: #6366f1;
        font-weight: 500;
        text-align: center;
        display: none;
    }
    #error {
        margin-top: 8px;
        font-size: 0.8rem;
        color: #ef4444;
        text-align: center;
        display: none;
    }
</style>
</head>
<body>
<div id="drop-zone" onclick="document.getElementById('folderInput').click()">
    <div class="icon">📁</div>
    <div class="title">Click to Select Folder</div>
    <div class="subtitle">or drag &amp; drop a folder here</div>
</div>
<div id="status"></div>
<div id="error"></div>
<input type="file" id="folderInput" webkitdirectory directory multiple
       style="display:none">

<script>
const dropZone = document.getElementById('drop-zone');
const folderInput = document.getElementById('folderInput');
const statusEl = document.getElementById('status');
const errorEl = document.getElementById('error');

// Drag events
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
    const items = e.dataTransfer.items;
    if (items) {
        getAllFilesFromDataTransfer(items).then(files => processFiles(files));
    }
});

// Folder picker
folderInput.addEventListener('change', () => {
    processFiles(Array.from(folderInput.files));
});

async function getAllFilesFromDataTransfer(items) {
    const files = [];
    async function traverse(entry) {
        if (entry.isFile) {
            return new Promise((resolve) => {
                entry.file(file => { files.push(file); resolve(); });
            });
        } else if (entry.isDirectory) {
            const reader = entry.createReader();
            return new Promise((resolve) => {
                reader.readEntries(async (entries) => {
                    for (const e of entries) { await traverse(e); }
                    resolve();
                });
            });
        }
    }
    for (let i = 0; i < items.length; i++) {
        const entry = items[i].webkitGetAsEntry();
        if (entry) { await traverse(entry); }
    }
    return files;
}

async function processFiles(files) {
    if (!files || files.length === 0) return;
    errorEl.style.display = 'none';
    statusEl.style.display = 'block';
    statusEl.textContent = 'Reading ' + files.length + ' file(s)...';

    const allowed = ['txt', 'pdf', 'docx', 'xlsx', 'xls', 'pptx'];
    const results = [];

    for (const file of files) {
        const ext = file.name.split('.').pop().toLowerCase();
        const relPath = file.webkitRelativePath || file.name;
        if (!allowed.includes(ext)) continue;

        try {
            const arrayBuf = await file.arrayBuffer();
            const bytes = new Uint8Array(arrayBuf);
            let binary = '';
            for (let i = 0; i < bytes.length; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            const b64 = btoa(binary);
            results.push({
                name: relPath,
                type: ext,
                content_b64: b64
            });
        } catch(e) {
            console.error('Error reading ' + file.name, e);
        }
    }

    if (results.length === 0) {
        statusEl.style.display = 'none';
        errorEl.style.display = 'block';
        errorEl.textContent = 'No supported files found (.txt, .pdf, .docx, .xlsx, .pptx).';
        return;
    }

    statusEl.textContent = '✓ ' + results.length + ' file(s) ready';

    // Send to Streamlit
    window.parent.postMessage({
        isStreamlitMessage: true,
        type: 'streamlit:setComponentValue',
        data: { files: results }
    }, '*');
}
</script>
</body>
</html>
"""


def _get_file_icon(ext: str) -> str:
    """Get emoji icon based on file type."""
    icons = {
        "pdf": "📕",
        "docx": "📘", "doc": "📘",
        "xlsx": "📊", "xls": "📊",
        "pptx": "📽️", "ppt": "📽️",
        "txt": "📝"
    }
    return icons.get(ext.lower(), "📄")


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _render_file_card_loading(filename: str, ext: str):
    """Render a file card in loading/processing state."""
    icon = _get_file_icon(ext)
    # Truncate filename if too long
    display_name = filename if len(filename) <= 35 else filename[:32] + "..."

    st.markdown(f"""
    <div class="file-card loading">
        <div class="file-card-icon {ext.lower()}">{icon}</div>
        <div class="file-card-info">
            <div class="file-card-name">{display_name}</div>
            <div class="file-card-meta">
                <span class="file-card-badge {ext.lower()}">{ext.upper()}</span>
                <span class="file-card-spinner"></span>
                <span>Processing...</span>
            </div>
            <div class="file-card-progress">
                <div class="file-card-progress-bar"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_file_card_success(filename: str, ext: str, size_bytes: int = 0, can_remove: bool = False, key: str = ""):
    """Render a file card in success/completed state."""
    icon = _get_file_icon(ext)
    # Truncate filename if too long
    display_name = filename if len(filename) <= 35 else filename[:32] + "..."
    size_str = _format_file_size(size_bytes) if size_bytes > 0 else "Ready"

    close_btn = ""
    if can_remove and key:
        close_btn = f'<button class="file-card-close" onclick="alert(\'Remove: {filename}\')">✕</button>'

    st.markdown(f"""
    <div class="file-card success">
        <div class="file-card-icon {ext.lower()}">{icon}</div>
        <div class="file-card-info">
            <div class="file-card-name">{display_name}</div>
            <div class="file-card-meta">
                <span class="file-card-badge {ext.lower()}">{ext.upper()}</span>
                <span>✓ {size_str}</span>
            </div>
        </div>
        {close_btn}
    </div>
    """, unsafe_allow_html=True)


def _render_folder_dropdown(folder_name: str, file_count: int = 0):
    """Render a folder dropdown/selector showing the folder name."""
    count_text = f"{file_count} file(s)" if file_count > 0 else "Select folder"
    st.markdown(f"""
    <div class="folder-dropdown">
        <div class="folder-dropdown-icon">📁</div>
        <div class="folder-dropdown-text">
            <div class="folder-dropdown-label">Selected Folder:</div>
            <div class="folder-dropdown-name">{folder_name}</div>
        </div>
        <div class="folder-dropdown-arrow">▼</div>
    </div>
    """, unsafe_allow_html=True)
    if file_count > 0:
        st.caption(f"📊 {count_text} ready to upload")


def _render_file_list_header(title: str, count: int):
    """Render the file list container header."""
    st.markdown(f"""
    <div class="file-list-container">
        <div class="file-list-header">
            <div class="file-list-title">{title}</div>
            <div class="file-list-count">{count} file(s)</div>
        </div>
    """, unsafe_allow_html=True)


def _render_file_list_footer():
    """Close the file list container."""
    st.markdown("</div>", unsafe_allow_html=True)


def _render_file_tree(tree: dict, depth: int = 0):
    """Recursively render a Finder-like file tree."""
    indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth

    # Render folders first
    for key, value in sorted(tree.items()):
        if key == "__files__":
            continue
        if isinstance(value, dict):
            with st.expander(f"{indent}📁 **{key}/**", expanded=(depth < 2)):
                _render_file_tree(value, depth + 1)

    # Render files
    files = tree.get("__files__", [])
    if files:
        for f in sorted(files, key=lambda x: x["name"]):
            ext = f["name"].split(".")[-1].lower() if "." in f["name"] else "txt"
            icon = ICON_MAP.get(ext, "📄")
            st.markdown(
                f"{indent}&nbsp;&nbsp;&nbsp;&nbsp;{icon} `{f['name']}` "
                f"<span style='color:#94a3b8;font-size:0.8rem;'>({f['chars']:,} chars)</span>",
                unsafe_allow_html=True
            )


def _render_raw_file_tree(files_data: list):
    """Render a file tree from raw folder picker data (before processing).
    Builds a tree from file paths and shows it like Finder."""
    tree = {}
    for f in files_data:
        fname = f.get("name", "unknown")
        parts = fname.replace("\\", "/").split("/")
        current = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                if "__files__" not in current:
                    current["__files__"] = []
                current["__files__"].append({
                    "name": part,
                    "full_path": fname,
                    "type": f.get("type", "txt"),
                })
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]

    _render_raw_tree(tree)


def _render_raw_tree(tree: dict, depth: int = 0):
    """Render a raw file tree (no char counts, just names)."""
    indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth

    for key, value in sorted(tree.items()):
        if key == "__files__":
            continue
        if isinstance(value, dict):
            with st.expander(f"{indent}📁 **{key}/**", expanded=(depth < 2)):
                _render_raw_tree(value, depth + 1)

    files = tree.get("__files__", [])
    if files:
        for f in sorted(files, key=lambda x: x["name"]):
            ext = f["name"].split(".")[-1].lower() if "." in f["name"] else "txt"
            icon = ICON_MAP.get(ext, "📄")
            st.markdown(
                f"{indent}&nbsp;&nbsp;&nbsp;&nbsp;{icon} `{f['name']}`",
                unsafe_allow_html=True
            )


def render_upload():
    """
    Renders the Upload Material page.
    Demonstrates POLYMORPHISM: creates TextDocument, PDFDocument, or MultiFileDocument
    based on input type, all treated as Document objects.
    """

    st.title("Upload Study Material")

    st.markdown(
        "Paste text, upload files, or drop an entire folder. "
        "Supports **TXT**, **PDF**, **DOCX**, **XLSX**, and **PPTX** formats."
    )

    tab1, tab2, tab3 = st.tabs(["📝 Paste Text", "📄 Upload Files", "📁 Upload Folder"])

    # --- Tab 1: Paste Text ---
    with tab1:
        st.subheader("Paste or Type Text")
        text_input = st.text_area(
            "Enter your study material here:",
            height=280,
            placeholder="Paste your notes, articles, or any study material...",
            label_visibility="collapsed",
        )

        if st.button("✨ Process Text", key="process_text", type="primary"):
            if not text_input or not text_input.strip():
                st.error("Please enter some text before processing.")
            else:
                try:
                    doc = TextDocument(title="Pasted Material")
                    doc.process(text_input)
                    st.session_state["document"] = doc
                    st.success(
                        f"✅ Text processed successfully! "
                        f"({len(doc.get_content()):,} characters)"
                    )
                    with st.expander("🔍 Preview Content"):
                        preview = doc.get_content()
                        st.text(preview[:1500] + ("..." if len(preview) > 1500 else ""))
                except ValueError as e:
                    st.error(str(e))

    # --- Tab 2: Single/Multiple Files ---
    with tab2:
        st.subheader("Upload One or More Files")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=list(ALLOWED_EXTENSIONS),
            accept_multiple_files=True,
            help="Supported: TXT, PDF, DOCX, XLSX, PPTX. You can select multiple files.",
            label_visibility="collapsed",
        )

        if uploaded_files:
            # Show file cards for selected files
            _render_file_list_header("Selected Files", len(uploaded_files))
            
            # Track which files to remove
            if "files_to_remove" not in st.session_state:
                st.session_state["files_to_remove"] = set()
            
            files_to_process = []
            for i, uploaded_file in enumerate(uploaded_files):
                # Skip files marked for removal
                if uploaded_file.name in st.session_state["files_to_remove"]:
                    continue
                    
                files_to_process.append(uploaded_file)
                ext = uploaded_file.name.split(".")[-1].lower()
                size_bytes = uploaded_file.size
                
                # Render file card with remove button
                col1, col2 = st.columns([6, 1])
                with col1:
                    _render_file_card_success(uploaded_file.name, ext, size_bytes)
                with col2:
                    if st.button("✕", key=f"remove_file_{i}_{uploaded_file.name}", help="Remove this file"):
                        st.session_state["files_to_remove"].add(uploaded_file.name)
                        st.rerun()
            
            _render_file_list_footer()
            
            if files_to_process:
                st.caption(f"{len(files_to_process)} file(s) ready to process")
                
                if st.button("✨ Process Files", key="process_files", type="primary", use_container_width=True):
                    # Show loading state for each file
                    loading_placeholder = st.empty()
                    with loading_placeholder.container():
                        _render_file_list_header("Processing Files...", len(files_to_process))
                        for uploaded_file in files_to_process:
                            ext = uploaded_file.name.split(".")[-1].lower()
                            _render_file_card_loading(uploaded_file.name, ext)
                        _render_file_list_footer()
                    
                    # Process files
                    if len(files_to_process) == 1:
                        _process_single_file(files_to_process[0])
                    else:
                        _process_multiple_files(files_to_process)
                    
                    # Clear loading state and remove list
                    loading_placeholder.empty()
                    st.session_state["files_to_remove"] = set()
            else:
                st.info("All files have been removed. Please select new files.")
                if st.button("🔄 Reset Selection", key="reset_files"):
                    st.session_state["files_to_remove"] = set()
                    st.rerun()

    # --- Tab 3: Folder Upload ---
    with tab3:
        st.subheader("Upload Entire Folder")
        
        # Use native Streamlit widgets for folder upload
        folder_name_input = st.text_input(
            "Folder Name:",
            placeholder="e.g., My Study Materials",
            help="Enter a name for this folder collection"
        )
        
        st.markdown(
            "<p style='color:#64748b;font-size:0.9rem;margin-bottom:0.5rem;'>"
            "Select multiple files from your folder using Ctrl+A (select all) or Ctrl+Click (select multiple). "
            "All supported files (.txt, .pdf, .docx, .xlsx, .pptx) will be processed.</p>",
            unsafe_allow_html=True,
        )
        
        folder_files = st.file_uploader(
            "Choose files from folder",
            type=list(ALLOWED_EXTENSIONS),
            accept_multiple_files=True,
            help="Select multiple files from your folder (Ctrl+A to select all)",
            label_visibility="collapsed",
            key="folder_file_uploader"
        )

        # Store selected folder files in session state so they persist across reruns
        if "pending_folder_files_native" not in st.session_state:
            st.session_state["pending_folder_files_native"] = None
        if "folder_name" not in st.session_state:
            st.session_state["folder_name"] = ""

        if folder_files:
            st.session_state["pending_folder_files_native"] = folder_files
            if folder_name_input:
                st.session_state["folder_name"] = folder_name_input

        files_data = st.session_state["pending_folder_files_native"]
        current_folder_name = st.session_state["folder_name"] or folder_name_input or "Uploaded Folder"

        if files_data:
            # Show folder dropdown with name
            _render_folder_dropdown(current_folder_name, len(files_data))
            
            # Show file list with cards
            _render_file_list_header("Files in Folder", len(files_data))
            
            for uploaded_file in files_data:
                ext = uploaded_file.name.split(".")[-1].lower()
                size_bytes = uploaded_file.size
                _render_file_card_success(uploaded_file.name, ext, size_bytes)
            
            _render_file_list_footer()
            
            # Show file tree preview
            with st.expander("🗂 Preview File Structure", expanded=False):
                # Build tree structure from file names
                tree_files = []
                for f in files_data:
                    tree_files.append({
                        "name": f.name,
                        "type": f.name.split(".")[-1].lower(),
                        "chars": f.size  # Approximate with file size
                    })
                
                # Simple list display
                for f in sorted(tree_files, key=lambda x: x["name"]):
                    icon = ICON_MAP.get(f["type"], "📄")
                    st.markdown(
                        f"&nbsp;&nbsp;&nbsp;&nbsp;{icon} `{f['name']}` "
                        f"<span style='color:#94a3b8;font-size:0.8rem;'>({f['chars']:,} bytes)</span>",
                        unsafe_allow_html=True
                    )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Process Folder Files", key="process_folder_native", type="primary", use_container_width=True):
                    # Show loading state
                    loading_placeholder = st.empty()
                    with loading_placeholder.container():
                        st.markdown(f"""
                        <div class="folder-dropdown" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-color: #f59e0b;">
                            <div class="folder-dropdown-icon">📁</div>
                            <div class="folder-dropdown-text">
                                <div class="folder-dropdown-label">Processing Folder:</div>
                                <div class="folder-dropdown-name">{current_folder_name}</div>
                            </div>
                            <div class="folder-dropdown-arrow"><span class="file-card-spinner"></span></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        _render_file_list_header("Processing Files...", len(files_data))
                        for f in files_data[:5]:  # Show first 5 files
                            ext = f.name.split(".")[-1].lower()
                            _render_file_card_loading(f.name, ext)
                        if len(files_data) > 5:
                            st.caption(f"... and {len(files_data) - 5} more files")
                        _render_file_list_footer()
                    
                    # Process the files
                    _process_native_folder_files(files_data, current_folder_name)
                    loading_placeholder.empty()
                    st.session_state["pending_folder_files_native"] = None
                    st.session_state["folder_name"] = ""

            with col2:
                if st.button("🗑 Clear Selection", key="clear_folder_native", use_container_width=True):
                    st.session_state["pending_folder_files_native"] = None
                    st.session_state["folder_name"] = ""
                    st.rerun()

    # --- Current Document Info ---
    if "document" in st.session_state and st.session_state["document"] is not None:
        doc = st.session_state["document"]
        st.markdown("---")
        st.subheader("📌 Current Document")

        col_a, col_b = st.columns([3, 1])
        with col_a:
            if isinstance(doc, MultiFileDocument):
                st.info(
                    f"**{doc.get_title()}** — {doc.get_file_count()} files, "
                    f"{doc.get_total_chars():,} total characters"
                )
                with st.expander("🗂 View File Structure (Finder)"):
                    _render_file_tree(doc.get_file_tree())
            else:
                st.info(
                    f"**{doc.get_title()}** — {len(doc.get_content()):,} characters"
                )

        with col_b:
            if st.button("🗑 Clear Document", use_container_width=True, type="secondary"):
                st.session_state["document"] = None
                st.session_state.pop("last_summary", None)
                st.session_state.pop("last_quiz", None)
                st.session_state.pop("qa_pairs", None)
                st.session_state.pop("last_tasks", None)
                st.rerun()

        st.caption("✅ This document is now available for Summaries, Q&A, Quizzes, and Tasks.")


def _process_single_file(uploaded_file):
    """Process a single uploaded file into a Document using polymorphism."""
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        st.error(f"Unsupported file type: .{file_extension}")
        return

    try:
        file_bytes = uploaded_file.read()

        doc_class = EXT_TO_CLASS.get(file_extension)
        if doc_class is None:
            st.error(f"No handler for .{file_extension}")
            return

        doc = doc_class(title=uploaded_file.name)

        if file_extension == "txt":
            doc.process(file_bytes.decode("utf-8", errors="replace"))
        else:
            doc.process(file_bytes)

        st.session_state["document"] = doc
        st.success(
            f"✅ '{doc.get_title()}' processed — {len(doc.get_content()):,} characters"
        )
        with st.expander("🔍 Preview Content"):
            preview = doc.get_content()
            st.text(preview[:1500] + ("..." if len(preview) > 1500 else ""))

    except UnicodeDecodeError:
        st.error("Could not decode the TXT file. Please ensure it is a valid text file.")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")


def _process_native_folder_files(uploaded_files, folder_name: str):
    """Process files from the native Streamlit file uploader."""
    if not uploaded_files:
        st.error("No files selected.")
        return

    doc = MultiFileDocument(title=folder_name)
    processed = 0
    errors = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {i + 1}/{len(uploaded_files)}: {uploaded_file.name}")
        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension not in ALLOWED_EXTENSIONS:
            errors.append(f"Skipped {uploaded_file.name}: unsupported type")
            continue

        doc_class = EXT_TO_CLASS.get(file_extension)
        if doc_class is None:
            errors.append(f"Skipped {uploaded_file.name}: no handler")
            continue

        try:
            file_bytes = uploaded_file.read()

            if file_extension == "txt":
                content = file_bytes.decode("utf-8", errors="replace")
            else:
                temp_doc = doc_class(title=uploaded_file.name)
                temp_doc.process(file_bytes)
                content = temp_doc.get_content()

            doc.add_file(uploaded_file.name, content)
            processed += 1

        except Exception as e:
            errors.append(f"Error processing {uploaded_file.name}: {str(e)}")

        progress_bar.progress((i + 1) / len(uploaded_files))

    progress_bar.empty()
    status_text.empty()

    if processed == 0:
        st.error("No files could be processed.")
        for err in errors:
            st.caption(f"⚠️ {err}")
        return

    doc.process()
    st.session_state["document"] = doc

    st.success(
        f"✅ Folder '{folder_name}' processed! {processed} file(s), "
        f"{doc.get_total_chars():,} total characters"
    )

    if errors:
        with st.expander(f"⚠️ {len(errors)} warning(s)"):
            for err in errors:
                st.caption(err)

    with st.expander("🗂 View File Structure (Finder)"):
        _render_file_tree(doc.get_file_tree())


def _process_folder_files(files_data: list):
    """Process files from the custom folder picker (base64-encoded)."""
    if not files_data:
        st.error("No files selected.")
        return

    # Determine folder name from first file's relative path
    first_name = files_data[0].get("name", "unknown")
    if "/" in first_name:
        folder_name = first_name.split("/")[0]
    else:
        folder_name = "Uploaded Folder"

    doc = MultiFileDocument(title=folder_name)
    processed = 0
    errors = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, f in enumerate(files_data):
        fname = f.get("name", f"file_{i}")
        fext = f.get("type", "").lower()
        status_text.text(f"Processing {i + 1}/{len(files_data)}: {fname}")

        if fext not in ALLOWED_EXTENSIONS:
            errors.append(f"Skipped {fname}: unsupported type")
            continue

        try:
            raw_bytes = base64.b64decode(f["content_b64"])
            doc_class = EXT_TO_CLASS.get(fext)

            if doc_class is None:
                errors.append(f"Skipped {fname}: unsupported type")
                continue

            if fext == "txt":
                content = raw_bytes.decode("utf-8", errors="replace")
                doc.add_file(fname, content)
            else:
                # Use Document class to extract text
                temp_doc = doc_class(title=fname)
                temp_doc.process(raw_bytes)
                content = temp_doc.get_content()
                doc.add_file(fname, content)

            processed += 1

        except Exception as e:
            errors.append(f"Error processing {fname}: {str(e)}")

        progress_bar.progress((i + 1) / len(files_data))

    progress_bar.empty()
    status_text.empty()

    if processed == 0:
        st.error("No files could be processed.")
        for err in errors:
            st.caption(f"⚠️ {err}")
        return

    doc.process()
    st.session_state["document"] = doc

    st.success(
        f"✅ Folder processed! {processed} file(s), "
        f"{doc.get_total_chars():,} total characters"
    )

    if errors:
        with st.expander(f"⚠️ {len(errors)} warning(s)"):
            for err in errors:
                st.caption(err)

    with st.expander("🗂 View File Structure (Finder)"):
        _render_file_tree(doc.get_file_tree())


def _process_multiple_files(uploaded_files):
    """Process multiple uploaded files into a MultiFileDocument."""
    if not uploaded_files:
        st.error("No files selected.")
        return

    first_name = uploaded_files[0].name
    if "/" in first_name or "\\" in first_name:
        folder_name = first_name.replace("\\", "/").split("/")[0]
    else:
        folder_name = "Uploaded Files"

    doc = MultiFileDocument(title=folder_name)
    processed = 0
    errors = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {i + 1}/{len(uploaded_files)}: {uploaded_file.name}")
        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension not in ALLOWED_EXTENSIONS:
            errors.append(f"Skipped {uploaded_file.name}: unsupported type")
            continue

        doc_class = EXT_TO_CLASS.get(file_extension)
        if doc_class is None:
            errors.append(f"Skipped {uploaded_file.name}: no handler")
            continue

        try:
            file_bytes = uploaded_file.read()

            if file_extension == "txt":
                content = file_bytes.decode("utf-8", errors="replace")
            else:
                temp_doc = doc_class(title=uploaded_file.name)
                temp_doc.process(file_bytes)
                content = temp_doc.get_content()

            doc.add_file(uploaded_file.name, content)
            processed += 1

        except Exception as e:
            errors.append(f"Error processing {uploaded_file.name}: {str(e)}")

        progress_bar.progress((i + 1) / len(uploaded_files))

    progress_bar.empty()
    status_text.empty()

    if processed == 0:
        st.error("No files could be processed.")
        for err in errors:
            st.caption(f"⚠️ {err}")
        return

    doc.process()
    st.session_state["document"] = doc

    st.success(
        f"✅ Files processed! {processed} file(s), "
        f"{doc.get_total_chars():,} total characters"
    )

    if errors:
        with st.expander(f"⚠️ {len(errors)} warning(s)"):
            for err in errors:
                st.caption(err)

    with st.expander("🗂 View File Structure (Finder)"):
        _render_file_tree(doc.get_file_tree())
