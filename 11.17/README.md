# 最简图书管理系统

Python + FastAPI + SQLite + pytest 的课堂练习项目，只包含基础 CRUD、自动 OpenAPI 文档和必要测试。

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/books` | 查询全部图书 |
| GET | `/books/{id}` | 查询指定图书 |
| POST | `/books` | 添加图书 |
| PUT | `/books/{id}` | 修改图书 |
| DELETE | `/books/{id}` | 删除图书 |

- OpenAPI 文档：`http://127.0.0.1:8000/docs`
- OpenAPI JSON：`http://127.0.0.1:8000/openapi.json`
- SQLite 数据库文件：默认 `./books.db`，可通过环境变量 `DATABASE_PATH` 修改。

## 本地启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

不激活虚拟环境也可以直接运行：

```powershell
python -m uvicorn app.main:app --reload
```

## 快速验证

```powershell
curl http://127.0.0.1:8000/books
curl -X POST http://127.0.0.1:8000/books -H "Content-Type: application/json" -d "{\"title\":\"三体\",\"author\":\"刘慈欣\",\"year\":2006}"
curl http://127.0.0.1:8000/books/1
curl -X PUT http://127.0.0.1:8000/books/1 -H "Content-Type: application/json" -d "{\"title\":\"三体Ⅱ\",\"year\":2008}"
curl -X DELETE http://127.0.0.1:8000/books/1
```

测试：

```powershell
pytest -q
```

当前结果：`7 passed`。测试使用独立临时 SQLite 文件，不会污染本地 `books.db`。

## Git 变更记录

仓库已预置两次提交：

```bash
git log --oneline
git diff HEAD~1 HEAD
git diff HEAD~1 HEAD -- app/main.py
git show --stat HEAD
```

第二次提交是 CRUD 功能变更。项目根目录的 `crud_changes.diff` 也保存了同一份标准 unified diff，可用于课堂展示：

```bash
git apply --stat crud_changes.diff
```

如需从零重建相同历史：

```bash
git init
git add .
git commit -m "chore: init project skeleton"
# 应用 CRUD 代码后
git add .
git commit -m "feat: add book CRUD APIs and tests"
```

## 公网部署

### 方案 A：Render

1. 将项目推送到 GitHub/GitLab。
2. 在 Render 选择 **Blueprint**，仓库中的 `render.yaml` 会自动创建服务。
3. 部署完成后访问 Render 提供的公网域名和 `/docs`。

### 方案 B：Fly.io

先修改 `fly.toml` 中的 `app` 为全局唯一名称，然后执行：

```bash
fly volumes create books_data --region nrt --size 1
fly deploy
```

### 方案 C：任意支持 Docker 的平台

项目包含 `Dockerfile`，平台会自动识别；需要设置容器监听端口 `8000`，并持久化 `/data` 目录。

本机模拟部署：

```bash
docker compose up --build -d
curl http://127.0.0.1:8000/docs
```

### 方案 D：支持 Python 的 PaaS

使用 `Procfile` 与 `runtime.txt` 即可。`DATABASE_PATH` 建议指向平台提供的可写持久目录。

> SQLite 适合随堂演示。多实例、高并发的正式生产环境建议使用平台提供的 PostgreSQL/MySQL，并把数据库地址改为环境变量。
