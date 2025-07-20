# E-Book Generator using LangGraph and Gemini

A professional AI-powered e-book generation system using LangGraph and Google's Gemini API.

🚀 **Try it now**: [Launch the E-Book Generator App](https://ai-ebook-generator.streamlit.app/)

## Features

- **AI-Powered Content Generation**: Uses Google's Gemini API for intelligent content creation
- **Multi-Format Output**: Supports Markdown, DOC, and PDF formats
- **Interactive Interface**: User-friendly interface with input widgets
- **Professional Structure**: Modular design with separate components
- **Customizable Parameters**: Adjustable tone, audience, and format settings

## Project Structure

```
EBook/
├── main.py              # Main application entry point
├── config.py            # Configuration settings and constants
├── graph.py             # LangGraph workflow implementation
├── nodes.py             # Individual workflow nodes
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── .gitignore          # Git ignore rules
├── .env.example        # Environment variables template
├── output/             # Generated e-books directory
└── tests/              # Unit tests (optional)
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd EBook
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   copy .env.example .env
   # Edit .env file and add your Gemini API key
   ```

## Usage

### Running in Google Colab

The application is designed to work seamlessly in Google Colab:

1. Upload the project files to Colab
2. Run the main.py file
3. Use the interactive widgets to configure your e-book
4. Click "Generate E-book" to start the process

### Running Locally

```python
python main.py
```

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key

### Default Settings

- **Model**: gemini-pro
- **Temperature**: 0.7
- **Max Tokens**: 4000
- **Default Format**: DOC

## API Key Setup

1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Input Parameters

- **Topic**: The subject of your e-book
- **Target Audience**: Who the book is written for
- **Tone**: Writing style (professional, casual, academic, etc.)
- **Format**: Output format (Markdown, DOC, PDF)

## Output

The generated e-book will be saved in the `output/` directory and automatically downloaded in Colab environments.

## System Requirements

- Python 3.8+
- Internet connection for API calls
- Sufficient disk space for output files

## Dependencies

- IPython/Jupyter support
- Google Colab integration
- LangGraph for workflow management
- Google Generative AI
- Document processing libraries

## Version

Current version: 1.0.0

## Author

Created by: snigdhapaul2003

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
