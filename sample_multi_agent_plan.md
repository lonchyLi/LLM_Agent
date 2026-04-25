# 基于 `sample` 数据集的多 Agent 遥感篡改检测研发计划与 1.5 个月排期

## 1. 计划依据

本计划基于以下现有资料整理：

- `data_test/README.md`
- `data_test_plan.md`
- `sample/sample/unified_dataset/README.md`
- `sample/sample/unified_dataset/json/All_Images.json`
- `sample/sample/unified_dataset/json/All_Questions.json`
- `sample/sample/unify_datasets.py`

与 `data_test` 的 40 条双类子集不同，`sample` 已经是一个统一后的“最小全集”版本，能够直接支撑五类真实任务：

- `copy_move`
- `splice`
- `inpainting_removal`
- `inpainting_replacement`
- `aigc_global`

因此研发目标不应再停留在“两类验证闭环”，而应升级为“统一数据接口 + 多 Agent 路由 + 多工具取证 + 像素级定位 + 报告生成”的可运行系统。

## 2. `sample` 数据现状与工程含义

### 2.1 当前可直接使用的数据规模

`sample/sample/unified_dataset` 当前统计结果如下：

| 类别 | 图像数 | 是否有 `original` | 是否有 `mask` | 备注 |
|---|---:|---|---|---|
| `copy_move` | 5000 | 是 | 是 | 另有 `source_crop` / `target_crop` |
| `splice` | 5000 | 是 | 是 | 可视为传统拼接主监督集 |
| `inpainting_removal` | 2500 | 是 | 是 | AI 修复移除 |
| `inpainting_replacement` | 2500 | 是 | 是 | AI 修复替换 |
| `aigc_global` | 5000 | 否 | 否 | 全图生成，仅全局判别，不做真值定位 |
| 合计 | 20000 | 部分 | 部分 | 五类统一格式 |

补充信息：

- 英文问题总数：436358
- 中文问题总数：436358
- 问题类型：24 类
- 图像主索引字段较完整，已含 `image_path`、`original_path`、`tampered_path`、`mask_path`、`tamper_type`、`info`

### 2.2 这套数据对系统设计的直接约束

1. 系统必须同时支持“局部篡改”和“全图生成”两种不同任务形态。
2. `aigc_global` 没有 `original` 和 `mask`，所以不能要求所有样本都输出像素级真值定位。
3. 统一数据里当前 `tamper_type` 使用的是 `splice`，但现有路由 schema 里写的是 `splicing`，上线前必须统一标签名。
4. 所有篡改类样本的 `Q1` 都是 `Yes`，因此“真实未篡改”类别不能直接从 `All_Images.json` 拿到，需要从 `original_path` 构造负样本池。
5. `copy_move`、`splice`、`inpainting` 与 `aigc_global` 的问题空间并不一致，训练时不能简单把所有问题当成同构监督。

## 3. 1.5 个月内的研发目标

### 3.1 总目标

在约 6 周内完成一个可演示、可批跑、可出报告的多 Agent 遥感篡改检测系统 `MVP`，满足：

- 输入一张遥感图像或一个样本 ID
- 自动判断：真实 / 局部篡改 / 全图生成 / 不确定
- 对局部篡改样本给出类型候选与掩码结果
- 产出多轮调度日志、证据汇总和最终报告

### 3.2 阶段目标

本轮 1.5 个月只追求以下交付：

- 跑通统一数据读取与切分
- 跑通 Router + 专家 Agent + 传统工具 + 融合 + 报告
- 支持至少 2 轮调度反思，最多 3 轮
- 支持 5 类最终判别
- 对 4 类局部任务提供定位结果

本轮不建议强推的内容：

- 不做正式 GRPO 训练
- 不做复杂学习式融合主上线版本
- 不把所有能力都压在单一大模型上
- 不在第一版中追求论文级最优指标

## 4. 系统总体方案

系统采用六层结构：

1. 数据层
2. Router Agent 层
3. 专家检测 Agent 层
4. 传统取证与定位工具层
5. 融合裁决层
6. 报告与评测层

### 4.1 数据层

建议先构建统一的 `manifest` 与切分文件，而不是直接在原始 JSON 上硬编码。

建议新增产物：

- `splits/train.json`
- `splits/val.json`
- `splits/test.json`
- `splits/challenge.json`
- `metadata/label_map.json`
- `metadata/question_type_map.json`

数据层必须完成的工作：

- 统一标签名：`splice` 与 `splicing` 二选一，建议全工程统一为 `splice`
- 为局部篡改样本保留 `original/tampered/mask`
- 从 `original_path` 构造 `authentic` 负样本集
- 保证同一对 `original/tampered` 不会跨训练和验证集合泄漏
- 为 `aigc_global` 单独记录“仅分类，无掩码”的评测模式

### 4.2 Router Agent

Router 负责首轮粗判和后续轮次调度，不直接做最终裁决。

建议输出字段：

```json
{
  "sample_id": "200000",
  "round_id": 1,
  "coarse_label": "manipulated",
  "coarse_type_candidates": [
    {"label": "splice", "score": 0.61},
    {"label": "inpainting_replacement", "score": 0.21},
    {"label": "copy_move", "score": 0.08}
  ],
  "uncertainty": 0.22,
  "task_description": "判断是否为拼接篡改并尝试定位区域",
  "tool_candidates": [
    {"tool": "splice_agent", "priority": 1, "reason": "语义冲突明显"},
    {"tool": "fft_detector", "priority": 1, "reason": "边界频域异常"},
    {"tool": "mask_segmentor", "priority": 2, "reason": "需要定位区域"}
  ],
  "need_next_round": true,
  "reasoning_summary": [
    "局部区域疑似与背景上下文不一致",
    "候选类型更偏向拼接类",
    "需要传统频域证据交叉验证"
  ]
}
```

Router 的核心职责：

- 判断是 `authentic / manipulated / fully_generated / unknown`
- 产生前 2 到 3 个类型候选
- 决定调用哪些 Agent 与工具
- 根据上一轮冲突结果决定是否继续下一轮

### 4.3 专家检测 Agent

建议按任务类型拆成 4 个专家分支，而不是一个总包模型：

1. `copy_move_agent`
2. `splice_agent`
3. `inpainting_agent`
4. `aigc_global_agent`

每个专家 Agent 输出统一结构：

- 类型支持分数
- 证据摘要
- 可疑区域框或粗热图
- 是否建议继续调用额外工具

建议策略：

- `copy_move_agent` 重点看重复纹理、源目标相似性、局部空间关系
- `splice_agent` 重点看上下文冲突、边界融合、局部噪声不一致
- `inpainting_agent` 重点看纹理延拓、局部平滑、语义替换痕迹
- `aigc_global_agent` 重点看全局布局、传感器噪声缺失、生成痕迹

### 4.4 传统取证与定位工具层

第一版只保留最有性价比的工具，避免铺太大：

- `self_similarity`：主攻 `copy_move`
- `fft_detector`：主攻 `splice` / `aigc_global`
- `noise_residual`：主攻 `inpainting`
- `edge_blending`：辅助 `splice` / `replacement`
- `mask_segmentor`：统一输出像素级定位图

建议定位实现：

- 第一版优先做轻量分割头或现成二分类分割 baseline
- `copy_move` 可额外输出 `source-target` 对应区域
- `aigc_global` 默认不输出真值掩码，只输出 `null` 和原因

### 4.5 融合裁决层

第一版必须选择规则融合，不建议一开始上学习式融合。

融合输入包括：

- Router 候选类型分数
- 专家 Agent 打分
- 传统工具打分
- 掩码面积、连通域、区域一致性
- 跨轮次一致性

最终输出包括：

- `final_label`
- `final_type`
- `confidence`
- `uncertainty`
- `human_review_flag`
- `final_mask_path`

建议停机条件：

- 置信度大于阈值且不确定性低
- 前后两轮标签一致且提升很小
- 达到最大 3 轮

### 4.6 报告与评测层

每个样本要能生成：

- 路由 JSON
- 工具结果 JSON
- 最终融合 JSON
- Markdown 报告
- 关键可视化图

核心评测指标：

- 分类准确率 / 宏平均 F1
- 五类识别准确率
- `authentic` 与 `aigc_global` 区分能力
- 局部任务 `IoU` / `F1`
- 平均每样本工具调用数
- 平均推理时延

## 5. 研发实施路线

### 5.1 第一阶段：先做“统一数据 + 单轮闭环”

目标：

- 跑通读取、切分、单轮推理、单轮报告

完成标志：

- 能从统一索引中读取任意样本
- 能对五类样本跑出统一格式结果
- 能保存日志和可视化

### 5.2 第二阶段：补齐“专家化 + 定位 + 双轮调度”

目标：

- 专家 Agent 替代单一路由粗判
- 加入定位与冲突处理

完成标志：

- 局部任务能输出掩码或热图
- 结果冲突时能触发第二轮重试

### 5.3 第三阶段：做“批量评测 + 稳定化 + Demo”

目标：

- 批量跑验证集
- 汇总错误案例
- 打磨汇报演示版本

完成标志：

- 有固定评测脚本
- 有错误样例分析
- 有可展示的最终报告样本

## 6. 详细排期（总周期约 6 周）

## 第 1 周：数据审计与统一接口

目标：

- 把 `sample` 真正变成工程可消费数据

任务：

- 审核 `All_Images.json` / `All_Questions.json` 字段完整性
- 统一标签枚举，修正 `splice` / `splicing` 命名冲突
- 生成 `train/val/test/challenge` 切分
- 从 `original_path` 派生 `authentic` 样本索引
- 写数据读取器和单样本可视化脚本

交付物：

- `manifest` 与 `split` 文件
- 数据校验脚本
- 样本浏览脚本

验收标准：

- 五类样本均可正确加载
- 真实样本与篡改样本切分无泄漏

## 第 2 周：最小多 Agent 推理闭环

目标：

- 跑通 Router + 2 个基础工具 + 报告

任务：

- 定型 Router 输出 schema
- 完成调度器原型
- 接入 `fft_detector`
- 接入 `noise_residual`
- 接入一个通用视觉 Agent 或规则专家 Agent
- 输出单轮融合结果与 Markdown 报告

交付物：

- 单轮推理脚本
- 结构化中间结果
- 首版报告模板

验收标准：

- 至少能稳定处理 `splice`、`inpainting_removal`、`aigc_global`

## 第 3 周：专家 Agent 拆分与定位分支

目标：

- 从“一个总模型”转为“按类专家分工”

任务：

- 增加 `copy_move_agent`
- 增加 `splice_agent`
- 增加 `inpainting_agent`
- 增加 `aigc_global_agent`
- 接入 `mask_segmentor`
- 为 `copy_move` 增加 `self_similarity`

交付物：

- 四类专家接口
- 局部任务的掩码输出
- 初版工具对比表

验收标准：

- 四类局部任务都有可解释的证据输出
- `copy_move` 有专门工具，不再走通用分支糊过去

## 第 4 周：双轮/三轮调度与规则融合

目标：

- 让系统具备“证据冲突后继续查”的能力

任务：

- 实现第二轮反思路由
- 实现最大三轮停机逻辑
- 设计规则融合分数
- 增加 `human_review_flag`
- 增加缓存与失败重试机制

交付物：

- 多轮调度器
- 规则融合模块
- 冲突处理日志

验收标准：

- 对高不确定样本可自动进入第二轮
- 能输出最终裁决原因

## 第 5 周：评测、误差分析与轻量训练数据导出

目标：

- 建立系统性评测，而不是只看个别案例

任务：

- 完成分类、定位、路由成本评测脚本
- 批跑验证集和挑战集
- 汇总混淆矩阵与错误案例
- 导出轻量 SFT-COT 样本
- 梳理哪些路由错误适合后续做 RL

交付物：

- 批量评测报告
- 错误样例集
- 轻量训练数据导出脚本

验收标准：

- 能回答“哪类错得最多、为什么错”
- 能给出下一轮训练重点

## 第 6 周：稳定化、展示化与答辩材料准备

目标：

- 把系统从“能跑”变成“能讲清楚”

任务：

- 清理配置、命名、目录结构
- 固化 Demo 流程
- 产出 5 到 10 个高质量报告案例
- 输出项目文档、流程图、结果图
- 准备答辩版 PPT 所需图表

交付物：

- 稳定版推理脚本
- 标准报告案例集
- 项目说明文档

验收标准：

- 新样本可一键推理
- 汇报时能展示完整闭环

## 7. 当前最可能存在的困难点

### 7.1 数据定义层面的困难

1. `authentic` 类不是显式标签，而是要从 `original_path` 反推生成。
2. `aigc_global` 没有掩码，导致“统一定位评测”天然不成立。
3. 各子集问题类型不同，监督信号不完全对齐。
4. 标签命名不统一，容易导致训练集和路由输出出现错配。

### 7.2 模型与算法层面的困难

1. `copy_move` 依赖重复区域匹配，单靠 LLM 很容易误判。
2. `splice` 与 `inpainting_replacement` 在视觉上接近，边界会混淆。
3. `aigc_global` 与高质量局部篡改在全局统计上可能重叠，需要单独规则。
4. 传统取证工具在遥感图像压缩、重采样、裁剪后会失效或变弱。
5. 多 Agent 输出天然会冲突，如果没有统一 schema 和融合规则，系统会越来越乱。

### 7.3 工程落地层面的困难

1. 多轮调度会拉高时延与显存压力。
2. 工具之间输入输出格式容易不统一。
3. 大批量实验时日志、缓存、失败重跑管理会很麻烦。
4. 如果前两周不先把数据接口和 schema 固定住，后面所有模块都会反复返工。

## 8. 风险规避建议

1. 先把标签空间、目录结构、schema 固化，再写 Agent。
2. 第一版统一采用规则融合，避免学习式融合把问题藏起来。
3. `aigc_global` 独立评测，不要强行和局部定位任务用一套指标。
4. 所有工具统一返回 JSON，不允许只返回自由文本。
5. 每周都留出半天做错误样例回看，不要最后一周才补分析。

## 9. 你和学弟的分工建议

原则：

- 你负责高风险、高耦合、会影响整体路线的工作
- 学弟负责低风险、标准化、可并行、容易验收的工作

### 9.1 你优先负责

1. 标签体系和任务边界的最终拍板
2. Router schema 与多轮调度逻辑
3. 融合策略设计
4. 关键实验结论与误差分析
5. 汇报叙事与最终验收

### 9.2 学弟最适合承担的工作

#### 工作包 A：数据工程与质检

- 检查图像、掩码、JSON 是否缺失或错位
- 生成统计表和可视化样本墙
- 产出 `train/val/test/challenge` 切分文件
- 建立 `authentic` 负样本索引

价值：

- 这部分工作量大但规则明确，能直接帮你省出一整周

#### 工作包 B：工具封装与批跑脚本

- 封装 `fft_detector`
- 封装 `noise_residual`
- 封装 `self_similarity`
- 统一命令行接口与输出 JSON 格式
- 写批量推理和日志保存脚本

价值：

- 这是最适合并行推进的模块，对整体进度提升最大

#### 工作包 C：评测与可视化

- 写分类、IoU、F1、时延、工具调用数统计脚本
- 画混淆矩阵、PR 曲线、错误样例图
- 生成自动汇总表格

价值：

- 你后期最缺的通常不是模型，而是可讲清楚的结果材料

#### 工作包 D：报告与前端展示辅助

- 根据模板生成 Markdown 报告
- 做可疑区域叠图
- 整理一个网页或 notebook 展示面板

价值：

- 可以大幅提升汇报质量，而且不会卡核心算法进度

#### 工作包 E：错误样例归档

- 按类别整理误判案例
- 记录“错因标签”
- 建立可检索 casebook

价值：

- 对后续 prompt 调整、规则修正和答辩问答都很有帮助

### 9.3 不建议直接交给学弟独立负责的部分

1. 最终标签体系定义
2. 多轮路由策略
3. 融合规则拍板
4. 核心实验结论解释

原因：

- 这些任务一旦方向错，返工成本最高，最好由你亲自掌控

## 10. 最推荐的提速方式

如果学弟只能帮一部分，优先级建议如下：

1. 先让他做数据切分、质检和 `authentic` 负样本构造
2. 再让他做工具封装和批跑脚本
3. 然后让他做评测统计与可视化
4. 最后再让他协助报告生成和案例整理

这样分配的好处是：

- 你能尽快把时间集中到 Router、融合和整体策略
- 学弟做的工作都能直接并行，不会频繁等你
- 前三周就能明显拉快进度，而不是最后才补边角料

## 11. 建议的最终交付清单

在 1.5 个月结束时，建议至少形成以下成果：

- 一套可复现的数据切分与索引文件
- 一个多 Agent 推理原型系统
- 一套统一的工具输出 schema
- 一个规则融合模块
- 一套批量评测脚本
- 一组可展示的报告案例
- 一份错误分析总结
- 一份后续 SFT / RL 优化路线说明

如果以上八项都能交付，这个项目就已经具备“可继续打磨成论文或系统原型”的基础，而不是停留在概念设计阶段。
