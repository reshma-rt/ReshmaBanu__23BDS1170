# 📄 Chat with Your Notes – PDF Q\&A Bot

A Generative AI-powered web app that allows users to upload any PDF (e.g., lecture notes, research papers, manuals) and interact with its content using natural language. Built using Streamlit and IBM watsonx, this project helps users ask questions, get contextual answers, and explore documents intelligently.

---

## 📝 Project Description

*Chat with Your Notes* simplifies document understanding by turning static PDFs into interactive Q\&A interfaces. Whether you're a student revising lecture notes or a researcher exploring academic papers, this tool lets you ask custom questions and get instant, accurate answers powered by an LLM (Large Language Model).

---

## 🚀 Features

* 📁 Upload any PDF document
* 👀 Preview the first few pages
* 🔍 Extract and display top keywords from the PDF
* 💬 Ask custom questions about the document
* 🔄 Follow-up questions supported (chat memory)
* 🧠 Choose between IBM watsonx or OpenAI models
* 📄 Export the Q\&A session as a downloadable PDF
* 🗑 Clear history to start fresh

---

## 🛠 Technologies Used

* Python
* Streamlit
* LangChain
* IBM watsonx (or OpenAI API)
* FAISS (for vector database)
* PyMuPDF (fitz)
* HuggingFace Embeddings
* dotenv (for secrets management)

---

## 📁 Folder Structure

```
Chat_with_Notes/
│
├── app.py
├── .env
├── requirements.txt
├── utils/
│   ├── pdf_reader.py
│   ├── chunking.py
│   └── vector_store.py
├── qa_engine/
│   └── chat_bot.py
└── outputs/
    └── exported_chats/
```

## 🌐 Live Demo

👉 (https://youtu.be/fVyv2aZD5vo)

---

## 🧠 Future Enhancements

* Add support for multiple PDFs
* Integrate voice-to-text input
* Support for scanned PDFs (OCR)
* Multi-language question support
https://youtu.be/fVyv2aZD5vo
