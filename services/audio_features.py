import numpy as np
import librosa
FEATURE_NAMES = ["mfcc_1","mfcc_2","mfcc_3","mfcc_4","mfcc_5","rms","spectral_centroid","zero_crossing_rate"]
def extract_features(file_path, sample_rate=22050, max_seconds=30):
    audio, sr = librosa.load(file_path, sr=sample_rate, mono=True, duration=max_seconds)
    if audio.size == 0: raise ValueError("The audio file is empty or could not be decoded.")
    if len(audio) < int(sr * 0.25): raise ValueError("Audio must be at least 0.25 seconds long.")
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=5)
    values = [*np.mean(mfcc,axis=1).tolist(),float(np.mean(librosa.feature.rms(y=audio))),float(np.mean(librosa.feature.spectral_centroid(y=audio,sr=sr))),float(np.mean(librosa.feature.zero_crossing_rate(y=audio)))]
    vector = np.asarray(values,dtype=np.float64)
    if not np.all(np.isfinite(vector)): raise ValueError("Audio features could not be calculated reliably.")
    return vector, {"duration_seconds":round(len(audio)/sr,2),"sample_rate":sr,"features":{n:round(float(v),5) for n,v in zip(FEATURE_NAMES,vector)}}
