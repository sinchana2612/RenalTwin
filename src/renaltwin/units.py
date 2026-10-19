class UnitError(ValueError): pass

def convert(obs_type: str, value: float, unit: str):
    if not __import__("math").isfinite(float(value)): raise UnitError("value must be finite")
    unit = unit.strip()
    canonical = {"creatinine":"mg/dL", "egfr":"mL/min/1.73 m2", "uacr":"mg/g", "hba1c":"%", "potassium":"mmol/L", "hemoglobin":"g/dL", "sbp_clinic":"mmHg", "hr_rest":"bpm", "sbp_home":"mmHg", "sleep_min":"min", "steps":"count"}.get(obs_type)
    if canonical is None: raise UnitError(f"unknown observation type: {obs_type}")
    if unit == canonical: return float(value), canonical
    if obs_type == "creatinine" and unit in {"umol/L", "µmol/L"}: return float(value)/88.4, canonical
    if obs_type == "hba1c" and unit == "mmol/mol": return 0.0915*float(value)+2.15, canonical
    raise UnitError(f"unsupported unit {unit!r} for {obs_type}; expected {canonical}")
