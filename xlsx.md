---
name: xlsx
description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization"
license: Proprietary
---

# XLSX Processing

## Overview

This guide covers Excel spreadsheet operations using Python libraries.

## Quick Start

```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws['A1'] = 'Hello'
wb.save('hello.xlsx')
```

## Python Libraries

### openpyxl - Basic Operations

#### Create Spreadsheet

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

wb = Workbook()
ws = wb.active

# Add data
ws['A1'] = 'Name'
ws['B1'] = 'Value'
ws['A2'] = 'Item 1'
ws['B2'] = 100

# Style header
header_font = Font(bold=True)
header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
ws['A1'].font = header_font
ws['A1'].fill = header_fill
ws['B1'].font = header_font
ws['B1'].fill = header_fill

wb.save('output.xlsx')
```

#### Read Spreadsheet

```python
from openpyxl import load_workbook

wb = load_workbook('data.xlsx')
ws = wb.active

for row in ws.iter_rows(values_only=True):
    print(row)
```

#### Add Formulas

```python
ws['C1'] = 'Total'
ws['C2'] = '=B2*1.1'  # 10% increase
ws['C3'] = '=SUM(B2:B10)'  # Sum range
```

### pandas - Data Analysis

```python
import pandas as pd

# Read Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# Process data
df['Total'] = df['Quantity'] * df['Price']

# Write back
df.to_excel('output.xlsx', index=False)
```

## Best Practices

1. **Zero Formula Errors**: Verify all cell references
2. **Use Excel formulas** instead of calculating in Python when possible
3. **Industry-standard colors** for professional look
4. **LibreOffice** required for formula recalculation

## Dependencies

- **openpyxl**: `pip install openpyxl`
- **pandas**: `pip install pandas openpyxl`
- **LibreOffice**: For formula recalculation
