---
name: excel-author
description: Build auditable financial workbooks headless via openpyxl. Use for financial projections, debt analysis, budget reports, and any Excel deliverable that requires formulas, formatting, and auditability.
---

# Excel Author — Financial Workbooks

Produce auditable .xlsx files using `openpyxl` with banker-grade conventions.

## Output Contract

- Write to `./out/<name>.xlsx`. Create `./out/` if it does not exist.
- One logical model per file.
- Return the relative path in final message.

## Core Conventions

### Color Coding
- **Blue** (`Font(color="0000FF")`) — hardcoded input (assumptions, market data)
- **Black** (default) — formula (derived cells)
- **Green** (`Font(color="006100")`) — link to another sheet

### Formulas Over Hardcodes
Every calculation cell MUST be a formula, never a Python-computed value.

```python
# WRONG
ws["D20"] = revenue * (1 + growth)

# CORRECT
ws["D20"] = "=D19*(1+$B$8)"
```

### Cell Comments on Every Hardcoded Input
```python
from openpyxl.comments import Comment
ws["C2"] = 1_250_000_000
ws["C2"].font = Font(color="0000FF")
ws["C2"].comment = Comment("Source: 10-K FY2024, p.47", "analyst")
```

### Balance Checks Tab
Include a `Checks` tab with TRUE/FALSE validation formulas.

### Named Ranges for Cross-Sheet References
```python
from openpyxl.workbook.defined_name import DefinedName
wb.defined_names["WACC"] = DefinedName("WACC", attr_text="Inputs!$C$8")
```

## Recalculating Before Delivery

```bash
libreoffice --headless --calc --convert-to xlsx ./out/model.xlsx --outdir ./out/
```

## Model Layout Planning

Before writing any formula:
1. Define ALL section row positions
2. Write ALL headers and labels
3. THEN write formulas using locked row positions
