# 医疗数据管理系统数据库关系设计

本文件基于 `design.md` 与 `medical-front/api.md`、前端 README 与源码视图（Indicators.vue、IndicatorDetail.vue、Admissions.vue、Dashboard.vue 等）整理出的后端数据库关系设计。面向首版实现使用 SQLite（可迁移 PostgreSQL）。命名与字段尽量贴合接口返回的语义，同时在库内保留更细粒度字段以便分析与约束。

## 设计原则
- 多用户：为所有主要业务表添加 `user_id` 并做行级隔离；所有查询均以 `user_id` 作为首要过滤条件；唯一约束与索引包含 `user_id` 前缀。
- 采用软删除（`deleted_at`）支持审计与恢复，必要时加唯一索引与约束。
- 时间字段统一使用 `UTC` ISO8601；前端展示按本地时区转换。
- 细粒度存储（如 `ref_low/ref_high`）与聚合展示分离（如 `referenceRange`）。
- 审计与异步任务统一模型，便于系统观察与维护。

## 实现说明（Implementation Notes）
目前后端已实现以下模型并在应用启动时自动创建对应数据表：
- 用户与鉴权：`User`
- 指标与记录：`Indicator`, `IndicatorRecord`
- 住院管理：`AdmissionFolder`, `Admission`, `AdmissionFile`
- 用药管理：`Medication`, `MedicationRecord`

数据库连接与配置：
- 默认连接：`sqlite+aiosqlite:///./medical.sqlite3`
- 可通过环境变量覆盖：在后端项目根目录 `.env` 中设置 `SQLITE_URL`
- 表创建：应用启动事件会调用 `SQLModel.metadata.create_all` 自动初始化所有表

索引与约束：上述设计中描述的主键、唯一约束与索引将逐步按需补充；当前版本已为高频查询字段添加索引，如 `user_id`、`measured_at`、`is_current` 等。

## 核心实体与关系概览
- User N—N Indicator（通过 UserIndicator 关联“用户关注/个性化配置”）；User ——< Admission / MedicationRecord / ChatSession / AuditLog
- Indicator ——< IndicatorRecord；Indicator ——1—1 IndicatorDetail（知识与建议）
- AdmissionFolder ——< Admission；Admission ——< AdmissionFile；AdmissionFile ——< OcrTask
- KnowledgeDoc 1—N KnowledgeChunk
- ChatSession 1—N ChatMessage
- ExportTask 独立；WebSearchQuery 独立；SystemLog 独立

---

## 用户与鉴权

### User
- id: integer, PK, auto
- username: varchar(64), unique, not null
- password_hash: varchar(255), not null
- email: varchar(128), unique, null
- role: varchar(32), not null, default 'user'  // user|admin|developer
- created_at: datetime, not null
- last_login: datetime, null
- deleted_at: datetime, null

约束与说明：
- username 唯一索引；role 走 RBAC；软删除通过 `deleted_at`。

---

## 体检指标模块

### Indicator（指标定义，系统级 + 用户自定义）
- id: integer, PK, auto
- code: varchar(64), unique, null  // 系统内置指标使用全局 code；用户自定义可为空
- owner_user_id: integer, FK → User.id, null  // 自定义指标归属者；内置指标为 NULL
- name_cn: varchar(128), not null
- name_en: varchar(128), null
- unit: varchar(32), not null
- category: varchar(64), null
- reference_min: numeric(12,4), null
- reference_max: numeric(12,4), null
- is_builtin: boolean, not null, default false
- created_at: datetime, not null
- deleted_at: datetime, null

索引：
- idx_indicator_owner (owner_user_id)
- idx_indicator_category (category)
唯一约束（建议）：
- unique(code)  // 仅针对内置指标
- unique(owner_user_id, name_cn, unit)  // 用户自定义在用户域内唯一

接口映射：
- `/api/v1/indicators` 列表：支持查询内置与自定义；“我关注的”需联表 `UserIndicator`。

### IndicatorRecord（指标记录）
- id: integer, PK, auto
- indicator_id: integer, FK → Indicator.id, not null
- user_id: integer, FK → User.id, not null
- measured_at: date, not null
- value: numeric(12,4), not null
- unit: varchar(32), not null
- ref_low: numeric(12,4), null
- ref_high: numeric(12,4), null
- ref_text: varchar(255), null
- source: varchar(32), not null  // manual|ocr|import
- note: varchar(255), null
- admission_file_id: integer, FK → AdmissionFile.id, null  // 可选关联：记录来源文件
- created_at: datetime, not null
- deleted_at: datetime, null

索引与约束：
- idx_record_indicator_date (indicator_id, measured_at)
- idx_record_user_date (user_id, measured_at)
- idx_record_file (admission_file_id)
- 可选唯一约束：同一用户同一指标在同一天仅一条固定来源记录 → unique(user_id, indicator_id, measured_at, source)
一致性：
- 写入校验 `IndicatorRecord.user_id == AdmissionFile.user_id`（若 `admission_file_id` 非空）。

接口映射：
- `/api/v1/indicators/{id}/records` → `date(measured_at)`, `value`, `unit`, `status(由 value 与 ref_low/ref_high 计算)`。
- `/api/v1/admissions/{admissionId}/files/{fileId}/indicator-records` → 通过 `admission_file_id` 过滤记录。

### UserIndicator（用户-指标关联与个性化，N-N）
- id: integer, PK, auto
- user_id: integer, FK → User.id, not null
- indicator_id: integer, FK → Indicator.id, not null
- alias: varchar(128), null
- threshold_min: numeric(12,4), null
- threshold_max: numeric(12,4), null
- favorite: boolean, not null, default false
- created_at: datetime, not null

索引与约束：
- unique(user_id, indicator_id)
- idx_ui_user (user_id)
- idx_ui_user_fav (user_id, favorite)

接口映射：
- `/api/v1/user-indicators`：关注、取消关注与个性化配置；列表按照 `user_id` 过滤。

### IndicatorDetail（指标知识与建议，1:1）
- id: integer, PK, auto
- indicator_id: integer, FK → Indicator.id, unique, not null
- introduction_text: text, null
- measurement_method: text, null
- clinical_significance: text, null
- high_meaning: text, null
- low_meaning: text, null
- high_advice: text, null
- low_advice: text, null
- normal_advice: text, null
- general_advice: text, null
- unit: varchar(32), null
- reference_range: varchar(64), null  // 展示用；计算仍以记录的 ref_low/ref_high
- updated_at: datetime, not null

接口映射：
- GET `/api/v1/indicators/{id}/detail`
- PUT `/api/v1/indicators/{id}/detail`

---

## 指标分析

（分析为计算结果，通常不入库；如需缓存可用临时表或缓存键）

### IndicatorStatsCache（可选）
- id: integer, PK, auto
- indicator_id: integer, FK → Indicator.id
- window: varchar(16)  // day|week|month|custom
- mean: numeric(12,4)
- std: numeric(12,4)
- trend_slope: numeric(12,6)
- abnormal_count: integer
- updated_at: datetime

索引：
- unique(indicator_id, window)

---

## 住院管理模块

### AdmissionFolder（年月分组）
- id: integer, PK, auto
- user_id: integer, FK → User.id, not null
- year: integer, not null
- month: integer, not null  // 1-12

索引：
- unique(user_id, year, month)

### Admission（住院记录）
- id: integer, PK, auto
- folder_id: integer, FK → AdmissionFolder.id, not null
- user_id: integer, FK → User.id, not null
- hospital: varchar(128), not null
- department: varchar(64), null
- diagnosis: varchar(255), null
- admission_date: date, not null
- discharge_date: date, null
- tags_json: text, null  // JSON 字符串
- notes: text, null
- created_at: datetime, not null
- deleted_at: datetime, null

索引：
- idx_admission_folder (folder_id)
- idx_admission_user (user_id)
- idx_admission_dates (admission_date, discharge_date)

### AdmissionFile（文件项）
- id: integer, PK, auto
- admission_id: integer, FK → Admission.id, not null
- user_id: integer, FK → User.id, not null
- filename: varchar(255), not null
- oss_key: varchar(255), null  // 或本地路径
- pages: integer, null
- ocr_done: boolean, not null, default false
- extracted_text: text, null
- meta_json: text, null
- uploaded_at: datetime, not null
- deleted_at: datetime, null

索引：
- idx_file_admission (admission_id)
- idx_file_user (user_id, uploaded_at)
 -（与指标记录联动）建议为 `indicator_record.admission_file_id` 创建索引 `idx_record_file`，支持按文件反查记录。

---

## 用药管理模块

### Medication（药物字典）
- id: integer, PK, auto
- name: varchar(128), not null
- generic_name: varchar(128), null
- spec: varchar(64), null
- unit: varchar(32), null
- created_at: datetime, not null
- deleted_at: datetime, null

索引：
- unique(name, spec)

### MedicationRecord（用药记录）
- id: integer, PK, auto
- medication_id: integer, FK → Medication.id, not null
- user_id: integer, FK → User.id, not null
- start_date: date, not null
- end_date: date, null
- dose: varchar(64), null
- frequency: varchar(64), null  // BID/QD/TID 等
- route: varchar(32), null  // PO/IV/IM 等
- purpose: varchar(255), null
- notes: text, null
- is_current: boolean, not null, default true
- created_at: datetime, not null
- deleted_at: datetime, null

索引：
- idx_mr_medication (medication_id)
- idx_mr_current (is_current)
- idx_mr_user (user_id, is_current)

---

## 知识库模块（KB）

### KnowledgeDoc（文档）
- id: integer, PK, auto
- title: varchar(255), not null
- source_type: varchar(16), not null  // pdf|url
- oss_key: varchar(255), null
- url: varchar(255), null
- meta_json: text, null
- uploaded_at: datetime, not null
- deleted_at: datetime, null

索引：
- idx_kb_source (source_type)

### KnowledgeChunk（分块）
- id: integer, PK, auto
- doc_id: integer, FK → KnowledgeDoc.id, not null
- chunk_index: integer, not null
- chunk_text: text, not null
- embedding_ref: varchar(255), null  // 向量存储引用或外键 ID
- created_at: datetime, not null

索引：
- unique(doc_id, chunk_index)
- idx_chunk_doc (doc_id)

---

## 聊天与消息

### ChatSession
- id: varchar(64), PK  // 如 cs-1；也可 integer PK
- user_id: integer, FK → User.id, not null
- title: varchar(255), not null
- created_at: datetime, not null
- deleted_at: datetime, null
索引：
- idx_session_user (user_id, created_at)

### ChatMessage
- id: varchar(64), PK  // 如 m-1；也可 integer PK
- session_id: varchar(64), FK → ChatSession.id, not null
- role: varchar(16), not null  // user|assistant|tool
- content: text, not null
- tool_calls_json: text, null
- created_at: datetime, not null
- deleted_at: datetime, null

索引：
- idx_msg_session (session_id, created_at)

---

## OCR 与导出任务

### OcrTask
- id: varchar(64), PK  // 如 ocr-123
- admission_id: integer, FK → Admission.id, not null
- file_id: integer, FK → AdmissionFile.id, not null
- user_id: integer, FK → User.id, not null
- status: varchar(16), not null  // pending|running|done|failed
- language: varchar(8), null  // zh|en
- engine: varchar(32), null  // paddleocr 等
- created_at: datetime, not null
- updated_at: datetime, null
- deleted_at: datetime, null

索引：
- idx_ocr_file (file_id, status)
- idx_ocr_user (user_id, status)

### ExportTask
- id: varchar(64), PK  // exp-1
- user_id: integer, FK → User.id, not null
- format: varchar(8), not null  // csv|json
- scope: varchar(32), not null  // indicators|admissions|medications|all
- filters_json: text, null
- status: varchar(16), not null  // queued|running|done|failed
- download_url: varchar(255), null
- created_at: datetime, not null
- updated_at: datetime, null
- deleted_at: datetime, null

索引：
- idx_export_status (status)
- idx_export_user (user_id, status)

---

## 系统与审计

### SystemLog
- id: integer, PK, auto
- level: varchar(16), not null  // info|warn|error
- message: text, not null
- context_json: text, null
- created_at: datetime, not null

### AuditLog
- id: integer, PK, auto
- user_id: integer, FK → User.id, null
- action: varchar(32), not null
- entity: varchar(64), not null  // Indicator/Admission/...
- entity_id: varchar(64), null
- payload_json: text, null
- created_at: datetime, not null

索引：
- idx_audit_entity (entity, entity_id)
- idx_audit_user (user_id, created_at)

---

## 其他（可选模块）

### WebSearchQuery
- id: varchar(64), PK
- user_id: integer, FK → User.id, not null
- query: varchar(255), not null
- provider: varchar(32), null
- results_json: text, null
- created_at: datetime, not null

索引：
- idx_web_user (user_id, created_at)
### ModelProviderStatus
- id: integer, PK, auto
- provider_key: varchar(32), not null
- status: varchar(16), not null  // ok|failed
- latency_ms: integer, null
- message: varchar(255), null
- checked_at: datetime, not null

索引：
- idx_provider_key (provider_key, checked_at)

---

## 关系图（文字说明）
- User ——< Indicator ——< IndicatorRecord
- Indicator ——1 IndicatorDetail
- User ——< AdmissionFolder ——< Admission ——< AdmissionFile ——< OcrTask
- KnowledgeDoc ——< KnowledgeChunk
- User ——< ChatSession ——< ChatMessage
- User ——< AuditLog；User ——< ChatSession（可选）
- User ——< ExportTask；User ——< WebSearchQuery
- SystemLog、ModelProviderStatus 独立（系统级）

---

## 字段与接口对照表（关键映射）
- `/indicators` 列表：indicator(name_cn), unit, referenceRange(reference_min/reference_max 聚合), measureDate(最新 IndicatorRecord.measured_at)；“我关注的”由 `UserIndicator` 关联
- `/indicators/{id}/records`：date(measured_at), value, unit, status(计算), source, note, admissionFileId
- `/admissions/{admissionId}/files/{fileId}/indicator-records`：按 `admission_file_id` 过滤记录
- `/indicators/{id}/detail`：introductionText(introduction_text), measurementMethod(measurement_method), clinicalSignificance(clinical_significance), highAdvice/lowAdvice/normalAdvice/generalAdvice，对应字段同名
- `/admissions/*`：hospital/department/diagnosis/admissionDate/dischargeDate ↔ Admission；文件 `filename/uploaded_at/pages/ocr_done`
- `/medications/*`：药物字典 ↔ Medication，记录 ↔ MedicationRecord
- `/kb/*`：文档 ↔ KnowledgeDoc；分块 ↔ KnowledgeChunk
- `/chat/*`：会话 ↔ ChatSession；消息 ↔ ChatMessage
- `/ocr/tasks` ↔ OcrTask；`/export/*` ↔ ExportTask；`/system/logs` ↔ SystemLog；`/audit/logs` ↔ AuditLog

---

## 迁移建议与示例（SQL 表示，SQLite 方言）

（示例仅列部分关键表，实际以 ORM 迁移工具生成为准）

```sql
CREATE TABLE indicator (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE,
  owner_user_id INTEGER,
  name_cn TEXT NOT NULL,
  name_en TEXT,
  unit TEXT NOT NULL,
  category TEXT,
  reference_min REAL,
  reference_max REAL,
  is_builtin INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  deleted_at TEXT,
  FOREIGN KEY(owner_user_id) REFERENCES user(id)
);

CREATE TABLE indicator_record (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  indicator_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  measured_at TEXT NOT NULL,
  value REAL NOT NULL,
  unit TEXT NOT NULL,
  ref_low REAL,
  ref_high REAL,
  ref_text TEXT,
  source TEXT NOT NULL,
  note TEXT,
  admission_file_id INTEGER,
  created_at TEXT NOT NULL,
  deleted_at TEXT,
  FOREIGN KEY(indicator_id) REFERENCES indicator(id),
  FOREIGN KEY(user_id) REFERENCES user(id),
  FOREIGN KEY(admission_file_id) REFERENCES admission_file(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX ux_record_indicator_date_source ON indicator_record(user_id, indicator_id, measured_at, source);
CREATE INDEX idx_record_file ON indicator_record(admission_file_id);

CREATE TABLE indicator_detail (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  indicator_id INTEGER NOT NULL UNIQUE,
  introduction_text TEXT,
  measurement_method TEXT,
  clinical_significance TEXT,
  high_meaning TEXT,
  low_meaning TEXT,
  high_advice TEXT,
  low_advice TEXT,
  normal_advice TEXT,
  general_advice TEXT,
  unit TEXT,
  reference_range TEXT,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(indicator_id) REFERENCES indicator(id)
);

CREATE TABLE user_indicator (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  indicator_id INTEGER NOT NULL,
  alias TEXT,
  threshold_min REAL,
  threshold_max REAL,
  favorite INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  UNIQUE(user_id, indicator_id),
  FOREIGN KEY(user_id) REFERENCES user(id),
  FOREIGN KEY(indicator_id) REFERENCES indicator(id)
);
```

---

## 数据一致性与演进
- 软删除：业务查询默认过滤 `deleted_at IS NULL`。
- 多用户过滤：所有列表与详情查询均以当前 `user_id` 作为过滤前提；写入时校验实体归属。对 `IndicatorRecord.admission_file_id` 的写入需校验与 `AdmissionFile.user_id` 一致。
- 审计：重要变更（指标定义/用药记录/住院信息/知识更新）写入 AuditLog。
- 缓存：指标详情 GET 可做缓存；更新 PUT 需同时失效缓存键。
- 迁移：初始 SQLite，后续迁移 PostgreSQL 时将 `text`/`json` 字段替换为 `JSONB`，并补充外键与级联策略。

## 命名约定
- 表名：下划线小写；字段同理。
- 接口对外字段沿用前端文案（小驼峰），后端映射在序列化层处理。

## 变更历史
- v0.1 初版：覆盖指标/住院/用药/知识库/聊天/任务/系统/审计。
