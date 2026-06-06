# 高校竞赛项目管理系统

本项目用于数据库工程作业，采用 B/S 架构。系统围绕高校竞赛、科研项目、团队、学生、教师、成果和经费信息进行管理，重点体现 MySQL 数据库中的事务、触发器、存储过程和视图查询。

## 技术栈

- 前端：HTML、CSS、JavaScript
- 后端：Python 3.9.19、FastAPI
- 数据库：MySQL 8.0.46
- 数据库驱动：PyMySQL
- 数据库客户端：Navicat

## 系统功能

当前系统实现了一个最小但完整的业务流程：

1. 人员管理
   - 新增学生
   - 查看学生
   - 新增教师
   - 查看教师
2. 团队管理
   - 创建团队
   - 添加团队成员
   - 查看团队成员
3. 项目申报
   - 团队报名竞赛并创建竞赛项目
   - 团队申报科研项目
4. 项目管理
   - 查看项目综合信息
   - 修改项目状态
   - 删除项目
5. 项目统计
   - 通过视图展示项目、团队、教师、团队人数、成果数量和经费总额

## 数据库作业要求对应

| 作业要求 | 项目实现 |
| --- | --- |
| 含有事务应用的删除操作 | 删除项目时，同时删除成果、经费、竞赛项目扩展和科研项目扩展记录 |
| 触发器控制下的添加操作 | 团队报名竞赛时，`Registration` 表触发器检查报名数据 |
| 存储过程控制下的更新操作 | 项目管理页面调用存储过程更新项目状态 |
| 含有视图的查询操作 | `v_ProjectSummary` 视图查询项目综合统计信息 |

## 目录结构

```text
Database-Program/
|-- backend/
|   |-- requirements.txt
|   |-- .env.example
|   |-- src/
|       |-- main.py
|       |-- database.py
|       |-- config/
|       |   |-- settings.py
|       |-- routers/
|           |-- auth.py
|           |-- health.py
|           |-- lookups.py
|           |-- people.py
|           |-- projects.py
|           |-- registrations.py
|           |-- statistics.py
|           |-- teams.py
|-- database/
|   |-- init.sql
|   |-- required-demo.sql
|-- frontend/
|   |-- login.html
|   |-- index.html
|-- PROJECT_STRUCTURE.md
|-- README.md
```

## MySQL 启动

本项目使用 MySQL 8.0.46 免安装版，路径为：

```text
C:\Users\86915\Desktop\mysql-8.0.46-winx64
```

启动 MySQL：

```powershell
cd C:\Users\86915\Desktop\mysql-8.0.46-winx64
.\bin\mysqld.exe --console --basedir="C:\Users\86915\Desktop\mysql-8.0.46-winx64" --datadir="C:\Users\86915\Desktop\mysql-8.0.46-winx64\data"
```

看到类似 `ready for connections` 后表示 MySQL 已启动。该 PowerShell 窗口需要保持打开，关闭窗口后 MySQL 会停止运行。

测试 MySQL 登录：

```powershell
cd C:\Users\86915\Desktop\mysql-8.0.46-winx64
.\bin\mysql.exe -u root -p
```

默认密码：

```text
123456
```

## 数据库初始化

打开 Navicat，连接本机 MySQL：

```text
主机：localhost
端口：3306
用户名：root
密码：123456
```

连接成功后，执行：

```text
database/init.sql
```

该脚本会完成：

- 创建 `competition_project` 数据库
- 创建数据表
- 创建主键和外键
- 创建触发器
- 创建存储过程
- 创建视图
- 插入演示数据

如果修改了 `init.sql`，需要在 Navicat 中重新执行该脚本。

## 后端启动

另开一个 PowerShell，进入后端目录：

```powershell
cd C:\Users\86915\Desktop\数据库\Database-Program\backend
```

首次运行时创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

启动后端：

```powershell
uvicorn src.main:app --reload
```

浏览器测试：

```text
http://127.0.0.1:8000/api/health
```

后端默认连接串：

```text
mysql+pymysql://root:******@localhost:3306/competition_project?charset=utf8mb4
```

实际连接参数在：

```text
backend/.env
```

如果要修改数据库端口，修改：

```env
DB_PORT=3306
```

修改后重启 FastAPI 后端。如果 MySQL 服务本身也更改了监听端口，还需要修改 MySQL 配置并重启 MySQL。

## 前端打开

后端启动后，直接用浏览器打开：

```text
C:\Users\86915\Desktop\数据库\Database-Program\frontend\login.html
```

默认账号：

```text
用户名：admin
密码：123456
```

也可以在登录页面切换到注册，新建账号后进入系统。

## 答辩重点代码

| 内容 | 文件 |
| --- | --- |
| 数据库连接配置 | `backend/src/config/settings.py` |
| MySQL 连接代码 | `backend/src/database.py` |
| 事务删除项目 | `backend/src/routers/projects.py` |
| 触发器定义 | `database/init.sql` |
| 存储过程定义 | `database/init.sql` |
| 视图定义 | `database/init.sql` |
| 视图查询接口 | `backend/src/routers/statistics.py` |
| 人员管理接口 | `backend/src/routers/people.py` |
| 团队管理接口 | `backend/src/routers/teams.py` |
| 前端登录页 | `frontend/login.html` |
| 前端主页面 | `frontend/index.html` |

## 演示流程

1. 启动 MySQL。
2. 在 Navicat 中执行 `database/init.sql`。
3. 启动 FastAPI 后端。
4. 打开 `frontend/login.html`。
5. 使用 `admin / 123456` 登录。
6. 在“人员管理”中查看或新增学生、教师。
7. 在“团队管理”中创建团队并添加成员。
8. 在“项目申报”中报名竞赛并创建竞赛项目，或申报科研项目。
9. 在“项目管理”中修改项目状态、删除项目并查看综合统计信息。

## 说明

`database/required-demo.sql` 不是系统运行必需文件，而是报告和答辩用的 SQL 演示脚本。它把单表查询、多表连接查询、嵌套查询、事务删除、触发器插入、存储过程调用和视图查询整理在一起，方便在 Navicat 中截图和讲解。
