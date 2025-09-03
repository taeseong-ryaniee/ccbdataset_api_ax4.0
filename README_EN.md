# 🎨 Artwork Q&A Builder for Dataset

An AI-powered Q&A generation system for artwork datasets.  
This project originated from creating datasets for the Cheongju International Craft Competition chatbot and has been made public with customizable prompt features for universal art exhibitions.

Built with **SKT A.X 4.0 free API** and **uv package manager**.  
Generates **80 Q&As total**: **General Visitor perspective (30)** + **Curator's Artwork perspective (30)** + **Curator's Artist perspective (20)**

## 🚀 Quick Start

```bash
# 1. Environment Setup (install uv)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# 2. Prepare Data
cp your_artwork_data.json data/  # or refer to data/sample.json

# 3. Run
uv run python main.py            # Fast mode
uv run python main.py --precise  # Precise mode
./run_ax4.sh                     # Use script

# 4. Check Results
ls final_output/                 # Generated as ArtistName_ArtworkTitle.json
```

## 📋 Data Format

JSON files must include the following fields:

```json
{
  "items": [
    {
      "nationality": "UK",
      "artist_name": "John Smith", 
      "artist_name_eng": "John SMITH",
      "artist_info": "{\"birth\":\"1985\",\"exhibits\":[\"Exhibition history\"],\"awards\":[\"Awards\"]}",
      "title": "Traces of Time",
      "title_eng": "Traces of Time", 
      "size": "120×80×10cm",
      "weight": "8",
      "year": "2024",
      "materials": "Canvas, Acrylic",
      "artist_note": "Artist's intention and creation process description...",
      "description": "Brief summary of the artwork"
    }
  ]
}
```

## 📊 Output Results

Each artwork generates a `final_output/ArtistName_ArtworkTitle.json` file containing 80 Q&As:

```json
[
  {
    "instruction": "What philosophy does the artist reveal in this work?",
    "input": "nationality: UK, artist_name: John Smith, title: Traces of Time...",
    "output": "John Smith's 'Traces of Time' reveals a unique philosophy that views time not as a linear flow but as layers of accumulated experience...",
    "system": "",
    "history": []
  }
]
```

**Perspective Breakdown**: General Visitor (30) + Curator Artwork (30) + Curator Artist (20)

## 🎨 Prompt Customization

### Prompt File Structure
```
prompts/
├── visitor_questions.md         # General visitor perspective
├── curator_artwork_questions.md # Curator artwork analysis  
└── curator_artist_questions.md  # Curator artist background
```

### Modification Methods
1. **Question Count**: Change target numbers in each file
2. **Categories**: Adjust question classification and counts
3. **Style**: Set answer tone and manner
4. **New Perspectives**: Add new prompt files + code modification

### Prompt Writing Tips
✅ **Good Practice**: Specific roles, clear format, precise quantities  
❌ **Avoid**: Vague instructions, open formats, unclear roles

## ⚙️ Configuration

### API Settings (config.py)
```python
AX4_API_BASE_URL = "https://guest-api.sktax.chat/v1"
AX4_API_KEY = "sktax-XyeKFrq67ZjS4EpsDlrHHXV8it"  # Free guest key
AX4_MODEL = "ax4"
```

### Generation Modes
- `--fast`: Fast mode (temperature=0.7, max_tokens=12288)
- `--precise`: Precise mode (temperature=0.8, max_tokens=16384)

## 🔧 Troubleshooting

```bash
# Check API connection
curl -I https://guest-api.sktax.chat/v1
uv run python main.py --help

# Dependencies issues
uv cache clean && uv sync

# Memory shortage
python -c "import psutil; print(f'{psutil.virtual_memory().available/1024**3:.1f}GB')"
```

## 📁 Project Structure

```
ccbdataset_api_ax4.0/
├── 📄 main.py                   # Main executor
├── 🔧 config.py                # Configuration
├── 🛠️ models/ax4_api_agent.py  # A.X 4.0 API agent
├── ⚙️ processors/ax4_processor.py # Data processor
├── 📝 prompts/                 # Prompt templates (3 files)
├── 📊 data/sample.json         # Sample data
├── 📁 final_output/            # Generated results
└── 🚀 run_ax4.sh              # Run script
```

## 📜 License

MIT License

## 📞 Support

- [GitHub Issues](https://github.com/your-repo/issues)
- [A.X 4.0 API Documentation](https://github.com/SKT-AI/A.X-4.0/blob/main/apis/README.md)

## 🌐 Language

- 한국어: [README.md](README.md)
- English: [README_EN.md](README_EN.md)

---

**⚡ Fast and easy Q&A generation with uv + A.X 4.0 API!**