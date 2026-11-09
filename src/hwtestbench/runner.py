"""JSON-configured voltage/current/frequency tests and machine-readable reports."""
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
import json, math
from pathlib import Path
from .instruments import SimulatedInstruments

@dataclass(frozen=True)
class TestResult:
    name:str
    measured:float
    expected:float
    tolerance:float
    unit:str
    passed:bool

def evaluate(name,measured,expected,tolerance,unit):
    if not all(math.isfinite(float(x)) for x in (measured,expected,tolerance)) or tolerance<0: raise ValueError("measurements and tolerance must be finite; tolerance non-negative")
    return TestResult(name,float(measured),float(expected),float(tolerance),unit,abs(measured-expected)<=tolerance)

def run_plan(plan:dict,instruments:SimulatedInstruments):
    results=[]
    try:
        tests=plan.get("tests")
        if not isinstance(tests,list) or not tests: raise ValueError("test plan requires a non-empty tests list")
        for test in tests:
            kind=test["measurement"]
            if kind=="voltage_v": measured=instruments.measure_voltage(); unit="V"
            elif kind=="current_a": measured=instruments.measure_current(); unit="A"
            elif kind=="frequency_hz": measured=instruments.measure_frequency(); unit="Hz"
            else: raise ValueError(f"unsupported measurement {kind}")
            results.append(evaluate(test["name"],measured,test["expected"],test["tolerance"],unit))
    finally: instruments.disable_output()
    return {"test_plan":plan.get("name","unnamed"),"timestamp_utc":datetime.now(timezone.utc).isoformat(),"source":"simulated instruments","passed":all(x.passed for x in results),"results":[asdict(x) for x in results]}

def export(report:dict,path:str|Path):
    target=Path(path); target.parent.mkdir(parents=True,exist_ok=True)
    if target.suffix.lower()==".json": target.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    elif target.suffix.lower()==".csv":
        import csv
        fields=["name","measured","expected","tolerance","unit","passed"]
        with target.open("w",newline="",encoding="utf-8") as stream:
            writer=csv.DictWriter(stream,fieldnames=fields); writer.writeheader(); writer.writerows(report["results"])
    else: raise ValueError("report path must end in .json or .csv")
