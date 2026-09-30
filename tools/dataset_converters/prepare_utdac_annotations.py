#!/usr/bin/env python3
"""Create derived, leakage-free UTDAC train/val COCO JSON files.

The input annotation files and images are read-only. Exact duplicate image
content shared by train and val is retained in val and removed from train.
Annotations with non-finite/invalid COCO boxes or non-positive area are omitted
from the derived JSON so the evaluator sees the same valid targets as MMDet's
training parser. The source archive remains unchanged.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path


def load_json(path):
    with path.open('r', encoding='utf-8') as stream:
        return json.load(stream)


def image_digest(image_root, image):
    path = image_root / image['file_name']
    if not path.is_file():
        raise FileNotFoundError(f"Image from annotation file is missing: {path}")
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def valid_annotation(annotation):
    bbox = annotation.get('bbox')
    if not isinstance(bbox, list) or len(bbox) != 4:
        return False
    try:
        x, y, width, height = (float(value) for value in bbox)
        area = float(annotation.get('area', width * height))
    except (TypeError, ValueError):
        return False
    return (all(math.isfinite(value) for value in (x, y, width, height, area))
            and width >= 1 and height >= 1 and area > 0)


def write_copy(source, destination, drop_image_ids):
    images = [image for image in source['images']
              if image['id'] not in drop_image_ids]
    retained_ids = {image['id'] for image in images}
    annotations = [annotation for annotation in source['annotations']
                   if annotation['image_id'] in retained_ids
                   and valid_annotation(annotation)]
    output = dict(source)
    output['images'] = images
    output['annotations'] = annotations
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('w', encoding='utf-8') as stream:
        json.dump(output, stream, ensure_ascii=False)
        stream.write('\n')
    return len(source['images']) - len(images), \
        len(source['annotations']) - len(annotations)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-json', required=True, type=Path)
    parser.add_argument('--val-json', required=True, type=Path)
    parser.add_argument('--train-images', required=True, type=Path)
    parser.add_argument('--val-images', required=True, type=Path)
    parser.add_argument('--out-dir', required=True, type=Path)
    args = parser.parse_args()

    train = load_json(args.train_json)
    val = load_json(args.val_json)
    val_digests = {}
    for image in val['images']:
        val_digests.setdefault(image_digest(args.val_images, image), []).append(image)

    drop_train_ids = set()
    for image in train['images']:
        digest = image_digest(args.train_images, image)
        matches = val_digests.get(digest, [])
        if matches:
            drop_train_ids.add(image['id'])
            names = ', '.join(item['file_name'] for item in matches)
            print(f"Train duplicate excluded: {image['file_name']} (id={image['id']}) "
                  f"matches validation image(s): {names}")

    train_images_removed, train_annotations_removed = write_copy(
        train, args.out_dir / 'instances_train2017.json', drop_train_ids)
    val_images_removed, val_annotations_removed = write_copy(
        val, args.out_dir / 'instances_val2017.json', set())
    print(f"Train: removed {train_images_removed} duplicate image(s), "
          f"{train_annotations_removed} invalid/duplicate annotation(s)")
    print(f"Val: removed {val_images_removed} image(s), "
          f"{val_annotations_removed} invalid annotation(s)")
    print(f"Wrote derived annotations under {args.out_dir}")


if __name__ == '__main__':
    main()
