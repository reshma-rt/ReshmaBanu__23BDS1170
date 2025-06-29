import streamlit as st
from utils.pdf_reader import extract_text_from_pdf
from utils.chunking import chunk_text
from utils.vector_store import create_vector_store
from qa_engine.chat_bot import get_answer_from_query
from fpdf import FPDF
from keybert import KeyBERT
from pdf2image import convert_from_bytes
from PIL import Image

st.set_page_config(page_title="Chat with Your Notes", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    html, body, .main, .block-container {
        background-color: #f8f9fa;
        color: #212529;
        font-family: 'Segoe UI', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #f1f3f5 !important;
    }
    .use-case-box {
        background-color: #ffffff;
        border: 1px solid #ced4da;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .user-query-box, .answer-box {
        max-width: 800px;
        margin: 0 auto 1rem auto;
    }
    .user-query-box {
        background-color: #ffffff;
        border: 2px solid #0d6efd;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: #0b3c5d;
        font-size: 16px;
        box-shadow: 0 2px 4px rgba(13,110,253,0.1);
    }
    .answer-box {
        background-color: #e7f1ff;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: #0b3c5d;
        font-size: 16px;
        border-left: 4px solid #0d6efd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    input[type="text"] {
        width: 100% !important;
        max-width: 700px;
        margin: 0 auto 1rem auto;
        display: block;
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        font-size: 18px;
        border: 2px solid #0d6efd !important;
        background-color: #fff !important;
        box-shadow: 0 1px 6px rgba(13, 110, 253, 0.1);
    }
    .stButton > button {
        display: block;
        margin: 0 auto;
        max-width: 200px;
        border-radius: 10px;
    }
    .keywords-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #0d6efd;
    }
    .keywords-title {
        color: #212529;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    .keywords-list {
        padding-left: 1.2rem;
        margin: 0;
    }
    .keywords-list li {
        margin-bottom: 0.6rem;
        color: #495057;
        line-height: 1.5;
    }
    
    .use-case-box {
        background-color: #ffffff;
        border: 1px solid #ced4da;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        font-size: 14px;  /* Smaller text */
        line-height: 1.4;
    }
    
    .use-case-box h3 {
        font-size: 16px;
        margin-bottom: 0.5rem;
    }
    .use-case-box ul {
        padding-left: 1.2rem;
    }
    .use-case-box li {
        margin-bottom: 0.3rem;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
defaults = {
    "hide_sidebar": False,
    "last_query": "",
    "last_response": "",
    "selected_model": "",
    "history": []
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

if st.session_state["history"]:
    st.session_state["hide_sidebar"] = True

if st.session_state["hide_sidebar"]:
    left_col = st.container()
    right_col = None
else:
    left_col, right_col = st.columns([1, 2])

with left_col:
    if st.session_state["hide_sidebar"] or st.session_state["history"]:
        for item in st.session_state["history"]:
            st.markdown(f"""
                <div class='user-query-box'><b>You asked:</b><br>{item["question"]}</div>
                <div class='answer-box'>{item["answer"]}</div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Export Conversation"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for item in st.session_state["history"]:
                    q = item['question'].encode('latin-1', 'ignore').decode('latin-1')
                    a = item['answer'].encode('latin-1', 'ignore').decode('latin-1')
                    pdf.multi_cell(0, 10, f"Q: {q}\n\nA: {a}\n\n")
                pdf.output("conversation_history.pdf")
                st.success("✅ Downloaded conversation_history.pdf")

        with col2:
            if st.button("🔄 Clear History"):
                st.session_state["history"] = []
                st.rerun()

        with st.form("followup_form"):
            followup_query = st.text_input("💬 Ask a follow-up question")
            if st.form_submit_button("↩ Submit Follow-Up"):
                if followup_query.strip():
                    try:
                        context = "\n\n".join([
                            f"Q: {item['question']}\nA: {item['answer']}"
                            for item in st.session_state["history"][-3:]
                        ])
                        response = get_answer_from_query(
                            create_vector_store([context]),
                            followup_query
                        )
                        st.session_state["history"].append({
                            "question": followup_query,
                            "answer": response
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        st.markdown("## ⚙ Model Selection")
        model = st.selectbox(
            "Choose AI Model",
            [
                "ibm/granite-3-3-8b-instruct",
                "ibm/granite-3b-code-instruct",
                "meta-llama/llama-3-2-8b-instruct"
            ]
        )

        if st.button("✅ Confirm Model"):
            st.session_state["selected_model"] = model
            st.success(f"Selected Model: {model}")

        st.markdown("""
            <div class='use-case-box'>
                <h3>📝 Instructions</h3>
                <ul>
                    <li>📄 <b>Upload a PDF</b> (e.g., research papers, notes, reports)</li>
                    <li>🧠 <b>Ask any question</b> related to its content</li>
                    <li>🔍 <b>Get instant answers</b> with context from your document</li>
                    <li>📑 <b>Preview PDF pages</b> on the right panel</li>
                    <li>📌 <b>Review top keywords</b> for quick navigation</li>
                    <li>🔁 <b>Ask follow-up questions</b> to dig deeper</li>
                    <li>💾 <b>Export answers</b> to PDF anytime</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

# Right Panel - PDF Chat
if right_col is not None:
    with right_col:
        st.markdown("## 📚 Chat with Your Notes")
        uploaded_file = st.file_uploader("Choose your .pdf file", type="pdf", key="pdf_uploader")

        if uploaded_file:
            st.markdown(f"<div class='use-case-box'>✅ Uploaded: {uploaded_file.name}</div>", unsafe_allow_html=True)

            # PDF Preview
            st.markdown("### 📑 PDF Preview (first 3 pages)")
            uploaded_file.seek(0)
            try:
                images = convert_from_bytes(
                    uploaded_file.read(),
                    dpi=100,
                    first_page=1,
                    last_page=3,
                    poppler_path=r"C:\\Program Files\\poppler-24.08.0\\Library\\bin"
                )
                cols = st.columns(len(images))
                for i, img in enumerate(images):
                    new_width = int(img.width * 0.6)
                    new_height = int(img.height * 0.6)
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    with cols[i]:
                        st.image(resized_img, caption=f"Page {i+1}")
            except Exception as e:
                st.warning(f"Could not render preview: {e}")
            uploaded_file.seek(0)

            # Text + Index
            raw_text = extract_text_from_pdf(uploaded_file)
            chunks = chunk_text(raw_text)
            vector_store = create_vector_store(chunks)

            # Keyword Extraction
            try:
                kw_model = KeyBERT()
                keywords = kw_model.extract_keywords(
                    raw_text,
                    keyphrase_ngram_range=(1, 2),
                    stop_words='english',
                    top_n=10
                )
                st.markdown("""
                    <div class='keywords-container'>
                        <div class='keywords-title'>🔍 Top Keywords in PDF</div>
                        <ul class='keywords-list'>
                """, unsafe_allow_html=True)
                for kw, _ in keywords:
                    st.markdown(f"<li><b>{kw}</b></li>", unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Keyword extraction failed: {e}")

            # Ask a question
            with st.form("question_form"):
                user_query = st.text_input("💬 Ask a question from this PDF")
                submitted = st.form_submit_button("🔍 Get Answer")

            if submitted and user_query.strip():
                response = get_answer_from_query(vector_store, user_query)
                st.session_state["hide_sidebar"] = True
                st.session_state["last_query"] = user_query
                st.session_state["last_response"] = response
                st.session_state["history"].append({
                    "question": user_query,
                    "answer": response
                })
                if len(st.session_state["history"]) > 10:
                    st.session_state["history"].pop(0)
                st.success("✅ Answer generated successfully!")

        else:
            st.markdown("<div class='use-case-box'>📥 Drag & drop your PDF here or use the uploader above</div>", unsafe_allow_html=True)
            st.markdown("### 🚀 Example Use Cases")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='use-case-box'>📌 Research Summary</div>", unsafe_allow_html=True)
                st.markdown("<div class='use-case-box'>📌 Exam Preparation</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div class='use-case-box'>📌 Technical Documentation Help</div>", unsafe_allow_html=True)
                st.markdown("<div class='use-case-box'>📌 Legal/Policy Document Q&A</div>", unsafe_allow_html=True)