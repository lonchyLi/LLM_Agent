# 多Agent遥感篡改检测工程蓝图

## 1. 建议目录

```text
project_root/
├── configs/
│   ├── router.yaml
│   ├── tools.yaml
│   ├── fusion.yaml
│   └── report.yaml
├── data/
│   ├── data_test/
│   ├── train/
│   ├── val/
│   └── challenge/
├── artifacts/
│   └── <sample_id>/
│       ├── round_1/
│       ├── round_2/
│       ├── round_3/
│       └── final/
├── schemas/
│   ├── router_output.schema.json
│   ├── tool_result.schema.json
│   ├── fusion_result.schema.json
│   └── report_payload.schema.json
├── prompts/
│   ├── router_system.txt
│   ├── router_user.txt
│   ├── llm_agent_system.txt
│   └── reflection_system.txt
├── src/
│   ├── router/
│   │   ├── qwen_router.py
│   │   └── reflection_router.py
│   ├── agents/
│   │   ├── fakeshield_agent.py
│   │   ├── forgerygpt_agent.py
│   │   └── qwen_forensics_agent.py
│   ├── tools/
│   │   ├── fft_detector.py
│   │   ├── prnu_detector.py
│   │   ├── noise_residual.py
│   │   ├── self_similarity.py
│   │   ├── sam_wrapper.py
│   │   └── unet_wrapper.py
│   ├── fusion/
│   │   ├── rule_fusion.py
│   │   └── learned_fusion.py
│   ├── reports/
│   │   ├── report_builder.py
│   │   └── gpt4o_payload.py
│   ├── orchestration/
│   │   ├── round_controller.py
│   │   ├── scheduler.py
│   │   └── cache_store.py
│   └── eval/
│       ├── metrics_cls.py
│       ├── metrics_mask.py
│       └── metrics_route.py
├── scripts/
│   ├── run_sample.py
│   ├── run_dataset.py
│   ├── export_sft_data.py
│   └── export_grpo_traces.py
└── docs/
    ├── data_test_plan.md
    └── forensics_blueprint.md
```

## 2. 核心模块职责

### 2.1 `router/`

- 输入：图像、元数据、历史轮次证据
- 输出：结构化路由 JSON
- 关键要求：低温、固定 schema、可复现实验

### 2.2 `agents/`

- 负责运行 LLM 检测模型
- 不直接做最终裁决
- 必须返回结构化证据，而不是只返回自由文本

### 2.3 `tools/`

- 负责传统取证与分割模块
- 统一产出得分、区域、日志路径、摘要

### 2.4 `orchestration/`

- 负责并行派发
- 负责多轮反思
- 负责停机逻辑与缓存

### 2.5 `fusion/`

- 第一版建议规则融合
- 第二版再切换学习式融合

### 2.6 `reports/`

- 把所有中间证据整理成固定格式
- 输出给 GPT-4o 与人工审稿

## 3. 首版最小可运行链路

建议先实现以下最小闭环：

1. `Qwen Router`
2. `ForgeryGPT-Agent`
3. `FFTDetector`
4. `NoiseResidual`
5. `SAM/UNet` 二选一
6. `RuleFusion`
7. `ReportBuilder`

这样能先覆盖 `data_test` 的两大主类：

- `inpainting_removal`
- `inpainting_replacement`

## 4. 多轮控制伪代码

```python
def run_case(sample, max_rounds=3):
    history = []
    state = init_state(sample)

    for round_id in range(1, max_rounds + 1):
        router_output = router.decide(sample=sample, state=state, history=history)
        selected_tools = scheduler.select(router_output)

        tool_results = scheduler.run_parallel(
            sample=sample,
            round_id=round_id,
            selected_tools=selected_tools,
        )

        fusion_result = fusion.merge(
            router_output=router_output,
            tool_results=tool_results,
            history=history,
        )

        history.append({
            "round_id": round_id,
            "router_output": router_output,
            "tool_results": tool_results,
            "fusion_result": fusion_result,
        })

        if should_stop(history, fusion_result):
            break

        state = update_state(state, history)

    final_report = report_builder.build(sample=sample, history=history)
    return history, final_report
```

## 5. 停机规则建议

```python
def should_stop(history, fusion_result):
    if fusion_result["confidence"] >= 0.85 and fusion_result["uncertainty"] <= 0.15:
        return True

    if len(history) >= 2:
        prev = history[-2]["fusion_result"]
        curr = fusion_result
        same_label = prev["final_label"] == curr["final_label"]
        small_delta = abs(prev["confidence"] - curr["confidence"]) < 0.03
        if same_label and small_delta:
            return True

    if len(history) >= 3:
        return True

    return False
```

## 6. 针对 `data_test` 的首版实现优先级

### P0

- 路由 schema 定型
- 单轮并行执行
- 规则融合
- 报告输出

### P1

- 双轮反思
- 基于掩码的空间一致性校验
- SFT 训练样本导出

### P2

- GRPO 路由优化
- 学习式融合
- `copy-move` 与 `fully-generated` 扩展
