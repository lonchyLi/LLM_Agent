# 基于 `data_set` 的多 Agent 遥感篡改检测详细计划

## 1. 数据现状与约束

### 1.1 `data_set` 当前真实内容

与此前仅覆盖 `data_test` 的 40 个局部篡改样本不同，当前 `data_set` 已经给出了一套**统一格式的正式训练集 V1**。

从 [`data_set/README.md`](/Users/lilongqi/PycharmProjects/2026/0322/data_set/README.md:1)、[`data_set/field_mapping.md`](/Users/lilongqi/PycharmProjects/2026/0322/data_set/field_mapping.md:1)、[`data_set/schema/sample_record.schema.json`](/Users/lilongqi/PycharmProjects/2026/0322/data_set/schema/sample_record.schema.json:1) 和 [`data_set/examples/sample_records_demo.json`](/Users/lilongqi/PycharmProjects/2026/0322/data_set/examples/sample_records_demo.json:1) 可确认：

- 总样本数：25
- 每类样本数：5
- 类别共 5 类：
  1. `copy_move`
  2. `splice`
  3. `inpainting_removal`
  4. `inpainting_replacement`
  5. `aigc_global`

统一目录结构为：

- `images/<sample_id>/`
- `schema/`
- `examples/`

统一记录文件为：

- `dataset_manifest_demo.json`
- `sample_records_demo.json`
- `question_records_demo.json`

### 1.2 `data_set` 的标签与任务模式

从 `manifest` 和 `schema` 可确认，当前统一标签空间已经明确为两层：

- 一级标签：`authentic / manipulated / fully_generated / unknown`
- 二级标签：`copy_move / splice / inpainting_removal / inpainting_replacement / aigc_global / none / uncertain`

任务模式也已经统一：

- `classification_localization`
- `classification`

其中：

- `copy_move / splice / inpainting_removal / inpainting_replacement` 有定位真值
- `aigc_global` 没有定位真值

### 1.3 当前数据的工程价值

`data_set` 的关键价值不在于样本量大，而在于它已经把：

- 标签空间
- 目录规范
- 样本记录
- QA 记录
- 路径命名
- 类别差异

统一到了同一个协议里。

这意味着项目现在可以不再围绕“某两类局部篡改数据的试验性闭环”来设计，而可以直接围绕：

- 统一路由
- 统一工具协议
- 统一评测输出
- 统一报告格式

做一个**5 类闭集多 Agent 正式系统 V1**。

### 1.4 当前数据的训练定位

本次计划中，`data_set` 不再被视为演示样本，而是被视为**当前阶段的正式训练集与评测集基础版本**。

这意味着：

- 当前 5 类任务都进入正式训练范围
- 当前统一 schema 直接作为正式数据协议
- 当前样本记录与 QA 记录直接用于训练样本构造
- 后续扩展主要体现在样本数增加和类别继续扩容，而不是推翻现有设计

当前版本仍有几个客观特点：

- `copy_move` 额外有 `source_crop/target_crop`
- `splice` 没有成对源目标区域裁剪
- 两类 `inpainting` 的 QA 更密集
- `aigc_global` 只有分类真值，没有定位真值

但这些差异不再被视为“不能训练”的理由，而是被视为：

- 多任务统一建模时需要显式处理的类别差异
- 后续扩容时继续沿用的字段差异

## 2. 需要先修正的设计点

### 2.1 相比 `data_test_plan.md` 的变化

旧的 [`data_test_plan.md`](/Users/lilongqi/PycharmProjects/2026/0322/data_test_plan.md:1) 之所以把系统设计成“两层标签空间 + 开放集扩展”，是因为当时只有：

- `inpainting_removal`
- `inpainting_replacement`

两类数据有可靠监督，`copy_move` 和 `fully-generated` 只能预留接口。

现在换成 `data_set` 后，情况已经变化：

- `copy_move` 已有样本
- `splice` 已有样本
- `inpainting_removal` 已有样本
- `inpainting_replacement` 已有样本
- `aigc_global` 已有样本

也就是说，**第一版原型已经可以在已知 5 类标签空间内运行**，不再只是两类主监督。

### 2.2 设计上需要做的不是降级，而是分层训练

既然 `data_set` 现在被定义为正式训练集，设计重点就不再是“要不要训练”，而是“如何分层训练”。

核心问题有三个：

- 各类别任务模式不完全一致
- QA 信息密度不同
- 分类与定位共享一套路由，但监督信号不同

因此要做的不是回避训练，而是把训练拆成：

- 分类训练
- 定位训练
- Router/SFT 训练
- 融合层训练
- 第二阶段 GRPO 优化

### 2.3 修改后的总体原则

基于 `data_set`，本阶段最合理的原则是：

- 保留旧计划中的“两层标签空间”
- 直接按 5 类闭集做正式训练
- 继续保留 `uncertain / unknown / need_human_review` 作为扩展接口
- 先完成多 Agent 结构化闭环，再进入训练优化
- 把当前 `data_set` 视为 V1 正式数据，后续仅做扩样和扩类

这样做的好处是：

- 当前即可启动正式训练和正式评测
- 结构上已对齐后续扩样版本
- 后续增加类别和样本数时，不需要推翻接口

## 3. 总体架构

整体仍采用“轻路由 + 并行执行 + 多轮反思 + 证据融合 + 报告生成”的五段式结构，延续 `data_test_plan.md` 的核心设计，只是把类别空间从“局部两类 + 占位扩展”升级成“5 类统一协议”。

### 3.1 Router Agent：7B 级 Qwen 低温结构化路由

Router 继续负责第一入口，建议使用：

- `Qwen2.5-VL-7B-Instruct` 或同量级模型
- 推理温度：`0.1 ~ 0.2`
- 输出强制结构化 JSON

在 `data_set` 中，Router 首轮应完成四件事：

1. 识别当前样本任务模式是 `classification` 还是 `classification_localization`
2. 给出一级标签 `l1`
3. 给出二级标签 `l2` 的候选分布
4. 给出需要调用的工具列表

建议输出：

```json
{
  "sample_id": "400000",
  "task_mode": "classification_localization",
  "modality": "remote_sensing_rgb",
  "coarse_label": "manipulated",
  "coarse_type_candidates": [
    {"label": "inpainting_replacement", "score": 0.63},
    {"label": "splice", "score": 0.19},
    {"label": "inpainting_removal", "score": 0.11}
  ],
  "uncertainty": 0.24,
  "task_description": "检测是否存在语义替换型篡改，并输出掩码",
  "tool_candidates": [
    {"tool": "ForgeryGPT", "priority": 1},
    {"tool": "NoiseResidualDetector", "priority": 1},
    {"tool": "MaskHead", "priority": 2}
  ],
  "need_next_round": true,
  "reasoning_trace": "..."
}
```

### 3.2 Execution Layer：并行工具派发

延续旧计划，Execution Layer 把 Router 的输出转成并行任务图。

第一版建议至少保留三组模块：

#### A. LLM 检测 Agent

- `FakeShield-Agent`
- `ForgeryGPT-Agent`
- 可选：自定义 `Qwen-Forensics-Agent`

职责：

- 输出文字证据
- 输出二级标签排序
- 解释异常区域和语义冲突
- 生成供融合层读取的结构化结论

#### B. 非 LLM 取证模块

继续保留 `data_test_plan.md` 中的传统取证工具思路，但按 `data_set` 的 5 类任务重排优先级：

- `FFT / frequency artifact`
- `PRNU / noise residual consistency`
- `ELA / compression inconsistency`
- `edge / boundary blending`
- `patch self-similarity`
- `global generative artifact detector`

其中：

- `patch self-similarity` 对 `copy_move` 是关键
- `PRNU + boundary blending + frequency inconsistency` 对 `splice` 更关键
- `noise residual + texture continuity` 对两类 `inpainting` 更关键
- `global generative prior` 对 `aigc_global` 更关键

#### C. 掩码 / 定位模块

- `SAM`：候选区域提议
- `UNet` 或轻量分割头：输出异常区域热图
- 可选：基于传统取证热图的后处理融合

职责：

- 对局部篡改类输出像素级掩码
- 对 `aigc_global` 明确输出 `has_localization_output = false`
- 统一向融合层返回 `mask + area_ratio + confidence`

## 4. 多轮路由策略

### 4.1 第一轮：基于任务模式的粗检并行

在 `data_set` 中，Router 第一步先区分：

- `classification_localization`
- `classification`

再决定工具调用策略：

- 当样本更像局部篡改时：调用 LLM Agent + 传统局部异常工具 + 掩码模块
- 当样本更像 `aigc_global` 时：优先调用全图生成痕迹检测，而不是掩码模块

建议规则：

- `uncertainty < 0.2` 时：走轻量并行，只派 2 到 3 个最相关工具
- `0.2 <= uncertainty < 0.4` 时：走标准并行，派 3 到 5 个工具
- `uncertainty >= 0.4` 时：增加第二个 LLM Agent 做交叉验证

### 4.2 第二轮：类别冲突交叉验证

第二轮重点不是继续盲目加工具，而是解决类型冲突：

- 如果 `copy_move` 与 `splice` 分歧大：
  强制增加 `self-similarity / dense matching`
- 如果 `splice` 与 `inpainting_replacement` 分歧大：
  强制增加 `boundary blending + PRNU + mask refinement`
- 如果 `inpainting_removal` 与 `inpainting_replacement` 分歧大：
  强制增加 `texture continuity + object disappearance cues`
- 如果 `aigc_global` 得分升高：
  回退局部定位工具，增加全图生成检测

### 4.3 第三轮：定位与文本证据对齐

第三轮仅在以下情况触发：

- 掩码与文本证据位置不一致
- 多个工具类型结论趋同，但掩码极差
- `classification_localization` 样本被多次判断为无局部异常

此轮主要动作：

- 局部裁剪后重跑 LLM Agent
- 重新融合热图
- 降低最终置信度并打上 `human_review_flag`

### 4.4 停机条件

建议延续旧计划思路：

- `R_max = 3`
- 每轮最多新增 2 个工具
- 单样本工具总调用不超过 8 次

停止条件满足任一即可：

- Top-1 标签两轮不变
- 置信度变化低于阈值
- 掩码 IoU 改善低于阈值
- 新增工具不再改变结论

## 5. 面向 5 类任务的专用路由规则

### 5.1 `copy_move`

第一优先工具：

- `patch self-similarity`
- `block matching`
- `dense feature correspondence`

辅助工具：

- `SAM / UNet`
- `ForgeryGPT-Agent`

关键判据：

- 源区域与目标区域存在高相似复制关系
- `source_crop` 与 `target_crop` 在语义上高度一致
- 掩码对应局部位置转移而不是外源拼接

### 5.2 `splice`

第一优先工具：

- `PRNUConsistency`
- `FFTArtifactDetector`
- `edge/boundary blending`

辅助工具：

- `FakeShield-Agent`
- `SAM / UNet`

关键判据：

- 局部噪声源不一致
- 边界过渡不自然
- 纹理、光照、压缩统计与周边区域冲突

### 5.3 `inpainting_removal`

第一优先工具：

- `noise residual`
- `texture continuity`
- `mask refinement`

辅助工具：

- `ForgeryGPT-Agent`
- `UNet mask head`

关键判据：

- 原有目标消失
- 背景连续但细节延拓异常
- 纹理存在平滑化或补全痕迹

### 5.4 `inpainting_replacement`

第一优先工具：

- `noise residual`
- `boundary inconsistency`
- `semantic replacement detector`

辅助工具：

- `FakeShield-Agent`
- `SAM / UNet`

关键判据：

- 局部目标没有消失而是被替换成新语义
- 新旧区域边界有融合痕迹
- 目标类别与周边语义关系不协调

### 5.5 `aigc_global`

第一优先工具：

- `global frequency prior`
- `diffusion / generative artifact detector`
- `scene-layout consistency checker`

辅助工具：

- `FakeShield-Agent`

关键判据：

- 全图缺失真实传感器噪声模式
- 整体频谱分布更像生成图
- 文本描述、地理元数据和视觉内容之间可能存在物理不一致

## 6. 基于 `data_set` 的阶段化落地方案

### 6.1 阶段 A：先在 `data_set` 上建立正式训练闭环

目标是把 `data_set` 作为 V1 正式训练集，完成 5 类任务的训练、推理、评测闭环。

本阶段输入：

- `images/<sample_id>/input.png`
- 可用时的 `original.png / tampered.png / mask.png`
- `sample_record`
- `question_record`

本阶段任务：

- 建立统一数据读取器
- 建立正式 `train / val / test` 划分方案
- 建立 Router 的结构化输出协议
- 建立分类与定位训练样本构造逻辑
- 接入最少一组 LLM Agent
- 接入最少两组非 LLM 取证模块
- 接入一个统一定位模块
- 完成基础训练与基础评测
- 输出统一报告和统一证据对象

本阶段不建议做的事：

- 不建议过早引入 5 类独立专用大模型
- 不建议在第一轮就引入过重的模型集群

### 6.2 阶段 B：按类别补齐工具优先级与评测

在第一阶段跑通后，第二阶段重点是把 5 类路由逻辑补完整：

- `copy_move`：增加复制匹配类证据
- `splice`：增强边界与噪声一致性分析
- `inpainting_removal`：增强目标移除型证据
- `inpainting_replacement`：增强语义替换型证据
- `aigc_global`：增强全图生成检测

### 6.3 阶段 C：预留开放集和正式数据扩展接口

虽然当前 `data_set` 已覆盖 5 类闭集，但正式系统仍然需要：

- `known_class`
- `uncertain`
- `unknown_manipulation`
- `need_human_review`

因此第一版就要把这些字段留在输出协议中，避免后续接口重构。

## 7. 训练路线：SFT-COT 先行，GRPO 后置

你要求按 `data_test_plan.md` 的路线来，这一部分继续保留，而且现在直接把 `data_set` 当作正式训练集来设计。

### 7.1 SFT-COT 阶段

SFT 的目标是先把 Router 和多 Agent 调度训练到可用状态：

- 学会任务模式识别
- 学会 5 类闭集类型判断
- 学会工具选择
- 学会输出结构化路由 JSON
- 学会在分类类与定位类任务之间做区分

建议训练样本组织：

- 输入：图像 + 样本元数据摘要 + 上轮证据
- 输出：`reasoning_summary + routing_json + preliminary_verdict`

建议训练时保留完整 COT 或摘要式推理痕迹，部署时输出摘要式 reasoning。

建议输出：

```json
{
  "reasoning_summary": [
    "该样本存在明显局部异常区域，属于 classification_localization",
    "候选类型更接近 inpainting_replacement 而非 splice",
    "建议调用语义替换检测与掩码模块进一步验证"
  ],
  "routing_decision": {}
}
```

### 7.2 GRPO 阶段

GRPO 在本计划中不再只是接口预留，而是第二阶段正式优化手段。

更合理的顺序是：

- 先用 SFT 固化 Router 输出格式
- 再用监督评测找出高频错路由
- 再用 GRPO 优化“是否继续探索”“工具选择顺序”“路由成本控制”

需要注意的只是：

- `classification` 与 `classification_localization` 要分开算奖励
- `aigc_global` 不参与 `R_mask`
- 局部篡改类需要同时看类型和掩码

### 7.3 多目标奖励设计

沿用旧计划思路，未来正式数据上可使用：

- `R_cls`：一级标签正确
- `R_type`：二级标签正确
- `R_mask`：掩码 IoU / F1
- `R_route_cost`：工具调用成本
- `R_consistency`：多轮前后一致性
- `R_report`：报告完整度

总奖励示意：

```text
R = w1*R_cls + w2*R_type + w3*R_mask + w4*R_consistency + w5*R_report - w6*R_route_cost
```

因此 GRPO 可作为第 2 个月内的正式交付项之一，但范围应控制在路由策略优化，不建议一开始就优化所有模块。

## 8. 证据融合设计

### 8.1 统一证据对象

每个工具回传统一证据结构：

```json
{
  "tool_name": "PRNUConsistency",
  "round_id": 2,
  "target_region": [x1, y1, x2, y2],
  "score": 0.74,
  "label_support": {
    "splice": 0.51,
    "inpainting_replacement": 0.28,
    "copy_move": 0.04,
    "aigc_global": 0.03
  },
  "mask_path": "artifacts/sample_xxx/prnu_mask.png",
  "log_path": "artifacts/sample_xxx/prnu.log",
  "summary": "局部边界附近存在明显噪声一致性下降"
}
```

### 8.2 融合层输出

最终融合输出建议包含：

- `final_label`
- `tamper_type_level_1`
- `tamper_type_level_2`
- `confidence`
- `uncertainty`
- `final_mask`
- `tool_calls`
- `core_logs`
- `human_review_flag`

建议实现顺序：

- 第一版使用规则融合
- 第二版升级为轻量 MLP / XGBoost 融合

这样与旧计划一致，同时也适合作为当前正式训练集 V1 的第一版融合方案。

## 9. GPT-4o 可读报告模板

延续旧计划，所有证据最终汇总为统一报告，供 GPT-4o 或人工审阅。

### 9.1 结构模板

```markdown
# Forensic Report

## Sample
- sample_id:
- image_path:
- task_mode:
- source_dataset:

## Final Verdict
- final_label:
- tamper_type_level_1:
- tamper_type_level_2:
- confidence:
- uncertainty:
- human_review_flag:

## Localization
- final_mask_path:
- mask_area_ratio:
- key_regions:

## Multi-round Routing Trace
- round_1_router_decision:
- round_2_router_decision:
- round_3_router_decision:

## Tool Evidence
- tool_name:
  - round:
  - score:
  - summary:
  - artifact_path:
  - log_path:

## Cross-validation Summary
- agreement:
- conflict_points:
- final_resolution_reason:

## Short Reasoning Summary
- point_1:
- point_2:
- point_3:
```

### 9.2 面向 `data_set` 的补充要求

由于 `data_set` 中 `aigc_global` 带有 `caption` 和 `geo_meta`，报告中建议额外保留：

- `caption`
- `caption_zh`
- `geo_meta`

用于后续全图生成检测和场景合理性分析。

## 10. 推荐的工程落地顺序

### 10.1 第一批最小实现

1. 建立 `Router Agent` 的结构化输出协议
2. 接入 1 到 2 个 LLM Agent
3. 接入 2 到 3 个非 LLM 取证模块
4. 接入 1 个统一定位模块
5. 实现最多 3 轮循环控制
6. 实现统一证据缓存与报告输出

### 10.2 第二批增强

1. 增加 `copy_move` 专项匹配工具
2. 增加 `aigc_global` 全图检测分支
3. 从规则融合升级到学习式融合
4. 在当前 `data_set` 上正式开展 SFT
5. 在当前 `data_set` 上开展受控 GRPO

## 11. 对应详细周期计划

你要求周期控制在 2 个月左右，因此建议按 8 周推进，每周都有明确的交付目标。

### 第 1 周：数据理解、正式划分与协议冻结

目标：

- 完整理解 `data_set`
- 冻结统一输入 / 输出协议
- 冻结正式训练集划分

工作内容：

- 解析 `manifest / sample_records / question_records`
- 完成 schema 校验脚本
- 统计 5 类样本与问题类型
- 制定 `train / val / test` 划分
- 设计统一样本对象
- 设计统一 Router 输出 JSON

阶段交付：

- 数据说明文档
- 数据划分文件
- 样本索引脚本
- Router JSON 协议初版

### 第 2 周：最小 Router、数据可视化与训练样本构造

目标：

- 跑通“输入样本 -> Router 决策”
- 跑通训练样本构造

工作内容：

- 实现单样本 Router 推理脚本
- 对 `classification` 与 `classification_localization` 做分流
- 实现样本浏览与调试工具
- 生成每类 5 个样本的调试页
- 构造分类训练样本、定位训练样本、SFT 样本

阶段交付：

- Router 原型
- 数据浏览脚本
- 调试输出目录
- 训练样本生成脚本

### 第 3 周：接入第一批检测 Agent 与分类训练

目标：

- 跑通 Router 到工具调用的闭环
- 跑通 5 类闭集分类训练

工作内容：

- 接入 `FakeShield-Agent`
- 接入 `ForgeryGPT-Agent`
- 统一各 Agent 的输出结构
- 增加 tool result cache
- 训练一级 / 二级分类基线
- 输出分类评测结果

阶段交付：

- Agent 调用适配层
- 工具结果 JSON
- 单轮联调结果
- 分类训练日志
- 分类评测结果

### 第 4 周：接入传统取证模块与定位训练

目标：

- 完成“LLM + 非 LLM”并行证据链
- 完成局部篡改定位训练闭环

工作内容：

- 接入 `FFT / PRNU / edge` 中至少两类
- 接入 `copy_move` 所需的 `self-similarity`
- 完成非 LLM 工具结果格式统一
- 实现基础规则融合
- 训练定位模块
- 输出 IoU / F1 基线

阶段交付：

- 非 LLM 取证模块适配层
- 基础融合器
- 5 类单轮证据输出
- 定位训练日志
- 定位评测结果

### 第 5 周：接入定位模块、掩码评测与 SFT 训练

目标：

- 完成局部篡改类定位闭环
- 完成 Router 的 SFT 初版

工作内容：

- 接入 `SAM` 或轻量分割头
- 输出预测掩码
- 实现 mask 后处理
- 实现 IoU / F1 评测
- 对 `aigc_global` 明确跳过定位
- 组织多轮路由 SFT 样本
- 训练 Router SFT 模型

阶段交付：

- 定位模块
- 掩码输出目录
- 定位评测脚本
- SFT 数据集
- SFT 模型初版

### 第 6 周：实现多轮控制、类别专用路由与融合训练

目标：

- 从单轮推理升级到最多 3 轮反思式路由
- 完成基础融合训练

工作内容：

- 实现第二轮、第三轮触发条件
- 为 5 类定义专用工具优先级
- 增加 `human_review_flag`
- 增加不确定性回退机制
- 训练规则融合或轻量学习式融合器

阶段交付：

- 多轮控制器
- 分类别路由规则表
- 失败样本回退策略
- 融合器初版

### 第 7 周：GRPO 优化、QA 生成与报告输出

目标：

- 输出可读、可审计的最终结果
- 完成 Router 的受控 GRPO 优化

工作内容：

- 基于已有路由轨迹设计奖励
- 开展小规模 GRPO 训练
- 基于 `question_record` 生成样本级回答
- 汇总分类、定位、工具证据
- 输出 `result.json`
- 输出 `report.md`

阶段交付：

- GRPO 路由优化结果
- QA 生成器
- 报告生成器
- 样本级完整产物

### 第 8 周：全集联调、正式评测与验收

目标：

- 跑通 `data_set` 全量数据
- 固化第一版正式训练系统

工作内容：

- 全集批量运行
- 检查所有失败样本
- 修正输出协议问题
- 汇总训练、验证、测试结果
- 整理使用说明与目录规范
- 汇总阶段结果与下一阶段路线

阶段交付：

- 端到端全流程结果
- 最终报告模板
- 使用文档
- 正式评测结果
- 第一版验收结果

## 12. 里程碑汇总

### 里程碑 1：第 2 周结束

完成：

- 数据协议冻结
- 数据正式划分
- Router 原型
- 样本可视化

### 里程碑 2：第 4 周结束

完成：

- LLM Agent 接入
- 非 LLM 工具接入
- 分类 / 定位训练基线
- 单轮证据链跑通

### 里程碑 3：第 6 周结束

完成：

- 定位模块
- Router SFT
- 多轮控制
- 5 类专用路由规则
- 融合器初版

### 里程碑 4：第 8 周结束

完成：

- GRPO 路由优化
- QA 生成
- 报告输出
- 全量联调
- 第一版正式交付

## 13. 针对当前数据的明确结论

基于 `data_set`，我建议你把当前项目的近期目标定义为：

**把 `data_set` 作为当前阶段的正式训练集，完成面向 `copy_move / splice / inpainting_removal / inpainting_replacement / aigc_global` 五类任务的多 Agent 取证系统训练、路由、定位、QA 与报告输出。**

这比继续沿用 `data_test` 阶段“只围绕局部两类做开放集预留”的表述更准确，也更符合你现在的项目定义。

后续第二阶段的变化主要就是：

- 扩大每类样本数
- 增加新的篡改类别
- 继续沿用当前统一协议和训练路线

## 14. 本次相对旧版计划的修改

相对 `data_test_plan.md`，本次只做三类必要替换：

1. 把数据事实从“40 个两类局部篡改样本”替换为“25 个五类统一格式正式训练集”
2. 把标签支持范围从“两类主监督 + 两类预留扩展”替换为“5 类闭集正式训练”
3. 把落地周期细化为包含训练、SFT、GRPO、评测的 8 周详细实施计划

旧计划的骨架仍然保留：

- 多 Agent 架构
- 多轮路由
- 证据融合
- SFT-COT 先行、GRPO 后置
- 报告输出

只是全部改成更符合 `data_set` 真实情况的版本。
