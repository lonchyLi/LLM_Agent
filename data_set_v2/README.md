# `data_set_v2` 归档格式说明

这个目录是当前代码默认读取的数据集版本。

它延续了 `data_set` 的统一协议，但已经补入 `600000+` 段的真实图样本，因此更适合作为第 1-3 周代码和产物的默认数据源。

## 当前实际内容

当前磁盘中实际包含：

- `60` 个样本目录
- `60` 条样本记录
- `1313` 条问答记录

类别分布为：

- `copy_move`：`10`
- `splice`：`10`
- `inpainting_removal`：`10`
- `inpainting_replacement`：`10`
- `aigc_global`：`10`
- `authentic / none`：`10`

一级标签分布为：

- `manipulated`：`40`
- `fully_generated`：`10`
- `authentic`：`10`

## 目录结构

```text
data_set_v2/
├── README.md
├── field_mapping.md
├── dataset_manifest.json
├── sample_records.json
├── question_records.json
├── schema/
│   ├── dataset_manifest.schema.json
│   ├── sample_record.schema.json
│   └── question_record.schema.json
└── images/
    ├── 100000/ - 100009/    (copy_move)
    ├── 200000/ - 200009/    (splice)
    ├── 300000/ - 300009/    (inpainting_removal)
    ├── 400000/ - 400009/    (inpainting_replacement)
    ├── 500000/ - 500009/    (aigc_global)
    └── 600000/ - 600009/    (authentic)
```

## 图片命名

图片统一放在：

- `images/<sample_id>/`

字段与文件名对应关系：

- `image_path` -> `input.png`
- `original_path` -> `original.png`
- `tampered_path` -> `tampered.png`
- `mask_path` -> `mask.png`
- `source_crop_path` -> `source_crop.png`
- `target_crop_path` -> `target_crop.png`

其中：

- 局部篡改样本通常同时包含 `input/original/tampered/mask`
- `copy_move` 额外包含 `source_crop/target_crop`
- `aigc_global` 只有 `input/tampered`
- `authentic` 只有 `input`

## 标签空间

一级标签：

- `authentic`
- `manipulated`
- `fully_generated`
- `unknown`

二级标签：

- `copy_move`
- `splice`
- `inpainting_removal`
- `inpainting_replacement`
- `aigc_global`
- `none`
- `uncertain`

## `authentic` 样本说明

当前 `600000-600009` 这 10 个样本是新增真实图类别，记录形式为：

- `tamper_status_l1 = "authentic"`
- `tamper_type_l2 = "none"`
- `task_mode = "classification"`
- `has_localization_gt = false`
- `question_ids = []`

当前这 10 个真实样本都来自 `CM_dataset` 的原图，对应关系记录在：

- `raw_meta.derived_from_sample`

例如：

- `600000 <- 100000`
- `600001 <- 100001`

## 文件入口

当前代码使用以下入口文件：

- `dataset_manifest.json`
- `sample_records.json`
- `question_records.json`
- `schema/*.json`

第 1-2 周的数据审计、split、分类/定位/SFT 样本构造，以及第 3 周的分类基线和 Agent 适配层，默认都以这一版数据为输入。
