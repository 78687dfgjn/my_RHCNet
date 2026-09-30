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

- Protocol selected: **standard public UTDAC2020**. RHCNet paper states 5,643 images; the public standard split in the supplied archive is 5,168 train + 1,293 val = 6,461 image entries (818 more than the paper count). The result must be labeled `standard public UTDAC2020 protocol`, not as the paper's undocumented 5,643-image protocol.
- Original four-class annotations: `train2017/` has 5,168 image entries and 37,196 annotation entries; `val2017/` has 1,293 image entries and 9,489 annotation entries. Total annotation entries: 46,685. Source JSONs are `annotations/instances_train2017.json` and `annotations/instances_val2017.json`.
- Content audit: 6,461 image entries contain 6,460 unique image contents. One exact duplicate crosses splits: `train2017/000004.jpg` and `val2017/000001.jpg`. It is recorded and retained; neither image nor annotation is removed from the official-release or paper-hparam benchmark configs.
- Categories in the standard files: ID 1 `echinus`, 2 `starfish`, 3 `holothurian`, 4 `scallop`. This is the same four-class set as the RHCNet config; category IDs are not in the same order as the config's `classes` tuple, so MMDetection's name-based COCO mapping must be retained.
- The ZIP also includes `_waterweeds.json` five-class annotations. Those add 50 train and 21 val annotations for `waterweeds`; they are not used by the repository's four-class config and should not be mixed into this reproduction.
- Five standard-file annotations have negative box dimensions: train IDs 17748 (`000864.jpg`, scallop, width -130), 33350 (`000332.jpg`, echinus, height -24), 34076 (`000213.jpg`, scallop, width -168), 35079 (`001063.jpg`, scallop, height -574); val ID 6920 (`001067.jpg`, scallop, width -695). They remain in the original JSONs used by the benchmark configs; no manual correction or deletion is applied. The unchanged MMDetection COCO parser skips boxes with nonpositive area or width/height below 1: parsed targets are 37,192 train and 9,488 val boxes, while dataset image counts remain 5,168 and 1,293.
- `testA.json`/`testB.json` each reference 1,200 images, but matching `testA`/`testB` image directories are absent from the archive and the annotation category counts do not match the standard set. They are not usable for evaluation from the uploaded archive.
- A previous preparation attempt created `annotations_reproduction/` with the duplicated training image and invalid boxes excluded. Source archives and standard JSONs were not changed, but those derivative files do not match the selected benchmark definition and must not be used. All official-release and paper-hparam configs point to the original `annotations/` JSONs. The old derived files remain only as an explicitly unselected audit artifact.
- The official and paper-hparam configs were loaded with MMDetection and their datasets built successfully against original JSONs. They report 5,168 train and 1,293 val images and class order `('holothurian', 'echinus', 'scallop', 'starfish')`; categories map by category name, not numeric ID. Config values were verified: official release uses LR 0.001, 35 epochs, steps `[24, 30]`; paper-hparam uses the same optimizer/epochs and steps `[27, 32]`.

## Metric references

The paper's Table 1 references are DUO AP/AP50/AP75/APS/APM/APL = 70.53/87.56/77.29/56.63/71.70/69.94, and UTDAC = 53.35/86.93/58.97/27.23/48.90/59.29. The README separately reports UTDAC AP 50.8. These references will not be conflated.
