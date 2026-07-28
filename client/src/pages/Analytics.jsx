function Analytics() {
  return (
    <div className="container-wide">
      <div className="text-center mb-4">
        <h2 className="section-title gradient-text-accent">Deep Analytics Dashboard</h2>
        <p className="section-subtitle">Aggregated insights across all diagnostic parameters</p>
      </div>

      <div className="grid-3 mb-4">
        <div className="glass-card-sm text-center animate-in">
          <div className="text-muted text-sm mb-1 fw-800">TOTAL PATIENTS ANALYZED</div>
          <div className="gradient-text" style={{fontSize: '2rem', fontWeight: 800}}>1,248</div>
          <div className="text-xs text-muted mt-1">+12% from last month</div>
        </div>
        <div className="glass-card-sm text-center animate-in delay-1">
          <div className="text-muted text-sm mb-1 fw-800">HIGH RISK DETECTIONS</div>
          <div style={{fontSize: '2rem', fontWeight: 800, color: 'var(--danger)'}}>184</div>
          <div className="text-xs text-muted mt-1">Requiring immediate attention</div>
        </div>
        <div className="glass-card-sm text-center animate-in delay-2">
          <div className="text-muted text-sm mb-1 fw-800">AVG CONFIDENCE SCORE</div>
          <div className="gradient-text-accent" style={{fontSize: '2rem', fontWeight: 800}}>94.2%</div>
          <div className="text-xs text-muted mt-1">Across all 6 diagnostic classes</div>
        </div>
      </div>

      <div className="grid-2">
        <div className="glass-card animate-in delay-3">
          <h3 className="section-title text-sm mb-3">Risk Distribution</h3>
          <div className="prob-item">
            <span>Healthy</span>
            <span>45%</span>
          </div>
          <div className="prob-bar"><div className="prob-fill" style={{width: '45%', background: 'var(--c0)'}}></div></div>

          <div className="prob-item mt-3">
            <span>Suspected Dysfunction</span>
            <span>22%</span>
          </div>
          <div className="prob-bar"><div className="prob-fill" style={{width: '22%', background: 'var(--c1)'}}></div></div>

          <div className="prob-item mt-3">
            <span>Severe Failure</span>
            <span>8%</span>
          </div>
          <div className="prob-bar"><div className="prob-fill" style={{width: '8%', background: 'var(--c2)'}}></div></div>
          
          <div className="prob-item mt-3">
            <span>Uric/Calcium Stones Risk</span>
            <span>25%</span>
          </div>
          <div className="prob-bar"><div className="prob-fill" style={{width: '25%', background: 'var(--c4)'}}></div></div>
        </div>

        <div className="glass-card animate-in delay-4 text-center">
          <h3 className="section-title text-sm mb-4 text-left">Model Accuracy</h3>
          
          <div className="gauge-container mb-3 mt-4">
            <div className="gauge-bg">
              <div className="gauge-fill" style={{background: 'linear-gradient(to right, var(--primary), var(--secondary))', transform: 'rotate(170deg)'}}></div>
            </div>
            <div className="gauge-value gradient-text">95%</div>
            <div className="gauge-label">Validation Accuracy</div>
          </div>
          
          <p className="text-sm text-muted mt-4 text-left">
            The XGBoost model continues to perform with high accuracy across the validation dataset. Continuous learning is enabled.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
