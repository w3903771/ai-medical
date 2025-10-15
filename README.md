<div align="right">
  <details>
    <summary>🌐 Language</summary>
    <div>
      <div align="right">
        <p><a href="./docs/README.zh.md">简体中文</a></p>
        <p><a href="./docs/README.en.md">English</a></p>
      </div>
    </div>
  </details>
</div>

<h1 align="center">
  <a href="https://github.com/w3903771/ai-medical">
    <img src="https://img.shields.io/badge/Medical%20Demo-blue?style=for-the-badge" width="150" height="150" alt="banner" /><br>
  </a>
</h1>

 <p align="center">简体中文 | <a href="./docs/README.en.md">English</a> | <a href="https://github.com/w3903771/ai-medical/issues">反馈</a> | <a href="./docs/api.md">API 文档</a> | <a href="./docs/design.md">设计文档</a> | <a href="./docs/database_design.md">数据库设计</a> | <a href="./medical-back/README.md">后端开发</a> | <a href="./medical-front/README.md">前端开发</a></p>



 <div align="center">
   <img src="https://img.shields.io/github/stars/w3903771/ai-medical?style=for-the-badge" />
   <img src="https://img.shields.io/github/forks/w3903771/ai-medical?style=for-the-badge" />
   <img src="https://img.shields.io/github/issues/w3903771/ai-medical?style=for-the-badge" />
   <img src="https://img.shields.io/github/license/w3903771/ai-medical?style=for-the-badge" />
 </div>

 <div align="center">
   <img src="https://img.shields.io/github/last-commit/w3903771/ai-medical?style=for-the-badge" />
   <img src="https://img.shields.io/github/languages/top/w3903771/ai-medical?style=for-the-badge" />
   <img src="https://img.shields.io/github/repo-size/w3903771/ai-medical?style=for-the-badge" />
 </div>

---

# Github Stats
 <div align="center">
    ​​​​<img src="https://github-readme-stats.vercel.app/api?username=w3903771&show_icons=true" />
 </div>
 
# 🏥 医疗数据管理项目 Demo

本项目是一个医疗数据管理系统的演示版本，旨在为医疗机构提供高效的数据管理解决方案。项目包含前后端代码及相关设计文档，支持住院管理、病历管理等核心功能。

---

## 📦 项目结构

```
medical/
├── docs/                # 设计文档、API文档、数据库设计
├── medical-back/        # 后端服务（Python FastAPI）
├── medical-front/       # 前端应用（Vue3 + Vite）
```

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/w3903771/ai-medical.git
```

### 2. 后端启动
```bash
cd medical-back
pip install -r requirements.txt
python main.py
```

### 3. 前端启动
```bash
cd medical-front
npm install
npm run dev
```

---

## 📚 文档说明
- 设计文档、API接口、数据库设计请见 `docs/` 目录。

---

## 🛠 技术栈
- 后端：Python FastAPI
- 前端：Vue3 + Vite
- 数据库：可扩展（设计文档中有详细说明）

---

## 🌟 项目亮点
1. 住院管理、病历管理等核心医疗数据功能
2. 前后端分离，易于扩展和维护
3. 详细的数据库设计与API文档
4. 支持多端部署，适配医疗机构实际需求

---

## 🧩 核心功能
- 指标管理与记录：`Indicator`、`IndicatorRecord`、用户关注与个性化（`UserIndicator`）
- 住院档案管理：`AdmissionFolder` 年/月分组、`Admission` 住院记录、`AdmissionFile` 文件与 OCR 结果
- 用药管理：`Medication` 药物字典、`MedicationRecord` 当前/历史用药
- 趋势与分析：基础统计、趋势与异常检测（接口见 `docs/api.md` 分析章节）
- 权限与审计：多用户行级隔离、软删除与可审计字段设计

---

## 🤝 贡献指南
欢迎提交 Issue 或 Pull Request 共同完善项目。

---

## 📄 License
GPL-3.0 License