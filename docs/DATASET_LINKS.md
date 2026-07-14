# Dataset links

This compact index complements the legal and technical detail in [DATASETS.md](DATASETS.md).
Third-party raw data is not committed to this repository.

| Registry key | Official source | Intended use | Repository redistribution |
|---|---|---|---|
| `steelds` | Zenodo record 20271102 | Conveyor steel/copper object detection, instance segmentation and sequential inspection | No raw mirror; official archives + checksums only |
| `visa` | Amazon Research VisA repository | Pixel-level industrial anomaly segmentation | No raw mirror; official downloader only |
| `aebad` | CUHK-AIM-Group/AeBAD | Cross-domain image/video anomaly evaluation | No raw mirror; official links only |
| `mvtec_ad` | MVTec AD official dataset page | Optional research-only anomaly benchmark | Prohibited from commercial demo dependency; noncommercial license |
| `steel_defects_roboflow` | Roboflow Universe Steel Defects | Lightweight steel defect bounding-box adapter checks | No raw mirror; manual Roboflow export |
| `factoryvision_demo` | Generated locally by `make demo` | Deterministic smoke test and CI | Yes, CC0-generated assets |

## Direct real-data links

- SteelDS record: https://zenodo.org/records/20271102
- SteelDS file downloads: `a1.zip`, `a2.zip`, `a3.zip`, `a4.zip`, `a5.zip` from the Zenodo record above.
- SteelDS baseline layout: https://github.com/MelanieNeubauer/SteelDS_Baseline
- Roboflow Steel Defects bounding boxes: https://universe.roboflow.com/hamdi-ali-akgungor/steel-defects-xbfez
- VisA AWS Open Data: https://registry.opendata.aws/visa/
- VisA archive: https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar

Run `factoryvision data list` for machine-readable metadata and consult
`datasets/registry.yaml` before any download or redistribution.
