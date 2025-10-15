# medical-back（FastAPI 后端）

后端服务基于 FastAPI 和 SQLModel，提供用户、指标、住院档案、用药等基础数据模型与路由前缀管理，并在应用启动时自动创建数据库表。开发阶段与前端通过统一的 API 前缀 `"/api/v1"` 对接。

## 技术栈
- FastAPI + Uvicorn（Web 框架与开发服务器）
- SQLite（异步）+ SQLModel（ORM 模型）
- Loguru（结构化日志）
- ContextVars 中间件（请求跟踪：`request_id` / `trace_id`）
- APIRouter（模块化路由，统一前缀）

## 快速开始
1. 安装并准备 Conda 环境：
   - `conda create -y -n medical python=3.11`
   - `conda activate medical`
2. 安装依赖：
   - `pip install -r requirements.txt`
   - 或手动安装：`pip install fastapi uvicorn[standard] sqlmodel aiosqlite loguru pydantic-settings`

## 启动服务
- 开发模式（默认端口 `8000`）：`uvicorn main:app --reload`
- 如需与前端联调（示例端口 `8001`）：`uvicorn main:app --reload --port 8001`
- 健康检查：`GET /api/v1/health` 返回 `{"status":"ok"}`

## 数据库配置
- 默认数据库：`sqlite+aiosqlite:///./medical.sqlite3`
- 支持通过 `.env` 覆盖（字段名为 `SQLITE_URL`）：
  - 示例（Windows 绝对路径）：`SQLITE_URL=sqlite+aiosqlite:///c:/Users/TG/Desktop/medical/medical-back/medical.sqlite3`
- 应用启动时自动创建全部模型对应的表（`init_db → SQLModel.metadata.create_all`），无需手动迁移。

### 数据库设置在哪里？
- 代码入口：`app/core/settings.py` 的 `sqlite_url` 字段（可被环境变量 `.env` 中的 `SQLITE_URL` 覆盖）。
- 配置文件：在项目根目录（`medical-back/`）创建 `.env` 文件，填入数据库连接串（DSN）。

### 连接串（DSN）是什么意思？
- 这是告诉 ORM/驱动如何连接数据库的统一写法，包含“驱动前缀 + 地址/路径 +（可选）用户名密码”。
- 本项目默认使用 SQLite 的异步驱动：`sqlite+aiosqlite`。

### 路径、用户名、密码是多少？
- SQLite（默认）：
  - 路径：默认相对路径 `./medical.sqlite3`，位于 `medical-back/` 下；也可使用绝对路径。
  - 用户名/密码：SQLite 文件数据库不需要用户名与密码。
  - 示例 DSN：
    - 相对路径：`sqlite+aiosqlite:///./medical.sqlite3`
    - 绝对路径（Windows）：`sqlite+aiosqlite:///c:/Users/TG/Desktop/medical/medical-back/medical.sqlite3`
- PostgreSQL（如需切换）：
  - 需要安装驱动：`pip install asyncpg`
  - 示例 DSN：`postgresql+asyncpg://db_user:db_password@localhost:5432/medical`
  - 其中 `db_user`/`db_password` 为数据库的用户名/密码；`medical` 为库名。
- MySQL（如需切换）：
  - 需要安装驱动：`pip install aiomysql`
  - 示例 DSN：`mysql+aiomysql://db_user:db_password@localhost:3306/medical`

### `.env` 示例
```
# 使用 SQLite（默认）
SQLITE_URL=sqlite+aiosqlite:///./medical.sqlite3

# 切换到 PostgreSQL（需安装 asyncpg）
# SQLITE_URL=postgresql+asyncpg://medical_user:secret@127.0.0.1:5432/medical

# 切换到 MySQL（需安装 aiomysql）
# SQLITE_URL=mysql+aiomysql://medical_user:secret@127.0.0.1:3306/medical
```

### 其他注意事项
- Windows 下建议使用绝对路径并保留驱动前缀（例如 `sqlite+aiosqlite`）。
- 首次启动后端会自动建表；若后续更换数据库类型或字段结构，请先清理旧库或使用迁移工具。

### 种子数据（内置字典）
- 后端启动后会执行种子导入：
  - 指标定义来自 `app/data/indicators.json`
  - 分类定义来自 `app/data/category.json`
- 若 `category.json` 缺失，仍兼容旧版结构（从 `indicators.json` 的 `categories` 读取）。
- 导入幂等：重复启动只会更新字段，不会产生重复记录。

## 目录结构
- `app/core`：应用设置、日志、请求上下文中间件
- `app/utils`：请求上下文变量（`request_id`、`trace_id`）
- `app/api`：路由定义（统一前缀在 `settings.api_prefix`）
- `app/db`：异步引擎与会话、初始化数据库
- `app/models`：SQLModel 数据模型定义

## API 前缀约定
- 所有路由均在 `"/api/v1"` 下挂载，配置项位于 `app/core/settings.py` 的 `api_prefix`。

## 模型总览（简要说明）
- 用户：`User`
  - 基本字段：`username`、`password_hash`、`email`、`role`、`last_login`
  - 通用字段：`id`、`created_at`、`updated_at`、`deleted_at`
- 指标：`Indicator`
  - 基础字段：`name_cn`、`name_en`、`unit`、`reference_min`、`reference_max`、`is_builtin`、`loinc`
  - 关联关系：`categories`（多对多，联结表 `IndicatorCategoryLink`），`records`，`detail`
  - `loinc` 字段：LOINC编码（唯一，可选），用于标准化医疗指标编码，便于与外部系统对接。
  - 说明：分类成员来源于 `category.json` 的 `categories[*].members`（如使用），自动建立关联；未配置成员时可在后续接口或脚本中维护。
  - 指标基础信息（中文名、英文名、单位、分类、参考范围等），支持软删除与时间戳。
- 指标记录：`IndicatorRecord`
  - 指标值的逐次记录（测量时间、数值、单位、参考范围、来源、备注），可关联住院文件。
- 住院档案目录：`AdmissionFolder`
  - 按用户、年、月进行住院记录分组。
- 住院记录：`Admission`
  - 住院的主体信息（医院、科室、诊断、入出院日期、标签、备注等）。
- 住院文件：`AdmissionFile`
  - 住院期间的文件上传信息（文件名、URL/OSS Key、页数、OCR 状态、提取文本、元数据 JSON）。
- 用药：`Medication`
  - 药品基础信息（通用名、规格、单位等）。
- 用药记录：`MedicationRecord`
  - 用户的用药时间段、剂量、频率、途径、目的、备注等，支持标记当前用药。

## 日志与请求追踪
- 通过 `loguru` 输出结构化日志，包含 `request_id` 与 `trace_id`，便于排查与关联请求。
- 中间件自动为每次请求注入并返回对应的追踪 ID（响应头 `X-Request-ID` / `X-Trace-ID`）。

## 与前端对接
- 前端 `axios` 基础地址为 `'/api/v1'`，开发环境通过 `vite.config.js` 代理到后端（例如 `http://127.0.0.1:8001`）。
- 若后端端口或地址变更，请同步更新前端开发代理。

## 响应结构建议
- 前端拦截器期望统一响应结构：`{ code, message, data }` 且 `code === 200` 时视为成功。
- 当前健康检查返回 `{ status: "ok" }`，不影响前端页面加载；建议后续接口按统一结构返回，或调整前端拦截器兼容多种格式。

## 已实现接口摘要（Auth & Account）
- 前缀：`/api/v1`（见 `app/core/settings.py`）

- 鉴权（Auth）：
  - `POST /auth/register`：请求体包含 `username,name,password,email(optional)`；返回 `{ id, username }`；失败返回 `HTTPException(detail)`。
  - `POST /auth/login`：请求体 `{ username, password }`；返回 `{ token, expiresIn, user }`，其中 `user` 为精简的个人资料结构；401 时 `detail` 为“用户不存在/密码错误”。
  - `POST /auth/logout`：无状态；返回 `{ success: true }`。
  - 刷新令牌：当前未实现（`/auth/refresh`）。

- 账户（Account）：
  - `GET /account/profile`：返回用户资料对象（`id, username, name, email, role, birthDate, gender, createdAt, lastLogin`）。
  - `PUT /account/profile`：请求体 `{ email, name, gender, birthDate }`；返回 `{ success: true }`；邮箱唯一约束冲突时返回 `HTTPException(detail)`。
  - `PUT /account/password`：请求体 `{ oldPassword, newPassword }`；返回 `{ success: true }`；旧密码错误时返回 `HTTPException(detail)`。

- 错误语义：
  - 所有错误通过 FastAPI 的 `HTTPException` 返回，`detail` 字段用于前端提示。
  - 常见 401/403/404/422/500 均按照语义返回；前端拦截器已优先显示 `detail`。

- 前端约定（参考 `medical-front/src/utils/request.js`）：
  - Axios 基础地址 `/api/v1`，开发代理到 `http://127.0.0.1:8001`。
  - 请求拦截器自动注入 `Authorization: Bearer <token>`。
  - 响应拦截器兼容 `{code,message,data}` 与原始 JSON；401 自动清理并跳转登录；错误优先显示 `detail`。

## 常见问题
- SQLite 文件路径在 Windows 下建议使用绝对路径并包含驱动前缀（如 `sqlite+aiosqlite:///c:/data/medical.sqlite3`）。
- 首次启动会自动创建数据表；若结构变更，需重建或迁移（当前未引入迁移框架）。

## 版本与配置
- 应用名称与版本见 `app/core/settings.py`。
- 日志级别与格式可在 `Settings` 中配置或通过环境变量覆盖。