from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from pipeline import predict_risk, get_sodium_for_location, get_sodium_risk_level, LOCATION_WATER_SODIUM

app = FastAPI(title="Large-Scale Kidney Diagnostic API", description="120k Sample Model — Gender, Smoking & Environment Aware")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Models ───────────────────────────────────────────────────────────

class PatientData(BaseModel):
    age: float
    gender: int                              # 0=Female, 1=Male
    smoker: int                              # 0=No, 1=Yes
    creatinine: float
    urine_calcium: Optional[float] = None
    urine_ph: Optional[float] = None
    uric_acid: Optional[float] = None
    location: Optional[str] = None           # e.g. "Cairo"
    water_sodium: Optional[float] = None     # direct override (ppt converted to mg/L internally)


# ── Class label mapping ─────────────────────────────────────────────────────

CLASSES = {
    0: "Healthy",
    1: "Suspected Kidney Dysfunction",
    2: "Severe Kidney Failure",
    3: "Uric Acid Stones Risk",
    4: "Calcium Stones Risk",
    5: "Multiple Stone Risk"
}

CLASS_SEVERITY = {0: 0, 1: 1, 2: 3, 3: 2, 4: 2, 5: 3}


# ── Predict Endpoint ────────────────────────────────────────────────────────

@app.post("/predict")
def predict(data: PatientData):
    # Resolve water sodium: explicit value > location lookup > default
    if data.water_sodium is not None:
        sodium = data.water_sodium
    elif data.location:
        sodium = get_sodium_for_location(data.location)
    else:
        sodium = 80.0  # world average

    result = predict_risk(
        age=data.age,
        gender=data.gender,
        smoker=data.smoker,
        creatinine=data.creatinine,
        urine_calcium=data.urine_calcium,
        urine_ph=data.urine_ph,
        uric_acid=data.uric_acid,
        water_sodium=sodium
    )
    
    predicted_class_name = CLASSES[result["prediction_class"]]
    
    # ── Risk factor warnings ────────────────────────────────────────────
    risk_factors = []
    
    # Gender-based warnings
    if data.gender == 1:
        risk_factors.append({
            "factor": "Male Gender",
            "icon": "♂",
            "detail": "Males have 2× higher kidney stone prevalence and higher baseline creatinine levels.",
            "severity": "moderate"
        })
    else:
        risk_factors.append({
            "factor": "Female Gender",
            "icon": "♀",
            "detail": "Estrogen provides some protective effect against kidney stones before menopause.",
            "severity": "low"
        })
    
    # Smoking warnings
    if data.smoker == 1:
        risk_factors.append({
            "factor": "Active Smoker",
            "icon": "🚬",
            "detail": "Smoking causes renal vasoconstriction and oxidative stress, accelerating kidney damage by 40-60%.",
            "severity": "high"
        })
    
    # Water quality warnings
    sodium_risk = get_sodium_risk_level(sodium)
    if sodium > 120:
        risk_factors.append({
            "factor": f"Water Quality: {sodium_risk['level']}",
            "icon": "💧",
            "detail": f"Water salinity at {(sodium / 1000):.2f} ppt — {sodium_risk['description']}",
            "severity": "high" if sodium > 250 else "moderate"
        })
    
    # ── Urgent Hospital Logic (enhanced) ────────────────────────────────
    is_urgent = False
    urgent_reasons = []
    
    # Severe Kidney Failure check
    if result["prediction_class"] == 2:
        # Lower threshold for smokers
        threshold = 0.45 if data.smoker == 1 else 0.60
        if result["probabilities"][2] > threshold:
            is_urgent = True
            urgent_reasons.append("High probability of severe kidney failure")
    
    if data.creatinine > 3.0:
        is_urgent = True
        urgent_reasons.append("Critically elevated creatinine")
    
    # Smoker + high creatinine compound risk
    if data.smoker == 1 and data.creatinine > 2.0:
        is_urgent = True
        urgent_reasons.append("Smoker with elevated creatinine — accelerated kidney damage risk")
    
    # High sodium + stone risk compound
    if sodium > 300 and result["prediction_class"] in [4, 5]:
        risk_factors.append({
            "factor": "Environmental Alert",
            "icon": "⚠️",
            "detail": "Dangerous water sodium combined with stone risk — consider water filtration or relocation.",
            "severity": "critical"
        })
        
    return {
        "status": "success",
        "predicted_class": predicted_class_name,
        "prediction_class_id": result["prediction_class"],
        "probabilities": result["probabilities"],
        "urgent_hospital_visit": is_urgent,
        "urgent_reasons": urgent_reasons,
        "risk_factors": risk_factors,
        "water_sodium_mg_l": sodium,
        "water_risk": sodium_risk,
        "patient_summary": {
            "gender": "Male" if data.gender == 1 else "Female",
            "smoker": "Yes" if data.smoker == 1 else "No",
            "location": data.location or "Not specified",
            "age": data.age
        }
    }


# ── Analytics Endpoint ──────────────────────────────────────────────────────

@app.post("/analytics")
def analytics(data: PatientData):
    """Deep analytics endpoint: returns risk breakdowns, comparisons, and recommendations."""
    # Resolve sodium
    if data.water_sodium is not None:
        sodium = data.water_sodium
    elif data.location:
        sodium = get_sodium_for_location(data.location)
    else:
        sodium = 80.0

    # Run prediction for this patient
    main_result = predict_risk(
        age=data.age, gender=data.gender, smoker=data.smoker,
        creatinine=data.creatinine, urine_calcium=data.urine_calcium,
        urine_ph=data.urine_ph, uric_acid=data.uric_acid,
        water_sodium=sodium
    )
    
    # Compare: same patient as opposite gender
    alt_gender = 1 - data.gender
    alt_gender_result = predict_risk(
        age=data.age, gender=alt_gender, smoker=data.smoker,
        creatinine=data.creatinine, urine_calcium=data.urine_calcium,
        urine_ph=data.urine_ph, uric_acid=data.uric_acid,
        water_sodium=sodium
    )
    
    # Compare: same patient as non-smoker
    nonsmoker_result = predict_risk(
        age=data.age, gender=data.gender, smoker=0,
        creatinine=data.creatinine, urine_calcium=data.urine_calcium,
        urine_ph=data.urine_ph, uric_acid=data.uric_acid,
        water_sodium=sodium
    )
    
    # Compare: same patient with clean water (0.02 ppt)
    clean_water_result = predict_risk(
        age=data.age, gender=data.gender, smoker=data.smoker,
        creatinine=data.creatinine, urine_calcium=data.urine_calcium,
        urine_ph=data.urine_ph, uric_acid=data.uric_acid,
        water_sodium=20.0
    )
    
    # Smoking impact score (0-100)
    if data.smoker == 1:
        # How much worse is smoking making things?
        healthy_prob_diff = nonsmoker_result["probabilities"][0] - main_result["probabilities"][0]
        smoking_impact = min(100, max(0, int(healthy_prob_diff * 200 + 30)))
    else:
        smoking_impact = 0
    
    # Water impact score (0-100)
    water_healthy_diff = clean_water_result["probabilities"][0] - main_result["probabilities"][0]
    water_impact = min(100, max(0, int(water_healthy_diff * 200 + (sodium / 5))))
    
    # Generate personalized recommendations
    recommendations = []
    
    if data.smoker == 1:
        recommendations.append({
            "priority": "critical",
            "icon": "🚭",
            "title": "Quit Smoking Immediately",
            "detail": f"Smoking is increasing your kidney damage risk. Quitting could improve your healthy probability by {max(0, healthy_prob_diff*100):.1f}%.",
            "category": "lifestyle"
        })
    
    sodium_risk = get_sodium_risk_level(sodium)
    if sodium > 120:
        recommendations.append({
            "priority": "high" if sodium > 200 else "moderate",
            "icon": "💧",
            "title": "Address Water Quality",
            "detail": f"Your area's water has {(sodium / 1000):.2f} ppt salinity ({sodium_risk['level']}). Consider a reverse-osmosis filter or bottled low-sodium water.",
            "category": "environment"
        })
    
    if data.creatinine > 1.5:
        recommendations.append({
            "priority": "high",
            "icon": "🏥",
            "title": "Regular Kidney Function Monitoring",
            "detail": "Elevated creatinine warrants regular eGFR testing every 3-6 months.",
            "category": "medical"
        })
    
    if main_result["prediction_class"] in [3, 4, 5]:
        recommendations.append({
            "priority": "high",
            "icon": "🥤",
            "title": "Increase Water Intake",
            "detail": "Drink 2.5-3L of clean water daily to reduce stone formation risk. Avoid high-oxalate foods.",
            "category": "lifestyle"
        })
    
    if data.gender == 1 and data.age > 50:
        recommendations.append({
            "priority": "moderate",
            "icon": "📋",
            "title": "Annual Prostate & Kidney Screening",
            "detail": "Males over 50 should get annual kidney and urological screenings.",
            "category": "medical"
        })
    
    if data.gender == 0 and data.age > 50:
        recommendations.append({
            "priority": "moderate",
            "icon": "📋",
            "title": "Post-Menopausal Kidney Monitoring",
            "detail": "Estrogen decline after menopause removes kidney protection. Regular monitoring recommended.",
            "category": "medical"
        })
    
    return {
        "status": "success",
        "current_prediction": {
            "class": CLASSES[main_result["prediction_class"]],
            "class_id": main_result["prediction_class"],
            "probabilities": main_result["probabilities"]
        },
        "gender_comparison": {
            "current_gender": "Male" if data.gender == 1 else "Female",
            "current_probabilities": main_result["probabilities"],
            "opposite_gender": "Male" if alt_gender == 1 else "Female",
            "opposite_probabilities": alt_gender_result["probabilities"],
        },
        "smoking_analysis": {
            "is_smoker": data.smoker == 1,
            "impact_score": smoking_impact,
            "current_probabilities": main_result["probabilities"],
            "if_nonsmoker_probabilities": nonsmoker_result["probabilities"],
        },
        "water_analysis": {
            "current_sodium_mg_l": sodium,
            "risk": sodium_risk,
            "impact_score": water_impact,
            "current_probabilities": main_result["probabilities"],
            "if_clean_water_probabilities": clean_water_result["probabilities"],
            "location": data.location or "Not specified"
        },
        "recommendations": recommendations
    }


# ── Locations Endpoint ──────────────────────────────────────────────────────

@app.get("/locations")
def get_locations():
    """Return all available locations with their water sodium levels."""
    locations = []
    for name, sodium in sorted(LOCATION_WATER_SODIUM.items()):
        risk = get_sodium_risk_level(sodium)
        locations.append({
            "name": name,
            "sodium_mg_l": sodium,
            "risk_level": risk["level"],
            "risk_color": risk["color"]
        })
    return {"locations": locations}


if __name__ == "__main__":
    print("Starting local API server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
