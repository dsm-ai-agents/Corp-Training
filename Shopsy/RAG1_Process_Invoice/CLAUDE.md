# RAG1 Process Invoice

Pipeline that turns Apex AI Solutions invoice PDFs into Markdown (for RAG) and an Excel workbook (for analysis).

## Folder layout

| Folder / file | Purpose |
| --- | --- |
| `INVOICES/` | **Inbox.** Drop new invoice PDFs here. Empty after a successful run. |
| `converted/` | One `.md` per invoice, produced by MarkItDown. |
| `completed/` | PDFs that converted successfully are moved here. |
| `data/invoices.xlsx` | Analysis workbook, rebuilt from **all** files in `converted/`. |
| `convert_invoices.py` | Step 1: PDF → Markdown, then move PDF to `completed/`. |
| `build_invoice_excel.py` | Step 2: Markdown → `data/invoices.xlsx`. |

## Processing new invoices

When the user says they have new files (or asks to "redo" / "run the pipeline"):

1. Check that `INVOICES/` has PDFs. If they're in a zip, extract them into `INVOICES/` first.
2. Run step 1, then step 2 (commands below), from this folder.
3. Report the results: how many converted, any `[fail]` lines from step 1, and any invoice whose `Check` is not `OK` in step 2.
4. If a check fails, open that invoice's `.md` in `converted/` and fix the parser (see "Parser notes"). Don't hand-edit the Excel file, because it's regenerated on every run.

```powershell
$env:Path = [Environment]::GetEnvironmentVariable('Path','User') + ';' + [Environment]::GetEnvironmentVariable('Path','Machine')
$py = "$env:APPDATA\uv\python\cpython-3.12.16-windows-x86_64-none\python.exe"
uv run --python $py convert_invoices.py
uv run --python $py build_invoice_excel.py
```

Both scripts declare their dependencies inline (PEP 723), so `uv run` installs them automatically. Each script exits with code 1 if anything failed.

## Environment gotchas (this Windows machine)

- **No system Python.** `python` is only the Microsoft Store placeholder. Python 3.12 is managed by **uv** (installed with winget, per user). Run everything with `uv run`.
- **Pass the full interpreter path to `--python`.** uv couldn't create its `cpython-3.12-...` shortcut link (possibly the sandbox), so `--python 3.12` may fail with "Missing expected target directory". Running `uv python install 3.12 --reinstall` in a normal terminal may fix that. If the path above no longer exists, find the current one with `uv python list --only-installed`.
- **Open a new shell after installing uv, or refresh PATH.** The first line of the command block above reloads PATH so `uv` is found in an existing shell.
- **Don't use pandas.** Windows Application Control blocks pandas' compiled DLLs ("An Application Control policy has blocked this file"). The Excel step uses **openpyxl only** (pure Python). The PDF step's MarkItDown dependencies (numpy, onnxruntime, magika) did load without problems.

## Workbook contents (`data/invoices.xlsx`)

- **Invoices** (one row per invoice): Invoice No, Invoice Type (`Client Invoice` for `INV-`, `Internal Expense` for `EXP-`), Invoice Date, Year, Month, Due Date, Client, Client Address, Service Type, Line Count, Subtotal, Tax Rate, Tax, Total Due, Notes, Source File, Check.
- **Line Items** (one row per line): Invoice No, Line No, Invoice Type, Invoice Date, Year, Month, Client, Service Type, Description, Qty, Unit Price, Amount.
- `Check` is `OK` only when qty × unit price = amount on every line, the lines sum to the subtotal, subtotal + tax = total, and both client and service type were found.

## Parser notes (`build_invoice_excel.py`)

MarkItDown's PDF output is inconsistent. The same field can end up in a markdown table cell on one invoice and on a plain line on another, and table header/separator rows show up in odd places. To handle this, the parser:

- Drops `|---|` separator rows and flattens each table row into space-separated text before matching.
- Reads line items between the `DESCRIPTION` header and `Subtotal`, using the pattern `<description> <qty> $<unit> $<amount>`. If a line doesn't match, the script raises an error instead of silently skipping it.
- Takes the BILL TO block from `BILL TO` up to `DESCRIPTION`: the first remaining piece is the client and the rest is the address. The service type is found by matching against the hard-coded `SERVICE_TYPES` list, because sometimes it's glued onto the end of the address line.
- **A new service type** gets flagged by the Check column ("missing client or service type"). Add it to `SERVICE_TYPES` and rerun.
- **A new invoice layout or field** (different currency, discount line, multiple tax lines): look at the `.md` first, then extend the regexes. Keep the arithmetic checks in place.

## Rerunning from scratch

Step 2 always rebuilds the workbook from everything in `converted/`, so rerunning it is safe. To reconvert old PDFs, move them from `completed/` back to `INVOICES/` and run step 1. Existing `.md` files get overwritten.
