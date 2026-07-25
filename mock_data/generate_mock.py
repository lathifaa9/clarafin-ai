import os
import csv
import pandas as pd
from datetime import datetime

def create_mock_data():
    os.makedirs('mock_data', exist_ok=True)
    
    # 1. Generate bank_statement.csv (Transactions with anomalies)
    bank_file = 'mock_data/bank_statement.csv'
    bank_headers = ['Date', 'Description', 'Amount', 'Balance', 'Category']
    balance = 50000.0
    transactions = []
    
    raw_txs = [
        # May 2026
        ('2026-05-01', 'Client ACME Corp Revenue Deposit', 12500.0, 'Revenue'),
        ('2026-05-02', 'Office Rent Payment', -3200.0, 'Rent'),
        ('2026-05-05', 'AWS Cloud Services Hosting', -850.0, 'Software'),
        ('2026-05-05', 'Google Workspace Email', -120.0, 'Software'),
        ('2026-05-10', 'Vendor Stark Industries Materials', -4500.0, 'COGS'),
        ('2026-05-15', 'Monthly Payroll', -8000.0, 'Payroll'),
        ('2026-05-18', 'Office Supplies Depot', -350.0, 'Office Expense'),
        ('2026-05-20', 'Client Wayne Enterprises Revenue Deposit', 15000.0, 'Revenue'),
        ('2026-05-22', 'Electric Utility Bill', -450.0, 'Utilities'),
        ('2026-05-25', 'Facebook Ad Campaigns', -1500.0, 'Marketing'),
        ('2026-05-28', 'Director Cash Withdrawal (Unexplained)', -5000.0, 'Anomaly'),
        
        # June 2026
        ('2026-06-01', 'Client ACME Corp Revenue Deposit', 12500.0, 'Revenue'),
        ('2026-06-02', 'Office Rent Payment', -3200.0, 'Rent'),
        ('2026-06-05', 'AWS Cloud Services Hosting', -850.0, 'Software'),
        ('2026-06-05', 'Google Workspace Email', -120.0, 'Software'),
        ('2026-06-06', 'AWS Cloud Services Hosting (Duplicate)', -850.0, 'Software'),
        ('2026-06-10', 'Vendor Stark Industries Materials', -6000.0, 'COGS'),
        ('2026-06-15', 'Monthly Payroll', -8000.0, 'Payroll'),
        ('2026-06-18', 'Office Supplies Depot', -220.0, 'Office Expense'),
        ('2026-06-20', 'Client Wayne Enterprises Revenue Deposit', 15000.0, 'Revenue'),
        ('2026-06-22', 'Electric Utility Bill', -900.0, 'Utilities'),
        ('2026-06-25', 'Facebook Ad Campaigns', -3000.0, 'Marketing'),
        
        # July 2026
        ('2026-07-01', 'Client ACME Corp Revenue Deposit', 12500.0, 'Revenue'),
        ('2026-07-02', 'Office Rent Payment', -3200.0, 'Rent'),
        ('2026-07-05', 'AWS Cloud Services Hosting', -850.0, 'Software'),
        ('2026-07-05', 'Google Workspace Email', -120.0, 'Software'),
        ('2026-07-10', 'Vendor Stark Industries Materials', -7500.0, 'COGS'),
        ('2026-07-15', 'Monthly Payroll', -8000.0, 'Payroll'),
        ('2026-07-18', 'Office Supplies Depot', -180.0, 'Office Expense'),
        ('2026-07-22', 'Electric Utility Bill', -480.0, 'Utilities'),
        ('2026-07-25', 'Facebook Ad Campaigns', -1500.0, 'Marketing'),
    ]
    
    for dt, desc, amt, cat in raw_txs:
        balance += amt
        transactions.append([dt, desc, amt, round(balance, 2), cat])
        
    with open(bank_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(bank_headers)
        writer.writerows(transactions)
    print(f"Generated {bank_file}")

    # 2. Generate open_invoices.csv (Receivables with status and due dates)
    invoice_file = 'mock_data/open_invoices.csv'
    invoice_headers = ['InvoiceID', 'CustomerName', 'Amount', 'IssueDate', 'DueDate', 'Status']
    invoices = [
        ('INV-2026-001', 'ACME Corp', 12500.0, '2026-04-15', '2026-05-15', 'Paid'),
        ('INV-2026-002', 'Wayne Enterprises', 15000.0, '2026-04-20', '2026-05-20', 'Paid'),
        ('INV-2026-003', 'ACME Corp', 12500.0, '2026-05-15', '2026-06-15', 'Paid'),
        ('INV-2026-004', 'Wayne Enterprises', 15000.0, '2026-05-20', '2026-06-20', 'Paid'),
        ('INV-2026-005', 'ACME Corp', 12500.0, '2026-06-15', '2026-07-15', 'Paid'),
        ('INV-2026-006', 'Wayne Enterprises', 15000.0, '2026-06-20', '2026-07-20', 'Unpaid'),
        ('INV-2026-007', 'LexCorp', 5000.0, '2026-06-25', '2026-07-25', 'Unpaid'),
        ('INV-2026-008', 'ACME Corp', 12500.0, '2026-07-15', '2026-08-15', 'Unpaid'),
        ('INV-2026-009', 'Stark Industries', 8000.0, '2026-07-18', '2026-08-18', 'Unpaid'),
    ]
    with open(invoice_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(invoice_headers)
        writer.writerows(invoices)
    print(f"Generated {invoice_file}")

    # 3. Generate profit_loss.xlsx
    pl_file = 'mock_data/profit_loss.xlsx'
    pl_data = {
        'Line Item': [
            'Revenue', '  ACME Corp', '  Wayne Enterprises', 'Total Revenue',
            'Cost of Goods Sold (COGS)', 'Gross Profit',
            'Operating Expenses', '  Salaries & Payroll', '  Rent', '  Marketing & Ads',
            '  Software & Cloud Hosting', '  Utilities', '  Office Expenses',
            'Total Operating Expenses', 'Net Operating Profit', 'Net Margin (%)'
        ],
        'May 2026': [
            '', 12500.0, 15000.0, 27500.0, -4500.0, 23000.0,
            '', -8000.0, -3200.0, -1500.0, -970.0, -450.0, -350.0, -14470.0, 8530.0, 31.0
        ],
        'June 2026': [
            '', 12500.0, 15000.0, 27500.0, -6000.0, 21500.0,
            '', -8000.0, -3200.0, -3000.0, -1820.0, -900.0, -220.0, -17140.0, 4360.0, 15.8
        ],
        'July 2026': [
            '', 12500.0, 15000.0, 27500.0, -7500.0, 20000.0,
            '', -8000.0, -3200.0, -1500.0, -970.0, -480.0, -180.0, -14330.0, 5670.0, 20.6
        ]
    }
    df_pl = pd.DataFrame(pl_data)
    with pd.ExcelWriter(pl_file, engine='openpyxl') as writer:
        df_pl.to_excel(writer, index=False, sheet_name='P&L Statement')
    print(f"Generated {pl_file}")

    # 4. Generate balance_sheet.xlsx (For Liquidity/Solvency ratios)
    bs_file = 'mock_data/balance_sheet.xlsx'
    bs_data = {
        'Account': [
            'ASSETS', 'Current Assets', '  Cash and Cash Equivalents', 
            '  Accounts Receivable', '  Inventory', 'Total Current Assets',
            'Non-Current Assets', '  Property, Plant & Equipment', 'Total Non-Current Assets',
            'TOTAL ASSETS',
            'LIABILITIES & EQUITY', 'Current Liabilities', '  Accounts Payable',
            '  Accrued Expenses', 'Total Current Liabilities',
            'Long-Term Liabilities', '  Bank Loan', 'Total Long-Term Liabilities',
            'TOTAL LIABILITIES', 'Shareholders Equity', '  Retained Earnings', 'TOTAL LIABILITIES & EQUITY'
        ],
        'As of May 31, 2026': [
            '', '', 53530.0, 12500.0, 8000.0, 74030.0,
            '', 45000.0, 45000.0, 119030.0,
            '', '', 3400.0, 1200.0, 4600.0,
            '', 20000.0, 20000.0, 24600.0, '', 94430.0, 119030.0
        ],
        'As of June 30, 2026': [
            '', '', 57890.0, 15000.0, 12000.0, 84890.0,
            '', 44000.0, 44000.0, 128890.0,
            '', '', 5500.0, 1500.0, 7000.0,
            '', 15000.0, 15000.0, 22000.0, '', 106890.0, 128890.0
        ],
        'As of July 24, 2026': [
            '', '', 48560.0, 40500.0, 15000.0, 104060.0,
            '', 43000.0, 43000.0, 147060.0,
            '', '', 8200.0, 1800.0, 10000.0,
            '', 25000.0, 25000.0, 35000.0, '', 112060.0, 147060.0
        ]
    }
    df_bs = pd.DataFrame(bs_data)
    with pd.ExcelWriter(bs_file, engine='openpyxl') as writer:
        df_bs.to_excel(writer, index=False, sheet_name='Balance Sheet')
    print(f"Generated {bs_file}")

    # 5. Generate cash_flow.xlsx
    cf_file = 'mock_data/cash_flow.xlsx'
    cf_data = {
        'Activity': [
            'Cash Flow from Operating Activities',
            '  Net income',
            '  Adjustments for non-cash items',
            '  Changes in working capital',
            'Net Cash from Operating Activities',
            'Cash Flow from Investing Activities',
            '  Purchase of equipment',
            'Net Cash from Investing Activities',
            'Cash Flow from Financing Activities',
            '  Proceeds from bank loans',
            '  Repayments of bank loans',
            'Net Cash from Financing Activities',
            'Net Increase / Decrease in Cash',
            'Cash at Beginning of Period',
            'Cash at End of Period'
        ],
        'May 2026': [
            '', 8530.0, 1000.0, 1000.0, 10530.0,
            '', -2000.0, -2000.0,
            '', 0.0, -5000.0, -5000.0,
            3530.0, 50000.0, 53530.0
        ],
        'June 2026': [
            '', 4360.0, 1000.0, 4000.0, 9360.0,
            '', 0.0, 0.0,
            '', 0.0, -5000.0, -5000.0,
            4360.0, 53530.0, 57890.0
        ],
        'July 2026': [
            '', 5670.0, 1000.0, -26000.0, -19330.0,
            '', -5000.0, -5000.0,
            '', 15000.0, 0.0, 15000.0,
            -9330.0, 57890.0, 48560.0
        ]
    }
    df_cf = pd.DataFrame(cf_data)
    with pd.ExcelWriter(cf_file, engine='openpyxl') as writer:
        df_cf.to_excel(writer, index=False, sheet_name='Cash Flow')
    print(f"Generated {cf_file}")

if __name__ == '__main__':
    create_mock_data()
