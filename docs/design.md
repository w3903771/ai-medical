## 🤖 Assistant | GitHub Copilot


下面给你一份可以直接落地的完整设计与实施方案，面向“医疗数据管理分析平台”，覆盖需求分析、原型、类与数据模型、前后端技术栈与实现要点、AI/Agent集成（Letta）、测试、部署、以及本地环境清单。按你的背景（Python强、Web框架新手）和当前资源（1G1核 CentOS 7 + 宝塔 + 自有域名 + 本地 Win11）做了取舍，优先可维护性与轻量化。

一、总体架构与技术栈选择
- 架构风格
 - 后端：FastAPI + Uvicorn（轻量、类型友好、文档自动化）
 - 数据库：SQLite（单机轻量、易运维；后续可升 PostgreSQL）。对象层使用 SQLModel（或 SQLAlchemy + Pydantic）
 - 向量检索/知识库：LanceDB（本地嵌入式）或 Chroma。为省资源，嵌入向量使用云端 Embedding API（如 OpenAI/Zhipu）生成
 - OCR：PaddleOCR（中文+医疗票据表现好，CPU可跑）
 - PDF：前端 pdf.js 浏览；后端 PyMuPDF 提取文本与页码信息
 - 前端：Vue 3 + Vite + Pinia + Vue Router + Element Plus（表格和树组件强、上手快）+ ECharts（趋势图）
 - 鉴权：JWT（fastapi-jwt-auth 或自实现）
 - Agent/LLM：Letta（Python SDK）+ 可插拔 LLM（OpenAI/DeepSeek/智谱等）；检索增强使用知识库
 - 移动端/Android：PWA 优先；用 Capacitor 或 Android WebView 打包生成 APK（低成本）
 - 任务异步：FastAPI BackgroundTasks 或 APScheduler（小型场景避免 Redis/Celery 占内存）
 - 存储：文件磁盘或阿里云 OSS（推荐：稳定、减轻服务器磁盘压力）
 - 日志/监控：结构化日志 + 宝塔面板/Nginx 访问日志；Sentry 可选（后期）

- 选择理由
 - 你的 Python 背景 + 服务器资源受限 → 轻量、嵌入式优先
 - Web 端框架选 Vue 3 + Element Plus → 列表、树、右键菜单、表单、对话框都容易
 - Android 先走 PWA/封装 → 复用前端，快速上线

二、功能拆解与数据模型（类设计）
1) 用户与鉴权
- User
 - id, username, password_hash, email, role, created_at, last_login
- Token（不入库）：JWT

2) 体检指标
- Indicator（指标定义）
 - id, name_cn, name_en, unit, created_at, deleted_at
- IndicatorRecord（指标记录）
 - id, indicator_id, measured_at, value, ref_low, ref_high, ref_text, source(manual/ocr/import), note, created_at
- 统计/缓存（可选）
 - IndicatorStatsCache：indicator_id, window, mean, std, trend_slope, updated_at

3) 住院记录与文档
- AdmissionFolder（用于树形分组：年/月）
 - id, year, month
- Admission（住院档案）
 - id, folder_id, hospital, admission_date, discharge_date, department, diagnosis, tags(json), notes
- AdmissionFile（文件）
 - id, admission_id, filename, url/oss_key, pages, ocr_done, extracted_text, meta(json), uploaded_at

4) 药物与用药
- Medication
 - id, name, generic_name, spec, unit
- MedicationRecord（当前用药/历史记录）
 - id, medication_id, start_date, end_date, dose, frequency, route, purpose, notes, is_current

5) LLM/Agent 与知识库
- KnowledgeDoc（指南/资料）
 - id, title, source_type(pdf/url), url/oss_key, meta(json), uploaded_at
- KnowledgeChunk（分块）
 - id, doc_id, chunk_text, embedding(vector ref), chunk_index
- ChatSession / ChatMessage（对话/日志）
 - session_id, user_id, created_at
 - message_id, role(user/assistant/tool), content, tool_calls(json), related_ids

6) 审计与安全（可选）
- AuditLog：user_id, action, entity, entity_id, payload, created_at
- Soft delete：deleted_at 字段

三、页面与原型（信息架构）
- 导航结构
 - 首页 Dashboard：体重/血压/血糖关键指标卡片、最近异常、当前用药卡片、生活建议卡片（LLM 生成或规则）
 - 指标数据：大表格（行=指标，列=时间点）；右键弹出菜单（新增/删除/修改/查看变化/调用大模型）；支持多选行进行联合分析
 - 住院管理：左侧树（年-月-住院记录），右侧标签页（住院信息、PDF阅读、PDF上传）。PDF 内嵌 pdf.js
 - 大模型界面：对全量数据提问（检索增强），支持选择数据范围（全部/某指标/某住院档案）
 - 知识库管理（后期）：上传指南 PDF，分块、生成 embedding
 - 设置：账号/数据导入导出/备份

- 原型工具与流程
 - Figma/Excalidraw：出低保真线框（Dashboard 卡片位置、指标表格右键菜单、住院树/右侧布局、全局搜索框）
 - 原子/组件化：卡片组件、表格组件、树组件、pdf-viewer 组件、LLM Chat 组件

四、开发里程碑与顺序（建议 6-8 周）
- Sprint 0：项目脚手架与原型（0.5 周）
 - 仓库初始化（前后端），Figma 原型，CI 基础（lint、格式化）
- Sprint 1：后端基础与鉴权（0.5-1 周）
 - FastAPI + SQLite + SQLModel，用户注册/登录/JWT，中间件、错误处理、日志
- Sprint 2：体检指标 CRUD 与表格（1 周）
 - 指标定义与记录模型/接口；前端指标表格（分页/搜索）；右键菜单：新增/删除/编辑/导入CSV
- Sprint 3：趋势与可视化（0.5-1 周）
 - 单指标折线/箱线图，异常点标记，移动平均/日周月聚合；多指标对比图
- Sprint 4：OCR 与导入（1 周）
 - 文件上传、PaddleOCR 解析、字段映射与人工校对；导入历史体检报告
- Sprint 5：住院档案模块（1-1.5 周）
 - 树形组织（年/月/住院记录）；右侧信息表单；PDF 上传与预览（pdf.js）；OCR 文本提取与检索
- Sprint 6：LLM + Letta 初步集成（1 周）
 - 知识库上传/分块/embedding 入库；Letta 工具函数：query_metrics、trend_summary、fetch_admission_text 等；接口打通：单指标/多指标分析、体检报告分析、住院报告分析；LLM 界面
- Sprint 7：Dashboard、用药管理、打磨与测试（0.5-1 周）
 - 首页卡片、当前用药 CRUD；回归测试；PWA/Android 打包
- 部署与文档（并行 2-3 天）
 - 服务器部署、域名/HTTPS、备份策略、使用手册

五、后端设计要点
- API 结构（示例，高层）
 - /auth: login, refresh
 - /indicators: list/create/update/delete
 - /indicators/{id}/records: list/create/update/delete, bulk-import
 - /analysis: trend, multi-indicator-compare, abnormal-detect
 - /admissions: folders(list), admission CRUD, files upload/list, ocr, extract
 - /medications: CRUD, current
 - /kb: upload_doc, list_docs, build_embeddings, search
 - /llm: analyze_metrics, analyze_report, general_qa
 - /files: signed-url 或直传策略（若接 OSS）
- 服务模块
 - AuthService：JWT、密码哈希（argon2/bcrypt）
 - IndicatorService：CRUD、记录批量导入、统计缓存
 - AnalysisService：趋势/异常/对比、统计特征
 - OCRService：PDF/JPG 调用 PaddleOCR；字段提取模板可配置
 - PDFService：PyMuPDF 提取文本、页码；缩略图（可选）
 - KBService：分块、调用 Embedding API、落 LanceDB/Chroma、相似度检索
 - LLMService：统一 LLM 客户端（OpenAI/智谱等），重试/超时
 - AgentService（Letta）：注册工具函数（见下一节），组合工作流
 - StorageService：本地磁盘或 Aliyun OSS（推荐）
- 分块与检索
 - 文档分块：按段落或固定 token 数（如 500-800 tokens）
 - 向量存储：LanceDB（嵌入式，轻量）
 - 召回：top-k + 多路召回（指南+个人数据）+ 重排序（可后期）
- 分析算法基础
 - 移动平均、季节性分解（可选）、异常检测（z-score/阈值）
 - 参考区间对齐：按记录 ref_low/ref_high 标注超界
 - 趋势 slope：线性回归或 Theil-Sen 鲁棒估计

六、前端设计要点
- 核心页面组件
 - Dashboard：卡片组件（指标当前值/变化箭头）、异常列表、当前用药、建议卡片
 - 指标表格页
 - 表格为“指标 x 时间点”的透视视图：后端提供 pivot 数据或前端以 records 做 pivot
 - 右键菜单：新增/编辑/删除/新增数据/查看变化/大模型分析
 - 多选行：联合分析与对比图
 - ECharts 折线图/散点；阈值带显示
 - 住院页
 - 左树（年-月-住院记录）；右侧 Tabs：基本信息表单、PDF 预览（pdf.js iframe）、PDF 上传表单
 - PDF 解析状态与 OCR 结果展示（可下载抽取文本）
 - LLM 页
 - 问答输入框、历史对话、上下文来源显示（引用文档/指标）
 - 高级选项：勾选数据范围
- 状态管理与网络
 - Pinia 做全局用户态/会话态；axios 封装 API，拦截器注入 JWT
- 细节
 - 表格右键菜单：使用 Element Plus Dropdown + 自定义右键触发
 - PWA：manifest、service worker，移动端适配方案
 - 国际化可后期（中/英）

七、Agent 与知识库（Letta 集成）
- 工具函数建议（注册到 Letta，供模型调用）
 - query_metric(name_en or id, start, end) → 返回时间序列与参考区间
 - summarize_trend(series) → 返回整体变化、波动、异常次数
 - compare_metrics([ids], start, end) → 返回对比统计与相关性（可选）
 - fetch_admission_text(admission_id) → 返回 OCR 文本/结构化信息
 - fetch_current_medications() → 当前用药列表
 - kb_search(query, top_k) → 返回检索的指南分块 + 引文
 - web_search(query) → 可选联网能力（后期）
- 工作流样例
 - 单指标分析：检索指标序列→计算趋势→召回指南段落→生成解释与建议
 - 多指标联合分析：取多指标准备对比→召回相关指南→输出风险点/用药建议/下一步计划
 - 体检报告分析：从 OCR 文本中抽取指标→匹配库中历史指标→对比与总结
- 嵌入策略
 - 服务器算力有限→使用云 API 生成 embedding（OpenAI text-embedding-3-small 或 智谱 Embedding）
 - 私密数据：只上传文本片段到 Embedding API，避免完整原文；或在本地生成（后期考虑本地轻量模型）
- 提示词工程
 - 先抽象：角色/目标/工具使用约束/输出格式（JSON + 可视化建议）

八、Android 端方案
- PWA 先行：保证移动端响应式
- 第一版：Capacitor + Android Studio 生成 APK（打包 WebView），支持通知/文件访问权限
- 登录持久化：WebView 内 JWT 本地存储
- 后续若需要更原生：再考虑 Flutter/React Native

九、测试与质量保证
- 后端
 - pytest + httpx 测 API；单元测试：服务层与数据层；集成测试：关键流程（OCR 导入→指标新增→分析）
- 前端
 - Vitest + Vue Test Utils（组件）；Playwright（端到端：登录→表格操作→图表查看→PDF 预览→LLM 调用）
- 性能与稳定性
 - 小数据基准：指标 10^4 级别、PDF 100 份内；定期清理临时文件
- 安全
 - 强密码/哈希（bcrypt/argon2）；JWT 过期/刷新；HTTPS 强制；上传文件类型白名单；防 XSS/CSRF（同源策略+Token）
- 隐私
 - 最小可用日志；导出/删除数据功能

十、部署方案（宝塔 + CentOS 7）
- 强烈建议：Docker 化隔离（CentOS 7 已 EOL）。1G 内存下尽量少容器
- 方案 A（推荐）：Docker Compose
 - 服务：backend（FastAPI）、frontend（静态构建后由 Nginx 提供）、lancedb/chroma（若独立则容器，使用嵌入式可省）
 - 静态资源：前端构建后放入 Nginx 容器或宝塔站点目录
 - Nginx（宝塔）做反向代理到 backend:8000
- 方案 B（更省内存）
 - 后端直接用 Uvicorn/Gunicorn 运行为系统服务；前端静态文件放宝塔站点；宝塔 Nginx 反代后端
- 域名与 HTTPS
 - 宝塔面板添加站点→申请 Let’s Encrypt 证书→配置反向代理到 backend
- 文件存储
 - 本地：/data/medapp/{uploads,pdfs,ocr,tmp}
 - 或阿里云 OSS：后端获取 STS 临时凭证，前端直传
- 备份与日志
 - SQLite 与知识库定期压缩备份（每日/每周），异地存储一份
 - 日志轮转，上传异常告警（可选钉钉/飞书 Webhook）

十一、本地开发环境清单（Win11, 32G）
- 系统与基础
 - Python 3.11+
 - Node.js 20+ 与 pnpm 或 npm
 - Git 与 Git LFS（如存示例 PDF）
 - VSCode（推荐扩展：Python, Pylance, Ruff, Prettier, Vue Language Features）
- Python 依赖（示例）
 - fastapi, uvicorn[standard], sqlmodel 或 sqlalchemy+pydantic, aiosqlite
 - passlib[bcrypt], python-jose 或 pyjwt, httpx
 - pydantic-settings（配置管理）
 - paddleocr, pymupdf
 - lancedb 或 chromadb
 - openai 或 zhipuai（根据选的厂商）
 - tenacity（重试）, loguru（日志可选）
 - pytest, httpx, coverage
- 前端依赖（示例）
 - vue@3, vite, pinia, vue-router, axios
 - element-plus, echarts, pdfjs-dist
 - vitest, @vue/test-utils, playwright（可后置）
- 可选
 - Docker Desktop（便于与服务器一致）
 - mkcert（本地 HTTPS）
- 配置与密钥
 - .env（后端）：JWT_SECRET, LLM_API_KEY, EMBEDDING_API_KEY, STORAGE_CONFIG, BASE_URL
 - 前端 .env：VITE_API_BASE

十二、实现关键点与接口示意
- 指标透视表实现
 - 后端提供两种数据：原始 records（indicator_id, measured_at, value）+ 列表时间点；或直接返回 pivot 后的数据结构
 - 前端根据选择时间粒度（天/周/月）聚合
- OCR 流程
 - 前端上传→后端保存原始文件→异步调用 PaddleOCR→返回候选字段→用户校对后写入指标记录
- LLM 分析接口
 - POST /llm/analyze_metrics：入参包含指标 id 列表、时间范围、输出维度；后端 Agent 调用 tools 汇总→生成回答（附引用）
 - POST /llm/general_qa：入参 query + 可选范围；先 kb_search，再与用户数据拼接提示给 LLM
- 权限与多用户
 - 初期单用户；如多用户，所有表加 user_id，文件存储按用户隔离

十三、样例字段定义（无代码版）
- Indicator：name_cn, name_en, unit
- IndicatorRecord：value, measured_at, ref_low, ref_high, ref_text, source, note
- Admission：hospital, admission_date, discharge_date, department, diagnosis, tags, notes
- AdmissionFile：url/oss_key, pages, extracted_text
- MedicationRecord：dose, frequency, route, is_current, start_date, end_date
- KnowledgeChunk：chunk_text, embedding_ref

十四、风险与优化建议
- 服务器资源紧张
 - 避免本地大模型推理与本地 embedding；改用云 API
 - OCR 批量任务排队，限制并发；定期清理临时文件
- CentOS 7 EOL
 - 使用 Docker 或计划迁移 AlmaLinux/Rocky 后续版本
- 数据隐私
 - 禁止在日志中记录原文医疗信息；敏感文件加访问控制；必要时开启数据库加密（后期）
- 后续扩展
 - 切换数据库至 PostgreSQL
 - 加入规则引擎（如指标阈值、复诊提醒）
 - 更完善的审计与导出

十五、启动路径（你可以这样开始）
- 第 1 天：后端 FastAPI + SQLite + 鉴权跑通；前端 Vue 模板 + 登录
- 第 2-3 天：指标/记录 CRUD + 表格展示 + 右键菜单；单指标折线图
- 第 4-5 天：住院模块基本结构 + PDF 预览；文件上传
- 第 6-7 天：OCR 接入与人工校对流程
- 第 8-9 天：Letta 接入 + 知识库分块与检索 + 单指标分析
- 第 10 天：Dashboard 与当前用药；PWA/Android 打包；本地/服务器部署联调

如果你愿意，我可以基于以上方案为你生成：
- 后端 FastAPI 项目骨架（目录、依赖、示例路由与模型）
- 前端 Vue 3 + Element Plus 模板（布局、登录页、指标表格页雏形）
- Docker/部署脚本与宝塔反代配置示例
- Letta 工具函数样板与一个 end-to-end 的“多指标分析”示例调用流程
