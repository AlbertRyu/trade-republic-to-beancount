from models import Transaction
from datetime import datetime

## Hardcoded page structure for TradeRepublic Account Statements
COLUMNS = [
    (74,  100, 'datum'),
    (100, 160, 'typ'),
    (160, 368, 'beschreibung'),
    (368, 422, 'eingang'),
    (422, 475, 'ausgang'),
    (475, 9999, 'saldo'),
]


def parse_the_page(words):

    transaction_per_page = []
    
    rows = group_words_by_row(words)

    for row in rows:
        t = parse_row(row)
        transaction_per_page.append(t)

    return transaction_per_page


def group_words_by_row(words, tolerance=20):
    """group the words with similar top values as one row"""
    rows = []
    
    for word in sorted(words, key=lambda w: w['top']):
        if not (word['top'] > 159 and word['top'] < 750): # Hardcoded limit for the middle of the page.
            continue

        # Check that if the word belongs to an existing row.
        placed = False
        for row in rows:
            row_top = row[0]['top']
            if abs(word['top'] - row_top) <= tolerance:
                row.append(word)
                placed = True
                break
        
        # If not, create a new row.
        if not placed:
            rows.append([word])
    
    return rows  # List[List[word]]


def get_column(x0):
    for start, end, name in COLUMNS:
        if start <= x0 < end:
            return name
    return None


def parse_row(row_words):
    """one row of word → one Transaction."""
    # columns
    columns = {'datum': [], 'typ': [], 'beschreibung': [], 
               'eingang': [], 'ausgang': [], 'saldo': []}
    
    for word in row_words:
        col = get_column(word['x0'])
        if col:
            columns[col].append(word['text'])
    
    # if doesn't contains a datum, it's not a transaction.
    if not columns['datum']:
        return None
    
    # Join the words for different column
    date_str = " ".join(columns['datum'])      # "02 Jan. 2026"
    typ      = " ".join(columns['typ'])         # "Handel"
    desc     = " ".join(columns['beschreibung'])
    eingang  = " ".join(columns['eingang'])     # "100,00 €" or empty
    ausgang  = " ".join(columns['ausgang'])
    saldo  = " ".join(columns['saldo'])

    
    # Transform the date 
    date = datetime.strptime(date_str, "%d %b. %Y").date()
    
    # Parse the amount（German format, "1.234,56 €" → 1234.56）
    def parse_amount(s):
        if not s:
            return 0.0
        s = s.replace("€", "").replace(".", "").replace(",", ".").strip()
        return float(s)
    
    return Transaction(
        date=date,
        typ=typ,
        description=desc,
        amount_in=parse_amount(eingang),
        amount_out=parse_amount(ausgang),
        saldo=parse_amount(saldo)
    )
