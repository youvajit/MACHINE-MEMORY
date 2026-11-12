import json, uuid
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename
from config import Config
from database.db import get_db, init_db, close_db
from services.audio_features import extract_features
from services.anomaly import train_baseline, load_model, score_sample
def create_app(test_config=None):
    app=Flask(__name__); app.config.from_object(Config)
    if test_config: app.config.update(test_config)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True,exist_ok=True)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True,exist_ok=True)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db(); db=get_db()
        db.execute("INSERT OR IGNORE INTO machines(name) VALUES (?)",("Machine 1",)); db.commit()
    def save_upload(upload):
        original=secure_filename(upload.filename or "")
        if not original or "." not in original or original.rsplit(".",1)[1].lower() not in app.config["ALLOWED_EXTENSIONS"]:
            raise ValueError("Only WAV audio files are accepted.")
        filename=uuid.uuid4().hex+"_"+original; path=Path(app.config["UPLOAD_FOLDER"])/filename
        upload.save(path); return filename,path
    @app.get("/")
    def index(): return render_template("index.html",machines=get_db().execute("SELECT * FROM machines ORDER BY name").fetchall())
    @app.get("/api/dashboard")
    def dashboard():
        db=get_db()
        t=db.execute("SELECT COUNT(*) total,SUM(result='NORMAL') normal_count,SUM(result='ABNORMAL') abnormal_count,ROUND(AVG(health_score),1) avg_health FROM analyses").fetchone()
        recent=db.execute("SELECT a.*,m.name machine_name FROM analyses a JOIN machines m ON m.id=a.machine_id ORDER BY a.id DESC LIMIT 8").fetchall()
        return jsonify(total=t["total"] or 0,normal=t["normal_count"] or 0,abnormal=t["abnormal_count"] or 0,avg_health=t["avg_health"],recent=[dict(x) for x in recent])
    @app.post("/api/machines")
    def add_machine():
        name=(request.json or {}).get("name","").strip()
        if not name or len(name)>60: return jsonify(error="Enter a machine name (1–60 characters)."),400
        db=get_db()
        try: cur=db.execute("INSERT INTO machines(name) VALUES (?)",(name,)); db.commit()
        except Exception: return jsonify(error="That machine name may already exist."),409
        return jsonify(id=cur.lastrowid,name=name),201
    @app.post("/api/baseline/<int:machine_id>")
    def train(machine_id):
        uploads=request.files.getlist("files")
        if len(uploads)<5: return jsonify(error="Upload at least 5 normal WAV recordings."),400
        db=get_db()
        if not db.execute("SELECT id FROM machines WHERE id=?",(machine_id,)).fetchone(): return jsonify(error="Machine profile not found."),404
        vectors=[]
        for upload in uploads:
            filename,path=save_upload(upload)
            try: vector,_=extract_features(path,app.config["SAMPLE_RATE"],app.config["MAX_AUDIO_SECONDS"]); vectors.append(vector)
            finally: path.unlink(missing_ok=True)
        model_bytes,count=train_baseline(vectors)
        db.execute("INSERT INTO baselines(machine_id,model,sample_count) VALUES (?,?,?) ON CONFLICT(machine_id) DO UPDATE SET model=excluded.model,sample_count=excluded.sample_count,created_at=CURRENT_TIMESTAMP",(machine_id,model_bytes,count)); db.commit()
        return jsonify(message="Baseline trained.",sample_count=count)
    @app.post("/api/analyze/<int:machine_id>")
    def analyze(machine_id):
        upload=request.files.get("file")
        if not upload: return jsonify(error="Choose a WAV file first."),400
        db=get_db(); baseline=db.execute("SELECT model FROM baselines WHERE machine_id=?",(machine_id,)).fetchone()
        if not baseline: return jsonify(error="Train this machine's normal baseline first."),400
        filename,path=save_upload(upload)
        try:
            vector,details=extract_features(path,app.config["SAMPLE_RATE"],app.config["MAX_AUDIO_SECONDS"])
            result,anomaly,health=score_sample(load_model(baseline["model"]),vector)
            cur=db.execute("INSERT INTO analyses(machine_id,filename,result,anomaly_score,health_score,features) VALUES (?,?,?,?,?,?)",(machine_id,filename,result,anomaly,health,json.dumps(details["features"]))); db.commit()
            return jsonify(id=cur.lastrowid,filename=filename,result=result,anomaly_score=anomaly,health_score=health,**details)
        finally: path.unlink(missing_ok=True)
    @app.get("/api/history")
    def history():
        rows=get_db().execute("SELECT a.*,m.name machine_name FROM analyses a JOIN machines m ON m.id=a.machine_id ORDER BY a.id DESC LIMIT 100").fetchall()
        return jsonify([dict(x) for x in rows])
    @app.delete("/api/history/<int:analysis_id>")
    def delete_analysis(analysis_id):
        db=get_db(); cur=db.execute("DELETE FROM analyses WHERE id=?",(analysis_id,)); db.commit()
        if not cur.rowcount: return jsonify(error="Analysis not found."),404
        return jsonify(message="Analysis deleted.")
    return app
app=create_app()
if __name__=="__main__": app.run(debug=True)
