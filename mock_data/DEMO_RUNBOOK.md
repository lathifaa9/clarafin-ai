# Financial-document intelligence demo runbook

This is a fictional SME scenario designed directly around the hackathon brief. It gives the agent enough source material to provide autonomous current-state analysis and forward-looking flags, while deliberately leaving a small set of business documents absent so that it can demonstrate helpful gap detection.

## Upload set

Upload these documents together, then select **Analyze documents** without entering a question:

- `bank_statement.csv`
- `open_invoices.csv`
- `accounts_receivable_aging.csv`
- `accounts_payable.csv`
- `profit_loss.xlsx`
- `balance_sheet.xlsx`
- `cash_flow.xlsx`

Do not include `Profit and loss.csv` in this run. It is the original 2019-2022 Kaggle file and belongs to a different company/time period.

## Scope decisions

| Decision | Prototype scope |
| --- | --- |
| Accepted documents | PDF, CSV, XLSX, and XLS. These are the formats handled by the current upload parser. |
| Minimum meaningful input | Bank statement + P&L + open-invoice register. This supports cash, margin, concentration, and receivables observations. Add the balance sheet and cash-flow statement for liquidity and cash-flow interpretation. |
| Agent boundary | Analysis and flags only. It must not give tax advice, legal advice, or investment recommendations. |
| Traceability rule | Every metric and observation must cite the uploaded filename and exact CSV row or Excel sheet/row. A missing source must be stated as `cannot be determined from the uploaded documents`; figures must not be estimated. |

## Expected current-state signals

These are check values for the demo, not text that should be uploaded as an analysis source.

| Signal | Derivation from uploaded documents | Interpretation to expect |
| --- | --- | --- |
| Liquidity | `balance_sheet.xlsx`, Balance Sheet rows 7 and 17: July current assets $104,060 / current liabilities $10,000 = **10.41x current ratio** | Strong reported short-term coverage, subject to receivable collectability. |
| Margin trend | `profit_loss.xlsx`, P&L rows 5 and 7: gross margin is **83.6%** in May ($23,000 / $27,500), **78.2%** in June ($21,500 / $27,500), and **72.7%** in July ($20,000 / $27,500). | Gross margin has declined for three consecutive months as COGS rises while revenue is flat. |
| Revenue concentration | `profit_loss.xlsx`, P&L rows 3-5: July revenue is ACME $12,500 and Wayne $15,000 out of total revenue $27,500. | The top customer, Wayne Enterprises, represents **54.5%** of July revenue; the two customers represent 100%. |
| Receivables | `accounts_receivable_aging.csv`, rows 2-5: $40,500 open, including Wayne's $15,000 invoice five days overdue. | Collection timing is a near-term cash risk; this is an observation, not a collection recommendation. |
| Expense anomalies | `bank_statement.csv`, row 17: duplicate AWS charge; row 12: unexplained director cash withdrawal; June marketing and utility rows 23 and 22 are above May equivalents. | Flag for review with the cited transaction, never label a transaction as fraudulent. |

## Expected forward-looking flags

Forward-looking flags describe a trajectory in the provided records. They are not forecasts or advice.

- **Receivables risk - Medium:** $15,000 of Wayne Enterprises receivables is already five days past due (`accounts_receivable_aging.csv`, row 2), while that customer is the largest July revenue source (`profit_loss.xlsx`, P&L row 4).
- **Margin pressure - Medium:** Gross margin fell from 83.6% in May to 72.7% in July (`profit_loss.xlsx`, P&L rows 5-7).
- **Cash/runway pressure - Medium:** The bank balance falls from $57,890 after 25 June to $48,560 after 25 July (`bank_statement.csv`, rows 23 and 33), while the balance sheet's bank loan rises from $15,000 in June to $25,000 in July (`balance_sheet.xlsx`, Balance Sheet row 18). This is a flag for review, not a forecast of failure.

## Intentional gaps to detect

The following files are intentionally absent. The agent should describe the decision that each absence blocks, rather than invent a number.

| Missing document | Decision blocked |
| --- | --- |
| Approved budget and forecast | Variance-to-plan and forecasted cash runway cannot be determined from the uploaded documents. |
| 13-week cash forecast / committed cash calendar | Exact future liquidity timing cannot be determined from the uploaded documents. |
| Inventory aging and purchase-order schedule | Inventory obsolescence and committed supplier-cash exposure cannot be determined from the uploaded documents. |
| Payroll, tax, and statutory-payment schedules | Upcoming statutory and payroll obligations cannot be determined from the uploaded documents. |

## Source datasets

The supplied `Profit and loss.csv` matches the [Kaggle Profit and Loss Statement dataset](https://www.kaggle.com/datasets/shantanubiswas99/profit-and-loss-statement). The remaining files in this folder are a small, internally related synthetic SME scenario, which is more suitable for an end-to-end upload demo than mixing unrelated public-company datasets. Kaggle's [customer-invoices dataset](https://www.kaggle.com/datasets/pradumn203/payment-date-prediction-for-invoices-dataset) is a suitable optional source for expanding invoice-aging examples; check its CC BY-NC 4.0 license before reuse outside this prototype.

All records in the 2026 scenario are fictional and for demo/testing only.
