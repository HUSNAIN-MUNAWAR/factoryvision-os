from pathlib import Path
import pytest

from factoryvision.cv.synthetic import generate_anomaly_dataset

pytest.importorskip("torch")

from factoryvision.cv.anomaly_autoencoder import AutoencoderAnomaly  # noqa: E402

def test_autoencoder_trains_and_scores(tmp_path:Path):
    generate_anomaly_dataset(tmp_path/'a',count=8)
    normal=sorted((tmp_path/'a/normal').glob('*.png')); abnormal=sorted((tmp_path/'a/anomaly').glob('*.png'))
    model=AutoencoderAnomaly(size=(32,32)); history=model.fit(normal[:6],epochs=2,batch_size=3)
    metrics=model.evaluate(normal[6:],abnormal[:2])
    assert len(history)==2 and 0<=metrics['image_auroc']<=1
