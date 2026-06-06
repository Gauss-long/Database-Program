# 后端说明

后端使用 FastAPI 编写，连接 MySQL 数据库。当前接口围绕数据库工程作业的四类重点操作实现：

- 事务删除项目
- 触发器控制报名添加
- 存储过程更新项目状态
- 视图查询项目汇总

## 启动步骤

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn src.main:app --reload
```

启动前需要先安装 MySQL，并执行 `database/init.sql` 初始化数据库。

