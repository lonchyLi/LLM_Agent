# Unified Format Demo

这个 `demo/` 文件夹给出一套适用于遥感篡改归档格式数据的最小完整示例。

目标不是替换完整数据，而是保留与正式归档版一致的目录结构、字段组织方式和图片命名方式，方便：

1. 快速查看目录层次
2. 对照字段格式开发读取脚本
3. 作为最小样例进行工具接入与联调
4. 演示不同子数据类型在统一格式中的表现

## 建议目录

```text
demo/
├── README.md
├── field_mapping.md
├── images/
│   ├── 100000/
│   ├── 100001/
│   ├── 100002/
│   ├── ...
│   └── 500004/
├── schema/
│   ├── dataset_manifest.schema.json
│   ├── sample_record.schema.json
│   └── question_record.schema.json
└── examples/
    ├── dataset_manifest_demo.json
    ├── sample_records_demo.json
    └── question_records_demo.json
```

## 具体图片放哪里

建议直接放在：

- `demo/images/<sample_id>/`

每个样本一个目录，目录内统一命名：

- `input.png`
- `original.png`
- `tampered.png`
- `mask.png`
- `source_crop.png`
- `target_crop.png`

说明：

- `input.png`：默认送入模型的图
- `original.png`：原图，没有就不放
- `tampered.png`：篡改图或生成图
- `mask.png`：真值掩码，没有就不放
- `source_crop.png` / `target_crop.png`：只对 `copy_move` 常见

当前已放好的示例目录按类别各取 5 个样本：

- `copy_move`：`100000` - `100004`
- `splice`：`200000` - `200004`
- `inpainting_removal`：`300000` - `300004`
- `inpainting_replacement`：`400000` - `400004`
- `aigc_global`：`500000` - `500004`

## 本 demo 覆盖的样本类型

- `copy_move`：5 个样本
- `splice`：5 个样本
- `inpainting_removal`：5 个样本
- `inpainting_replacement`：5 个样本
- `aigc_global`：5 个样本

总计：

- `25` 个样本目录
- `25` 条 `sample_record`
- 对应子集样本的全部 `question_record`

## `examples/` 是什么

`examples/` 用来放这套 demo 对应的示例 JSON 文件，而不是图片。

其中：

- `dataset_manifest_demo.json`：demo 的总清单
- `sample_records_demo.json`：demo 的样本级记录
- `question_records_demo.json`：demo 的问答级记录

这样目录职责会分得更清楚：

- `images/` 放图片
- `schema/` 放结构约束
- `examples/` 放示例记录文件

## 统一设计原则

### 1. 一个样本只对应一个 `sample_record`

无论原始数据来自：

- `CM_dataset`
- `splice_dataset`
- `AIGC-inpainting-removal`
- `AIGC-inpainting-replacement`
- `AIGC-global`

都先转成一条统一样本记录。

### 2. 输入图像统一用 `image_path`

`image_path` 表示默认送入模型的图像路径。

- 对局部篡改类：通常等于 `tampered_path`
- 对 `aigc_global`：等于生成图路径

### 3. 可定位和不可定位要显式区分

必须增加：

- `task_mode`
- `has_localization_gt`

因为：

- `copy_move / splice / inpainting_*` 有定位真值
- `aigc_global` 没有定位真值

### 4. 一级标签和二级标签分开

- 一级标签：`authentic / manipulated / fully_generated / unknown`
- 二级标签：`copy_move / splice / inpainting_removal / inpainting_replacement / aigc_global / none / uncertain`

### 5. 原始数据差异不要直接丢掉

原始数据里的子集专有字段不要硬塞到顶层，统一放进：

- `attributes`
- `raw_meta`

这样统一格式稳定，但原始信息不丢。

## 该 demo 的用途

你可以直接拿这套结构去做：

- 数据读取器开发
- `manifest` 解析
- 最小样例测试
- 工具接入与输出校验
- 前端或接口演示
