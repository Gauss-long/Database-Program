CREATE DATABASE IF NOT EXISTS competition_project
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE competition_project;

SET FOREIGN_KEY_CHECKS = 0;
DROP VIEW IF EXISTS v_ProjectSummary;
DROP TRIGGER IF EXISTS trg_registration_before_insert;
DROP PROCEDURE IF EXISTS sp_UpdateProjectStatus;
DROP TABLE IF EXISTS Funding;
DROP TABLE IF EXISTS Achievement;
DROP TABLE IF EXISTS Research_Project;
DROP TABLE IF EXISTS Competition_Project;
DROP TABLE IF EXISTS Registration;
DROP TABLE IF EXISTS Project;
DROP TABLE IF EXISTS Competition;
DROP TABLE IF EXISTS Participate;
DROP TABLE IF EXISTS Team;
DROP TABLE IF EXISTS Teacher;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Account;
DROP TABLE IF EXISTS Users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE Account (
    AccountID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    PasswordHash VARCHAR(64) NOT NULL,
    Role VARCHAR(20) NOT NULL DEFAULT 'admin',
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    UserName VARCHAR(50) NOT NULL,
    Gender VARCHAR(10),
    Phone VARCHAR(20),
    Email VARCHAR(80)
);

CREATE TABLE Student (
    UserID INT PRIMARY KEY,
    StuNo VARCHAR(20) NOT NULL UNIQUE,
    College VARCHAR(50),
    Major VARCHAR(50),
    Grade VARCHAR(20),
    CONSTRAINT FK_Student_Users FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE Teacher (
    UserID INT PRIMARY KEY,
    TeacherNo VARCHAR(20) NOT NULL UNIQUE,
    College VARCHAR(50),
    Title VARCHAR(30),
    CONSTRAINT FK_Teacher_Users FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE Team (
    TeamID INT AUTO_INCREMENT PRIMARY KEY,
    TeamName VARCHAR(100) NOT NULL,
    CreateDate DATE,
    LeaderID INT,
    CONSTRAINT FK_Team_Student FOREIGN KEY (LeaderID) REFERENCES Student(UserID)
);

CREATE TABLE Participate (
    StudentID INT,
    TeamID INT,
    PRIMARY KEY (StudentID, TeamID),
    CONSTRAINT FK_Participate_Student FOREIGN KEY (StudentID) REFERENCES Student(UserID),
    CONSTRAINT FK_Participate_Team FOREIGN KEY (TeamID) REFERENCES Team(TeamID)
);

CREATE TABLE Competition (
    CompetitionID INT AUTO_INCREMENT PRIMARY KEY,
    CompetitionName VARCHAR(100) NOT NULL,
    Organizer VARCHAR(100),
    CompetitionLevel VARCHAR(30),
    CompetitionType VARCHAR(50),
    StartDate DATE,
    EndDate DATE
);

CREATE TABLE Project (
    ProjectID INT AUTO_INCREMENT PRIMARY KEY,
    ProjectName VARCHAR(100) NOT NULL,
    ProjectType VARCHAR(30),
    StartDate DATE,
    EndDate DATE,
    ProjectStatus VARCHAR(30),
    TeamID INT,
    TeacherID INT,
    CONSTRAINT FK_Project_Team FOREIGN KEY (TeamID) REFERENCES Team(TeamID),
    CONSTRAINT FK_Project_Teacher FOREIGN KEY (TeacherID) REFERENCES Teacher(UserID)
);

CREATE TABLE Competition_Project (
    ProjectID INT PRIMARY KEY,
    CompetitionID INT NOT NULL,
    CONSTRAINT FK_CompetitionProject_Project FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID),
    CONSTRAINT FK_CompetitionProject_Competition FOREIGN KEY (CompetitionID) REFERENCES Competition(CompetitionID)
);

CREATE TABLE Research_Project (
    ProjectID INT PRIMARY KEY,
    Source VARCHAR(100),
    ResearchLevel VARCHAR(30),
    CONSTRAINT FK_ResearchProject_Project FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID)
);

CREATE TABLE Registration (
    RegistrationID INT AUTO_INCREMENT PRIMARY KEY,
    TeamID INT NOT NULL,
    CompetitionID INT NOT NULL,
    RegisterTime DATE NOT NULL,
    Status VARCHAR(30) NOT NULL,
    CONSTRAINT UQ_Registration UNIQUE (TeamID, CompetitionID),
    CONSTRAINT FK_Registration_Team FOREIGN KEY (TeamID) REFERENCES Team(TeamID),
    CONSTRAINT FK_Registration_Competition FOREIGN KEY (CompetitionID) REFERENCES Competition(CompetitionID)
);

CREATE TABLE Achievement (
    AchievementID INT AUTO_INCREMENT PRIMARY KEY,
    AchievementName VARCHAR(100) NOT NULL,
    AchievementType VARCHAR(50),
    SubmitDate DATE,
    AwardInfo VARCHAR(100),
    ProjectID INT NOT NULL,
    CONSTRAINT FK_Achievement_Project FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID)
);

CREATE TABLE Funding (
    FundingID INT AUTO_INCREMENT PRIMARY KEY,
    Amount DECIMAL(10, 2) NOT NULL,
    Source VARCHAR(100),
    ReceivedDate DATE,
    Description VARCHAR(200),
    ProjectID INT NOT NULL,
    CONSTRAINT FK_Funding_Project FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID)
);

DELIMITER //

CREATE TRIGGER trg_registration_before_insert
BEFORE INSERT ON Registration
FOR EACH ROW
BEGIN
    IF NEW.Status IS NULL OR NEW.Status = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '报名状态不能为空';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM Participate WHERE TeamID = NEW.TeamID
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '报名团队必须至少包含一名成员';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM Competition
        WHERE CompetitionID = NEW.CompetitionID
          AND EndDate < CURDATE()
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '竞赛已结束，不能报名';
    END IF;
END//

CREATE PROCEDURE sp_UpdateProjectStatus(IN p_project_id INT, IN p_status VARCHAR(30))
BEGIN
    DECLARE v_achievement_count INT DEFAULT 0;
    DECLARE v_total_funding DECIMAL(10, 2) DEFAULT 0;

    IF NOT EXISTS (
        SELECT 1 FROM Project WHERE ProjectID = p_project_id
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '项目不存在，无法更新状态';
    END IF;

    IF p_status IS NOT NULL AND p_status <> '' THEN
        UPDATE Project
        SET ProjectStatus = p_status
        WHERE ProjectID = p_project_id;
    ELSE

        SELECT COUNT(*)
        INTO v_achievement_count
        FROM Achievement
        WHERE ProjectID = p_project_id;

        SELECT IFNULL(SUM(Amount), 0)
        INTO v_total_funding
        FROM Funding
        WHERE ProjectID = p_project_id;

        IF v_achievement_count > 0 AND v_total_funding > 0 THEN
            UPDATE Project
            SET ProjectStatus = '已完成'
            WHERE ProjectID = p_project_id;
        ELSE
            UPDATE Project
            SET ProjectStatus = '进行中'
            WHERE ProjectID = p_project_id;
        END IF;
    END IF;
END//

DELIMITER ;

CREATE VIEW v_ProjectSummary AS
SELECT
    p.ProjectID,
    p.ProjectName,
    p.ProjectType,
    p.ProjectStatus,
    t.TeamName,
    u.UserName AS TeacherName,
    COUNT(DISTINCT pa.StudentID) AS MemberCount,
    COUNT(DISTINCT a.AchievementID) AS AchievementCount,
    IFNULL(SUM(DISTINCT f.Amount), 0) AS TotalFunding
FROM Project p
LEFT JOIN Team t ON p.TeamID = t.TeamID
LEFT JOIN Participate pa ON t.TeamID = pa.TeamID
LEFT JOIN Teacher te ON p.TeacherID = te.UserID
LEFT JOIN Users u ON te.UserID = u.UserID
LEFT JOIN Achievement a ON p.ProjectID = a.ProjectID
LEFT JOIN Funding f ON p.ProjectID = f.ProjectID
GROUP BY
    p.ProjectID,
    p.ProjectName,
    p.ProjectType,
    p.ProjectStatus,
    t.TeamName,
    u.UserName;

INSERT INTO Users (UserID, UserName, Gender, Phone, Email) VALUES
(1, '郭鑫隆', '男', '13800000001', 'student1@nankai.edu.cn'),
(2, '李明', '男', '13800000002', 'student2@nankai.edu.cn'),
(3, '王雨', '女', '13800000003', 'student3@nankai.edu.cn'),
(4, '张老师', '男', '13900000001', 'teacher1@nankai.edu.cn'),
(5, '刘老师', '女', '13900000002', 'teacher2@nankai.edu.cn');

INSERT INTO Account (Username, PasswordHash, Role) VALUES
('admin', SHA2('123456', 256), 'admin');

INSERT INTO Student (UserID, StuNo, College, Major, Grade) VALUES
(1, '2311754', '软件学院', '软件工程', '2023'),
(2, '2311001', '计算机学院', '计算机科学与技术', '2023'),
(3, '2311002', '人工智能学院', '智能科学与技术', '2023');

INSERT INTO Teacher (UserID, TeacherNo, College, Title) VALUES
(4, 'T2024001', '软件学院', '副教授'),
(5, 'T2024002', '计算机学院', '讲师');

INSERT INTO Team (TeamID, TeamName, CreateDate, LeaderID) VALUES
(1, '数据库竞赛一队', '2026-03-01', 1),
(2, '智能项目组', '2026-03-10', 2);

INSERT INTO Participate (StudentID, TeamID) VALUES
(1, 1),
(2, 1),
(2, 2),
(3, 2);

INSERT INTO Competition (CompetitionID, CompetitionName, Organizer, CompetitionLevel, CompetitionType, StartDate, EndDate) VALUES
(1, '全国大学生电子设计竞赛', '教育部', '国家级', '学科竞赛', '2026-07-01', '2026-09-01'),
(2, '南开大学数据库设计竞赛', '南开大学', '校级', '课程竞赛', '2026-05-01', '2026-12-01');

INSERT INTO Project (ProjectID, ProjectName, ProjectType, StartDate, EndDate, ProjectStatus, TeamID, TeacherID) VALUES
(1, '高校竞赛项目管理系统', '竞赛项目', '2026-04-01', '2026-06-20', '进行中', 1, 4),
(2, '智能问答数据分析项目', '科研项目', '2026-04-10', '2026-10-30', '进行中', 2, 5);

INSERT INTO Competition_Project (ProjectID, CompetitionID) VALUES
(1, 2);

INSERT INTO Research_Project (ProjectID, Source, ResearchLevel) VALUES
(2, '学院科研训练计划', '院级');

INSERT INTO Registration (TeamID, CompetitionID, RegisterTime, Status) VALUES
(1, 2, '2026-05-10', '已报名');

INSERT INTO Achievement (AchievementName, AchievementType, SubmitDate, AwardInfo, ProjectID) VALUES
('系统原型', '软件作品', '2026-06-01', '待评审', 1),
('数据分析报告', '论文', '2026-06-05', '院级优秀', 2);

INSERT INTO Funding (Amount, Source, ReceivedDate, Description, ProjectID) VALUES
(3000.00, '学院支持', '2026-05-20', '服务器和资料费用', 1),
(5000.00, '科研训练经费', '2026-05-25', '数据采集和实验费用', 2);
