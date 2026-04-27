import requests
from bs4 import BeautifulSoup

r = requests.get("https://afx.kwayisi.org/nse/")
soup = BeautifulSoup(r.text, "html.parser")

tables = soup.find_all("table")
print("Number of tables found:", len(tables))

for i, table in enumerate(tables):
    print(f"\nTable {i}: class={table.get('class')}, id={table.get('id')}")
    rows = table.find_all("tr")
    print(f"  Rows: {len(rows)}")
    if rows:
        first_row = rows[0]
        cells = first_row.find_all(["th", "td"])
        for j, cell in enumerate(cells):
            print(f"    Cell {j}: '{cell.text.strip()}'")
        
        # Print first 3 data rows
        for row in rows[1:4]:
            cells = row.find_all("td")
            values = [c.text.strip() for c in cells]
            print(f"  Data: {values}")