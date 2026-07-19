PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO topics(name, category, status, priority) VALUES
    ('英语', 'core', 'active', 4),
    ('健身教练', 'core', 'active', 4),
    ('金融投资', 'core', 'inbox', 3),
    ('Python', 'core', 'active', 5),
    ('SQL', 'core', 'active', 5),
    ('Swift 与 Apple 平台', 'extended', 'maintenance', 3),
    ('AI Agent 与语音转录', 'extended', 'maintenance', 3);

DELETE FROM sessions WHERE source = 'demo';
DELETE FROM goals WHERE notes = 'demo';
DELETE FROM artifacts WHERE notes = 'demo';

INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-01', 25, 'input', '完成英语听力基线', 2, 'demo' FROM topics WHERE name = '英语';
INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-02', 45, 'project', '初始化学习记录 CLI', 3, 'demo' FROM topics WHERE name = 'Python';
INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-03', 40, 'practice', '完成基础聚合查询', 2, 'demo' FROM topics WHERE name = 'SQL';
INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-04', 50, 'practice', '完成高位下拉动作分析', 3, 'demo' FROM topics WHERE name = '健身教练';
INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-05', 30, 'review', '复盘养老金输入变量', 2, 'demo' FROM topics WHERE name = '金融投资';
INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-07', 55, 'project', '为导出功能增加测试', 4, 'demo' FROM topics WHERE name = 'Python';
INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-08', 35, 'practice', '完成 JOIN 查询', 3, 'demo' FROM topics WHERE name = 'SQL';
INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-09', 20, 'practice', '录制两分钟英语复述', 3, 'demo' FROM topics WHERE name = '英语';
INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-11', 60, 'project', '设计四周新手计划', 3, 'demo' FROM topics WHERE name = '健身教练';
INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
SELECT id, '2026-07-12', 45, 'test', '完成窗口函数练习', 3, 'demo' FROM topics WHERE name = 'SQL';

INSERT INTO goals(topic_id, title, target_date, status, success_criteria, notes)
SELECT id, '完成学习记录工具第一版', '2026-07-31', 'open', '测试通过并记录十次真实会话', 'demo'
FROM topics WHERE name = 'Python';
INSERT INTO goals(topic_id, title, target_date, status, success_criteria, notes)
SELECT id, '完成 SQL 基础练习', '2026-07-31', 'open', '完成前十个查询并解释验证方法', 'demo'
FROM topics WHERE name = 'SQL';
INSERT INTO artifacts(topic_id, title, artifact_type, location, completed_on, notes)
SELECT id, '英语听力基线', 'recording', 'local/demo-english-baseline.m4a', '2026-07-01', 'demo'
FROM topics WHERE name = '英语';
