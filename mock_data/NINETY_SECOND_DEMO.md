# 90-second judge demo

1. Sign in with the demo account and add a Groq API key in the workspace.
2. Drag in exactly `demo_profit_loss_jan_mar.csv` and `demo_bank_statement_jan_feb_incomplete.csv` together. Do not type a question.
3. The upload starts analysis automatically. Keep the progress card visible while it parses both files, checks liquidity/margins, checks document coverage, and evaluates forward patterns.
4. In **Current state**, point to the gross-margin trend: 70.0%, 65.0%, and 60.0% on rows 2-5 of the P&L CSV.
5. In **Gaps detected**, point to the missing March bank coverage: the P&L includes March while the bank statement ends on 20 February. The exact March cash position must be reported as `cannot be determined from the uploaded documents`.
6. In **Forward flags**, show that gross margin falls by 10 percentage points while revenue is flat. Explain that this is a pattern-based flag, not a prediction.
7. Click a citation chip to show the cited source excerpt. State the boundary: the product analyzes evidence and declines tax, legal, and investment recommendations, including whether someone should take a loan.

Honest limitation: results depend on the documents supplied and the configured Groq model; it cannot establish a missing March cash balance without a March bank statement.
