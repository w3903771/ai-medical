# 医疗数据管理分析平台 后端 API 文档

本文件为前后端对接用的 RESTful 接口文档。已覆盖当前原型中的 Dashboard、指标管理、指标记录、指标详情知识、分析、住院管理、LLM、设置、文件服务与用药模块。每个接口均标注英文名、公共前置地址、接口路径、请求方法、请求体/查询参数、响应体与说明。

## 公共约定（Common Conventions）

- Prefix（公共前置地址）：`http://<host>/api/v1`
 - Health（健康检查）：`GET /api/v1/health` 返回 `{ "status": "ok" }`
- Auth（鉴权）：`Authorization: Bearer <jwtToken>`（登录与刷新令牌除外）
- Content-Type：JSON 使用 `application/json`；上传使用 `multipart/form-data`
- Pagination（分页）：`page`, `pageSize`；筛选：`keyword`, `startDate`, `endDate`, `category`, `sortBy`, `order`
- Standard Response（统一响应）：
  - 成功：`{ "code": 0, "message": "OK", "data": <payload>, "traceId": "<id>" }`
  - 失败：`{ "code": <nonzero>, "message": "<error>", "data": null, "traceId": "<id>" }`
- Error Codes（错误码）：`0` 成功；`400` 参数错误；`401` 未鉴权；`403` 禁止；`404` 不存在；`409` 冲突；`422` 校验失败；`500` 系统错误
- Idempotency（幂等性）：写操作支持 `Idempotency-Key`（可选）
- Upload Safety（上传安全）：仅允许 PDF/JPG/PNG 白名单

---

## 鉴权（Auth）

### 登录（Login）
- Prefix：`/api/v1`
- Endpoint：`/auth/login`
- Method：`POST`
- Request（Body）：`{ "username": "string", "password": "string" }`
- Response（Body）：`{ "token": "jwt", "expiresIn": 3600, "user": { "id": 1, "username": "..." } }`
- Notes：返回 JWT；后续请求通过 `Authorization` 头携带

### 注册（Register）
- Prefix：`/api/v1`
- Endpoint：`/auth/register`
- Method：`POST`
- Request（Body）：`{ "username": "string", "password": "string", "email": "string(optional)" }`
- Response（Body）：`{ "id": 1, "username": "..." }`
- Notes：用户名唯一；密码使用强哈希（bcrypt/argon2）存储

### 刷新令牌（Refresh Token）
- Prefix：`/api/v1`
- Endpoint：`/auth/refresh`
- Method：`POST`
- Request（Headers）：`Authorization: Bearer <token>`
- Response（Body）：同登录
- Notes：用于延长会话有效期

### 获取用户信息（Get Profile）
- Prefix：`/api/v1`
- Endpoint：`/account/profile`
- Method：`GET`
- Request（Headers）：`Authorization`
- Response（Body）：`{ "id": 1, "username": "...", "email": "...", "role": "user", "lastLogin": "YYYY-MM-DDTHH:mm:ssZ" }`
- Notes：登录后拉取用户信息，前端用于初始化用户状态

### 更新用户信息（Update Profile）
- Prefix：`/api/v1`
- Endpoint：`/account/profile`
- Method：`PUT`
- Request（Body）：`{ "email": "string", "username": "string(optional)" }`
- Response（Body）：`{ "code": 0 }`
- Notes：仅允许更新非敏感字段；`username` 若更新需唯一校验

### 修改密码（Change Password）
- Prefix：`/api/v1`
- Endpoint：`/account/password`
- Method：`PUT`
- Request（Body）：`{ "oldPassword": "string", "newPassword": "string" }`
- Response（Body）：`{ "code": 0 }`
- Notes：后端校验旧密码；新密码复杂度校验

### 登出（Logout）
- Prefix：`/api/v1`
- Endpoint：`/auth/logout`
- Method：`POST`
- Request：`{}` 或仅头部携带当前令牌
- Response（Body）：`{ "code": 0 }`
- Notes：前端清除本地令牌；后端可加入黑名单（可选）

---

## Dashboard（Dashboard Summary）

### 概览卡片与提醒（Dashboard Summary）
- Prefix：`/api/v1`
- Endpoint：`/dashboard/summary`
- Method：`GET`
- Request（Query）：`dateRangeStart`, `dateRangeEnd`（可选）
- Response（Body）：
```json
{
  "cards": [
    { "indicator": "weight", "value": 70.1, "unit": "kg", "trend": "up|down|flat", "status": "normal|high|low", "measureDate": "YYYY-MM-DD" }
  ],
  "alerts": [ { "type": "indicator", "indicator": "bloodSugar", "level": "high", "message": "..." } ],
  "currentMedications": [ { "name": "Metformin", "dose": "500mg", "frequency": "BID" } ]
}
```
- Notes：供首页卡片与提醒展示

---

## 指标定义与列表（Indicators）

### 指标列表（Get Indicators List）
- Prefix：`/api/v1`
- Endpoint：`/indicators`
- Method：`GET`
- Request（Query）：`page`, `pageSize`, `keyword`, `category`, `startDate`, `endDate`, `sortBy=measureDate`, `order=desc`, `favorites=true|false`（仅返回我关注的），`builtin=true|false`（过滤内置/自定义），`owner=me|all`（自定义指标归属过滤）
- Response（Body）：
```json
{
  "items": [
    { "id": 101, "indicator": "血压", "value": 120, "unit": "mmHg", "referenceRange": "90-140", "status": "normal|high|low", "measureDate": "YYYY-MM-DD", "category": "血压", "source": "manual|ocr|import", "note": "", "isBuiltin": true, "code": "BP_SYS", "favorite": true }
  ],
  "total": 123
}
```
- Notes：每项为“最新记录快照”，匹配 `Indicators.vue` 表格字段；`favorite` 字段来源于 `UserIndicator`；`isBuiltin/code` 用于区分系统内置指标与自定义指标。

### 新增指标定义（Create Indicator）
- Prefix：`/api/v1`
- Endpoint：`/indicators`
- Method：`POST`
- Request（Body）：`{ "indicator": "血压", "unit": "mmHg", "referenceMin": 90, "referenceMax": 140, "category": "血压", "introductionText": "", "measurementMethod": "", "code": null }`
- Response（Body）：`{ "id": 101 }`
- Notes：校验 `referenceMin <= referenceMax`；普通用户创建为“自定义指标”，后端自动记录归属用户；`code` 仅用于管理员创建“内置指标”（可选）。

### 获取指标定义（Get Indicator）
- Prefix：`/api/v1`
- Endpoint：`/indicators/{id}`
- Method：`GET`
- Response（Body）：`{ "id": 101, "indicator": "血压", "unit": "mmHg", "referenceMin": 90, "referenceMax": 140, "category": "血压" }`
- Notes：用于编辑与详情

### 更新指标定义（Update Indicator）
- Prefix：`/api/v1`
- Endpoint：`/indicators/{id}`
- Method：`PUT`
- Request（Body）：同“新增指标定义”
- Response（Body）：`{ "code": 0 }`
- Notes：全量更新

### 删除指标定义（Delete Indicator）
- Prefix：`/api/v1`
- Endpoint：`/indicators/{id}`
- Method：`DELETE`
- Response（Body）：`{ "code": 0 }`
- Notes：支持软删除（可选）

---

## 指标记录（Indicator Records）

### 查询指标记录（List Indicator Records）
- Prefix：`/api/v1`
- Endpoint：`/indicators/{id}/records`
- Method：`GET`
- Request（Query）：`page`, `pageSize`, `startDate`, `endDate`, `admissionFileId`（可选：按来源文件过滤）
- Response（Body）：
```json
{
  "items": [
    { "recordId": 888, "date": "YYYY-MM-DD", "value": 118, "unit": "mmHg", "status": "normal|high|low", "source": "manual|ocr|import", "note": "", "admissionFileId": "f-1" }
  ],
  "total": 200
}
```
- Notes：供 `IndicatorDetail.vue` 历史表与图使用

### 新增记录（Create Indicator Record）
- Prefix：`/api/v1`
- Endpoint：`/indicators/{id}/records`
- Method：`POST`
- Request（Body）：`{ "date":"YYYY-MM-DD", "value":118, "unit":"mmHg", "referenceMin":90, "referenceMax":140, "source":"manual", "note":"", "admissionFileId": "f-1" }`
- Response（Body）：`{ "recordId": 888 }`
- Notes：校验日期与参考值范围；若携带 `admissionFileId`，需与当前用户一致并存在于住院文件中。

### 更新记录（Update Indicator Record）
- Prefix：`/api/v1`
- Endpoint：`/indicators/{id}/records/{recordId}`
- Method：`PATCH`
- Request（Body）：同上任意字段
- Response（Body）：`{ "code": 0 }`
- Notes：部分字段更新

### 删除记录（Delete Indicator Record）
- Prefix：`/api/v1`
- Endpoint：`/indicators/{id}/records/{recordId}`
- Method：`DELETE`
- Response（Body）：`{ "code": 0 }`
- Notes：谨慎操作，支持软删除（可选）

### 批量导入记录（Import Indicator Records）
- Prefix：`/api/v1`
- Endpoint：`/indicators/{id}/records/import`
- Method：`POST`
- Request（FormData）：`file=<csv>`
- Response（Body）：`{ "imported": 200, "skipped": 3 }`
- Notes：CSV 列需与指标字段映射一致

---

## 指标详情知识（Indicator Detail）

### 指标知识信息（Get Indicator Detail）
- Prefix：`/api/v1`
- Endpoint：`/indicators/{id}/detail`
- Method：`GET`
- Response（Body）：
```json
{
  "indicatorName": "血压",
  "introductionText": "...",
  "measurementMethod": "...",
  "clinicalSignificance": "...",
  "referenceRange": "90-140",
  "unit": "mmHg",
  "highMeaning": "...",
  "lowMeaning": "...",
  "highAdvice": "...",
  "lowAdvice": "...",
  "normalAdvice": "..."
}
```
- Notes：用于 `IndicatorDetail.vue` 的文案与说明

---

## 指标分析（Analysis）

### 趋势分析（Get Indicator Trend）
- Prefix：`/api/v1`
- Endpoint：`/analysis/indicators/trend`
- Method：`GET`
- Request（Query）：`indicatorId`, `startDate`, `endDate`, `granularity=day|week|month`
- Response（Body）：
```json
{
  "series": [ { "date":"YYYY-MM-DD", "value":120, "refLow":90, "refHigh":140 } ],
  "stats": { "mean": 115.2, "std": 8.3, "trend": "up|down|flat", "abnormalCount": 2 }
}
```
- Notes：供图表计算与异常提示

---

## 住院管理（Admissions）

### 树状结构（Get Admissions Tree）
- Prefix：`/api/v1`
- Endpoint：`/admissions/tree`
- Method：`GET`
- Response（Body）：
```json
{
  "nodes": [
    { "id": "2024", "type": "year", "label": "2024", "children": [
      { "id": "2024-10", "type": "month", "label": "10月", "children": [
        { "id": "adm-1001", "type": "admission", "label": "记录编号", "hospital": "某医院", "department": "内科" }
      ] }
    ] }
  ]
}
```
- Notes：用于左侧树；`admission` 节点展示 `hospital/department`

### 住院记录列表（Get Admissions List）
- Prefix：`/api/v1`
- Endpoint：`/admissions`
- Method：`GET`
- Request（Query）：`page`, `pageSize`, `keyword`, `startDate`, `endDate`
- Response（Body）：
```json
{
  "items": [
    { "id":"adm-1001", "label":"A-1001", "hospital":"...", "department":"...", "diagnosis":"...", "admissionDate":"YYYY-MM-DD", "dischargeDate":"YYYY-MM-DD" }
  ],
  "total": 42
}
```
- Notes：供总览表展示

### 新增住院记录（Create Admission）
- Prefix：`/api/v1`
- Endpoint：`/admissions`
- Method：`POST`
- Request（Body）：`{ "hospital": "...", "department": "...", "admissionDate": "YYYY-MM-DD", "dischargeDate": "YYYY-MM-DD", "diagnosis": "...", "notes": "" }`
- Response（Body）：`{ "id": "adm-1001" }`
- Notes：与表单字段一致

### 更新住院记录（Update Admission）
- Prefix：`/api/v1`
- Endpoint：`/admissions/{id}`
- Method：`PUT`
- Request（Body）：同“新增住院记录”
- Response（Body）：`{ "code": 0 }`
- Notes：全量更新

### 删除住院记录（Delete Admission）
- Prefix：`/api/v1`
- Endpoint：`/admissions/{id}`
- Method：`DELETE`
- Response（Body）：`{ "code": 0 }`
- Notes：谨慎操作

### 住院记录详情（Get Admission）
- Prefix：`/api/v1`
- Endpoint：`/admissions/{id}`
- Method：`GET`
- Response（Body）：同列表条目并包含 `filesSummary`
- Notes：右侧“住院信息”页签使用

### 文件列表（List Admission Files）
- Prefix：`/api/v1`
- Endpoint：`/admissions/{id}/files`
- Method：`GET`
- Response（Body）：`[ { "fileId":"f-1", "filename":"report.pdf", "uploadDate":"YYYY-MM-DD", "pages":10, "ocrStatus":"pending|done|failed" } ]`
- Notes：供文件标签页列表

### 上传文件（Upload Admission File）
- Prefix：`/api/v1`
- Endpoint：`/admissions/{id}/files`
- Method：`POST`
- Request（FormData）：`file=<pdf|image>`
- Response（Body）：`{ "fileId": "f-1", "previewUrl": "http://.../files/f-1", "pages": 10 }`
- Notes：返回 `previewUrl` 供前端内嵌 pdf.js

### 文件预览与下载（Get Admission File）
- Prefix：`/api/v1`
- Endpoint：`/admissions/{id}/files/{fileId}`
- Method：`GET`
- Response（Body）：`{ "fileId":"f-1", "filename":"report.pdf", "previewUrl":"http://...", "downloadUrl":"http://..." }`
- Notes：供预览与下载链接

### 文件对应的指标记录列表（List Indicator Records by Admission File）
- Prefix：`/api/v1`
- Endpoint：`/admissions/{id}/files/{fileId}/indicator-records`
- Method：`GET`
- Request（Query）：`page`, `pageSize`, `startDate`, `endDate`
- Response（Body）：
```json
{
  "items": [
    { "recordId": 888, "indicatorId": 101, "date": "YYYY-MM-DD", "value": 118, "unit": "mmHg", "status": "normal|high|low", "source": "ocr", "note": "", "admissionFileId": "f-1" }
  ],
  "total": 200
}
```
- Notes：按住院文件反查其抽取/录入的指标记录；与 OCR/文本抽取联动使用。

### OCR 解析（OCR Admission File）
- Prefix：`/api/v1`
- Endpoint：`/admissions/{id}/files/{fileId}/ocr`
- Method：`POST`
- Request（Body）：`{ "language": "zh", "engine": "paddleocr" }`
- Response（Body）：`{ "taskId":"ocr-123", "status":"queued" }`
- Notes：异步任务；结合后台任务队列

### 抽取文本（Get Admission File Extracted Text）
- Prefix：`/api/v1`
- Endpoint：`/admissions/{id}/files/{fileId}/extracted-text`
- Method：`GET`
- Response（Body）：`{ "text": "......", "meta": { "pages": 10 } }`
- Notes：供文本查看与后续分析

---

## LLM（LLM Interface）

### 指标与住院数据分析（Analyze Metrics）
- Prefix：`/api/v1`
- Endpoint：`/llm/analyzeMetrics`
- Method：`POST`
- Request（Body）：
```json
{
  "dataScope": "all|indicators|admissions|custom",
  "selectedIndicators": ["weight","bloodPressure","bloodSugar","heartRate","temperature"],
  "selectedAdmissions": ["adm-1001","adm-1002"],
  "dateRange": ["YYYY-MM-DD","YYYY-MM-DD"],
  "model": { "provider": "openai|deepseek|ollama|...", "modelName": "gpt-4o-mini", "maxTokens": 1024, "temperature": 0.2 }
}
```
- Response（Body）：`{ "answer":"...", "summary": { "risk":"...", "advice":"..." }, "references": [ { "type":"indicator", "id":101 }, { "type":"admissionFile", "id":"f-1" } ] }`
- Notes：与 `LLMInterface.vue` 的 `queryConfig` 字段一致

### 通用问答（General QA）
- Prefix：`/api/v1`
- Endpoint：`/llm/generalQA`
- Method：`POST`
- Request（Body）：`{ "query":"...", "scope": { "indicators":[ids], "admissions":[ids], "dateRange":[start,end] }, "model": { ... } }`
- Response（Body）：同上
- Notes：知识库与用户数据检索增强（RAG）

---

## 设置（Settings）

### 账号信息（Account Profile）
- Prefix：`/api/v1`
- Endpoint：`/account/profile`
- Method：`GET` / `PUT`
- Request（Body，PUT）：`{ "username":"", "email":"", "phone":"", "gender":"male|female|other", "birthDate":"YYYY-MM-DD" }`
- Response（Body）：同结构
- Notes：映射 `AccountSettings.vue`

### 更新密码（Update Password）
- Prefix：`/api/v1`
- Endpoint：`/account/password`
- Method：`PUT`
- Request（Body）：`{ "oldPassword":"", "newPassword":"", "confirmPassword":"" }`
- Response（Body）：`{ "code": 0 }`
- Notes：后端校验旧密码并加密存储新密码

### 模型服务设置（Model Settings）
- Prefix：`/api/v1`
- Endpoint：`/settings/models`
- Method：`GET` / `PUT`
- Request（Body，PUT）：`{ "providers":[ { "key":"openai", "enabled":true, "apiUrl":"...", "apiKey":"***", "modelName":"gpt-4o-mini", "maxTokens":1024, "temperature":0.2 } ] }`
- Response（Body）：同结构
- Notes：映射 `model.js` 与 `ModelServiceSettings.vue`

### 数据管理路径（Data Settings）
- Prefix：`/api/v1`
- Endpoint：`/settings/data`
- Method：`GET` / `PUT`
- Request（Body，PUT）：`{ "storagePath":"...", "logPath":"...", "kbPath":"..." }`
- Response（Body）：同结构
- Notes：映射 `DataManagementSettings.vue`

### 备份与恢复（Backup Settings & Operations）
- Prefix：`/api/v1`
- Endpoints：
  - 设置：`/settings/backup`（`GET` / `PUT`）
  - 运行：`/backup/run`（`POST`）
  - 列表：`/backup/list`（`GET`）
  - 恢复：`/backup/restore`（`POST`）
- Requests：
  - 设置 Body：`{ "autoBackup":true, "frequency":"daily|weekly|monthly", "time":"HH:mm", "dayOfWeek":1, "dayOfMonth":1, "keepCount":10, "path":"..." }`
  - 恢复 Body：`{ "backupId": "bk-20241010" }`
- Responses：任务与列表结构
- Notes：映射 `BackupRestoreSettings.vue`

### 导出设置（Export Settings）
- Prefix：`/api/v1`
- Endpoint：`/settings/export`
- Method：`GET` / `PUT`
- Request（Body，PUT）：`{ "format":"csv|json", "includeFields":[...], "path":"..." }`
- Response（Body）：同结构
- Notes：映射 `export.js`

### 网络搜索设置（Websearch Settings）
- Prefix：`/api/v1`
- Endpoint：`/settings/websearch`
- Method：`GET` / `PUT`
- Request（Body，PUT）：`{"provider":"bing|google|custom","apiKey":"***","enabled":true}`
- Response（Body）：同结构
- Notes：映射 `webSearch.js`

### 文档处理设置（Docproc Settings）
- Prefix：`/api/v1`
- Endpoint：`/settings/docproc`
- Method：`GET` / `PUT`
- Request（Body，PUT）：`{"providers":[{"key":"paddleocr","enabled":true,"apiUrl":"...","token":"***"}],"languages":["zh","en"]}`
- Response（Body）：同结构
- Notes：映射 `docProcessing.js`

### 系统配置（System Settings）
- Prefix：`/api/v1`
- Endpoint：`/settings/system`
- Method：`GET` / `PUT`
- Request（Body，PUT）：`{"theme":"light|dark","locale":"zh-CN","enablePWA":true}`
- Response（Body）：同结构
- Notes：映射 `SystemConfigSettings.vue`

---

## 文件服务（Files）

### 上传文件（Upload File）
- Prefix：`/api/v1`
- Endpoint：`/files/upload`
- Method：`POST`
- Request（FormData）：`file`
- Response（Body）：`{ "url":"http://...", "expiresIn":600 }`
- Notes：本地存储或 OSS 直传策略

### 获取签名链接（Get Signed URL）
- Prefix：`/api/v1`
- Endpoint：`/files/signed-url`
- Method：`POST`
- Request（Body）：`{ "key":"path/to/object", "method":"GET" }`
- Response（Body）：`{ "url":"http://...", "expiresIn":600 }`
- Notes：如采用 OSS/云存储

---

## 用药（Medications）

### 当前用药列表（Get Current Medications）
- Prefix：`/api/v1`
- Endpoint：`/medications/current`
- Method：`GET`
- Response（Body）：`[ { "name":"Metformin", "dose":"500mg", "frequency":"BID", "route":"PO", "isCurrent":true } ]`
- Notes：供 Dashboard 卡片展示

---

## 字段一致性（Field Consistency）

- `Indicators.vue` 表格：`indicator`, `value`, `unit`, `referenceRange`, `status`, `measureDate`, `category`, `source`, `note`, `isBuiltin`, `favorite` ← `/indicators`
- `IndicatorDetail.vue` 历史：`date`, `value`, `unit`, `status`, `source`, `note`, `admissionFileId` ← `/indicators/{id}/records`
- `IndicatorDetail.vue` 文案：`introductionText` 等 ← `/indicators/{id}/detail`
- `Admissions.vue` 总览/文件：`label/hospital/department/diagnosis/admissionDate/dischargeDate`；文件：`filename/uploadDate/pages/ocrStatus`
- 树：`type=year|month|admission`；`admission` 节点附带 `hospital/department`
- `LLMInterface.vue` 的 `queryConfig` 字段 ↔ `/llm/analyzeMetrics`

---

## 错误与校验（Errors & Validation）

- HTTP：`200/201/204` 成功；`400/401/403/404/422/500` 失败
- 示例（422）：`{ "code": 422, "message": "referenceMin must be <= referenceMax", "data": null, "traceId":"..." }`

---

## 前端对接（Axios & Interceptors）

- 通过 `src/utils/request.js` 注入 `Authorization` 头；统一错误处理
- 后端启用 CORS；暴露 `Authorization`、`traceId`

---

## 示例（Examples）

### 获取指标列表（筛选）
```bash
curl "http://<host>/api/v1/indicators?page=1&pageSize=20&keyword=血&category=血压"
```
```js
axios.get('/api/v1/indicators',{ params:{ page:1, pageSize:20, keyword:'血', category:'血压' }})
```

### 获取我关注的指标（Favorites）
```bash
curl "http://<host>/api/v1/indicators?page=1&pageSize=20&favorites=true"
```
```js
axios.get('/api/v1/indicators',{ params:{ page:1, pageSize:20, favorites:true }})
```

### 新增指标记录
```bash
curl -X POST http://<host>/api/v1/indicators/101/records \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"date":"2025-10-01","value":118,"unit":"mmHg","referenceMin":90,"referenceMax":140,"source":"manual","note":"","admissionFileId":"f-1"}'
```
```js
axios.post('/api/v1/indicators/101/records',{
  date:'2025-10-01', value:118, unit:'mmHg', referenceMin:90, referenceMax:140, source:'manual', admissionFileId:'f-1'
})
```

### 触发 OCR
```bash
curl -X POST http://<host>/api/v1/admissions/adm-1001/files/f-1/ocr \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"language":"zh","engine":"paddleocr"}'
```

### 按住院文件查看指标记录
```bash
curl "http://<host>/api/v1/admissions/adm-1001/files/f-1/indicator-records?page=1&pageSize=50"
```
```js
axios.get('/api/v1/admissions/adm-1001/files/f-1/indicator-records',{ params:{ page:1, pageSize:50 }})
```

---

## 用户-指标关联（User Indicators）
- Prefix：`/api/v1`

### 关注列表（List User Indicators）
- Endpoint：`/user-indicators`
- Method：`GET`
- Request（Query）：`page`, `pageSize`
- Response（Body）：`{ "items": [ { "id": 11, "indicatorId": 101, "alias": "收缩压", "thresholdMin": 90, "thresholdMax": 140, "favorite": true, "createdAt": "YYYY-MM-DD" } ], "total": 3 }`
- Notes：返回当前用户的关注与个性化配置；与 `/indicators?favorites=true` 联动。

### 新增/更新关注（Create/Update User Indicator）
- Endpoint：`/user-indicators`
- Method：`POST` / `PUT`
- Request（Body）：`{ "indicatorId": 101, "alias": "收缩压", "thresholdMin": 90, "thresholdMax": 140, "favorite": true }`
- Response（Body）：`{ "id": 11 }` 或 `{ "code": 0 }`
- Notes：`POST` 新建；`PUT` 更新已存在的同一 `indicatorId` 的配置。

### 取消关注（Delete User Indicator）
- Endpoint：`/user-indicators/{id}`
- Method：`DELETE`
- Response（Body）：`{ "code": 0 }`
- Notes：删除后 `/indicators` 列表不再显示 `favorite=true`。
```js
axios.post('/api/v1/admissions/adm-1001/files/f-1/ocr',{ language:'zh', engine:'paddleocr' })
```

### LLM 指标分析
```js
axios.post('/api/v1/llm/analyzeMetrics',{
  dataScope:'indicators',
  selectedIndicators:['bloodPressure','bloodSugar'],
  dateRange:['2025-07-01','2025-10-01'],
  model:{ provider:'openai', modelName:'gpt-4o-mini', maxTokens:2048, temperature:0.2 }
})
```

---

## 说明与未来扩展（Notes & Future）

- 已覆盖当前前端原型的全部模块。后续可按设计文档扩展：知识库 `/kb`（上传/分块/embedding/search）、多指标对比 `/analysis/indicators/compare` 等。
- 后端存储 `refLow/refHigh` 等细粒度字段；响应中提供聚合字段（如 `referenceRange`）以匹配 UI。
- 文件存储可接入 OSS；建议返回签名 URL 以优化安全与性能。

---

## 补充：未覆盖模块的接口（按功能分组，覆盖 CRUD）

### 用药（Medications）补充
- Prefix：`/api/v1`

- 用药字典列表（Get Medications）
  - Endpoint：`/medications`
  - Method：`GET`
  - Request（Query）：`page`, `pageSize`, `keyword`
  - Response：`{ "items": [ { "id":1, "name":"Metformin", "genericName":"...", "spec":"500mg", "unit":"mg" } ], "total": 12 }`
  - Notes：药物基础字典维护

- 新增/获取/更新/删除用药字典（Create/Get/Update/Delete Medication）
  - Endpoint：`/medications`（`POST`），`/medications/{id}`（`GET` / `PUT` / `DELETE`）
  - Request（Body，POST/PUT）：`{ "name":"", "genericName":"", "spec":"", "unit":"" }`
  - Response：`{ "id": 1 }` 或 `{ "code": 0 }`
  - Notes：避免重复；支持软删除（可选）

- 用药记录列表（List Medication Records）
  - Endpoint：`/medications/{id}/records`
  - Method：`GET`
  - Request（Query）：`page`, `pageSize`, `current=true|false`
  - Response：`{ "items": [ { "recordId":11, "startDate":"YYYY-MM-DD", "endDate":null, "dose":"500mg", "frequency":"BID", "route":"PO", "purpose":"", "notes":"", "isCurrent":true } ], "total": 3 }`
  - Notes：`current=true` 仅返回正在使用的记录

- 新增/更新/删除用药记录（Create/Update/Delete Medication Record）
  - Endpoint：`/medications/{id}/records`（`POST`），`/medications/{id}/records/{recordId}`（`PATCH` / `DELETE`）
  - Request（Body，POST）：`{ "startDate":"YYYY-MM-DD", "endDate":null, "dose":"500mg", "frequency":"BID", "route":"PO", "purpose":"", "notes":"", "isCurrent":true }`
  - Response：`{ "recordId": 11 }` 或 `{ "code":0 }`
  - Notes：`PATCH` 支持部分字段更新

---

## 知识库（Knowledge Base, KB）
- Prefix：`/api/v1`

- 文档列表（List Knowledge Docs）
  - Endpoint：`/kb/docs`
  - Method：`GET`
  - Request（Query）：`page`, `pageSize`, `keyword`, `sourceType=pdf|url`
  - Response：`{ "items": [ { "id":101, "title":"指南A", "sourceType":"pdf", "ossKey":"kb/guideA.pdf", "uploadedAt":"YYYY-MM-DD", "meta":{} } ], "total": 10 }`

- 上传/新增文档（Create Knowledge Doc）
  - Endpoint：`/kb/docs`
  - Method：`POST`
  - Request（FormData 或 JSON）：FormData：`file=<pdf>`；或 JSON：`{ "title":"...", "sourceType":"url", "url":"https://..." }`
  - Response：`{ "id": 101 }`
  - Notes：支持 PDF 上传或 URL 引入

- 获取/更新/删除文档（Get/Update/Delete Knowledge Doc）
  - Endpoint：`/kb/docs/{id}`
  - Method：`GET` / `PUT` / `DELETE`
  - Request（Body，PUT）：`{ "title":"...", "meta":{...} }`
  - Response：`{ "code": 0 }`
  - Notes：删除为软删（可选）

- 构建向量（Build Embeddings）
  - Endpoint：`/kb/docs/{id}/build-embeddings`
  - Method：`POST`
  - Request（Body）：`{ "embeddingProvider":"openai|zhipu", "chunkSize":800, "overlap":100 }`
  - Response：`{ "taskId":"kb-emb-123", "status":"queued" }`
  - Notes：后台异步分块并生成向量

- 分块列表与删除（List/Delete Chunks）
  - Endpoint：`/kb/docs/{id}/chunks`（`GET`），`/kb/chunks/{chunkId}`（`DELETE`）
  - Response：`{ "items": [ { "chunkId": "kc-1", "chunkIndex": 0, "textPreview": "......" } ], "total": 120 }`

- 检索搜索（Search KB）
  - Endpoint：`/kb/search`
  - Method：`POST`
  - Request（Body）：`{ "query":"...", "topK": 8 }`
  - Response：`{ "items": [ { "docId":101, "chunkId":"kc-1", "score":0.82, "text":"...", "title":"指南A" } ] }`
  - Notes：供 LLM/RAG 检索增强

---

## 聊天会话（Chat Sessions & Messages）
- Prefix：`/api/v1`

- 会话列表（List Chat Sessions）
  - Endpoint：`/chat/sessions`
  - Method：`GET`
  - Request（Query）：`page`, `pageSize`
  - Response：`{ "items": [ { "sessionId":"cs-1", "title":"指标分析", "createdAt":"YYYY-MM-DD" } ], "total": 5 }`

- 新建/获取/删除会话（Create/Get/Delete Chat Session）
  - Endpoint：`/chat/sessions`（`POST`），`/chat/sessions/{sessionId}`（`GET` / `DELETE`）
  - Request（Body，POST）：`{ "title":"指标分析" }`
  - Response：`{ "sessionId":"cs-1" }` 或 `{ "code":0 }`
  - Notes：删除会话可级联删除消息（可选）

- 消息列表（List Chat Messages）
  - Endpoint：`/chat/sessions/{sessionId}/messages`
  - Method：`GET`
  - Request（Query）：`page`, `pageSize`
  - Response：`{ "items": [ { "messageId":"m-1", "role":"user|assistant|tool", "content":"...", "createdAt":"YYYY-MM-DD HH:mm" } ], "total": 20 }`

- 发送/更新/删除消息（Send/Update/Delete Message）
  - Endpoint：`/chat/sessions/{sessionId}/messages`（`POST`），`/chat/sessions/{sessionId}/messages/{messageId}`（`PATCH` / `DELETE`）
  - Request（Body，POST）：`{ "role":"user", "content":"...", "toolCalls":[] }`
  - Response：`{ "messageId":"m-1" }` 或 `{ "code":0 }`

---

## 指标分析补充（Analysis Extensions）
- Prefix：`/api/v1`

- 多指标对比（Compare Multiple Indicators）
  - Endpoint：`/analysis/indicators/compare`
  - Method：`GET`
  - Request（Query）：`indicatorIds=1,2,3`, `startDate`, `endDate`
  - Response：`{ "series": { "1": [ { "date":"...", "value": ... } ], "2": [ ... ] }, "stats": { "correlation": { "1-2": 0.63 } } }`

- 异常检测（Detect Abnormal Records）
  - Endpoint：`/analysis/indicators/abnormal`
  - Method：`GET`
  - Request（Query）：`indicatorId`, `startDate`, `endDate`, `method=zscore|threshold`
  - Response：`{ "items": [ { "date":"...", "value": ..., "z": 2.3, "flag": true } ] }`

---

## 住院文件夹（Admission Folders）
- Prefix：`/api/v1`

- 文件夹列表与创建（List/Create Admission Folders）
  - Endpoint：`/admissions/folders`
  - Method：`GET` / `POST`
  - Request（Query，GET）：`page`, `pageSize`, `year`, `month`
  - Request（Body，POST）：`{ "year": 2024, "month": 10 }`
  - Response：`{ "items": [ { "id":"af-1", "year":2024, "month":10 } ], "total": 12 }` 或 `{ "id":"af-1" }`

- 获取/更新/删除文件夹（Get/Update/Delete Folder）
  - Endpoint：`/admissions/folders/{id}`
  - Method：`GET` / `PUT` / `DELETE`
  - Request（Body，PUT）：`{ "year": 2024, "month": 11 }`
  - Response：`{ "code": 0 }`
  - Notes：与树结构联动

---

## 导出任务（Export Tasks）
- Prefix：`/api/v1`

- 触发导出（Run Export Task）
  - Endpoint：`/export/run`
  - Method：`POST`
  - Request（Body）：`{ "format":"csv|json", "scope":"indicators|admissions|medications|all", "filters":{...} }`
  - Response：`{ "taskId":"exp-1", "status":"queued" }`

- 列表/详情/删除（List/Get/Delete Export Tasks）
  - Endpoint：`/export/tasks`（`GET`），`/export/tasks/{taskId}`（`GET` / `DELETE`）
  - Response：`{ "items":[ { "taskId":"exp-1", "status":"done", "downloadUrl":"http://..." } ], "total": 3 }`

---

## 网络搜索（Web Search）
- Prefix：`/api/v1`

- 搜索查询（Search Query）
  - Endpoint：`/websearch/query`
  - Method：`POST`
  - Request（Body）：`{ "query":"...", "provider":"bing|google|custom", "topK": 10 }`
  - Response：`{ "items": [ { "title":"...", "url":"...", "snippet":"..." } ] }`
  - Notes：结合设置中的 provider 与密钥

---

## 模型状态（Model Providers Status）
- Prefix：`/api/v1`

- 状态列表（Providers Status）
  - Endpoint：`/settings/models/status`
  - Method：`GET`
  - Response：`{ "providers": [ { "key":"openai", "status":"ok|failed", "latencyMs": 120, "message":"..." } ] }`

- 连接测试（Test Connection）
  - Endpoint：`/settings/models/test-connection`
  - Method：`POST`
  - Request（Body）：`{ "providerKey":"openai" }`
  - Response：`{ "status":"ok|failed", "latencyMs": 120, "message":"..." }`

---

## 系统健康与日志（System Health & Logs）
- Prefix：`/api/v1`

- 健康与信息（Health & Info）
  - Endpoint：`/system/health`（`GET`），`/system/info`（`GET`）
  - Response：健康状态与版本/依赖信息

- 日志列表/详情/删除（Logs List/Get/Delete）
  - Endpoint：`/system/logs`（`GET`），`/system/logs/{logId}`（`GET` / `DELETE`）
  - Request（Query，logs）：`page`, `pageSize`, `level`, `keyword`, `startDate`, `endDate`
  - Response：日志条目或下载链接

---

## 审计日志（Audit Logs）
- Prefix：`/api/v1`

- 列表与删除（List/Delete Audit Logs）
  - Endpoint：`/audit/logs`（`GET`），`/audit/logs/{id}`（`DELETE`）
  - Request（Query）：`page`, `pageSize`, `userId`, `action`, `entity`
  - Response：`{ "items": [ { "id": "al-1", "userId": 1, "action": "update", "entity": "Indicator", "entityId": 101, "createdAt": "..." } ], "total": 100 }`
  - Notes：后端自动写入；提供查询与删除

---

## OCR 任务（OCR Tasks）
- Prefix：`/api/v1`

- 任务列表/详情/删除（List/Get/Delete OCR Tasks）
  - Endpoint：`/ocr/tasks`（`GET`），`/ocr/tasks/{taskId}`（`GET` / `DELETE`）
  - Request（Query，GET）：`page`, `pageSize`, `status=pending|running|done|failed`
  - Response：`{ "items":[ { "taskId":"ocr-123", "admissionId":"adm-1001", "fileId":"f-1", "status":"running", "createdAt":"..." } ], "total": 8 }`
  - Notes：统一查看与管理 OCR 异步任务

### 更新指标知识信息（Update Indicator Detail）
- Endpoint：`/indicators/{id}/detail`
- Method：`PUT`
- Request（Body）：
  `{ "category":"基础指标", "introductionText":"...", "measurementMethod":"...", "clinicalSignificance":"...", "referenceRange":"...", "unit":"kg", "highMeaning":"...", "lowMeaning":"...", "highAdvice":"...", "lowAdvice":"...", "normalAdvice":"...", "generalAdvice":"..." }`
- Response：`{ "code": 0 }`
- Notes：仅管理员/开发者允许；支持部分字段更新可改为 `PATCH`

---

## 聊天会话（Chat Sessions & Messages）
- Prefix：`/api/v1`

- 会话列表（List Chat Sessions）
  - Endpoint：`/chat/sessions`
  - Method：`GET`
  - Request（Query）：`page`, `pageSize`
  - Response：`{ "items": [ { "sessionId":"cs-1", "title":"指标分析", "createdAt":"YYYY-MM-DD" } ], "total": 5 }`

- 新建/获取/删除会话（Create/Get/Delete Chat Session）
  - Endpoint：`/chat/sessions`（`POST`），`/chat/sessions/{sessionId}`（`GET` / `DELETE`）
  - Request（Body，POST）：`{ "title":"指标分析" }`
  - Response：`{ "sessionId":"cs-1" }` 或 `{ "code":0 }`
  - Notes：删除会话可级联删除消息（可选）

- 消息列表（List Chat Messages）
  - Endpoint：`/chat/sessions/{sessionId}/messages`
  - Method：`GET`
  - Request（Query）：`page`, `pageSize`
  - Response：`{ "items": [ { "messageId":"m-1", "role":"user|assistant|tool", "content":"...", "createdAt":"YYYY-MM-DD HH:mm" } ], "total": 20 }`

- 发送/更新/删除消息（Send/Update/Delete Message）
  - Endpoint：`/chat/sessions/{sessionId}/messages`（`POST`），`/chat/sessions/{sessionId}/messages/{messageId}`（`PATCH` / `DELETE`）
  - Request（Body，POST）：`{ "role":"user", "content":"...", "toolCalls":[] }`
  - Response：`{ "messageId":"m-1" }` 或 `{ "code":0 }`

---

## 指标分析补充（Analysis Extensions）
- Prefix：`/api/v1`

- 多指标对比（Compare Multiple Indicators）
  - Endpoint：`/analysis/indicators/compare`
  - Method：`GET`
  - Request（Query）：`indicatorIds=1,2,3`, `startDate`, `endDate`
  - Response：`{ "series": { "1": [ { "date":"...", "value": ... } ], "2": [ ... ] }, "stats": { "correlation": { "1-2": 0.63 } } }`

- 异常检测（Detect Abnormal Records）
  - Endpoint：`/analysis/indicators/abnormal`
  - Method：`GET`
  - Request（Query）：`indicatorId`, `startDate`, `endDate`, `method=zscore|threshold`
  - Response：`{ "items": [ { "date":"...", "value": ..., "z": 2.3, "flag": true } ] }`

---

## 住院文件夹（Admission Folders）
- Prefix：`/api/v1`

- 文件夹列表与创建（List/Create Admission Folders）
  - Endpoint：`/admissions/folders`
  - Method：`GET` / `POST`
  - Request（Query，GET）：`page`, `pageSize`, `year`, `month`
  - Request（Body，POST）：`{ "year": 2024, "month": 10 }`
  - Response：`{ "items": [ { "id":"af-1", "year":2024, "month":10 } ], "total": 12 }` 或 `{ "id":"af-1" }`

- 获取/更新/删除文件夹（Get/Update/Delete Folder）
  - Endpoint：`/admissions/folders/{id}`
  - Method：`GET` / `PUT` / `DELETE`
  - Request（Body，PUT）：`{ "year": 2024, "month": 11 }`
  - Response：`{ "code": 0 }`
  - Notes：与树结构联动

---

## 导出任务（Export Tasks）
- Prefix：`/api/v1`

- 触发导出（Run Export Task）
  - Endpoint：`/export/run`
  - Method：`POST`
  - Request（Body）：`{ "format":"csv|json", "scope":"indicators|admissions|medications|all", "filters":{...} }`
  - Response：`{ "taskId":"exp-1", "status":"queued" }`

- 列表/详情/删除（List/Get/Delete Export Tasks）
  - Endpoint：`/export/tasks`（`GET`），`/export/tasks/{taskId}`（`GET` / `DELETE`）
  - Response：`{ "items":[ { "taskId":"exp-1", "status":"done", "downloadUrl":"http://..." } ], "total": 3 }`

---

## 网络搜索（Web Search）
- Prefix：`/api/v1`

- 搜索查询（Search Query）
  - Endpoint：`/websearch/query`
  - Method：`POST`
  - Request（Body）：`{ "query":"...", "provider":"bing|google|custom", "topK": 10 }`
  - Response：`{ "items": [ { "title":"...", "url":"...", "snippet":"..." } ] }`
  - Notes：结合设置中的 provider 与密钥

---

## 模型状态（Model Providers Status）
- Prefix：`/api/v1`

- 状态列表（Providers Status）
  - Endpoint：`/settings/models/status`
  - Method：`GET`
  - Response：`{ "providers": [ { "key":"openai", "status":"ok|failed", "latencyMs": 120, "message":"..." } ] }`

- 连接测试（Test Connection）
  - Endpoint：`/settings/models/test-connection`
  - Method：`POST`
  - Request（Body）：`{ "providerKey":"openai" }`
  - Response：`{ "status":"ok|failed", "latencyMs": 120, "message":"..." }`

---

## 系统健康与日志（System Health & Logs）
- Prefix：`/api/v1`

- 健康与信息（Health & Info）
  - Endpoint：`/system/health`（`GET`），`/system/info`（`GET`）
  - Response：健康状态与版本/依赖信息

- 日志列表/详情/删除（Logs List/Get/Delete）
  - Endpoint：`/system/logs`（`GET`），`/system/logs/{logId}`（`GET` / `DELETE`）
  - Request（Query，logs）：`page`, `pageSize`, `level`, `keyword`, `startDate`, `endDate`
  - Response：日志条目或下载链接

---

## 审计日志（Audit Logs）
- Prefix：`/api/v1`

- 列表与删除（List/Delete Audit Logs）
  - Endpoint：`/audit/logs`（`GET`），`/audit/logs/{id}`（`DELETE`）
  - Request（Query）：`page`, `pageSize`, `userId`, `action`, `entity`
  - Response：`{ "items": [ { "id": "al-1", "userId": 1, "action": "update", "entity": "Indicator", "entityId": 101, "createdAt": "..." } ], "total": 100 }`
  - Notes：后端自动写入；提供查询与删除

---

## OCR 任务（OCR Tasks）
- Prefix：`/api/v1`

- 任务列表/详情/删除（List/Get/Delete OCR Tasks）
  - Endpoint：`/ocr/tasks`（`GET`），`/ocr/tasks/{taskId}`（`GET` / `DELETE`）
  - Request（Query，GET）：`page`, `pageSize`, `status=pending|running|done|failed`
  - Response：`{ "items":[ { "taskId":"ocr-123", "admissionId":"adm-1001", "fileId":"f-1", "status":"running", "createdAt":"..." } ], "total": 8 }`
  - Notes：统一查看与管理 OCR 异步任务