import io
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
def train_baseline(feature_rows):
    rows=np.asarray(feature_rows,dtype=np.float64)
    if rows.ndim!=2 or rows.shape[0]<5: raise ValueError("At least 5 normal audio samples are required.")
    model=IsolationForest(n_estimators=150,contamination="auto",random_state=42).fit(rows)
    buffer=io.BytesIO(); joblib.dump(model,buffer)
    return buffer.getvalue(),int(rows.shape[0])
def load_model(model_bytes): return joblib.load(io.BytesIO(model_bytes))
def score_sample(model,feature_vector):
    prediction=int(model.predict([feature_vector])[0]); raw=float(model.decision_function([feature_vector])[0])
    anomaly=float(np.clip(0.5-raw,0.0,1.0))
    return ("NORMAL" if prediction==1 else "ABNORMAL"),round(anomaly,4),round(float((1-anomaly)*100),1)
