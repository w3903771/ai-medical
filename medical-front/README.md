# 医疗数据管理平台 - 前端项目

## 项目简介

这是一个基于 Vue 3 的医疗数据管理平台前端项目，采用现代化的技术栈和扁平化设计风格，为医疗数据的管理、分析和可视化提供直观易用的用户界面。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **UI 组件库**: Element Plus
- **HTTP 客户端**: Axios
- **图标**: Element Plus Icons
- **图表**: ECharts + Vue-ECharts

## 项目特性

### 🎨 设计特色
- 扁平化设计风格
- 响应式布局，支持多种设备
- 现代化的 UI 组件
- 流畅的动画效果
- 一致的视觉体验

### 📱 页面功能
- **Dashboard 首页**: 健康指标卡片、异常数据提醒、用药信息、健康建议
- **指标数据管理**: 数据表格展示、右键菜单操作、多选批量处理
- **住院管理**: 树形结构导航、标签页内容展示、PDF 文档管理
- **大模型界面**: AI 对话交互、数据范围选择、智能分析
- **设置中心**: 账号管理、数据导入导出、系统配置

### 🛠️ 技术特性
- 组件化开发
- TypeScript 支持（可选）
- 模块化状态管理
- 统一的 API 请求处理
- 自动化路由配置
- 主题定制支持

## 项目结构

```
medical-front/
├── src/
│   ├── layout/             # 布局组件
│   │   └── Layout.vue      # 主布局
│   ├── router/             # 路由配置
│   │   └── index.js        # 路由定义
│   ├── stores/             # 状态管理（多模块）
│   │   ├── account.js
│   │   ├── backup.js
│   │   ├── dataManagement.js
│   │   ├── docProcessing.js
│   │   ├── export.js
│   │   ├── model.js
│   │   ├── settings.js
│   │   ├── system.js
│   │   ├── user.js
│   │   └── webSearch.js
│   ├── utils/              # 工具函数
│   │   └── request.js      # API 请求配置
│   ├── views/              # 页面组件
│   │   ├── Admissions.vue      # 住院管理
│   │   ├── Dashboard.vue       # 首页
│   │   ├── IndicatorDetail.vue # 指标详情
│   │   ├── Indicators.vue      # 指标数据
│   │   ├── LLMInterface.vue    # 大模型界面
│   │   ├── Settings.vue        # 设置页面
│   │   └── settings/           # 设置子页面目录
│   ├── App.vue             # 根组件
│   ├── main.js             # 应用入口
│   └── style.css           # 全局样式
├── index.html              # HTML 模板
├── package.json            # 项目配置
├── vite.config.js          # Vite 配置
└── README.md               # 项目说明
```

## 快速开始

### 环境要求
- Node.js >= 16.0.0
- npm >= 7.0.0 或 yarn >= 1.22.0

### 安装依赖

```bash
# 使用 npm
npm install

# 或使用 yarn
yarn install
```

### 开发环境启动

```bash
# 启动开发服务器
npm run dev

# 或使用 yarn
yarn dev
```

项目将在 `http://localhost:3000` 启动

### 构建生产版本

```bash
# 构建生产版本
npm run build

# 或使用 yarn
yarn build
```

### 预览生产版本

```bash
# 预览构建结果
npm run preview

# 或使用 yarn
yarn preview
```

## 页面说明

### 1. Dashboard 首页
- 展示关键健康指标（体重、血压、血糖）
- 显示最近异常数据提醒
- 当前用药信息卡片
- AI 生成的健康建议

### 2. 指标数据页面
- 数据表格展示，支持时间区间筛选
- 右键菜单：新增、删除、修改、查看变化、调用大模型
- 多选行进行联合分析
- 数据导入导出功能
- 配有指标详情页面（IndicatorDetail.vue）以查看单项指标的详细信息

### 3. 住院管理页面
- 左侧：年-月-住院记录的树形结构
- 右侧：住院信息、PDF 阅读、PDF 上传标签页
- 内嵌 PDF.js 支持文档预览

### 4. 大模型界面
- 对全量数据进行智能问答
- 支持选择数据范围（全部/某指标/某住院档案）
- 检索增强生成 (RAG) 功能
- 对话历史管理

### 5. 设置页面
- 账号信息管理
- 数据导入导出
- 系统备份与恢复
- 个性化配置

## 开发指南

### 添加新页面
1. 在 `src/views/` 目录下创建新的 Vue 组件
2. 在 `src/router/index.js` 中添加路由配置
3. 在 `src/layout/Layout.vue` 中添加导航菜单项

### 状态管理
使用 Pinia 进行状态管理，在 `src/stores/` 目录下创建对应的 store 文件。

### API 请求
所有 API 请求通过 `src/utils/request.js` 中配置的 Axios 实例进行，支持：
- 统一的请求/响应拦截
- 自动 token 处理
- 错误处理和提示

#### 接口前缀与代理
- 前端请求基础地址为 `'/api/v1'`，与后端统一。
- 开发环境已在 `vite.config.js` 配置代理，将 `'/api/v1'` 代理到后端 `http://127.0.0.1:8001`。
- 如需自定义后端地址，可修改 `vite.config.js` 的 `server.proxy` 配置或使用环境变量 `VITE_API_BASE_URL`（后续可接入）。

### 鉴权与多用户
- 登录与注册：前端提供 `Login.vue` 与 `Register.vue` 页面，路由分别为 `/login` 与 `/register`。
- 令牌存储：登录成功后将 `token` 存入 `localStorage`，并在请求拦截器中自动附加 `Authorization: Bearer <token>`。
- 路由守卫：未登录访问受保护页面时自动重定向至 `/login`；登录后访问 `/login` 会重定向至首页。
 - 401 处理：响应拦截器在收到 `401` 时清除本地令牌并跳转到 `/login`；默认错误提示优先显示后端 `detail` 字段。
 - 返回结构：后端当前返回原始 JSON（无统一 `{code,message,data}` 包裹）；拦截器已兼容两种形式。
 - 用户信息：应用启动时在 `App.vue` 调用 `userStore.initUserInfo()`，从本地令牌恢复并通过 `/account/profile` 初始化用户信息。
 
 #### 前端 Pinia 状态与交互
 - `useUserStore`：管理 `userInfo` 与 `isLoggedIn`；动作包括：
   - `login` → `POST /auth/login`；成功后保存 `token` 并设置用户信息。
   - `register` → `POST /auth/register`；请求体包含 `username,name,email,password`。
   - `initUserInfo`/`fetchProfile` → `GET /account/profile`；用于会话恢复与资料拉取。
   - `updateProfile` → `PUT /account/profile`；支持 `email/name/gender/birthDate`；返回 `{success:true}` 后刷新资料。
   - `changePassword` → `PUT /account/password`；请求体 `{oldPassword,newPassword}`；返回 `{success:true}`。
   - `logout` → `POST /auth/logout`（无状态）；清理前端令牌与用户信息并跳转登录。
 - `request.js`：`baseURL=/api/v1`；自动注入 `Bearer token`；401 自动清理并重定向；错误提示兼容 `message/detail`。
 - 路由守卫：基于 `userStore.isLoggedIn` 与 `route.meta.public` 控制访问；首次导航支持基于本地令牌的快速恢复。
- 后端接口：详见 `docs/api.md` 的“鉴权（Auth）”章节，包括登录、注册、刷新令牌、用户资料与密码修改。

#### 开发阶段 Mock 账号
- 若后端未启动或未实现鉴权，前端支持一个内置管理员账号用于联调：
  - 用户名：`admin`
  - 密码：`admin`
- 使用该账号登录会在本地注入 `token` 并设置 `role=admin`，仅用于开发演示，生产环境请接入真实后端接口。

### 样式定制
- 全局样式在 `src/style.css` 中定义
- 使用 CSS 变量进行主题定制
- 支持响应式设计

## 命名规范（camelCase）

为统一项目的函数、变量与参数命名，采用统一的驼峰命名规范：

- 总则
  - 全局统一使用 `camelCase` 命名函数、变量、参数、路由名称、Pinia 状态与动作；组件文件使用 `PascalCase`。
  - 使用有意义的英文单词，避免不必要缩写；约定俗成缩写可用：`id`, `URL`, `API`, `HTML`, `OCR`。
  - 命名长度适中，能体现职责与作用。

- 函数命名
  - 动词开头：`get`、`set`、`create`、`update`、`delete`、`fetch`、`load`、`save`、`render`、`handle`。
  - 布尔函数前缀：`is`、`has`、`can`、`should`（例如：`isLoading`、`hasError`）。
  - 事件处理统一 `handleXxx`（例如：`handleRowClick`、`handleUploadError`）。
  - 异步函数可后缀 `Async`（例如：`fetchAdmissionsAsync`）。
  - 工具/领域函数以领域名+动作（例如：`formatDate`、`calculateDays`、`buildQueryParams`）。

- 变量命名
  - 名词或名词短语（例如：`admissionsList`、`selectedAdmission`、`activeTab`）。
  - 布尔变量使用 `is`、`has`、`can`、`should` 前缀（例如：`isExpanded`、`hasToken`）。
  - 集合使用复数（例如：`files`、`users`）；映射使用 `Map` 后缀（例如：`userMap`）。
  - 计数器/索引使用语义化名称（例如：`count`、`index`），避免无语义的单字母变量。
  - 常量仍使用 `camelCase`；环境变量使用 `UPPER_SNAKE_CASE`（例如：`VITE_API_BASE_URL`）。

- 参数命名
  - 使用清晰参数名（例如：`id`、`page`、`pageSize`、`startDate`、`endDate`）。
  - 选项对象参数命名为 `options` 或场景化（例如：`requestOptions`、`uploadOptions`）。
  - 事件对象统一使用 `event`；回调统一使用 `onXxx`（例如：`onSuccess`、`onError`）。

- Vue 组件、Props 与 Emits
  - 组件文件与组件名使用 `PascalCase`（例如：`Admissions.vue`、`LLMInterface.vue`）。
  - 组件内部变量与方法使用 `camelCase`。
  - Props 在 JS 中使用 `camelCase`，在模板中使用 `kebab-case`（例如：`modelValue` 对应 `model-value`）。
  - Emits 事件遵循内置约定（如 `update:modelValue`）；自定义建议使用 `xxx-change`、`xxx-submit`。
  - `ref` 变量以 `xxxRef`；`reactive` 状态以领域名+`State`（例如：`treeRef`、`admissionForm`、`uploadState`）。
  - `computed` 使用名词或可加 `Computed` 后缀（例如：`providerStatusText`）。

- Pinia Store
  - Store id 使用小写无空格（例如：`'user'`、`'dataManagement'`）。
  - 导出函数使用 `useXxxStore`（例如：`useUserStore`、`useDataManagementStore`）。
  - State/Getter/Action 使用 `camelCase`（例如：`storageInfo`、`saveDataSettings`、`clearCache`）。
  - 文件名与 store 名一致（例如：`dataManagement.js` 导出 `useDataManagementStore`）。

- 路由命名
  - 路由 `path` 使用 `kebab-case`（例如：`/llm-interface`、`/admissions`）。
  - 路由 `name` 使用 `camelCase`（例如：`llmInterface`、`admissions`）。
  - 路由参数与查询键使用 `camelCase`（例如：`pdfId`、`admissionId`）。

- API 与工具函数
  - Axios 实例命名为 `http` 或 `request`；接口函数采用动词+资源（例如：`getAdmissions`、`uploadFile`）。
  - 拦截器与工具以动词开头（例如：`setAuthToken`、`handleResponseError`）。

- 文件与目录
  - 组件文件使用 `PascalCase`；非组件文件使用 `camelCase`（例如：`dataManagement.js`、`request.js`）。
  - 目录使用小写无空格，集合使用复数（例如：`stores`、`views`）。

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 后续开发计划

- [ ] 知识库管理功能
- [ ] PDF 文档智能解析
- [ ] 数据可视化图表
- [ ] 移动端适配优化
- [ ] 离线功能支持 (PWA)
- [ ] 多语言国际化
- [ ] 单元测试覆盖

## 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至项目维护者

---

**注意**: 本项目目前仅实现了页面结构和基础交互，具体的业务逻辑和后端接口集成需要在后续开发中完善。