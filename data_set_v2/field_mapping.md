# `data_set_v2` 字段映射说明

这个文件说明当前 `data_set_v2` 中，6 类样本如何映射到统一字段。

## 子数据集到统一标签

| 来源 | `source_dataset` | `tamper_status_l1` | `tamper_type_l2` | `task_mode` | `has_localization_gt` |
|---|---|---|---|---|---|
| `CM_dataset` | `CM_dataset` | `manipulated` | `copy_move` | `classification_localization` | `true` |
| `splice_dataset` | `splice_dataset` | `manipulated` | `splice` | `classification_localization` | `true` |
| `AIGC-inpainting-removal` | `AIGC-inpainting-removal` | `manipulated` | `inpainting_removal` | `classification_localization` | `true` |
| `AIGC-inpainting-replacement` | `AIGC-inpainting-replacement` | `manipulated` | `inpainting_replacement` | `classification_localization` | `true` |
| `AIGC-global` | `AIGC-global` | `fully_generated` | `aigc_global` | `classification` | `false` |
| `600000+ authentic` | 当前版本全部继承 `CM_dataset` | `authentic` | `none` | `classification` | `false` |

## 当前 `authentic` 样本派生规则

当前版本只补入了 10 个真实样本：

- `600000` - `600009`

它们都由对应的 `copy_move` 原图派生得到：

- `600000 <- 100000`
- `600001 <- 100001`
- ...
- `600009 <- 100009`

派生规则为：

- `image_path = images/<authentic_id>/input.png`
- `original_path = images/<authentic_id>/input.png`
- `tampered_path = null`
- `mask_path = null`
- `source_crop_path = null`
- `target_crop_path = null`
- `question_ids = []`
- `raw_meta.derived_from_sample = <原篡改 sample_id>`

## 图像路径映射

| 字段 | 文件 |
|---|---|
| `image_path` | `input.png` |
| `original_path` | `original.png` |
| `tampered_path` | `tampered.png` |
| `mask_path` | `mask.png` |
| `source_crop_path` | `source_crop.png` |
| `target_crop_path` | `target_crop.png` |

## `attributes` 映射

局部篡改样本常见字段：

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

`AIGC-global` 额外使用：

- `attributes.geo_meta.lon`
- `attributes.geo_meta.lat`
- `attributes.geo_meta.gsd`
- `attributes.geo_meta.cloud`
- `attributes.geo_meta.year`
- `attributes.geo_meta.month`
- `attributes.geo_meta.day`

当前 `authentic` 样本的 `attributes` 为空对象 `{}`。

## `raw_meta` 映射

当前版本常见字段：

- `origin_dataset`
- `info`
- `file_name`
- `tag`
- `derived_from_sample`

其中 `derived_from_sample` 仅出现在 `authentic` 样本中。
