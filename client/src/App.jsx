import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Diagnosis from './pages/Diagnosis';
import Analytics from './pages/Analytics';
import './index.css';

function App() {
  return (
    <Router>
      <Navbar />
      <div className="page-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/diagnosis" element={<Diagnosis />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
