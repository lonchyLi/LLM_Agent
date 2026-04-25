# `artifacts/previews/` 图片索引说明

本文件用于说明 `artifacts/previews/` 目录下各图片的来源、含义和用途。

这些图片全部属于**数据预览与调试产物**，不是模型预测结果，也不是最终检测报告。

## 1. 目录用途

`artifacts/previews/` 主要服务于前两周的工作：

- 快速检查 `data_set` 是否能被正确读取
- 对比不同类别样本的视觉差异
- 核对样本目录中的多张图片是否对应正确
- 为后续训练、路由和错误分析提供人工可读材料

## 2. 图片类型说明

当前目录下的图片分为两类：

1. 类别总览图
2. 单样本明细图

---

## 3. 类别总览图

这类图片由脚本 [scripts/export_previews.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/export_previews.py:1) 生成。

生成逻辑：

- 按 `tamper_type_l2` 分组
- 每个类别取该类所有样本
- 读取每个样本的 `input.png`
- 拼成一个总览图

### 3.1 `preview_copy_move.png`

文件：

- [artifacts/previews/preview_copy_move.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_copy_move.png)

内容：

- 展示 `copy_move` 类的 5 个样本输入图
- 每个子图标题为 `sample_id | source_dataset`

用途：

- 快速观察复制粘贴类样本的视觉分布
- 为后续 `SelfSimilarityDetector` 接入提供人工参考

### 3.2 `preview_splice.png`

文件：

- [artifacts/previews/preview_splice.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_splice.png)

内容：

- 展示 `splice` 类的 5 个样本输入图

用途：

- 快速查看拼接类样本外观
- 为后续边界、频域和噪声类工具接入做参考

### 3.3 `preview_inpainting_removal.png`

文件：

- [artifacts/previews/preview_inpainting_removal.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_inpainting_removal.png)

内容：

- 展示 `inpainting_removal` 类的 5 个样本输入图

用途：

- 观察目标移除型样本的整体外观
- 为后续 `NoiseResidualDetector`、`MaskSegmentor` 做人工对照

### 3.4 `preview_inpainting_replacement.png`

文件：

- [artifacts/previews/preview_inpainting_replacement.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_inpainting_replacement.png)

内容：

- 展示 `inpainting_replacement` 类的 5 个样本输入图

用途：

- 观察语义替换型样本的整体外观
- 为后续 `ForgeryGPT-Agent` 和 `FakeShield-Agent` 的案例检查做准备

### 3.5 `preview_aigc_global.png`

文件：

- [artifacts/previews/preview_aigc_global.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/preview_aigc_global.png)

内容：

- 展示 `aigc_global` 类的 5 个样本输入图

用途：

- 查看全图生成类样本的整体风格
- 为后续全图真假判断和频域异常检测做参考

---

## 4. 单样本明细图

这类图片由脚本 [scripts/visualize_sample.py](/Users/lilongqi/PycharmProjects/2026/0322/scripts/visualize_sample.py:1) 生成。

生成逻辑：

- 输入一个 `sample_id`
- 自动读取该样本目录下实际存在的图像文件
- 将这些图像并排展示

这类图片不是只看 `input.png`，而是看该样本的“全套关联图”。

### 4.1 `100000.png`

文件：

- [artifacts/previews/100000.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/100000.png)

对应样本：

- `sample_id = 100000`
- 类别：`copy_move`

图中内容通常包括：

- `image_path` 对应的 `input.png`
- `original.png`
- `tampered.png`
- `mask.png`
- `source_crop.png`
- `target_crop.png`

用途：

- 检查 `copy_move` 样本的完整结构是否正确
- 验证 `source_crop` 与 `target_crop` 是否真实存在
- 为后续 `copy_move` 专用工具接入做对照

### 4.2 `500000.png`

文件：

- [artifacts/previews/500000.png](/Users/lilongqi/PycharmProjects/2026/0322/artifacts/previews/500000.png)

对应样本：

- `sample_id = 500000`
- 类别：`aigc_global`

图中内容通常包括：

- `input.png`
- `tampered.png`

说明：

- 该类样本没有 `mask`
- 也没有 `original`
- 所以展示图会比局部篡改类更简单

用途：

- 验证 `aigc_global` 的目录结构是否符合预期
- 确认这类样本不进入定位分支

---

## 5. 与后续结果的区别

这些 `previews` 图片和后续真正的模型产物要严格区分：

### 5.1 不是分类结果

- 不包含预测标签
- 不包含置信度
- 不包含 Router 决策

### 5.2 不是定位结果

- 不包含预测掩码
- 不包含 IoU、Dice 等评测信息

### 5.3 不是工具证据

- 不包含 `ForgeryGPT-Agent` 或 `FakeShield-Agent` 输出
- 不包含 FFT、PRNU、NoiseResidual 等工具结果

### 5.4 不是最终报告

- 不包含融合后的最终结论
- 不包含 QA 输出
- 不包含多轮路由历史

---

## 6. 当前目录下图片与来源脚本对照

| 图片文件 | 来源脚本 | 含义 |
|---|---|---|
| `preview_copy_move.png` | `export_previews.py` | `copy_move` 类输入图总览 |
| `preview_splice.png` | `export_previews.py` | `splice` 类输入图总览 |
| `preview_inpainting_removal.png` | `export_previews.py` | `inpainting_removal` 类输入图总览 |
| `preview_inpainting_replacement.png` | `export_previews.py` | `inpainting_replacement` 类输入图总览 |
| `preview_aigc_global.png` | `export_previews.py` | `aigc_global` 类输入图总览 |
| `100000.png` | `visualize_sample.py` | `sample_id=100000` 的完整样本明细图 |
| `500000.png` | `visualize_sample.py` | `sample_id=500000` 的完整样本明细图 |

## 7. 如何继续使用

如果后续需要继续生成预览图，可以直接运行：

```bash
python scripts/export_previews.py
python scripts/visualize_sample.py 100000
python scripts/visualize_sample.py 500000
```

如果要查看别的样本，把 `100000` 或 `500000` 换成目标 `sample_id` 即可。
