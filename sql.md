# SQL

## 目标

能够从业务问题出发设计数据模型、写出正确查询、验证结果、解释性能，并识别数据口径和缺失值风险。

## 当前练习数据

`schema.sql` 定义主题、目标、学习会话、成果和复盘五张表；`seed.sql` 提供可重复加载的演示数据；`sql-practice.sql` 从基础聚合推进到 JOIN、CTE、窗口函数和间隔分析。

```bash
python3 learning_tracker.py init
python3 learning_tracker.py seed
sqlite3 learns.db
.read sql-practice.sql
```

## 学习路线

第一阶段掌握 SELECT、WHERE、ORDER BY、GROUP BY 和 HAVING；第二阶段掌握 JOIN、子查询和 CTE；第三阶段掌握窗口函数、日期处理和数据质量检查；第四阶段学习索引、查询计划、事务和模型取舍。

## 查询前检查

先写清指标定义、时间范围、去重规则、空值处理和预期数量级；运行后用小样本手算、总数对账、边界日期和反例验证。

## 阶段产出

完成 `sql-practice.sql` 全部问题，为至少三个查询写验证方法，用 `EXPLAIN QUERY PLAN` 比较索引前后，并生成一份学习投入与产出的分析报告。

## 下一步

先完成前六个查询并用自己的话解释结果，再选择一个查询故意制造重复 JOIN，观察错误并记录预防方法。
