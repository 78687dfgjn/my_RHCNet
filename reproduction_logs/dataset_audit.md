# Dataset audit

This audit is based on the two user-provided ZIP files. They are present on the server at `/hy-tmp/DUO.zip` and `/hy-tmp/UTDAC2020.zip`; server-side sizes and SHA256 values match the source files below, both ZIP CRC checks passed, and both archives were extracted under `/hy-tmp/RHCNet/datasets/`. The previous incomplete copies were removed only after the complete archives passed these checks. No dataset was downloaded from the internet, and original archives/images/annotations were not modified.

## Archive identity

| Archive | Bytes | SHA256 |
|---|---:|---|
| `DUO.zip` | 2,940,459,407 | `5DE58F03A09C152607A99722F453100A0DE7C37FB1A6BC3B767A2E4293EE1992` |
| `UTDAC2020.zip` | 1,739,240,159 | `2F28943D2E808E983B0EC877DB5C7589A25BD582E7FE2D71D6CB44A9339740F3` |

## DUO

- ZIP layout: `DUO/images/train/`, `DUO/images/test/`, `DUO/annotations/instances_train.json`, and `DUO/annotations/instances_test.json`.
- Train: 6,671 images and 63,998 annotations. Test: 1,111 images and 10,517 annotations. Total: 7,782, matching the paper's stated dataset total.
- Four categories: ID 1 `holothurian`, 2 `echinus`, 3 `scallop`, 4 `starfish`; no invalid or non-positive boxes were found in either annotation file.
- The built MMDetection datasets contain 6,617 train and 1,100 test images: the source annotations include 54 train and 11 test images with no annotations, which the configured `CocoDataset` filters by default. No images were filtered for dimensions below 32 pixels. This is the actual smoke-training/evaluation count.
- The archive has no separate validation split. The checked-in config expects `train2017/`, `val2017/`, `test2017/` and COCO-style `instances_*2017.json` names. The reproduction config points to the actual `train/` and `test/` paths. The test set is reserved for a single smoke evaluation and final evaluation; it is not used for checkpoint selection.

## UTDAC2020

- Standard four-class annotation layout: `UTDAC2020/train2017/` (5,168 images, 37,196 annotations) and `UTDAC2020/val2017/` (1,293 images, 9,489 annotations), with the matching `instances_train2017.json` and `instances_val2017.json` files.
- Categories in the standard files: ID 1 `echinus`, 2 `starfish`, 3 `holothurian`, 4 `scallop`. This is the same four-class set as the RHCNet config; category IDs are not in the same order as the config's `classes` tuple, so MMDetection's name-based COCO mapping must be retained.
- The ZIP also includes `_waterweeds.json` five-class annotations. Those add 50 train and 21 val annotations for `waterweeds`; they are not used by the repository's four-class config and should not be mixed into this reproduction.
- Five standard-file annotations have negative box dimensions: train IDs 17748 (`000864.jpg`, scallop, width -130), 33350 (`000332.jpg`, echinus, height -24), 34076 (`000213.jpg`, scallop, width -168), 35079 (`001063.jpg`, scallop, height -574); val ID 6920 (`001067.jpg`, scallop, width -695). The corresponding `area` values are negative and `iscrowd=0`. `prepare_utdac_annotations.py` removes these invalid boxes only from derived JSON files; original JSON remains untouched.
- `testA.json`/`testB.json` each reference 1,200 images, but matching `testA`/`testB` image directories are absent from the archive and the annotation category counts do not match the standard set. They are not usable for evaluation from the uploaded archive.
- This archive has 6,461 train/val entries (6,460 unique image contents, with one duplicate across the splits), whereas the paper states 5,643 images: 818 fewer than the supplied archive. ZIP CRC audit identifies identical image contents at `train2017/000004.jpg` and `val2017/000001.jpg`. The derived annotation preparation keeps the validation copy and removes the training copy and its labels to avoid split leakage. Original archives/images/JSON are unchanged. The paper and archive version/count conflict remains.
- The derived training annotations contain 5,167 images and 37,186 annotations; validation contains 1,293 images and 9,488 annotations. Dataset construction passed for both splits using the reproduction config and class order `('holothurian', 'echinus', 'scallop', 'starfish')`.

## Metric references

The paper's Table 1 references are DUO AP/AP50/AP75/APS/APM/APL = 70.53/87.56/77.29/56.63/71.70/69.94, and UTDAC = 53.35/86.93/58.97/27.23/48.90/59.29. The README separately reports UTDAC AP 50.8. These references will not be conflated.
