#!/usr/bin/env python3
"""Generate analytics CSV and JSON from `ncaawlax.db`.

Produces `analytics.csv` (two columns: metric, data_json) and
`analytics.json` (structured object with separate arrays for each metric).
"""
import sqlite3
import json
import os
import csv


DB = os.path.join(os.path.dirname(__file__), 'ncaawlax.db')


def run_query(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall()
    return [dict(zip(cols, r)) for r in rows]


def main():
    if not os.path.exists(DB):
        print('Database not found:', DB)
        return

    conn = sqlite3.connect(DB)

    # 1) titles_per_team
    q1 = '''
    SELECT
        CASE
            WHEN instr(champion, '(') > 0
            THEN trim(substr(champion, 1, instr(champion, '(') - 1))
            ELSE trim(champion)
        END AS champion_name,
        COUNT(*) AS titles
    FROM ncaa_finals
    GROUP BY champion_name
    ORDER BY titles DESC;
    '''
    titles_per_team = run_query(conn, q1)

    # 2) avg_margin_per_champion
    q2 = '''
    SELECT
        CASE
            WHEN instr(champion, '(') > 0
            THEN trim(substr(champion, 1, instr(champion, '(') - 1))
            ELSE trim(champion)
        END AS champion_name,
        COUNT(*) AS titles,
        AVG(goal_diff) AS avg_margin
    FROM ncaa_finals
    GROUP BY champion_name
    ORDER BY avg_margin DESC;
    '''
    avg_margin_per_champion = run_query(conn, q2)

    # 3) margin_over_time (include location and individual goals so tooltips can show scores)
    q3 = '''
    SELECT year, champion_goals, runnerup_goals, goal_diff, total_goals, location, champion, runner_up
    FROM ncaa_finals
    ORDER BY year;
    '''
    margin_over_time = run_query(conn, q3)

    # 4) highest_scoring_games (keep all columns)
    q4 = '''
    SELECT * FROM ncaa_finals
    ORDER BY total_goals DESC
    LIMIT 10;
    '''
    highest_scoring_games = run_query(conn, q4)

    # 5) decade_closeness
    q5 = '''
    SELECT (year/10)*10 AS decade, AVG(goal_diff) AS avg_margin
    FROM ncaa_finals
    GROUP BY decade
    ORDER BY decade;
    '''
    decade_closeness = run_query(conn, q5)

    conn.close()

    analytics = {
        'titles_per_team': titles_per_team,
        'avg_margin_per_champion': avg_margin_per_champion,
        'margin_over_time': margin_over_time,
        'highest_scoring_games': highest_scoring_games,
        'decade_closeness': decade_closeness,
    }

    # Write JSON
    out_json = os.path.join(os.path.dirname(__file__), 'analytics.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(analytics, f, ensure_ascii=False, indent=2)

    # Write CSV where each row is metric + JSON string of that metric's data
    out_csv = os.path.join(os.path.dirname(__file__), 'analytics.csv')
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'data_json'])
        for k, v in analytics.items():
            writer.writerow([k, json.dumps(v, ensure_ascii=False)])

    print('Wrote', out_csv)
    print('Wrote', out_json)


if __name__ == '__main__':
    main()
