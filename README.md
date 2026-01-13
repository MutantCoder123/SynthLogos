![Language](https://img.shields.io/badge/language-Python%20%7C%20C%2B%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/status-Work_In_Progress-yellow?style=for-the-badge)

# SynthLogos: Hybrid Search Agent

> **Current Status: Building the Python-C++ Bridge.**

This project is an experiment to see what happens when you combine a **custom C++ search engine** (which I built from scratch) with a modern **LLM** for reasoning.

Most "RAG" (Retrieval-Augmented Generation) systems just use off-the-shelf tools like LangChain or Pinecone. I wanted to build the retrieval layer myself in C++ to understand the low-level performance, and then use Python to handle the AI logic.

## The Idea
I am trying to solve a specific problem: **Speed vs. Understanding.**
* **C++ is fast:** It can search thousands of files in microseconds using a Trie/Inverted Index.
* **AI is smart:** It understands context but is slow at searching vast amounts of data.

**My Solution:** Use the C++ binary to do the heavy lifting (finding keywords), and use Python to act as the "Brain" that reads those results and answers the user's question.

## How It Works (Architecture)
1.  **User asks a question** in the Python dashboard.
2.  **Python** extracts keywords and calls my compiled `engine.exe`.
3.  **C++ Engine** runs the search algorithm ($O(L)$ complexity) and returns the relevant file snippets via standard output.
4.  **Python** catches this output and feeds it to an LLM (I am currently testing different APIs).
5.  **Graph Visualization:** I am also using `NetworkX` to try and map out how the found documents are related visually.

## 📂 Project Structure

```text
├── backend/
│   ├── engine.exe      # My compiled C++ search engine (Integration Target)
│   └── data/           # The text files I'm searching through
├── modules/
│   ├── bridge.py       # Handles Python-C++ communication (subprocess)
│   ├── graph.py        # Logic to build the NetworkX graph
│   └── llm.py          # Wrapper for the Gemini API
├── app.py              # Main Streamlit dashboard
└── README.md
```
## To-Do List
- [x] **The Engine:** Finished the C++ Inverted Index (backend is ready).
- [ ] **The Bridge:** Currently implementing `modules/bridge.py` to capture C++ standard output via `subprocess`.
- [x] **The AI:** Integrated **Google Gemini 2.5 Flash** in `modules/llm.py` (chosen for its native JSON mode), though the architecture allows swapping for OpenAI later.
- [ ] **The Graph:** Writing logic in `modules/graph.py` to convert search snippets into NetworkX nodes/edges.
- [ ] **The UI:** Building the Streamlit dashboard in `app.py` to visualize the pipeline.

## 🔧 Setup
*Detailed installation instructions, including compiling the C++ backend and configuring the Gemini API, will be added upon the release of the v1.0 prototype.*