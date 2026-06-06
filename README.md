# 高校竞赛项目管理系统

本项目用于数据库工程作业，采用 B/S 架构。

技术栈：

- 前端：Vue 3、Vite、Element Plus、ECharts
- 后端：FastAPI
- 数据库：MySQL

## MySQL 安装

当前电脑只有 Navicat 时，还需要单独安装 MySQL Server。Navicat 是数据库客户端，只负责连接和管理数据库，不能替代数据库服务。

Windows 下安装步骤：

1. 下载并安装 MySQL Installer for Windows。
2. 安装类型选择 Developer Default 或 Server only。
3. 配置 MySQL Server，端口保持 `3306`。
4. 设置 root 密码，例如 `123456`，后续需要写入后端 `.env`。
5. 安装完成后确认 MySQL 服务处于 Running 状态。
6. 打开 Navicat，新建 MySQL 连接：
   - 主机：`localhost`
   - 端口：`3306`
   - 用户名：`root`
   - 密码：安装时设置的密码
7. 在 Navicat 中执行 `database/init.sql` 初始化数据库。

## 后端启动

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn src.main:app --reload
```

后端默认连接：

```text
mysql+pymysql://root:******@localhost:3306/competition_project?charset=utf8mb4
```

## 前端打开

后端启动后，直接用浏览器打开：

```text
frontend/login.html
```

默认账号：

```text
用户名：admin
密码：123456
```

也可以在登录框切换到注册，新建一个账号后再登录。
