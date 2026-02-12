---
name: pptx
description: "Presentation creation, editing, and analysis. When Claude needs to work with presentations (.pptx files) for: (1) Creating new presentations, (2) Modifying or editing content, (3) Working with layouts, (4) Adding comments or speaker notes, or any other presentation tasks"
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX creation, editing, and analysis

## Overview

A user may ask you to create, edit, or analyze the contents of a .pptx file. A .pptx file is essentially a ZIP archive containing XML files and other resources that you can read or edit. You have different tools and workflows available for different tasks.

## Reading and analyzing content

### Text extraction
```python
from markitdown import MarkItDown

md = MarkItDown().convert_file("presentation.pptx")
print(md.text_content)
```

## Creating a new PowerPoint presentation **without a template**

When creating a new PowerPoint presentation from scratch, use the **html2pptx** workflow to convert HTML slides to PowerPoint with accurate positioning.

### Design Principles

**CRITICAL**: Before creating any presentation, analyze the content and choose appropriate design elements:

1. **Consider the subject matter**: What is this presentation about? What tone, industry, or mood does it suggest?
2. **Check for branding**: If the user mentions a company/organization, consider their brand colors and identity
3. **Match palette to content**: Select colors that reflect the subject
4. **State your approach**: Explain your design choices before writing code

**Requirements**:
- ✅ State your content-informed design approach BEFORE writing code
- ✅ Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- ✅ Create clear visual hierarchy through size, weight, and color
- ✅ Ensure readability: strong contrast, appropriately sized text, clean alignment
- ✅ Be consistent: repeat patterns, spacing, and visual language across slides

### Workflow

1. Create an HTML file for each slide with proper dimensions (e.g., 720pt × 405pt for 16:9)
2. Create and run a JavaScript file using the `html2pptx.js` library to convert HTML slides to PowerPoint
3. **Visual validation**: Generate thumbnails and inspect for layout issues

## Creating a new PowerPoint presentation **using a template**

When you need to create a presentation that follows an existing template's design, you'll need to duplicate and re-arrange template slides before then replacing placeholder context.

### Workflow

1. **Extract template text AND create visual thumbnail grid**
2. **Analyze template and save inventory to a file**
3. **Create presentation outline based on template inventory**
4. **Duplicate, reorder, and delete slides using `rearrange.py`**
5. **Extract ALL text using the `inventory.py` script**
6. **Generate replacement text and save the data to a JSON file**
7. **Apply replacements using the `replace.py` script**

## Editing an existing PowerPoint presentation

When edit slides in an existing PowerPoint presentation, you need to work with the raw Office Open XML (OOXML) format. This involves unpacking the .pptx file, editing the XML content, and repacking it.

### Workflow

1. Unpack the presentation
2. Edit the XML files (primarily `ppt/slides/slide{N}.xml`)
3. **CRITICAL**: Validate immediately after each edit
4. Pack the final presentation

## Dependencies

- **markitdown**: `pip install "markitdown[pptx]"`
- **pptxgenjs**: `npm install -g pptxgenjs`
- **playwright**: `npm install -g playwright`
