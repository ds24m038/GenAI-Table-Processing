# GenAI Table Processing

A Python Streamlit application for processing tabular data (Excel) using AI to enrich rows with generated content.

## Features

- 📊 **Excel Upload**: Upload Excel files for AI processing
- 🔧 **Configurable Steps**: Define multiple processing steps with custom prompts
- 👁️ **Preview Mode**: Test with one row before processing all data
- 📈 **Token Tracking**: Monitor token usage and estimated costs
- 📥 **Download Results**: Export enriched data as Excel

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/GenAI-Table-Processing.git
cd GenAI-Table-Processing

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your-openai-api-key-here
```

## Usage

### Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Quick Start

1. **Upload** an Excel file using the sidebar
2. **Add processing steps** with prompts referencing your columns
3. **Use placeholders** like `{@CustomerReview}` to inject row data
4. **Preview** with one row to verify output
5. **Process all** rows and download the enriched Excel

### Example: Sentiment Analysis

**Input columns**: `ProductName`, `CustomerReview`, `Rating`

**Processing Step**:
- **Prompt**: 
  ```
  Analyze this review for {@ProductName}: "{@CustomerReview}"
  Determine the sentiment and key points mentioned.
  ```
- **Output Fields**: `sentiment, keyPoints, customerResponse`
- **Model**: `gpt-4o-mini`

**Result**: New columns `AI_sentiment`, `AI_keyPoints`, `AI_customerResponse` added to the Excel file.

## Project Structure

```
GenAI-Table-Processing/
├── app.py                  # Streamlit frontend
├── services/
│   └── processing.py       # OpenAI processing service
├── utils/
│   └── prompt_helper.py    # Placeholder replacement utilities
├── testing/
│   └── example_input_output.xlsx  # Example file
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not in git)
└── README.md
```

## Supported Models

| Model | Best For | Cost |
|-------|----------|------|
| `gpt-4o-mini` | Fast, cost-effective processing | $ |
| `gpt-4o` | High-quality output | $$$ |

