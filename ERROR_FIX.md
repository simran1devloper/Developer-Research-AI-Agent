# 🚨 Troubleshooting Guide

## Error Analysis & Solutions

### Error 1: `[Errno 111] Connection refused`

**What it means:** The application is trying to connect to Ollama but it's not running.

**Solution:**

```bash
# Step 1: Download Ollama (if not already installed)
# Visit: https://ollama.ai and download for your OS

# Step 2: Start Ollama server (in a new terminal)
ollama serve

# Step 3: Pull a model (in another new terminal)
ollama pull mistral
# OR
ollama pull llama2

# Step 4: Run your application
python3 main.py
```

**What models are available:**
```bash
ollama list  # See available models
ollama pull mistral  # Download a model
```

---

### Error 2: `'QdrantClient' object has no attribute 'search'`

**What it means:** The Qdrant database collection isn't initialized properly.

**Solution:**

```bash
# Reset the database
rm -rf qdrant_db
mkdir qdrant_db

# Run again
python3 main.py
```

---

### Error 3: `Authentication failed for https://api.smith.langchain.com`

**What it means:** LangChain tracing is enabled but there's no valid API key.

**Solution:**

The .env file has been updated to disable tracing by default:
```env
LANGCHAIN_TRACING_V2="false"
```

If you still see this error, run:
```bash
source .env
python3 main.py
```

---

## 🔧 Complete Setup (Step-by-Step)

### Step 1: Install Ollama

**On Mac/Linux/Windows:**
1. Visit https://ollama.ai
2. Download and install for your OS
3. Run `ollama serve` in a terminal

### Step 2: Pull a Model

In a **new terminal**, run:
```bash
# Recommended lightweight model
ollama pull mistral

# Alternative models
ollama pull llama2
ollama pull neural-chat
ollama pull orca-mini
```

### Step 3: Verify Ollama is Running

```bash
# In another terminal
curl http://localhost:11434/api/tags

# Should show your downloaded models
```

### Step 4: Install Dependencies

```bash
cd /workspaces/Developer-Research-AI-Agent
pip install -r requirements.txt
```

### Step 5: Update Config (if needed)

Edit `config.py`:
```python
MODEL_NAME = "mistral"  # Use the model you pulled
OLLAMA_BASE_URL = "http://localhost:11434"  # Default
```

### Step 6: Run the Agent

```bash
# Make sure Ollama is running in another terminal first!
python3 main.py
```

---

## 👀 Monitoring Errors

### Real-time Debugging

```bash
# Run with debug info
python3 main.py --debug

# Or check recent outputs
tail -f output/research_report_*.md
```

---

## 🐳 Docker Alternative (No Ollama Setup)

If you don't want to install Ollama locally, use Docker:

```bash
# Docker setup for Ollama
docker run -d --name ollama -p 11434:11434 ollama/ollama

# Pull a model
docker exec ollama ollama pull mistral

# Run the agent
python3 main.py
```

---

## ✅ Quick Verification Checklist

- [ ] Ollama is installed
- [ ] Ollama server is running (`ollama serve`)
- [ ] A model is downloaded (`ollama pull mistral`)
- [ ] Dependencies are installed (`pip install -r requirements.txt`)
- [ ] `.env` file exists with correct settings
- [ ] LangChain tracing is disabled (`LANGCHAIN_TRACING_V2="false"`)
- [ ] Qdrant database is initialized (`mkdir qdrant_db` if missing)

---

## 🎯 Quick Test Command

Once everything is set up:

```bash
# Start Ollama (Terminal 1)
ollama serve

# Run agent (Terminal 2)
cd /workspaces/Developer-Research-AI-Agent
python3 main.py

# Type a simple query
# > What is Python?
```

---

## 📞 Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| Connection refused | Ollama not running | Run `ollama serve` |
| No attribute 'search' | Qdrant not initialized | Delete `qdrant_db/` and restart |
| Authentication failed | Tracing enabled | Set `LANGCHAIN_TRACING_V2="false"` |
| Model not found | Wrong model name | Run `ollama list` |
| CUDA error | GPU memory full | Use smaller model |

---

## 🚀 Ready to Run?

Once all errors are fixed:

```bash
python3 main.py
```

Then type your research queries!

Good luck! 🎉
