# `data_set` 前两周实施进度与产出报告

## 1. 任务范围

本次实施按 [data_set_plan.md](/Users/lilongqi/PycharmProjects/2026/0322/data_set_plan.md:1) 的前两周目标执行，覆盖：

- 第 1 周：数据审计、正式划分、协议冻结
- 第 2 周：样本可视化、训练样本构造、最小 Router 原型

本轮不包含正式模型训练，也不包含 LLM Agent、传统取证模块、融合层与 GRPO。

## 2. 已完成事项总览

### 2.1 第 1 周完成内容

- 完成 `data_set` 的 manifest、sample_records、question_records 与 schema 校验
- 完成图像路径完整性检查
- 完成样本与问题映射关系检查
- 完成 5 类样本统计和问题类型统计
- 生成正式 `train / val / test` 划分
- 冻结 Router 输出 schema
- 冻结 Tool 结果 schema 的 V1 版本

### 2.2 第 2 周完成内容

- 完成样本可视化脚本
- 完成分类型预览图导出
- 完成分类训练样本构造
- 完成定位训练样本构造
- 完成 Router SFT 样本构造
- 完成最小 Router 原型
- 完成 Router 输出的 schema 校验

## 3. 新增代码与协议文件

### 3.1 公共与数据模块

- [src/common/json_io.py](/Users/lilongqi/PycharmProjects/2026/0322/src/common/json_io.py:1)
- [src/data/unified_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/src/data/unified_dataset.py:1)

主要作用：

- 统一读取 `manifest / sample_records / question_records`
- 统一 schema 校验
- 统一样本路径解析
- 统一样本摘要生成
- 统一 split 生成
- 统一分类、定位、SFT 数据集构造
- 统一最小 Router 目标生成

### 3.2 Router 原型

- [src/router/router_v1.py](/Users/lilongqi/PycharmProjects/2026/0322/src/router/router_v1.py:1)

当前实现说明：

- 这是一个**元数据驱动的启发式 Router 原型**
- 目标是先打通结构化路由协议和后续训练样本格式
- 不是正式视觉推理模型

### 3.3 脚本层

- [scripts/audit_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/audit_dataset.py:1)
- [scripts/make_splits.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/make_splits.py:1)
- [scripts/build_cls_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/build_cls_dataset.py:1)
- [scripts/build_loc_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/build_loc_dataset.py:1)
- [scripts/build_sft_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/build_sft_dataset.py:1)
- [scripts/visualize_sample.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/visualize_sample.py:1)
- [scripts/export_previews.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/export_previews.py:1)
- [scripts/run_router_v1.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/run_router_v1.py:1)

### 3.4 协议文件

- [protocols/router_output_v1.schema.json](/Users/lilongqi/PycharmProjects/2026/0322/protocols/router_output_v1.schema.json:1)
- [protocols/tool_result_v1.schema.json](/Users/lilongqi/PycharmProjects/2026/0322/protocols/tool_result_v1.schema.json:1)

说明：

- `router_output_v1` 已完全对齐 `data_set` 的标签空间
- `tool_result_v1` 修正了旧版 `tool_result.schema.json` 中 `splicing / fully_generated` 与当前计划不一致的问题，改为 `splice / aigc_global`

## 4. 实际执行结果

### 4.1 数据审计结果

执行脚本：

```bash
python scripts/audit_dataset.py
```

输出文件：

- [artifacts/audit/data_audit_report.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/audit/data_audit_report.json:1)
- [artifacts/audit/data_audit_report.md](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/audit/data_audit_report.md:1)

关键结果：

- 样本总数：`25`
- 问题总数：`647`
- 类型分布：
  - `copy_move`: `5`
  - `splice`: `5`
  - `inpainting_removal`: `5`
  - `inpainting_replacement`: `5`
  - `aigc_global`: `5`
- 任务模式分布：
  - `classification_localization`: `20`
  - `classification`: `5`
- 发现的问题数：`0`

结论：

- 当前 `data_set` 可直接作为前两周实施的正式数据基础
- 路径、结构、问题映射都没有阻塞性错误

### 4.2 正式 split 结果

执行脚本：

```bash
python scripts/make_splits.py
```

输出文件：

- [artifacts/splits/train.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/splits/train.json:1)
- [artifacts/splits/val.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/splits/val.json:1)
- [artifacts/splits/test.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/splits/test.json:1)

划分策略：

- 每类 5 个样本
- `train`: 每类 3 个，共 `15`
- `val`: 每类 1 个，共 `5`
- `test`: 每类 1 个，共 `5`

当前划分结果：

- `train`: `15`
- `val`: `5`
- `test`: `5`

### 4.3 分类训练样本

执行脚本：

```bash
python scripts/build_cls_dataset.py
```

输出文件：

- [artifacts/datasets/classification_dataset.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/datasets/classification_dataset.jsonl:1)

记录数：

- `25`

字段包含：

- `sample_id`
- `split`
- `image_path`
- `source_dataset`
- `task_mode`
- `label_l1`
- `label_l2`
- `metadata_summary`

说明：

- 已自动注入正式 `train / val / test`，不再使用原始 `demo`

### 4.4 定位训练样本

执行脚本：

```bash
python scripts/build_loc_dataset.py
```

输出文件：

- [artifacts/datasets/localization_dataset.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/datasets/localization_dataset.jsonl:1)

记录数：

- `20`

说明：

- 仅包含 `classification_localization` 的 4 类局部篡改样本
- `aigc_global` 被正确排除

### 4.5 Router SFT 样本

执行脚本：

```bash
python scripts/build_sft_dataset.py
```

输出文件：

- [artifacts/datasets/router_sft_dataset.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/datasets/router_sft_dataset.jsonl:1)

记录数：

- `25`

字段包含：

- `sample_id`
- `split`
- `image_path`
- `input`
- `target`

其中：

- `input` 包含任务模式、来源数据集、元数据摘要、问题预览
- `target` 为结构化 Router 输出目标

### 4.6 样本可视化与预览

执行脚本：

```bash
python scripts/export_previews.py
python scripts/visualize_sample.py 100000
python scripts/visualize_sample.py 500000
```

输出文件：

- [artifacts/previews/preview_copy_move.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_copy_move.png)
- [artifacts/previews/preview_splice.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_splice.png)
- [artifacts/previews/preview_inpainting_removal.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_inpainting_removal.png)
- [artifacts/previews/preview_inpainting_replacement.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_inpainting_replacement.png)
- [artifacts/previews/preview_aigc_global.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_aigc_global.png)
- [artifacts/previews/100000.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/100000.png)
- [artifacts/previews/500000.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/500000.png)

说明：

- 已补充本地 `MPLCONFIGDIR`，避免 `matplotlib` 默认缓存目录不可写
- macOS 字体系统仍会打印 `XType` 警告，但不影响产物生成

### 4.7 最小 Router 原型输出

执行脚本：

```bash
python scripts/run_router_v1.py
```

输出文件：

- [artifacts/router/router_v1_outputs.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/router/router_v1_outputs.jsonl:1)

记录数：

- `25`

校验结果：

- 已对 [protocols/router_output_v1.schema.json](/Users/lilongqi/PycharmProjects/2026/0322/protocols/router_output_v1.schema.json:1) 完成校验
- 通过数：`25 / 25`

当前 Router 原型特性：

- 输出 `task_mode`
- 输出 `coarse_label`
- 输出 `coarse_type_candidates`
- 输出 `tool_candidates`
- 输出 `reasoning_summary`

局限：

- 当前基于 `sample_record` 元数据规则，不是视觉模型
- 当前用于协议打通、样本准备和后续训练前的基线占位

## 5. 当前产物清单

### 5.1 代码文件

- [src/common/json_io.py](/Users/lilongqi/PycharmProjects/2026/0322/src/common/json_io.py:1)
- [src/data/unified_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/src/data/unified_dataset.py:1)
- [src/router/router_v1.py](/Users/lilongqi/PycharmProjects/2026/0322/src/router/router_v1.py:1)
- [scripts/audit_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/audit_dataset.py:1)
- [scripts/make_splits.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/make_splits.py:1)
- [scripts/build_cls_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/build_cls_dataset.py:1)
- [scripts/build_loc_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/build_loc_dataset.py:1)
- [scripts/build_sft_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/build_sft_dataset.py:1)
- [scripts/visualize_sample.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/visualize_sample.py:1)
- [scripts/export_previews.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/export_previews.py:1)
- [scripts/run_router_v1.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/run_router_v1.py:1)

### 5.2 协议文件

- [protocols/router_output_v1.schema.json](/Users/lilongqi/PycharmProjects/2026/0322/protocols/router_output_v1.schema.json:1)
- [protocols/tool_result_v1.schema.json](/Users/lilongqi/PycharmProjects/2026/0322/protocols/tool_result_v1.schema.json:1)

### 5.3 实际生成产物

- [artifacts/audit/data_audit_report.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/audit/data_audit_report.json:1)
- [artifacts/audit/data_audit_report.md](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/audit/data_audit_report.md:1)
- [artifacts/splits/train.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/splits/train.json:1)
- [artifacts/splits/val.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/splits/val.json:1)
- [artifacts/splits/test.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/splits/test.json:1)
- [artifacts/datasets/classification_dataset.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/datasets/classification_dataset.jsonl:1)
- [artifacts/datasets/localization_dataset.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/datasets/localization_dataset.jsonl:1)
- [artifacts/datasets/router_sft_dataset.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/datasets/router_sft_dataset.jsonl:1)
- [artifacts/router/router_v1_outputs.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/router/router_v1_outputs.jsonl:1)
- [artifacts/previews/preview_copy_move.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_copy_move.png)
- [artifacts/previews/preview_splice.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_splice.png)
- [artifacts/previews/preview_inpainting_removal.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_inpainting_removal.png)
- [artifacts/previews/preview_inpainting_replacement.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_inpainting_replacement.png)
- [artifacts/previews/preview_aigc_global.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_aigc_global.png)
- [artifacts/previews/100000.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/100000.png)
- [artifacts/previews/500000.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/500000.png)

## 6. 验收情况

### 6.1 第 1 周验收

- JSON schema 校验通过：`是`
- 路径存在率：`100%`
- 样本与问题映射错误数：`0`
- `train / val / test` 划分已生成：`是`
- 每类样本都进入 3 个 split：`是`

### 6.2 第 2 周验收

- 样本可视化可运行：`是`
- 分类训练样本构造完成：`是`
- 定位训练样本构造完成：`是`
- Router SFT 样本构造完成：`是`
- Router 原型输出完成：`是`
- Router 输出 schema 校验通过：`25 / 25`

## 7. 发现的问题与处理

### 7.1 原始 `sample_record` 的 `split` 为 `demo`

问题：

- 直接拿原始 `sample_record` 构造训练样本时，`split` 会保留为 `demo`

处理：

- 在数据集构造逻辑中显式应用第 1 周生成的 deterministic split
- 现在导出的分类、定位、SFT 数据集都已经写成 `train / val / test`

### 7.2 `tool_result.schema.json` 标签空间与当前计划不一致

问题：

- 旧文件仍使用 `splicing`、`fully_generated`
- 当前计划与 `data_set` 实际使用 `splice`、`aigc_global`

处理：

- 新增 [protocols/tool_result_v1.schema.json](/Users/lilongqi/PycharmProjects/2026/0322/protocols/tool_result_v1.schema.json:1)
- 后续 Agent 与工具统一对齐 V1 schema

### 7.3 `matplotlib` 默认缓存目录不可写

问题：

- 可视化脚本首次运行时会告警

处理：

- 在脚本里设置 `MPLCONFIGDIR=artifacts/mplconfig`
- 当前产物生成不受影响

## 8. 当前仍未开始的部分

以下工作还未实施，属于第 3 周之后内容：

- 分类模型训练
- LLM Agent 接入
- 传统取证模块接入
- 定位模型训练
- Router SFT 训练
- 多轮调度器
- 融合器
- QA 生成器
- 报告生成器
- GRPO

## 9. 建议的下一步

按计划进入第 3 周时，优先顺序建议固定为：

1. 训练 `l1 + l2` 分类基线
2. 接入 `ForgeryGPT-Agent` 和 `FakeShield-Agent` 的最小适配层
3. 统一 Agent 输出到 `tool_result_v1`
4. 基于当前 Router 输出与分类结果，开始搭批量推理骨架
