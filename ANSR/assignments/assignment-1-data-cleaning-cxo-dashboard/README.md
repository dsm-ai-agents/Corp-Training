# Assignment 1 — Data Cleaning, CXO Presentation & Dashboard



## Background
The extract was compiled from multiple regional teams and has not been cleaned.

## Dataset
[`dataset/gcc_talent_data_raw.csv`](dataset/gcc_talent_data_raw.csv)

## Your Task

### Part A — Data Cleaning
Clean the raw dataset. You'll find (non-exhaustive):
- Duplicate records with slight variations
- Inconsistent city names/spellings (e.g., Bengaluru / Bangalore / Blore, Gurugram / Gurgaon)
- Inconsistent casing across text fields
- Mixed date formats (DD-MM-YYYY, YYYY-MM-DD, year-only, "unknown")
- Salary figures in mixed formats (INR with commas, LPA shorthand, USD-tagged, raw numbers)
- Missing values
- Invalid/non-numeric entries in numeric columns (e.g., "invalid", "ERROR")
- Outlier/implausible values (e.g., attrition rate of 999% or -5%)
- Extra whitespace in fields
- Blank/junk rows

Document the cleaning decisions you made and why.

### Part B — CXO Presentation
Produce a **single-slide** executive presentation summarizing the cleaned data. Assume the audience is a CXO deciding where to invest in GCC expansion. Prioritize the 3-5 insights that matter most for that decision.

### Part C — Dashboard
Build a dashboard (tool of your choice — Excel, Power BI, Tableau, Looker Studio, etc.) on the cleaned dataset. At minimum, surface:
- Headcount and attrition by city/industry/function
- Salary benchmarks by role and location
- GCC maturity (tier, setup year) trends

## Deliverables
1. Cleaned dataset (file)
2. Brief note on cleaning decisions
3. One-slide CXO presentation
4. Dashboard (file or shareable link)
