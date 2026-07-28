import { useState, useEffect } from 'react';
import axios from 'axios';

function Diagnosis() {
  const [formData, setFormData] = useState({
    age: '',
    gender: 0,
    smoker: 0,
    creatinine: '',
    urine_calcium: '',
    urine_ph: '',
    uric_acid: '',
    location: ''
  });

  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // Find selected location details
  const selectedLoc = locations.find(l => l.name === formData.location) || {
    name: '',
    sodium_mg_l: 80,
    risk_level: 'Low Risk',
    risk_color: '#22d3ee'
  };

  useEffect(() => {
    // Fetch locations from API
    axios.get('http://localhost:8000/locations')
      .then(res => {
        setLocations(res.data.locations);
        if (res.data.locations.length > 0) {
          setFormData(prev => ({ ...prev, location: res.data.locations[0].name }));
        }
      })
      .catch(err => {
        console.error('Error fetching locations', err);
      });
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleToggle = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const payload = {
        age: parseFloat(formData.age),
        gender: formData.gender,
        smoker: formData.smoker,
        creatinine: parseFloat(formData.creatinine),
        location: formData.location
      };

      if (formData.urine_calcium) payload.urine_calcium = parseFloat(formData.urine_calcium);
      if (formData.urine_ph) payload.urine_ph = parseFloat(formData.urine_ph);
      if (formData.uric_acid) payload.uric_acid = parseFloat(formData.uric_acid);

      const res = await axios.post('http://localhost:8000/predict', payload);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError('An error occurred while analyzing the data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getMarkerPosition = (sodium) => {
    return Math.min(100, (sodium / 500) * 100);
  };

  const getClassColor = (classId) => {
    return `var(--c${classId})`;
  };

  const getClassNameFromId = (classId) => {
    const classes = {
      0: "Healthy",
      1: "Suspected Kidney Dysfunction",
      2: "Severe Kidney Failure",
      3: "Uric Acid Stones Risk",
      4: "Calcium Stones Risk",
      5: "Multiple Stone Risk"
    };
    return classes[classId] || "Unknown";
  };

  return (
    <div className="container-wide">
      <div className="text-center mb-4">
        <h2 className="section-title gradient-text">Kidney Diagnosis</h2>
        <p className="section-subtitle">Enter patient data for AI-powered 6-class diagnostic analysis</p>
      </div>

      {result && result.urgent_hospital_visit && (
        <div className="urgent-alert mt-2 mb-4" style={{ display: 'block' }}>
          <div style={{ fontSize: '1.1rem', fontWeight: 800 }}>⚠️ URGENT: CRITICAL INDICATORS DETECTED</div>
          <div style={{ fontSize: '0.85rem', marginTop: '4px', opacity: 0.9 }}>PLEASE VISIT A HOSPITAL OR CONSULT A DOCTOR IMMEDIATELY</div>
          <ul style={{ listStyle: 'none', padding: 0, marginTop: '8px', fontSize: '0.82rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {result.urgent_reasons.map((reason, idx) => (
              <li key={idx}>▲ {reason}</li>
            ))}
          </ul>
        </div>
      )}

      {error && <div className="urgent-alert mb-4" style={{ display: 'block' }}>{error}</div>}

      <div className="grid-2">
        {/* Left Column: Form */}
        <div className="glass-card">
          <form onSubmit={handleSubmit}>
            
            {/* Demographics Section */}
            <div className="form-card-title">
              👤 Demographics
            </div>
            
            <div className="grid-2">
              <div className="form-group">
                <div className="form-header">
                  <label className="form-label">Age</label>
                  <span className="tag tag-required">Required</span>
                </div>
                <input 
                  type="number" 
                  name="age" 
                  value={formData.age} 
                  onChange={handleChange} 
                  required 
                  min="0" 
                  max="120" 
                  className="input-field mt-1" 
                  placeholder="Enter age" 
                />
              </div>

              <div className="form-group">
                <div className="form-header">
                  <label className="form-label">Creatinine Level</label>
                  <span className="tag tag-required">Required</span>
                </div>
                <input 
                  type="number" 
                  name="creatinine" 
                  value={formData.creatinine} 
                  onChange={handleChange} 
                  required 
                  step="0.01" 
                  className="input-field mt-1" 
                  placeholder="mg/dL" 
                />
              </div>
            </div>

            <div className="form-group mt-2">
              <div className="form-header">
                <label className="form-label">Gender</label>
                <span className="tag tag-required">Required</span>
              </div>
              <div className="toggle-group mt-1">
                <button 
                  type="button" 
                  className={`toggle-option ${formData.gender === 0 ? 'active-pink' : ''}`} 
                  onClick={() => handleToggle('gender', 0)}
                >
                  Female
                </button>
                <button 
                  type="button" 
                  className={`toggle-option ${formData.gender === 1 ? 'active-blue' : ''}`} 
                  onClick={() => handleToggle('gender', 1)}
                >
                  Male
                </button>
              </div>
            </div>

            {/* Lifestyle Section */}
            <div className="form-card-title mt-4">
              🏃 Lifestyle
            </div>

            <div className="form-group">
              <div className="form-header">
                <label className="form-label">Smoking Status</label>
                <span className="tag tag-required">Required</span>
              </div>
              <div className="toggle-group mt-1">
                <button 
                  type="button" 
                  className={`toggle-option ${formData.smoker === 0 ? 'active' : ''}`} 
                  onClick={() => handleToggle('smoker', 0)}
                >
                  Non-Smoker
                </button>
                <button 
                  type="button" 
                  className={`toggle-option ${formData.smoker === 1 ? 'active-danger' : ''}`} 
                  onClick={() => handleToggle('smoker', 1)}
                >
                  Smoker
                </button>
              </div>
            </div>

            {/* Environment Section */}
            <div className="form-card-title mt-4">
              🌍 Environment
            </div>

            <div className="form-group">
              <div className="form-header">
                <label className="form-label">Location (Water Quality)</label>
                <span className="tag tag-optional">Optional</span>
              </div>
              <select 
                name="location" 
                value={formData.location} 
                onChange={handleChange} 
                className="input-field mt-1"
              >
                {locations.map(loc => (
                  <option key={loc.name} value={loc.name}>
                    {loc.name} ({loc.sodium_mg_l} mg/L — {loc.risk_level})
                  </option>
                ))}
              </select>
            </div>

            {formData.location && (
              <div className="form-group mt-3">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
                  <span 
                    className="badge-dot" 
                    style={{ background: selectedLoc.risk_color, width: '10px', height: '10px' }}
                  ></span>
                  <span>Water Sodium: </span>
                  <strong style={{ color: selectedLoc.risk_color }}>
                    {selectedLoc.sodium_mg_l} mg/L — {selectedLoc.risk_level}
                  </strong>
                </div>
                <div className="sodium-indicator">
                  <div 
                    className="sodium-marker" 
                    style={{ left: `${getMarkerPosition(selectedLoc.sodium_mg_l)}%` }}
                  ></div>
                </div>
                <div className="sodium-labels">
                  <span>0 mg/L</span>
                  <span>Safe</span>
                  <span>Moderate</span>
                  <span>High</span>
                  <span>500+ mg/L</span>
                </div>
              </div>
            )}

            {/* Lab Values Section */}
            <div className="form-card-title mt-4 border-t pt-3">
              🧪 Optional Lab Values
            </div>

            <div className="grid-3">
              <div className="form-group">
                <label className="form-label text-xs">Urine Calcium</label>
                <input 
                  type="number" 
                  name="urine_calcium" 
                  value={formData.urine_calcium} 
                  onChange={handleChange} 
                  step="0.01" 
                  className="input-field mt-1" 
                  placeholder="mg/dL" 
                />
              </div>
              <div className="form-group">
                <label className="form-label text-xs">Urine pH</label>
                <input 
                  type="number" 
                  name="urine_ph" 
                  value={formData.urine_ph} 
                  onChange={handleChange} 
                  step="0.1" 
                  className="input-field mt-1" 
                  placeholder="e.g. 6.0" 
                />
              </div>
              <div className="form-group">
                <label className="form-label text-xs">Uric Acid</label>
                <input 
                  type="number" 
                  name="uric_acid" 
                  value={formData.uric_acid} 
                  onChange={handleChange} 
                  step="0.01" 
                  className="input-field mt-1" 
                  placeholder="mg/dL" 
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary btn-block mt-4">
              {loading ? 'Analyzing...' : 'Analyze Data'}
            </button>
          </form>
        </div>

        {/* Right Column: Diagnostic Results / Welcome */}
        <div className="glass-card flex flex-col justify-center">
          {!result ? (
            <div className="text-center" style={{ padding: '2rem 1rem' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🧬</div>
              <h3 className="section-title">Diagnostic Analysis System</h3>
              <p className="text-muted" style={{ maxWidth: '400px', margin: '0 auto', fontSize: '0.9rem', lineHeight: '1.6' }}>
                Submit the patient demographics and lifestyle profile on the left. The XGBoost diagnostic engine will evaluate risk indices in real time.
              </p>
            </div>
          ) : (
            <div className="animate-in" style={{ width: '100%' }}>
              {/* Patient Badges Row */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '1.5rem' }}>
                <span className={`pill-badge ${formData.gender === 0 ? 'pill-female' : 'pill-male'}`}>
                  {formData.gender === 0 ? '♀ Female' : '♂ Male'}
                </span>
                <span className="pill-badge pill-age">
                  Age {formData.age}
                </span>
                <span className="pill-badge pill-smoker">
                  {formData.smoker === 1 ? '🚬 Smoker' : '🚭 Non-Smoker'}
                </span>
                {formData.location && (
                  <span className="pill-badge pill-location">
                    📍 {formData.location}
                  </span>
                )}
              </div>

              {/* Primary Diagnosis */}
              <div style={{ marginBottom: '1.5rem' }}>
                <h4 className="text-sm fw-800 text-muted mb-1">PRIMARY DIAGNOSIS</h4>
                <div 
                  style={{ 
                    fontSize: '1.8rem', 
                    fontWeight: 800, 
                    color: getClassColor(result.prediction_class_id) 
                  }}
                >
                  {result.predicted_class}
                </div>
              </div>

              {/* Diagnostic Risk Badges */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '2rem' }}>
                <span className="badge-dot-container">
                  <span className="badge-dot" style={{ background: 'var(--gender-female)' }}></span>
                  {formData.gender === 0 ? 'Female Gender' : 'Male Gender'}
                </span>
                {formData.smoker === 1 && (
                  <span className="badge-dot-container">
                    <span className="badge-dot" style={{ background: 'var(--smoker)' }}></span>
                    Active Smoker
                  </span>
                )}
                {formData.location && (
                  <span className="badge-dot-container">
                    <span className="badge-dot" style={{ background: selectedLoc.risk_color }}></span>
                    Water Quality: {selectedLoc.risk_level}
                  </span>
                )}
              </div>

              {/* Probabilities list */}
              <div style={{ marginBottom: '2rem' }}>
                <h4 className="text-sm fw-800 text-muted mb-2">DIAGNOSTIC CLASS PROBABILITIES</h4>
                {result.probabilities.map((prob, idx) => (
                  <div key={idx} style={{ marginBottom: '12px' }}>
                    <div className="prob-item" style={{ marginTop: '0', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 600, color: 'var(--text)' }}>
                        {getClassNameFromId(idx)}
                      </span>
                      <span style={{ fontWeight: 700, color: getClassColor(idx) }}>
                        {(prob * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="prob-bar">
                      <div 
                        className="prob-fill" 
                        style={{ 
                          width: `${prob * 100}%`, 
                          background: getClassColor(idx) 
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Water Quality section */}
              {formData.location && (
                <div>
                  <h4 className="text-sm fw-800 text-muted mb-2">WATER QUALITY METRICS</h4>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                    <span>Water Quality: <strong>{selectedLoc.name}</strong></span>
                    <span style={{ color: selectedLoc.risk_color, fontWeight: 700 }}>
                      {selectedLoc.sodium_mg_l} mg/L — {selectedLoc.risk_level}
                    </span>
                  </div>
                  <div className="sodium-indicator">
                    <div 
                      className="sodium-marker" 
                      style={{ left: `${getMarkerPosition(selectedLoc.sodium_mg_l)}%` }}
                    ></div>
                  </div>
                  <div className="sodium-labels">
                    <span>0 mg/L</span>
                    <span>Safe</span>
                    <span>Moderate</span>
                    <span>High</span>
                    <span>500+ mg/L</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Diagnosis;
