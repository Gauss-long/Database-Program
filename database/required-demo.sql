USE competition_project;

-- 1. 单表查询：查询进行中的项目
SELECT ProjectName, StartDate, EndDate
FROM Project
WHERE ProjectStatus = '进行中';

-- 2. 多表连接查询：查询项目、团队和指导教师
SELECT p.ProjectName, t.TeamName, u.UserName AS TeacherName
FROM Project p
JOIN Team t ON p.TeamID = t.TeamID
JOIN Teacher te ON p.TeacherID = te.UserID
JOIN Users u ON te.UserID = u.UserID;

-- 3. 嵌套查询：查询报名参加南开大学数据库设计竞赛的团队
SELECT TeamName
FROM Team
WHERE TeamID IN (
    SELECT TeamID
    FROM Registration
    WHERE CompetitionID IN (
        SELECT CompetitionID
        FROM Competition
        WHERE CompetitionName = '南开大学数据库设计竞赛'
    )
);

-- 4. EXISTS 查询：查询有成果记录的项目
SELECT p.ProjectName
FROM Project p
WHERE EXISTS (
    SELECT 1
    FROM Achievement a
    WHERE a.ProjectID = p.ProjectID
);

-- 5. 聚合查询：统计每个项目的经费总额
SELECT ProjectID, SUM(Amount) AS TotalFunding
FROM Funding
GROUP BY ProjectID;

-- 6. 事务删除演示：删除项目及其关联记录
START TRANSACTION;
DELETE FROM Achievement WHERE ProjectID = 2;
DELETE FROM Funding WHERE ProjectID = 2;
DELETE FROM Competition_Project WHERE ProjectID = 2;
DELETE FROM Research_Project WHERE ProjectID = 2;
DELETE FROM Project WHERE ProjectID = 2;
COMMIT;

-- 7. 触发器添加演示：向报名表插入数据，触发器会自动检查条件
INSERT INTO Registration (TeamID, CompetitionID, RegisterTime, Status)
VALUES (2, 1, CURDATE(), '已报名');

-- 8. 存储过程更新演示：根据成果和经费情况更新项目状态
CALL sp_UpdateProjectStatus(1);
SELECT ProjectID, ProjectName, ProjectStatus
FROM Project
WHERE ProjectID = 1;

-- 8.1 存储过程失败演示：项目不存在时，存储过程主动报错
CALL sp_UpdateProjectStatus(999);

-- 9. 视图查询演示：查询项目综合信息
SELECT *
FROM v_ProjectSummary;
