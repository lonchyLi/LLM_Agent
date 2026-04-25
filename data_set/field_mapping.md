# Field Mapping

这个文件说明原始 5 类数据在统一归档格式中的字段映射方式，以及本 `demo/` 中各示例样本的来源。

## 子数据集到统一标签的映射

| 原始来源 | `source_dataset` | `tamper_status_l1` | `tamper_type_l2` | `task_mode` | `has_localization_gt` |
|---|---|---|---|---|---|
| `CM_dataset` | `CM_dataset` | `manipulated` | `copy_move` | `classification_localization` | `true` |
| `splice_dataset` | `splice_dataset` | `manipulated` | `splice` | `classification_localization` | `true` |
| `AIGC-inpainting/removal` | `AIGC-inpainting-removal` | `manipulated` | `inpainting_removal` | `classification_localization` | `true` |
| `AIGC-inpainting/replacement` | `AIGC-inpainting-replacement` | `manipulated` | `inpainting_replacement` | `classification_localization` | `true` |
| `AIGC-global` | `AIGC-global` | `fully_generated` | `aigc_global` | `classification` | `false` |

## 图像路径映射

统一目录下每个样本都放在：

- `images/<sample_id>/`

字段到文件名的映射固定如下：

| 字段 | 对应文件 |
|---|---|
| `image_path` | `input.png` |
| `original_path` | `original.png` |
| `tampered_path` | `tampered.png` |
| `mask_path` | `mask.png` |
| `source_crop_path` | `source_crop.png` |
| `target_crop_path` | `target_crop.png` |

## `attributes` 映射

局部篡改类样本的统一 `attributes` 常见来自原始结构化信息：

| 统一字段 | 常见来源 |
|---|---|
| `object_class` | `info.Q2` |
| `source_region` | `info.Q4` |
| `target_region` | `info.Q6` |
| `tampered_area_bucket` | `info.Q8` |
| `tampered_area_ratio` | `info.Q8_tampered_size` |
| `source_area_ratio` | `info.Q8_source_size` |
| `relative_position` | `info.Q10` |
| `relative_size` | `info.Q12` |
| `rotation_applied` | `info.Q14` |
| `ai_used` | `info.Q16` |
| `quality_tier` | `info.Q17` |

`AIGC-global` 额外把地理元数据放进：

- `attributes.geo_meta.lon`
- `attributes.geo_meta.lat`
- `attributes.geo_meta.gsd`
- `attributes.geo_meta.cloud`
- `attributes.geo_meta.year`
- `attributes.geo_meta.month`
- `attributes.geo_meta.day`

## `raw_meta` 映射

`raw_meta` 用来保留不直接放进顶层的原始信息，当前示例中常见：

- `origin_dataset`
- `info`
- `file_name`
- `tag`

## 本 demo 样本来源

| demo 样本范围 | 说明 |
|---|---|
| `100000` - `100004` | `CM_dataset` 的 `copy_move` 示例 |
| `200000` - `200004` | `splice_dataset` 的 `splice` 示例 |
| `300000` - `300004` | `AIGC-inpainting-removal` 示例 |
| `400000` - `400004` | `AIGC-inpainting-replacement` 示例 |
| `500000` - `500004` | `AIGC-global` 示例 |
