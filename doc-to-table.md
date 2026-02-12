---
name: doc-to-table
description: This skill should be used when the user asks to "convert document to table", "extract table from", "parse document to Excel", "transform HTML to table", "export text to spreadsheet", mentions "table extraction", "document parsing", or discusses converting various file formats (PDF, PPT, MD, HTML, text) into tabular format. Automatically detects file format and preserves original styling.
version: 1.0.0
---

# Document to Table Converter

Universal skill for converting documents from various formats into Excel tables while preserving original formatting.

## When This Skill Activates

This skill activates when the user requests:
- Converting documents to tables/spreadsheets
- Extracting tables from files
- Parsing structured content from documents
- Transforming HTML into Excel
- Exporting text/markdown to table format
- Creating spreadsheets from various file formats

## Supported Input Formats

### 1. Text Documents (.txt, .md)
- Plain text files
- Markdown documents
- CSV files
- JSON/YAML structured data

### 2. Presentation Files (.ppt, .pptx)
- PowerPoint presentations
- Keynote files (exported to PPT)

### 3. PDF Documents (.pdf)
- Text-based PDFs
- Scanned PDFs (with OCR)
- PDFs with embedded tables

### 4. HTML Documents (.html, .htm)
- Web pages
- HTML tables
- HTML code snippets
- Web-scraped content

### 5. Other Formats
- RTF files
- Word documents (.doc, .docx)
- CSV files
- JSON/JSONL files

## Workflow

### Step 1: Analyze Input Document
1. Determine file format from extension or content
2. Check file size and complexity
3. Identify table structures in the document
4. Detect encoding and language

### Step 2: Choose Extraction Method
Based on input format:

**Text/Markdown:**
- Parse table structures (markdown tables)
- Extract tab/comma-separated data
- Detect list structures that can be tabularized

**PowerPoint:**
- Extract text from slides
- Identify table shapes
- Parse slide layouts

**PDF:**
- Use pdfplumber for text-based PDFs
- Use pdf2image + OCR for scanned PDFs
- Extract tables with camelot or tabula

**HTML:**
- Use BeautifulSoup to parse HTML
- Extract <table> elements
- Preserve inline styles (colors, fonts, alignment)
- Handle colspan/rowspan attributes

**Word:**
- Use python-docx to extract tables
- Preserve document structure
- Extract styling information

### Step 3: Process and Clean Data
1. Normalize text encoding (UTF-8)
2. Handle merged cells
3. Clean whitespace
4. Detect data types (numbers, dates, text)
5. Preserve formatting (bold, colors, alignment)

### Step 4: Generate Excel Output
1. Create Excel workbook with openpyxl
2. Apply original styling:
   - Font families and sizes
   - Cell colors (background, text)
   - Borders and alignment
   - Merged cells
3. Auto-adjust column widths
4. Save to output file

## Implementation Guidelines

### For Text/Markdown Files
```python
# Key considerations:
- Detect markdown table syntax: | col1 | col2 |
- Handle CSV delimiters (comma, tab, semicolon)
- Parse JSON/YAML into tabular format
- Preserve list indentation as hierarchy
```

### For HTML Files ⭐ CRITICAL
```python
# MUST preserve:
- Cell background colors (bgcolor, style="background:")
- Text colors (color, style="color:")
- Font families and sizes (font-family, font-size)
- Text alignment (text-align)
- Borders (border, border-left, etc.)
- Font weight (bold, strong)
- Cell merging (colspan, rowspan)
- Vertical alignment (valign)

# Use BeautifulSoup for parsing
# Use openpyxl for Excel styling
```

### For PDF Files
```python
# Choose method based on PDF type:
if text_based:
    use pdfplumber.extract_tables()
else:  # scanned
    use pdf2image + pytesseract OCR
    then extract tables from OCR text

# Handle:
- Multi-page tables
- Header rows
- Column alignment
- Merged cells (visual detection)
```

### For PowerPoint Files
```python
# Extract from:
- pptx.Shape objects with table properties
- Text frames organized by position
- Slide layouts with table placeholders

# Preserve:
- Slide titles as headers
- Table structure
- Basic formatting (bold, colors)
```

## Output Format

**Default:** Excel (.xlsx) file with same base name as input

**Location:** Same directory as input file (or user-specified)

**Filename pattern:**
```
input.docx → input.tables.xlsx
input.html → input.tables.xlsx
report.pdf → report.tables.xlsx
```

**Excel Structure:**
- Multiple sheets if source has multiple tables
- Sheet names: Table_1, Table_2, etc. (or descriptive names)
- First sheet: Summary (file metadata, extraction stats)
- Original styling preserved in all sheets

## Error Handling

### File Not Readable
- Check file permissions
- Verify file format
- Try alternative parsing methods
- Report specific error to user

### No Tables Found
- Inform user that no table structures detected
- Suggest alternative parsing approaches
- Offer to create table from lists/structured text

### Encoding Issues
- Detect encoding with chardet
- Try UTF-8, GBK, GB2312, Big5 for Chinese text
- Fallback to latin-1
- Report encoding used

### Large Files
- For PDFs: Process page by page
- For HTML: Stream parsing
- Show progress indicator
- Warn about memory usage

## Advanced Features

### Batch Processing
Process multiple files:
```bash
# Process all PDFs in directory
for file in *.pdf; do
    python scripts/convert_to_table.py "$file"
done
```

### Custom Table Detection
For complex layouts:
- Use YOLO-based table detection for images/PDFs
- Train custom model for specific document types
- Use layout parser (layoutparser)

### Merged Cell Handling
- Detect merged cells in HTML (colspan/rowspan)
- Visual detection in PDFs (white space analysis)
- Preserve in Excel using merge_cells()

### Style Mapping
Map HTML/CSS styles to Excel:
```python
STYLE_MAP = {
    'color': 'openpyxl.styles.Font.color',
    'background-color': 'openpyxl.styles.PatternFill.start_color',
    'font-weight': 'openpyxl.styles.Font.bold',
    'text-align': 'openpyxl.styles.Alignment.horizontal',
    'font-size': 'openpyxl.styles.Font.size'
}
```

## Required Python Libraries

Install before first use:
```bash
pip install openpyxl pandas BeautifulSoup4 lxml
pip install pdfplumber camelot-py tabula-py
pip install python-pptx python-docx
pip install pdf2image pytesseract pillow
pip install chardet
```

**Optional for OCR:**
- Install Tesseract OCR engine separately
- For Chinese: `tesseract-ocr` + `chi_sim` training data

## Quick Start Examples

### Convert HTML to Excel
```bash
python ~/.claude/plugins/custom-doc-to-table/scripts/convert_to_table.py report.html
```

### Convert PDF to Excel
```bash
python ~/.claude/plugins/custom-doc-to-table/scripts/convert_to_table.py data.pdf
```

### Convert Markdown Table to Excel
```bash
python ~/.claude/plugins/custom-doc-to-table/scripts/convert_to_table.py README.md
```

### Convert PowerPoint to Excel
```bash
python ~/.claude/plugins/custom-doc-to-table/scripts/convert_to_table.py presentation.pptx
```

## Best Practices

1. **Always preserve original file** - Never overwrite input
2. **Validate extracted data** - Check for garbled text, missing columns
3. **Handle Chinese text properly** - Use correct encoding (UTF-8, GBK)
4. **Test on sample first** - Process small sample before batch
5. **Report statistics** - Show number of tables, rows, columns found
6. **Provide preview** - Show first few rows of extracted tables
7. **Document limitations** - Warn about complex layouts, scanned docs

## Troubleshooting

### Issue: Garbled Chinese text
**Solution:** Force UTF-8 encoding or detect with chardet

### Issue: Tables not detected in PDF
**Solution:** Try different extraction methods (camelot vs tabula vs pdfplumber)

### Issue: HTML styles not preserved
**Solution:** Check inline styles vs CSS classes; inline only

### Issue: Large file processing fails
**Solution:** Increase memory, process page-by-page, use streaming

### Issue: Merged cells lost
**Solution:** Explicitly detect and preserve using merge_cells()

## Example Output

**Input (HTML):**
```html
<table>
  <tr style="background: #f0f0f0;">
    <th style="color: blue;">Name</th>
    <th>Age</th>
  </tr>
  <tr>
    <td style="font-weight: bold;">Alice</td>
    <td>25</td>
  </tr>
</table>
```

**Output (Excel):**
- Sheet: "Table_1"
- Row 1: Gray background, blue bold text for headers
- Row 2: Bold text for "Alice"
- Auto-fitted column widths

## Integration with Claude Code

When this skill is invoked:
1. Claude will automatically detect file format
2. Select appropriate conversion method
3. Execute conversion script
4. Report results with file path
5. Show extraction statistics
6. Offer to open/preview the Excel file

**Typical interaction:**
```
User: Convert this HTML file to table
Claude: [Invokes doc-to-table skill]
       → Detects HTML format
       → Parses tables with BeautifulSoup
       → Preserves inline styles
       → Generates Excel with openpyxl
       → Reports: "Found 3 tables, 45 rows total"
       → Output: data.html → data.tables.xlsx
```

## Limitations

- **Scanned PDFs:** OCR accuracy depends on image quality
- **Complex HTML layouts:** CSS positioning may not be preserved
- **Password-protected files:** Need password first
- **Very large files (>100MB):** May require chunking
- **Handwritten text:** OCR limitations

## Future Enhancements

- Support for Excel macros and formulas
- Detect and convert images with tables
- Multi-language OCR improvements
- Batch processing with progress bars
- GUI for non-technical users
- Cloud API integration for better OCR
