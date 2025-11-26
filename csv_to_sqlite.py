#!/usr/bin/env python3
"""Convert `table.csv` into `ncaawlax.db` with a single table `ncaa_finals`.

This script prefers pandas but falls back to the csv module if pandas is not available.
It attempts to parse year, champion, runner-up, score, and location, and computes
goal differential and total goals when possible.
"""
import re
import sqlite3
import os

try:
    import pandas as pd
except Exception:
    pd = None


def parse_score(s):
    if not isinstance(s, str):
        return None, None
    # match '12-8', '12–8', '12—8' and allow trailing '(OT)' etc
    m = re.search(r"(\d+)\s*[–—-]\s*(\d+)", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    # sometimes scores may be like 'Canceled' or empty
    return None, None


def clean_team(t):
    if not isinstance(t, str):
        return None
    t = t.strip()
    return t if t else None


def main():
    csv_path = os.path.join(os.path.dirname(__file__), 'table.csv')
    out_db = os.path.join(os.path.dirname(__file__), 'ncaawlax.db')

    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        return

    # Load CSV into a DataFrame-like structure (list of lists fallback)
    if pd is not None:
        try:
            df = pd.read_csv(csv_path, header=None, dtype=str)
        except Exception:
            df = None
    else:
        df = None

    if df is None:
        # fallback to csv reader
        import csv
        rows = []
        with open(csv_path, newline='', encoding='utf-8') as f:
            for r in csv.reader(f):
                rows.append(r)
        # convert to a simple list-of-lists DataFrame-like object
        import pandas as _pd
        df = _pd.DataFrame(rows)

    records = []
    for _, row in df.iterrows():
        first = row.iloc[0]
        if not isinstance(first, str):
            continue
        m = re.match(r'^\s*(\d{4})', first)
        if not m:
            continue
        year = int(m.group(1))
        site = row.iloc[1] if len(row) > 1 else ''
        stadium = row.iloc[2] if len(row) > 2 else ''
        champion = row.iloc[3] if len(row) > 3 else None
        score = row.iloc[4] if len(row) > 4 else None
        runner = row.iloc[5] if len(row) > 5 else None
        location = (site or '') + (f' | {stadium}' if stadium else '')
        champion = clean_team(champion)
        runner = clean_team(runner)
        champ_goals, runner_goals = parse_score(score)
        goal_diff = None
        total_goals = None
        if champ_goals is not None and runner_goals is not None:
            goal_diff = champ_goals - runner_goals
            total_goals = champ_goals + runner_goals

        records.append({
            'year': year,
            'champion': champion,
            'runner_up': runner,
            'champion_goals': champ_goals,
            'runnerup_goals': runner_goals,
            'goal_diff': goal_diff,
            'total_goals': total_goals,
            'location': location,
        })

    # write to sqlite
    conn = sqlite3.connect(out_db)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS ncaa_finals (
        id INTEGER PRIMARY KEY,
        year INTEGER,
        champion TEXT,
        runner_up TEXT,
        champion_goals INTEGER,
        runnerup_goals INTEGER,
        goal_diff INTEGER,
        total_goals INTEGER,
        location TEXT
    );''')
    cur.execute('DELETE FROM ncaa_finals;')
    insert_sql = '''INSERT INTO ncaa_finals (year, champion, runner_up, champion_goals, runnerup_goals, goal_diff, total_goals, location)
    VALUES (?,?,?,?,?,?,?,?);'''
    for r in records:
        cur.execute(insert_sql, (r['year'], r['champion'], r['runner_up'], r['champion_goals'], r['runnerup_goals'], r['goal_diff'], r['total_goals'], r['location']))
    conn.commit()
    conn.close()
    print(f"Wrote {len(records)} rows to {out_db}")


if __name__ == '__main__':
    main()
