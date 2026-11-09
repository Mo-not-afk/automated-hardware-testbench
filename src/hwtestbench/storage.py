"""Persist run summaries and individual results in SQLite."""
import json,sqlite3

def save_report(db:sqlite3.Connection,report:dict)->int:
    db.execute("CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, test_plan TEXT NOT NULL, timestamp_utc TEXT NOT NULL, source TEXT NOT NULL, passed INTEGER NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS results(id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL REFERENCES runs(id), name TEXT NOT NULL, measured REAL NOT NULL, expected REAL NOT NULL, tolerance REAL NOT NULL, unit TEXT NOT NULL, passed INTEGER NOT NULL)")
    cursor=db.execute("INSERT INTO runs(test_plan,timestamp_utc,source,passed) VALUES(?,?,?,?)",(report["test_plan"],report["timestamp_utc"],report["source"],int(report["passed"])))
    run_id=cursor.lastrowid
    db.executemany("INSERT INTO results(run_id,name,measured,expected,tolerance,unit,passed) VALUES(?,?,?,?,?,?,?)",[(run_id,r["name"],r["measured"],r["expected"],r["tolerance"],r["unit"],int(r["passed"])) for r in report["results"]])
    db.commit(); return int(run_id)

def get_report(db,run_id:int):
    run=db.execute("SELECT id,test_plan,timestamp_utc,source,passed FROM runs WHERE id=?",(run_id,)).fetchone()
    if run is None: raise KeyError(f"unknown run id {run_id}")
    results=db.execute("SELECT name,measured,expected,tolerance,unit,passed FROM results WHERE run_id=? ORDER BY id",(run_id,)).fetchall()
    return {"id":run[0],"test_plan":run[1],"timestamp_utc":run[2],"source":run[3],"passed":bool(run[4]),"results":[{"name":x[0],"measured":x[1],"expected":x[2],"tolerance":x[3],"unit":x[4],"passed":bool(x[5])} for x in results]}
