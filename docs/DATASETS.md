# Dataset Registry and Licensing

Access checked: **2026-07-14**. FactoryVision OS separates software licensing from dataset licensing. Raw third-party datasets are never committed by default.

## SteelDS
- **Official record:** https://zenodo.org/records/20271102
- **Direct files:** Zenodo record files `a1.zip` … `a5.zip`
- **Paper:** https://arxiv.org/abs/2605.26682
- **Repository:** https://github.com/MelanieNeubauer/SteelDS_Baseline
- **Size:** 67.6 GB, five archives; 24,297 labelled frames, 396 steel objects and 101 copper objects.
- **Annotations:** YOLO-format bounding-box labels in `labels/`, pixel-wise instance masks and material classes; high-resolution conveyor video/images.
- **License:** CC BY 4.0. Commercial reuse and redistribution are permitted with attribution.
- **FactoryVision purpose:** primary full-scale Workflow A source for detection, segmentation and tracking.
- **Raw files committed:** no.
- **Preparation:** download selected Zenodo archives into `datasets/raw/steelds`, extract them as `a1/`, `a2/`, etc., then run `python -m factoryvision.cli data validate steelds`; adapter implementation is intentionally manifest-first because the complete data is 67.6 GB.
- **Bounding-box layout:** the official baseline expects each subset to contain `train/images`, `train/labels`, `test/images` and `test/labels`. The label files are YOLO text annotations.
- **Integrity:** Zenodo publishes MD5 values: `a1.zip e8080e2ee06e204a5fbe837d6f64bef7`, `a2.zip 13adffb1ea8cf67ff3f9424f6ba1826d`, `a3.zip b2d49862d421770de6665a557c82c94a`, `a4.zip c1da8916a138d6a9fe29453ec0568f8e`, `a5.zip 895d4341ecf93da8689c6ea372dcf5ce`.
- **Limitations:** controlled laboratory setup; open-world contaminants and plant-specific illumination still require local validation.
- **Ethics/privacy:** no people or personal data are described.

## Roboflow Steel Defects bounding-box dataset
- **Official page:** https://universe.roboflow.com/hamdi-ali-akgungor/steel-defects-xbfez
- **Content:** 2,294 steel surface defect images across 12 object-detection classes.
- **Annotations:** bounding boxes; export manually from Roboflow Universe as YOLO, COCO or Pascal VOC.
- **License:** CC BY 4.0; attribution required. Confirm Roboflow export terms before redistribution.
- **FactoryVision purpose:** lightweight real bounding-box source for detector adapter smoke tests when SteelDS is too large to download.
- **Raw files committed:** no.
- **Download:** manual Roboflow Universe export into `datasets/raw/steel_defects_roboflow`.
- **Limitations:** dataset description is sparse on the source page, so use it as adapter/test data rather than as a production-quality benchmark without extra provenance review.

## Amazon VisA
- **Official page:** https://registry.opendata.aws/visa/
- **Download:** https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar
- **Paper:** https://arxiv.org/abs/2207.14315
- **Repository:** https://github.com/amazon-science/spot-diff
- **Size:** 10,821 images: 9,621 normal and 1,200 anomalous, across 12 object subsets.
- **Annotations:** image labels and pixel-level masks; official 1-class, 2-class high-shot and few-shot splits.
- **License:** CC BY 4.0; attribution required; commercial use allowed.
- **FactoryVision purpose:** open anomaly segmentation and supervised defect baseline.
- **Raw files committed:** no.
- **Download:** `python -m factoryvision.cli data download visa --out datasets/raw`.
- **Integrity:** the downloader should write a local SHA-256 manifest; AWS does not expose a checksum on the registry page.
- **Limitations:** mostly controlled still-image inspection; not a replacement for line-specific validation.
- **Ethics/privacy:** product imagery, no expected personal data.

## AeBAD-S and AeBAD-V
- **Official implementation/data page:** https://github.com/zhangzilongc/MMR
- **Paper:** https://arxiv.org/abs/2304.02216
- **Data links:** Google Drive and Tian Yi Cloud links maintained by the authors.
- **Content:** AeBAD-S single-blade images; AeBAD-V ordered blade videos with illumination, viewpoint and background domain shifts.
- **Annotations:** anomaly labels and masks; video sequence structure.
- **License:** repository includes CC BY 4.0 dataset license; attribution required.
- **FactoryVision purpose:** domain-shift and video anomaly research adapter.
- **Raw files committed:** no.
- **Download:** manual author-hosted link, followed by a SHA-256 manifest.
- **Limitations:** aero-engine blade domain; author-hosted links may require interactive download.
- **Ethics/privacy:** industrial components only.

## MVTec AD (optional, noncommercial)
- **Official page:** https://www.mvtec.com/research-teaching/datasets/mvtec-ad
- **Paper:** https://openaccess.thecvf.com/content_CVPR_2019/html/Bergmann_MVTec_AD_--_A_Comprehensive_Real-World_Dataset_for_Unsupervised_Anomaly_CVPR_2019_paper.html
- **Size:** 5,354 high-resolution images, 15 categories, over 70 anomaly types.
- **Annotations:** pixel-precise anomaly masks.
- **License:** CC BY-NC-SA 4.0. **Commercial use is explicitly prohibited.**
- **FactoryVision purpose:** optional research benchmark only; disabled from commercial demo paths.
- **Raw files committed:** no; redistribution disabled.
- **Download:** form-based official download only.
- **Limitations:** benchmark saturation and noncommercial restriction.

## FactoryVision deterministic demo dataset
- **Origin:** generated by `factoryvision.cv.synthetic`.
- **Size:** 54 ordered conveyor frames plus 24 normal and 8 anomalous inspection images.
- **Annotations:** pixel labels, object identities, anomaly masks, frame order.
- **License:** CC0-1.0.
- **Purpose:** legally redistributable smoke-test and CPU demonstration. It does not claim to represent production accuracy.
- **Command:** `make demo`.
- **Integrity:** deterministic seeds are fixed in source; generated artifacts can be hashed locally.
