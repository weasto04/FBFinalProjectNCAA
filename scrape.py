import requests
from bs4 import BeautifulSoup
import csv

url = "https://en.wikipedia.org/wiki/NCAA_Division_I_women%27s_lacrosse_tournament"
headers = {"User-Agent": "Mozilla/5.0 (compatible; simple-scraper/1.0)"}
response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table")
table = tables[1]
rows = table.find_all("tr")
csv_rows = []
for tr in rows:
	cells = tr.find_all(["th", "td"])
	csv_rows.append([cell.get_text(strip=True) for cell in cells])
with open("table.csv", "w", newline="", encoding="utf-8") as f:
	writer = csv.writer(f)
	writer.writerows(csv_rows)
print("Wrote", len(csv_rows), "rows to table.csv")
