from pathlib import Path
from factoryvision.cv.synthetic import generate_dataset,generate_anomaly_dataset
from factoryvision.cv.supervised import PixelSegmentationModel
from factoryvision.cv.anomaly import FeatureMemoryAnomaly

def test_real_models_train_and_predict(tmp_path:Path):
    generate_dataset(tmp_path/'c',frames=12,width=240,height=160)
    imgs=sorted((tmp_path/'c/images').glob('*.png')); masks=sorted((tmp_path/'c/masks').glob('*.png'))
    m=PixelSegmentationModel().fit(imgs[:8],masks[:8],pixels_per_image=1200); metrics=m.evaluate(imgs[8:],masks[8:]); assert metrics['pixel_accuracy']>.80
    generate_anomaly_dataset(tmp_path/'a',count=10); normals=sorted((tmp_path/'a/normal').glob('*.png')); anomalies=sorted((tmp_path/'a/anomaly').glob('*.png'))
    a=FeatureMemoryAnomaly().fit(normals[:7]); result=a.evaluate(normals[7:],anomalies); assert 0<=result['image_auroc']<=1
