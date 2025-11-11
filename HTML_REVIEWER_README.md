# HTML Structured Note Reviewer - Streamlit App

A powerful Streamlit web application for uploading, reviewing, and analyzing HTML structured notes.

## Features

### 📄 Rendered View
- View your HTML file as it would appear in a browser
- Interactive scrolling interface
- Preserves all styling and formatting

### 🔍 HTML Source
- View the raw HTML source code with syntax highlighting
- Line numbers for easy reference
- Download button to save the HTML file

### 🏗️ Structure Analysis
- **Headings Analysis**: See all H1-H6 headings with their content
- **Tags Usage**: View which HTML tags are used and how often
- **Links Analysis**: List of all links with their text and URLs
- **Images Analysis**: All images with their sources and alt text

### 📊 Statistics
- Word count, character count
- Number of paragraphs, lists, tables
- Total HTML elements
- Text content preview

## Installation

1. Install required dependencies:
```bash
pip install -r streamlit_requirements.txt
```

Or install manually:
```bash
pip install streamlit beautifulsoup4
```

## Usage

### Starting the App

Run the following command in your terminal:

```bash
streamlit run html_reviewer_app.py
```

This will:
1. Start the Streamlit server
2. Open your default browser automatically
3. Display the app at `http://localhost:8501`

### Using the App

1. **Upload Your HTML File**
   - Click the "Browse files" button
   - Select an HTML file from your computer (.html or .htm)

2. **Review in Different Tabs**
   - Switch between tabs to view different aspects of your HTML file
   - Use the rendered view to see how it looks
   - Check structure analysis to understand document organization
   - Review statistics for document metrics

3. **Download or Modify**
   - Download the HTML source from the "HTML Source" tab
   - Copy code snippets as needed

## Sample File

A sample HTML file (`sample_note.html`) is included to test the app. Try uploading it to see all the features in action.

## Command Line Options

Stop the app:
- Press `Ctrl+C` in the terminal where Streamlit is running

Run on a different port:
```bash
streamlit run html_reviewer_app.py --server.port 8502
```

Run without opening browser:
```bash
streamlit run html_reviewer_app.py --server.headless true
```

## Tips

- **Large Files**: The app can handle large HTML files, but very large files may take longer to render
- **External Resources**: If your HTML references external CSS or images, they will be loaded if accessible
- **Security**: Only upload HTML files you trust, as they will be rendered in your browser

## Troubleshooting

**App won't start:**
- Make sure Streamlit is installed: `pip install streamlit`
- Check if port 8501 is already in use

**HTML not rendering correctly:**
- Check if your HTML file is valid
- External resources (CSS, images) may not load if paths are incorrect

**Can't upload file:**
- Ensure the file has .html or .htm extension
- Check file permissions

## Technical Details

- Built with Streamlit 1.28+
- Uses BeautifulSoup4 for HTML parsing
- Supports all modern HTML5 features
- Responsive design for different screen sizes

## Files Included

- `html_reviewer_app.py` - Main Streamlit application
- `streamlit_requirements.txt` - Python dependencies
- `sample_note.html` - Example HTML file for testing
- `HTML_REVIEWER_README.md` - This file

## License

Free to use and modify for your purposes.
