from __future__ import annotations
from typing import Any

def calculate_news2_score_from_vitals(vital: dict[str, Any]) -> int:
    """
    Calculate the NEWS2 (National Early Warning Score 2) based on patient vitals.
    
    Parameters:
    - respiration_rate (RR): breaths per minute
    - spo2: oxygen saturation percentage
    - oxygen_support: liters per minute (0 if room air)
    - systolic_bp: systolic blood pressure
    - heart_rate: beats per minute
    - consciousness: 'A' (Alert), 'V' (Voice), 'P' (Pain), 'U' (Unresponsive)
    - temperature: degrees Celsius
    """
    score = 0
    
    # 1. Respiration Rate
    rr = vital.get("respiration_rate", 16)
    if rr <= 8 or rr >= 25: 
        score += 3
    elif 21 <= rr <= 24: 
        score += 2
    elif 9 <= rr <= 11: 
        score += 1
    
    # 2. SpO2 (Scale 1)
    # Note: NEWS2 has Scale 2 for hypercapnic respiratory failure, but Scale 1 is default.
    spo2 = vital.get("spo2", 98)
    if spo2 <= 91: 
        score += 3
    elif 92 <= spo2 <= 93: 
        score += 2
    elif 94 <= spo2 <= 95: 
        score += 1
    
    # 3. Air or Oxygen
    # If on supplemental oxygen, add 2 points
    if vital.get("oxygen_support", 0) > 0: 
        score += 2
    
    # 4. Systolic BP
    sbp = vital.get("systolic_bp", 120)
    if sbp <= 90 or sbp >= 220: 
        score += 3
    elif 91 <= sbp <= 100: 
        score += 2
    elif 101 <= sbp <= 110: 
        score += 1
    
    # 5. Heart Rate
    hr = vital.get("heart_rate", 70)
    if hr <= 40 or hr >= 131: 
        score += 3
    elif 111 <= hr <= 130: 
        score += 2
    elif (41 <= hr <= 50) or (91 <= hr <= 110): 
        score += 1
    
    # 6. Consciousness (ACVPU scale)
    # A=0, C/V/P/U = 3
    cv = str(vital.get("consciousness", "A")).upper()
    if cv != "A": 
        score += 3
    
    # 7. Temperature
    temp = vital.get("temperature", 37.0)
    if temp <= 35.0: 
        score += 3
    elif temp >= 39.1: 
        score += 2
    elif (35.1 <= temp <= 36.0) or (38.1 <= temp <= 39.0): 
        score += 1
    
    return score
