import numpy as np
from services.anomaly import train_baseline,load_model,score_sample
def test_baseline_training_and_scoring():
    normal=np.random.default_rng(7).normal(size=(12,8))
    payload,count=train_baseline(normal)
    assert count==12
    result,anomaly,health=score_sample(load_model(payload),normal[0])
    assert result in {"NORMAL","ABNORMAL"}
    assert 0<=anomaly<=1 and 0<=health<=100
