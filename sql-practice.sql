-- SQLite 练习。先运行：
-- python3 learning_tracker.py init
-- python3 learning_tracker.py seed
-- sqlite3 learns.db < sql-practice.sql

.headers on
.mode column

-- 1. 全部主题。
SELECT name, category, status, priority FROM topics ORDER BY priority DESC, name;

-- 2. 每个主题的次数和分钟数。
SELECT t.name, COUNT(s.id) AS session_count, COALESCE(SUM(s.minutes), 0) AS total_minutes
FROM topics t LEFT JOIN sessions s ON s.topic_id = t.id
GROUP BY t.id, t.name ORDER BY total_minutes DESC, t.name;

-- 3. 每种学习方式的投入。
SELECT kind, COUNT(*) AS sessions, SUM(minutes) AS total_minutes
FROM sessions GROUP BY kind ORDER BY total_minutes DESC;

-- 4. 平均信心低于 3 的主题。
SELECT t.name, ROUND(AVG(s.confidence), 2) AS avg_confidence
FROM topics t JOIN sessions s ON s.topic_id = t.id
WHERE s.confidence IS NOT NULL
GROUP BY t.id, t.name HAVING AVG(s.confidence) < 3
ORDER BY avg_confidence;

-- 5. 每日总分钟数。
SELECT session_date, SUM(minutes) AS total_minutes
FROM sessions GROUP BY session_date ORDER BY session_date;

-- 6. 每个主题最近一次学习日期。
SELECT t.name, MAX(s.session_date) AS last_session_date
FROM topics t LEFT JOIN sessions s ON s.topic_id = t.id
GROUP BY t.id, t.name ORDER BY last_session_date DESC;

-- 7. 开放目标及主题。
SELECT t.name AS topic, g.title, g.target_date, g.success_criteria
FROM goals g JOIN topics t ON t.id = g.topic_id
WHERE g.status = 'open' ORDER BY g.target_date, t.name;

-- 8. 有学习会话但没有成果记录的主题。
SELECT DISTINCT t.name
FROM topics t JOIN sessions s ON s.topic_id = t.id
LEFT JOIN artifacts a ON a.topic_id = t.id
WHERE a.id IS NULL ORDER BY t.name;

-- 9. 按自然周汇总。
SELECT strftime('%Y-W%W', session_date) AS year_week,
       SUM(minutes) AS total_minutes, COUNT(*) AS session_count
FROM sessions GROUP BY year_week ORDER BY year_week;

-- 10. 每个主题的累计分钟数。
SELECT t.name, s.session_date, s.minutes,
       SUM(s.minutes) OVER (PARTITION BY s.topic_id ORDER BY s.session_date, s.id) AS running_minutes
FROM sessions s JOIN topics t ON t.id = s.topic_id
ORDER BY t.name, s.session_date, s.id;

-- 11. 按总投入排名。
WITH topic_totals AS (
    SELECT topic_id, SUM(minutes) AS total_minutes FROM sessions GROUP BY topic_id
)
SELECT t.name, tt.total_minutes,
       DENSE_RANK() OVER (ORDER BY tt.total_minutes DESC) AS effort_rank
FROM topic_totals tt JOIN topics t ON t.id = tt.topic_id
ORDER BY effort_rank, t.name;

-- 12. 同一主题相邻学习间隔。
WITH ordered AS (
    SELECT topic_id, session_date,
           LAG(session_date) OVER (PARTITION BY topic_id ORDER BY session_date, id) AS previous_date
    FROM sessions
)
SELECT t.name, o.session_date, o.previous_date,
       CAST(julianday(o.session_date) - julianday(o.previous_date) AS INTEGER) AS gap_days
FROM ordered o JOIN topics t ON t.id = o.topic_id
WHERE o.previous_date IS NOT NULL
ORDER BY t.name, o.session_date;

-- 13. 主动学习和输入/复盘的平均信心。
SELECT CASE WHEN kind IN ('project', 'practice', 'test') THEN 'active'
            ELSE 'passive_or_review' END AS learning_mode,
       ROUND(AVG(confidence), 2) AS avg_confidence,
       SUM(minutes) AS total_minutes
FROM sessions WHERE confidence IS NOT NULL
GROUP BY learning_mode;

-- 14. 投入不少但信心仍低的主题。
WITH metrics AS (
    SELECT topic_id, SUM(minutes) AS total_minutes, AVG(confidence) AS avg_confidence
    FROM sessions WHERE confidence IS NOT NULL GROUP BY topic_id
)
SELECT t.name, m.total_minutes, ROUND(m.avg_confidence, 2) AS avg_confidence
FROM metrics m JOIN topics t ON t.id = m.topic_id
WHERE m.total_minutes >= 40 AND m.avg_confidence < 3
ORDER BY m.total_minutes DESC;

-- 15. 检查日期索引使用情况。
EXPLAIN QUERY PLAN
SELECT * FROM sessions
WHERE session_date BETWEEN '2026-07-01' AND '2026-07-31'
ORDER BY session_date;
