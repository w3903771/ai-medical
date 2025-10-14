# 医疗数据管理项目文档（中文）

本仓库包含一个医疗数据管理系统的演示版本，提供指标管理、住院档案、用药记录等核心能力。更多细节请参考：

- 项目概览与使用：`../README.md`
- 接口文档：`./api.md`
- 系统设计：`./design.md`
- 数据库设计：`./database_design.md`

## 快速开始
- 后端：进入 `medical-back`，安装依赖并运行 `python main.py`
- 前端：进入 `medical-front`，安装依赖并运行 `npm run dev`

## 目录
- 指标与记录：Indicator、IndicatorRecord
- 住院管理：AdmissionFolder、Admission、AdmissionFile
- 用药管理：Medication、MedicationRecord

如需英文文档请查看 `./README.en.md`。