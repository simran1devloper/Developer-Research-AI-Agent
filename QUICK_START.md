# Quick Start Commands

## 🚀 Installation & Setup

```bash
# 1. Enter the directory
cd /workspaces/Developer-Research-AI-Agent

# 2. Make scripts executable
chmod +x setup.sh
chmod +x run.sh

# 3. Run setup (installs dependencies + creates .env)
./setup.sh
```

## ▶️ Running the Application

### CLI Mode (Interactive Terminal)
```bash
./run.sh cli
```

Then type your research queries:
```
🔍 Enter your technical research query: What is the latest in AI/ML?
```

### Streamlit Web UI
```bash
./run.sh streamlit
```

Open browser to: `http://localhost:8501`

## Alternative: Direct Python Execution

### CLI
```bash
python3 main.py
```

### Streamlit
```bash
streamlit run app.py
```

## 🔧 Configuration

1. Edit `.env` file with your API keys:
   ```bash
   nano .env
   ```
   
   Add:
   ```env
   TAVILY_API_KEY="your_key_here"  # Optional
   OLLAMA_URL="http://localhost:11434/api/generate"
   ```

2. Edit `config.py` to change:
   - Model name
   - Ollama URL
   - Temperature
   - Query limits

## 📋 Environment Setup

The `.env` file has already been configured with:
- ✅ HuggingFace Model: `thunder-research-group/Llama-Thunder-LLM-8B`
- ✅ HF API Token: Present in config.py
- ✅ Ollama: Configured to use local instance
- ⚠️ Tavily API: Optional (add your key if needed)

## 🧪 Test Run

Quick test without API keys:
```bash
python3 main.py
```

Try this query:
```
What is Python used for?
```

## 📊 Generated Output

All research reports are saved to:
```
output/research_report_YYYYMMDD_HHMMSS.md
```

## 🔍 Troubleshooting

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**Reset database:**
```bash
rm -rf qdrant_db
mkdir qdrant_db
```

**Check Ollama running:**
```bash
curl http://localhost:11434/api/tags
```

## 📚 Full Documentation

See `SETUP_GUIDE.md` for detailed configuration and troubleshooting.
