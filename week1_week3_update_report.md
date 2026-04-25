# `data_set_v2` 周 1-3 更新、进度与结果

## 1. 本次更新范围

本次工作以 `data_set_v2` 为默认数据源，完成了两部分内容：

- 更新第 1-2 周已有代码与产物，使其从旧的 `data_set` demo 切换到 `data_set_v2`
- 完成第 3 周的最小可运行闭环：分类基线训练、分类推理脚本、首批 Agent 适配层与缓存结果

当前代码默认优先读取：

- [data_set_v2/README.md](/Users/lilongqi/PycharmProjects/2026/0322/data_set_v2/README.md:1)
- [data_set_v2/dataset_manifest.json](/Users/lilongqi/PycharmProjects/2026/0322/data_set_v2/dataset_manifest.json:1)
- [data_set_v2/sample_records.json](/Users/lilongqi/PycharmProjects/2026/0322/data_set_v2/sample_records.json:1)
- [data_set_v2/question_records.json](/Users/lilongqi/PycharmProjects/2026/0322/data_set_v2/question_records.json:1)

## 2. 对原计划的修正

`data_set_weekly_plan.docx` 的目标方向保留，但以下地方已按当前仓库实际情况修正：

1. `data_set_v2` 当前实际不是 35000 样本大版本，而是 60 样本子集。
2. 当前真实样本不是 15000 条，而是 `600000-600009` 这 10 条。
3. 当前 `authentic` 全部派生自 `CM_dataset`，还没有覆盖 `splice` 和两类 `inpainting`。
4. 第 3 周中的 “FakeShield-Agent / ForgeryGPT-Agent 接入” 目前落地为本地结构化适配层和缓存机制，而不是外部 API 联调版。
5. 第 3 周中的“分类基线训练”目前落地为轻量图像近邻基线，优先保证可训练、可推理、可复现实验。

## 3. 第 1-2 周更新结果

### 3.1 数据层与协议

已更新文件：

- [src/data/unified_dataset.py](/Users/lilongqi/PycharmProjects/2026/0322/src/data/unified_dataset.py:1)
- [src/common/json_io.py](/Users/lilongqi/PycharmProjects/2026/0322/src/common/json_io.py:1)
- [protocols/router_output_v1.schema.json](/Users/lilongqi/PycharmProjects/2026/0322/protocols/router_output_v1.schema.json:1)
- [protocols/tool_result_v1.schema.json](/Users/lilongqi/PycharmProjects/2026/0322/protocols/tool_result_v1.schema.json:1)

主要改动：

- 默认优先读取 `data_set_v2`
- 兼容 `dataset_manifest.json` / `sample_records.json` / `question_records.json` 新布局
- 把 `authentic / none` 纳入分类集、SFT 集和 Router 目标
- 新 split 逻辑按“原样本 + 派生真实样本”成组划分，避免泄漏
- Router 输出协议新增 `none` 候选
- Tool 结果协议新增 `none` 支持

### 3.2 重建后的周 1-2 产物

已重新生成：

- 审计报告：[artifacts/audit/data_audit_report.md](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/audit/data_audit_report.md:1)
- split 文件：[artifacts/splits/train.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/splits/train.json:1)、[val.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/splits/val.json:1)、[test.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/splits/test.json:1)
- 分类数据集：[artifacts/datasets/classification_dataset.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/datasets/classification_dataset.jsonl:1)
- 定位数据集：[artifacts/datasets/localization_dataset.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/datasets/localization_dataset.jsonl:1)
- Router SFT 数据集：[artifacts/datasets/router_sft_dataset.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/datasets/router_sft_dataset.jsonl:1)
- Router 原型输出：[artifacts/router/router_v1_outputs.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/router/router_v1_outputs.jsonl:1)
- 可视化预览：[artifacts/previews/preview_none.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_none.png)、[100000.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/100000.png)、[500000.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/500000.png)、[600000.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/600000.png)

当前统计：

- 样本数：`60`
- 问答数：`1313`
- `train / val / test`：`36 / 12 / 12`
- 分类样本：`60`
- 定位样本：`40`
- Router SFT 样本：`60`

配对安全划分已验证，例如：

- `100000` 与 `600000` 同属 `train`
- `100006` 与 `600006` 同属 `val`
- `100009` 与 `600009` 同属 `test`

## 4. 第 3 周完成结果

### 4.1 分类基线

新增文件：

- [src/classification/baseline_v1.py](/Users/lilongqi/PycharmProjects/2026/0322/src/classification/baseline_v1.py:1)
- [scripts/train_cls_baseline.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/train_cls_baseline.py:1)
- [scripts/run_cls_inference.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/run_cls_inference.py:1)

产物：

- 模型目录：[artifacts/models/classifier_baseline_v1](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/models/classifier_baseline_v1)
- 指标文件：[artifacts/models/classifier_baseline_v1/metrics.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/models/classifier_baseline_v1/metrics.json:1)
- 批量推理结果：[artifacts/classification/classification_predictions.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/classification/classification_predictions.jsonl:1)
- 单样本推理结果：[artifacts/classification/600000_prediction.json](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/classification/600000_prediction.json:1)
- 训练日志：[logs/classifier_baseline_v1_train.log](/Users/lilongqi/PycharmProjects/2026/0322/logs/classifier_baseline_v1_train.log:1)
- 批量推理日志：[logs/classifier_baseline_v1_inference.log](/Users/lilongqi/PycharmProjects/2026/0322/logs/classifier_baseline_v1_inference.log:1)
- 单样本推理日志：[logs/classifier_baseline_v1_inference_600000.log](/Users/lilongqi/PycharmProjects/2026/0322/logs/classifier_baseline_v1_inference_600000.log:1)

当前基线指标：

- 全集 `l1_accuracy = 0.55`
- 全集 `l2_accuracy = 0.516667`
- `test` 集 `l1_accuracy = 0.333333`
- `test` 集 `l2_accuracy = 0.333333`

说明：

- 这是一个轻量近邻图像基线，不是正式深度分类器
- 当前作用是给第 3 周提供可训练、可加载、可批推理的闭环起点
- 日志中额外记录了样本规模、split 分布、标签分布、总体指标、分 split 指标和部分误判样本

### 4.2 首批 Agent 适配层与缓存

新增文件：

- [src/agents/cache.py](/Users/lilongqi/PycharmProjects/2026/0322/src/agents/cache.py:1)
- [src/agents/fakeshield_agent.py](/Users/lilongqi/PycharmProjects/2026/0322/src/agents/fakeshield_agent.py:1)
- [src/agents/forgerygpt_agent.py](/Users/lilongqi/PycharmProjects/2026/0322/src/agents/forgerygpt_agent.py:1)
- [scripts/run_agent_adapters.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/run_agent_adapters.py:1)

产物：

- Agent 结果：[artifacts/agents/agent_results.jsonl](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/agents/agent_results.jsonl:1)
- 工具缓存目录：[artifacts/cache/tool_results](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/cache/tool_results)
- Agent 总日志：[logs/agent_adapters_run.log](/Users/lilongqi/PycharmProjects/2026/0322/logs/agent_adapters_run.log:1)
- `FakeShield` 日志：[logs/fakeshield_agent.log](/Users/lilongqi/PycharmProjects/2026/0322/logs/fakeshield_agent.log:1)
- `ForgeryGPT` 日志：[logs/forgerygpt_agent.log](/Users/lilongqi/PycharmProjects/2026/0322/logs/forgerygpt_agent.log:1)

当前结果统计：

- 总 Agent 结果数：`80`
- `FakeShield`：`40`
- `ForgeryGPT`：`40`
- 缓存文件数：`80`

说明：

- 当前是本地结构化适配层，不依赖外部网络或 API Key
- 输入为 Router 结构化输出，输出为统一 `ToolResultV1`
- 已打通 “Router -> Agent adapter -> cache -> result jsonl” 的第 3 周链路
- 日志中记录了样本范围、工具数量、缓存命中/新写入统计、主标签分布和结果摘要

## 5. 当前风险与下一步建议

1. 当前 `authentic` 只有 10 条，而且全部来自 `copy_move` 原图，分布还不够。
2. 审计结果显示 `600000+` 样本当前是 `512x512 L`，而其他类别是 `RGB`，模型可能学到颜色模式捷径。
3. 第 3 周分类基线精度偏低，后续应换成真正的 CNN / ViT 或更强特征。
4. Agent 适配层现在是本地启发式版本，下一步再接真实模型或 API。
5. 如果后续继续补 authentic，建议优先补 `splice`、`inpainting_removal`、`inpainting_replacement` 对应真实图，并保持配对 split 规则不变。
