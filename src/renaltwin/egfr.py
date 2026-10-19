def ckd_epi_2021(scr_mgdl: float, age: float, sex: str) -> float:
    """2021 race-free CKD-EPI creatinine equation; intended for research demos."""
    if scr_mgdl <= 0 or age <= 0 or sex not in {"F", "M"}:
        raise ValueError("scr and age must be positive and sex must be F or M")
    female = sex == "F"
    kappa, alpha = (0.7, -0.241) if female else (0.9, -0.302)
    return float(142 * min(scr_mgdl/kappa, 1)**alpha * max(scr_mgdl/kappa, 1)**(-1.2) * 0.9938**age * (1.012 if female else 1.0))

def creatinine_from_egfr(egfr: float, age: float, sex: str) -> float:
    lo, hi = 0.1, 30.0
    for _ in range(100):
        mid=(lo+hi)/2
        if ckd_epi_2021(mid, age, sex) > egfr: lo=mid
        else: hi=mid
    return (lo+hi)/2

def ckd_stage(egfr):
    if egfr is None: return None
    if egfr >= 90: return "G1"
    if egfr >= 60: return "G2"
    if egfr >= 45: return "G3a"
    if egfr >= 30: return "G3b"
    if egfr >= 15: return "G4"
    return "G5"
