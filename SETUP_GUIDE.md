# 🚀 Setup & Running Guide

This guide will help you set up and run the Developer Research AI Agent.

## Prerequisites

- **Python 3.8+** - Download from [python.org](https://www.python.org/)
- **Ollama** (optional) - For local LLM inference, download from [ollama.ai](https://ollama.ai)
- **API Keys** (optional) - Tavily API for enhanced web search

## Quick Start

### 1. Clone and Enter Directory
```bash
cd /workspaces/Developer-Research-AI-Agent
```

### 2. Run Setup Script (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create the `.env` file from `.env.example`
- Install all dependencies
- Create required directories

### 3. Configure Environment Variables

Edit `.env` file and add your API keys:

```env
# Ollama Server URL
OLLAMA_URL="http://localhost:11434/api/generate"

# Tavily API (optional, for web search)
TAVILY_API_KEY="your_key_here"

# HuggingFace Configuration
HF_API_TOKEN="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"
HF_MODEL="thunder-research-group/Llama-Thunder-LLM-8B"
```

## Running the Agent

### Option A: CLI Mode (Interactive Terminal)
```bash
./run.sh cli
```

Or directly:
```bash
python3 main.py
```

**Example interaction:**
```
🔍 Enter your technical research query: What are the latest trends in LLM optimization?
⏳ Processing...

✅ Completed Node: [guard]
✅ Completed Node: [context]
✅ Completed Node: [classify]
✅ Completed Node: [planner]
✅ Completed Node: [deep_research]
✅ Completed Node: [gap_analysis]
✅ Completed Node: [synthesize]
✅ Completed Node: [formatter]

==================================================
# Final Response

[Generated report with findings...]
==================================================
```

### Option B: Streamlit Web UI
```bash
./run.sh streamlit
```

Or directly:
```bash
streamlit run app.py
```

Then open: **http://localhost:8501**

## Manual Installation (If Not Using setup.sh)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create directories
mkdir -p output qdrant_db

# Copy env example
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your favorite editor
```

## Configuration

### Model Settings
Edit `config.py` to change:
- LLM model (default: `ministral-3:3b-cloud`)
- Ollama URL (default: `http://172.22.124.89:11434/api/generate`)
- Max tokens and iterations
- Temperature and other parameters

### Ollama Setup (Local)
```bash
# Download and run Ollama
# Visit https://ollama.ai to install

# Pull a model (example)
ollama pull mistral

# Start Ollama server (runs on localhost:11434)
ollama serve
```

## Troubleshooting

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

### Ollama Connection Error
- Make sure Ollama is running: `ollama serve`
- Check Ollama URL in `.env` matches your setup
- Default: `http://localhost:11434`

### Memory/Qdrant Errors
```bash
rm -rf qdrant_db
mkdir qdrant_db
```
This will reset the memory database.

### Streamlit Port Already In Use
```bash
streamlit run app.py --server.port 8502
```

## Running on Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN mkdir -p output qdrant_db

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t research-agent .
docker run -it -v $(pwd):/app --env-file .env research-agent
```

## Development Mode

Run with debug output:
```bash
python3 main.py --debug
```

Or check logs in real-time:
```bash
tail -f output/research_report_*.md
```

## Project Structure

```
.
├── main.py              # CLI entry point
├── app.py               # Streamlit web UI
├── config.py            # Configuration settings
├── state.py             # LangGraph state definition
├── memory.py            # Qdrant memory management
├── graph/
│   ├── nodes_pre.py     # Pre-processing nodes
│   ├── nodes_exec.py    # Execution nodes
│   └── nodes_post.py    # Post-processing nodes
├── tools/
│   ├── search_tools.py  # Web search tools
│   └── memory_tools.py  # Memory tools
├── prompts/
│   ├── research_prompts.py
│   └── report_templates.py
├── output/              # Generated reports
├── qdrant_db/           # Vector database
└── requirements.txt     # Python dependencies
```

## API Keys Setup

### Tavily Search (Optional)
1. Sign up at https://tavily.com
2. Copy your API key
3. Add to `.env`: `TAVILY_API_KEY=your_key`

### HuggingFace (Already configured)
- Model: `thunder-research-group/Llama-Thunder-LLM-8B`
- Token: Already set in config.py

## Performance Tips

1. **Use Quick Mode** for simple queries
2. **Limit Deep Mode Iterations** to 2-3 for faster results
3. **Reduce Token Limit** if you have memory constraints
4. **Use GPU** if available by configuring Ollama with CUDA

## Support

For issues or questions:
1. Check the README.md
2. Review the generated reports in `output/`
3. Enable debug mode: `python3 main.py --debug`
4. Check Ollama server status and logs

Happy researching! 🔬
