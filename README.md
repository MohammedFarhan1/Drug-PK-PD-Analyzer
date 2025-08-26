# 🧬 Drug PK/PD Analyzer v2.0

Advanced Pharmacokinetic & Pharmacodynamic Analysis Platform powered by AI

## ✨ Features

- 🎯 **Smart Drug Analysis** - AI-powered comprehensive drug analysis
- 🔍 **Intelligent Search** - Real-time drug name autocomplete
- 📊 **Multiple Analysis Types** - Comprehensive, comparison, and clinical views
- 📱 **Modern Interface** - Responsive, intuitive web application
- 🚀 **Fast & Secure** - Optimized performance with security best practices
- 📥 **Export Options** - Markdown and JSON export formats
- 💻 **CLI Support** - Command-line interface for automation
- 🌐 **API Ready** - RESTful API for integration

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Copy environment template
cp .env.example .env

# Add your Groq API key to .env
GROQ_API_KEY=your_key_here
```

### 3. Launch Application
```bash
python run.py
```

The application will automatically open in your browser at `http://127.0.0.1:5000`

## 💻 Usage

### Web Interface
1. Enter drug name (with smart autocomplete)
2. Select analysis type:
   - **Comprehensive**: Full PK/PD analysis
   - **Comparison**: Formulation comparison
   - **Clinical**: Clinical overview
3. View results in formatted or raw data tabs
4. Export results as Markdown or JSON

### Command Line Interface
```bash
# Basic analysis
python cli.py "Aspirin"

# Specific analysis type
python cli.py "Metformin" --type comparison

# Save to file
python cli.py "Ibuprofen" --output results.md --format markdown

# List available drugs
python cli.py --list-drugs
```

### API Endpoints
- `GET /api/drugs/search?q=query` - Search drugs
- `POST /api/analyze` - Analyze drug
- `GET /api/export/{format}` - Export results

## 🏗️ Architecture

```
├── core.py           # Core analysis engine
├── app.py            # Flask web application
├── cli.py            # Command-line interface
├── run.py            # Application launcher
├── templates/        # HTML templates
│   ├── index.html    # Main interface
│   └── error.html    # Error pages
└── requirements.txt  # Dependencies
```

## 🔧 Configuration

Environment variables in `.env`:

```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
SECRET_KEY=your_secret_key
```

## 📊 Analysis Types

### Comprehensive Analysis
- Complete PK/PD profile
- All release formulations (IR, SR, CR, DR, Targeted)
- Detailed pharmacokinetic parameters
- Clinical considerations

### Formulation Comparison
- Side-by-side comparison of release types
- Bioavailability differences
- Therapeutic implications

### Clinical Overview
- Dosing guidelines
- Metabolism pathways
- Drug interactions
- Therapeutic monitoring

## 🛡️ Security Features

- Input validation and sanitization
- Secure file handling
- CORS protection
- Error handling without information disclosure
- Environment-based configuration

## 📋 Requirements

- Python 3.8+
- Groq API key (free at groq.com)
- Modern web browser
- Internet connection

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Check the error messages for common issues
- Ensure Groq API key is valid
- Verify internet connection
- Update dependencies if needed

---

**Made with ❤️ for pharmaceutical research and education**