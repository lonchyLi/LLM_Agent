# RS-Tampering-Unified-Demo Audit Report

- dataset_root: `data_set_v2`
- dataset_name: `RS-Tampering-Unified-Demo`
- sample_count: `60`
- question_count: `1313`

## Per L1

- `authentic`: `10`
- `fully_generated`: `10`
- `manipulated`: `40`

## Per Type

- `aigc_global`: `10`
- `copy_move`: `10`
- `inpainting_removal`: `10`
- `inpainting_replacement`: `10`
- `none`: `10`
- `splice`: `10`

## Per Task Mode

- `classification`: `20`
- `classification_localization`: `40`

## Per Question Type

- `question_type=1`: `50`
- `question_type=10`: `27`
- `question_type=11`: `34`
- `question_type=12`: `27`
- `question_type=13`: `34`
- `question_type=14`: `37`
- `question_type=15`: `40`
- `question_type=16`: `30`
- `question_type=17`: `30`
- `question_type=18`: `10`
- `question_type=19`: `10`
- `question_type=2`: `37`
- `question_type=20`: `10`
- `question_type=21`: `10`
- `question_type=22`: `10`
- `question_type=23`: `70`
- `question_type=24`: `70`
- `question_type=3`: `174`
- `question_type=4`: `37`
- `question_type=5`: `214`
- `question_type=6`: `27`
- `question_type=7`: `194`
- `question_type=8`: `37`
- `question_type=9`: `94`

## Issues

- No validation or linkage issues found.

## Sample Summaries

- `100000` | `copy_move` | `classification_localization` | questions=`20` | image=`512x512 RGB`
- `100001` | `copy_move` | `classification_localization` | questions=`20` | image=`512x512 RGB`
- `100002` | `copy_move` | `classification_localization` | questions=`20` | image=`512x512 RGB`
- `100003` | `copy_move` | `classification_localization` | questions=`1` | image=`512x512 RGB`
- `100004` | `copy_move` | `classification_localization` | questions=`1` | image=`512x512 RGB`
- `100005` | `copy_move` | `classification_localization` | questions=`20` | image=`512x512 RGB`
- `100006` | `copy_move` | `classification_localization` | questions=`20` | image=`512x512 RGB`
- `100007` | `copy_move` | `classification_localization` | questions=`20` | image=`512x512 RGB`
- `100008` | `copy_move` | `classification_localization` | questions=`1` | image=`512x512 RGB`
- `100009` | `copy_move` | `classification_localization` | questions=`20` | image=`512x512 RGB`
- `200000` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `200001` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `200002` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `200003` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `200004` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `200005` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `200006` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `200007` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `200008` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `200009` | `splice` | `classification_localization` | questions=`16` | image=`512x512 RGB`
- `300000` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `300001` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `300002` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `300003` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `300004` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `300005` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `300006` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `300007` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `300008` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `300009` | `inpainting_removal` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400000` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400001` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400002` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400003` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400004` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400005` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400006` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400007` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400008` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `400009` | `inpainting_replacement` | `classification_localization` | questions=`47` | image=`512x512 RGB`
- `500000` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `500001` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `500002` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `500003` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `500004` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `500005` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `500006` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `500007` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `500008` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `500009` | `aigc_global` | `classification` | questions=`7` | image=`512x512 RGB`
- `600000` | `none` | `classification` | questions=`0` | image=`512x512 L`
- `600001` | `none` | `classification` | questions=`0` | image=`512x512 L`
- `600002` | `none` | `classification` | questions=`0` | image=`512x512 L`
- `600003` | `none` | `classification` | questions=`0` | image=`512x512 L`
- `600004` | `none` | `classification` | questions=`0` | image=`512x512 L`
- `600005` | `none` | `classification` | questions=`0` | image=`512x512 L`
- `600006` | `none` | `classification` | questions=`0` | image=`512x512 L`
- `600007` | `none` | `classification` | questions=`0` | image=`512x512 L`
- `600008` | `none` | `classification` | questions=`0` | image=`512x512 L`
- `600009` | `none` | `classification` | questions=`0` | image=`512x512 L`
