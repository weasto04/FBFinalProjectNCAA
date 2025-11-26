UPDATE ncaa_finals
SET goal_diff = champion_goals - runnerup_goals,
    total_goals = champion_goals + runnerup_goals;

-- 1) Championships per team
SELECT
    CASE 
        WHEN instr(champion, '(') > 0
        THEN substr(champion, 1, instr(champion, '(') - 1)
        ELSE champion
    END AS champion_name,
    COUNT(*) AS titles
FROM ncaa_finals
GROUP BY champion_name
ORDER BY titles DESC;

-- 2) Average margin per champion
SELECT
    CASE 
        WHEN instr(champion, '(') > 0
        THEN substr(champion, 1, instr(champion, '(') - 1)
        ELSE champion
    END AS champion_name,
    COUNT(*) AS titles,
    AVG(goal_diff) AS avg_margin
FROM ncaa_finals
GROUP BY champion_name
ORDER BY avg_margin DESC;

-- 3) Margin over time
SELECT 
    year, 
    goal_diff
FROM ncaa_finals
ORDER BY year;

-- 4) Highest scoring championship games
SELECT *
FROM ncaa_finals
ORDER BY total_goals DESC
LIMIT 10;

-- 5) Finals becoming closer by decade
SELECT 
    (year/10)*10 AS decade,
    AVG(goal_diff) AS avg_margin
FROM ncaa_finals
GROUP BY decade
ORDER BY decade;