# 🤖 GenAI Table Processing

> **Enrich your tabular data with AI-generated content**

A Python Streamlit application that processes Excel files row-by-row using OpenAI, adding AI-generated columns based on customizable prompts.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Excel Upload** | Drag-and-drop Excel files (`.xlsx`, `.xls`) for processing |
| 🔧 **Multi-Step Processing** | Chain multiple AI prompts in sequence |
| 🔗 **Dynamic Placeholders** | Reference any column with `{@ColumnName}` syntax |
| 👁️ **Preview Mode** | Test on a single row before processing all data |
| 📈 **Cost Tracking** | Real-time token usage and cost estimation |
| 📥 **Export Results** | Download enriched Excel with `AI_` prefixed columns |

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/GenAI-Table-Processing.git
cd GenAI-Table-Processing

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Run the App

```bash
streamlit run app.py
```

Open your browser to **http://localhost:8501**

---

## 📖 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Upload Excel    →   Your data with columns like            │
│                         ProductName, CustomerReview, Rating     │
├─────────────────────────────────────────────────────────────────┤
│  2. Configure       →   Define prompts using {@ColumnName}      │
│     Prompts             placeholders to reference row data      │
├─────────────────────────────────────────────────────────────────┤
│  3. Process         →   AI analyzes each row and generates      │
│                         structured JSON responses               │
├─────────────────────────────────────────────────────────────────┤
│  4. Download        →   Get enriched Excel with new AI_         │
│                         prefixed columns added                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💡 Example Use Case: Product Review Analysis

### Input Excel

| ProductID | ProductName | CustomerReview | Rating |
|-----------|-------------|----------------|--------|
| P001 | Wireless Mouse | Amazing! Super responsive and battery lasts forever. | 5 |
| P002 | USB-C Hub | Gets hot after prolonged use. Ports are loose. | 3 |

### Processing Step Configuration

**Prompt:**
```
Analyze this customer review for {@ProductName}: "{@CustomerReview}"

Determine:
1. The overall sentiment (positive/neutral/negative)
2. Key points mentioned by the customer
3. A professional response to the customer
```

**Output Fields:** `sentiment, keyPoints, customerResponse`

### Output Excel (with AI columns)

| ProductID | ProductName | CustomerReview | Rating | AI_sentiment | AI_keyPoints | AI_customerResponse |
|-----------|-------------|----------------|--------|--------------|--------------|---------------------|
| P001 | Wireless Mouse | Amazing! Super responsive... | 5 | positive | Responsive, Long battery | Thank you for your feedback... |
| P002 | USB-C Hub | Gets hot after prolonged use... | 3 | neutral | Overheating, Loose ports | We appreciate your honest... |

---

## 🗂️ Project Structure

```
GenAI-Table-Processing/
│
├── app.py                      # Streamlit frontend application
│
├── services/
│   ├── __init__.py
│   └── processing.py           # OpenAI API integration
│
├── utils/
│   ├── __init__.py
│   └── prompt_helper.py        # Placeholder replacement logic
│
├── testing/
│   └── example_input_output.xlsx   # Sample file for testing
│
├── requirements.txt            # Python dependencies
├── .env                        # API keys (gitignored)
└── README.md
```

---

## ⚙️ Supported Models

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| `gpt-4o-mini` | ⚡ Fast | Good | $ | Large datasets, prototyping |
| `gpt-4o` | Medium | Excellent | $$$ | Production, complex analysis |

---

## 🔧 Advanced Usage

### Chaining Multiple Steps

You can add multiple processing steps that build on each other:

**Step 1:** Classify the review
```
Classify this review: "{@CustomerReview}"
→ Output: category
```

**Step 2:** Generate response based on classification (references Step 1's output)
```
Write a response for this {@AI_category} review: "{@CustomerReview}"
→ Output: response
```

### Conditional Logic

Use the AI output from previous steps to guide subsequent processing. Each step can reference columns created by earlier steps using the `AI_` prefix.

---

## 📋 Requirements

- Python 3.9+
- OpenAI API key
- Dependencies: `streamlit`, `pandas`, `openpyxl`, `openai`, `python-dotenv`

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "OPENAI_API_KEY not found" | Ensure `.env` file exists with valid key |
| Excel upload fails | Check file is `.xlsx` or `.xls` format |
| Empty AI columns | Verify prompt uses correct `{@ColumnName}` syntax |
| High costs | Use `gpt-4o-mini` and preview before full processing |
