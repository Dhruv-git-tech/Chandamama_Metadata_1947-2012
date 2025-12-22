# Chandamama Magazine Indexer

A Streamlit application powered by Google's Gemini 2.5 Flash model to automatically extract and index stories from "Chandamama" magazine PDFs.

## Features

-   **Single File Mode**: Upload and process one PDF at a time.
-   **Bulk Processing Mode**: Process an entire directory of PDFs (e.g., a whole year) in one go.
-   **Verification UI**: Review and edit extracted data before saving.
-   **Robustness**:
    -   **Auto-Backup**: Progress is saved automatically. If the app crashes, it restores your session.
    -   **Error Handling**: Skips problematic files without stopping the queue.
-   **Custom Export**: Choose exactly where to save your JSON files.

## Prerequisites

1.  **Python 3.8+**
2.  **Gemini API Key**: You need a valid API key from Google AI Studio.

### Installation

Install the required Python packages:

```bash
pip install streamlit requests
```

## How to Run

1.  Open a terminal in the project directory.
2.  Run the Streamlit app:

```bash
streamlit run streamlit_indexer.py
```

3.  The app will open in your default web browser (usually at `http://localhost:8501`).

## Usage Guide

### 1. Single File Processing
Use this for quick testing or processing individual magazines.
1.  Select **"Single File"** in the sidebar.
2.  Enter your **Gemini API Key**.
3.  **Upload** a PDF file.
4.  Click **"Analyze PDF"**.
5.  Review the extracted stories in the table.
6.  Click **"Download JSON"** to save the result.

### 2. Bulk Processing (Recommended for Archives)
Use this to process large collections (e.g., 100+ files).

1.  Select **"Bulk Processing"** in the sidebar.
2.  Enter your **Gemini API Key**.
3.  **Input Directory**: Enter the full path to the folder containing your PDFs.
    *   *Example*: `C:/Chandamama/1947`
4.  **Output Directory**: Enter the path where you want JSONs saved.
    *   *Default*: Creates a `json` folder inside your input directory.
5.  Click **"Start Batch Processing"**.
    *   The app will process files one by one.
    *   **Progress is saved automatically**. You can close the browser and resume later.
6.  **Verification**:
    *   Once processing is done (or even during), scroll down to the "Verification" section.
    *   Select a file from the list (🟢 = Processed, 🔴 = Error).
    *   Edit the data in the table if needed.
    *   Click **"Mark as Verified"** (The icon will turn to ✅).
7.  **Export**:
    *   Click **"Generate JSONs for Verified Files"**.
    *   All verified files will be saved to your Output Directory.

## Input & Output

### Input
-   **Format**: PDF files.
-   **Naming Convention**: The app tries to derive metadata from the filename.
    *   *Example*: `Chandamama 1947 11.pdf` -> Book ID: `chandamama_1947_11`

### Output (JSON)
Each PDF generates a JSON file with the following structure:

```json
{
    "book_id": "chandamama_1947_11",
    "stories": [
        {
            "title": "Story Title in Telugu",
            "page_start": 5,
            "author": "Author Name or 'చందమామ బృందం'"
        },
        ...
    ]
}
```
