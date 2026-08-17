import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/landing.css";
import "../styles/global.css";
import "../styles/components.css";
import "./LandingPage.css";

const capabilities = [
  {
    number: "01",
    title: "RESOURCE INTELLIGENCE",
    description:
      "Evaluate solar irradiation and wind potential to identify renewable energy opportunities at a selected site.",
    icon: "☀"
  },
  {
    number: "02",
    title: "GEOSPATIAL INTELLIGENCE",
    description:
      "Analyze terrain, geographic conditions, infrastructure and site constraints using location intelligence.",
    icon: "⌖"
  },
  {
    number: "03",
    title: "SITE SUITABILITY",
    description:
      "Combine multiple environmental and geographic factors into an overall deployment suitability score.",
    icon: "◈"
  },
  {
    number: "04",
    title: "SOLAR POTENTIAL",
    description:
      "Estimate solar capacity, capacity factor and annual energy generation potential.",
    icon: "◉"
  },
  {
    number: "05",
    title: "WIND POTENTIAL",
    description:
      "Evaluate wind resource potential and determine whether wind deployment is technically viable.",
    icon: "≋"
  },
  {
    number: "06",
    title: "ENERGY FORECASTING",
    description:
      "Estimate annual renewable energy production based on the selected deployment technology.",
    icon: "↗"
  },
  {
    number: "07",
    title: "DEPLOYMENT OPTIMIZATION",
    description:
      "Compare Solar, Wind and Hybrid strategies and recommend the most suitable technology.",
    icon: "△"
  },
  {
    number: "08",
    title: "INVESTMENT INTELLIGENCE",
    description:
      "Estimate project cost, annual revenue, payback period and return on investment.",
    icon: "₹"
  }
];

const workflow = [
  {
    number: "01",
    title: "DEFINE SITE",
    description: "Select the geographic location and land area for assessment."
  },
  {
    number: "02",
    title: "ANALYZE RESOURCES",
    description: "Evaluate solar and wind resource potential."
  },
  {
    number: "03",
    title: "ASSESS SITE",
    description: "Evaluate terrain, infrastructure and technical constraints."
  },
  {
    number: "04",
    title: "MODEL PROJECT",
    description: "Estimate capacity, energy output and financial performance."
  },
  {
    number: "05",
    title: "MAKE DECISION",
    description: "Recommend Solar, Wind or Hybrid deployment."
  }
];

export default function LandingPage() {
  const navigate = useNavigate();

  const startAnalysis = () => {
    navigate("/analysis");
  };

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({
      behavior: "smooth"
    });
  };

  return (
    <div className="landing-page">

      {/* =====================================================
          NAVBAR
      ====================================================== */}

      <header className="landing-navbar">
        <div className="navbar-inner">

          <div
            className="brand"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          >
            <span className="brand-mark">SW</span>
            <span>SOLAR-WIND INTEL</span>
          </div>

          <nav className="nav-links">
            <button onClick={() => scrollTo("platform")}>
              Platform
            </button>

            <button onClick={() => scrollTo("capabilities")}>
              Capabilities
            </button>

            <button onClick={() => scrollTo("workflow")}>
              How It Works
            </button>

            <button
              className="nav-cta"
              onClick={startAnalysis}
            >
              Start Analysis
            </button>
          </nav>

        </div>
      </header>


      {/* =====================================================
          HERO
      ====================================================== */}

      <section className="hero-section" id="platform">

        <div className="hero-background-grid"></div>

        <div className="hero-container">

          <div className="hero-content">

            <div className="eyebrow">
              RENEWABLE ENERGY SITE INTELLIGENCE
            </div>

            <h1>
              Plan Smarter
              <br />
              Renewable Energy
              <br />
              <span>Deployments.</span>
            </h1>

            <p className="hero-description">
              Assess solar and wind potential, evaluate site suitability,
              estimate energy generation, analyze financial feasibility,
              and identify the optimal deployment strategy from one
              intelligent platform.
            </p>

            <div className="hero-actions">

              <button
                className="primary-button"
                onClick={startAnalysis}
              >
                Start Site Analysis
                <span>→</span>
              </button>

              <button
                className="secondary-button"
                onClick={() => scrollTo("capabilities")}
              >
                Explore Platform
              </button>

            </div>

            <div className="hero-note">
              <span className="status-dot"></span>
              Data-driven renewable deployment assessment
            </div>

          </div>


          {/* =================================================
              HERO VISUAL
          ================================================== */}

          <div className="hero-visual">

            <div className="energy-orbit orbit-one"></div>
            <div className="energy-orbit orbit-two"></div>

            <div className="solar-visual">

              <div className="sun"></div>

              <div className="solar-panel panel-one"></div>
              <div className="solar-panel panel-two"></div>
              <div className="solar-panel panel-three"></div>

              <div className="wind-turbine">
                <div className="turbine-head"></div>
                <div className="turbine-blade blade-one"></div>
                <div className="turbine-blade blade-two"></div>
                <div className="turbine-blade blade-three"></div>
                <div className="turbine-pole"></div>
              </div>

            </div>


            {/* Dashboard floating card */}

            <div className="hero-dashboard">

              <div className="dashboard-header">
                <span>LIVE SITE ASSESSMENT</span>
                <span className="live-status">●</span>
              </div>

              <div className="dashboard-location">
                Vellore, Tamil Nadu
              </div>

              <div className="dashboard-score">

                <div>
                  <small>SUITABILITY</small>
                  <strong>74.4</strong>
                  <span>/100</span>
                </div>

                <div className="score-ring">
                  74%
                </div>

              </div>

              <div className="dashboard-grid">

                <div>
                  <small>TECHNOLOGY</small>
                  <strong>HYBRID</strong>
                </div>

                <div>
                  <small>CAPACITY</small>
                  <strong>27 MW</strong>
                </div>

                <div>
                  <small>ANNUAL ENERGY</small>
                  <strong>35,951 MWh</strong>
                </div>

                <div>
                  <small>PAYBACK</small>
                  <strong>0.75 YR</strong>
                </div>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          VALUE STRIP
      ====================================================== */}

      <section className="intelligence-strip">

        <div>
          <strong>RESOURCE</strong>
          <span>Solar & Wind Potential</span>
        </div>

        <div>
          <strong>GEOSPATIAL</strong>
          <span>Terrain & Infrastructure</span>
        </div>

        <div>
          <strong>SUITABILITY</strong>
          <span>Multi-factor Assessment</span>
        </div>

        <div>
          <strong>ENERGY</strong>
          <span>Generation Forecasting</span>
        </div>

        <div>
          <strong>FINANCE</strong>
          <span>Cost, Revenue & ROI</span>
        </div>

      </section>


      {/* =====================================================
          INTRODUCTION
      ====================================================== */}

      <section className="intro-section">

        <div className="section-container">

          <div className="section-label">
            THE PLATFORM
          </div>

          <h2>
            From location data to
            <span> deployment decisions.</span>
          </h2>

          <p className="section-intro">
            Solar-Wind Deployment Intelligence transforms geographic,
            renewable-resource and project data into a structured
            site-assessment workflow for renewable energy planning.
          </p>


          <div className="intro-columns">

            <div className="intro-card large">

              <div className="intro-number">
                01
              </div>

              <h3>
                Assess before you deploy.
              </h3>

              <p>
                Instead of evaluating renewable projects using a single
                resource metric, the platform considers resource potential,
                geographic suitability, technical feasibility, energy yield
                and financial performance together.
              </p>

            </div>


            <div className="intro-side">

              <div>
                <strong>Solar Intelligence</strong>
                <span>Solar resource assessment</span>
              </div>

              <div>
                <strong>Wind Intelligence</strong>
                <span>Wind resource assessment</span>
              </div>

              <div>
                <strong>GIS Intelligence</strong>
                <span>Geospatial site analysis</span>
              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          CAPABILITIES
      ====================================================== */}

      <section
        className="capabilities-section"
        id="capabilities"
      >

        <div className="section-container">

          <div className="section-heading">

            <div>
              <div className="section-label">
                PLATFORM CAPABILITIES
              </div>

              <h2>
                Intelligence across the
                <span> entire deployment lifecycle.</span>
              </h2>
            </div>

            <p>
              A unified assessment framework covering resource,
              geospatial, technical, energy and financial intelligence.
            </p>

          </div>


          <div className="capability-grid">

            {capabilities.map((item) => (

              <div
                className="capability-card"
                key={item.number}
              >

                <div className="capability-top">

                  <span className="capability-number">
                    {item.number}
                  </span>

                  <span className="capability-icon">
                    {item.icon}
                  </span>

                </div>

                <h3>
                  {item.title}
                </h3>

                <p>
                  {item.description}
                </p>

                <div className="card-arrow">
                  →
                </div>

              </div>

            ))}

          </div>

        </div>

      </section>


      {/* =====================================================
          DASHBOARD PREVIEW
      ====================================================== */}

      <section className="dashboard-section">

        <div className="section-container">

          <div className="section-label">
            DECISION INTELLIGENCE
          </div>

          <div className="dashboard-heading">

            <h2>
              See the decision,
              <span> not just the data.</span>
            </h2>

            <p>
              Convert site assessment results into clear deployment
              recommendations and project-level metrics.
            </p>

          </div>


          <div className="dashboard-preview">

            <div className="preview-sidebar">

              <div className="preview-brand">
                SITE ANALYSIS
              </div>

              <div className="preview-menu active">
                Overview
              </div>

              <div className="preview-menu">
                Suitability
              </div>

              <div className="preview-menu">
                Renewable Potential
              </div>

              <div className="preview-menu">
                Energy Yield
              </div>

              <div className="preview-menu">
                Financial Analysis
              </div>

            </div>


            <div className="preview-main">

              <div className="preview-header">
                <div>
                  <small>SITE OVERVIEW</small>
                  <h3>Vellore, Tamil Nadu</h3>
                </div>

                <span className="recommended-badge">
                  HYBRID RECOMMENDED
                </span>
              </div>


              <div className="metrics-row">

                <div className="metric-card highlight">
                  <small>SUITABILITY</small>
                  <strong>74.4</strong>
                  <span>/100</span>
                </div>

                <div className="metric-card">
                  <small>CAPACITY</small>
                  <strong>27</strong>
                  <span>MW</span>
                </div>

                <div className="metric-card">
                  <small>ANNUAL ENERGY</small>
                  <strong>35,951</strong>
                  <span>MWh</span>
                </div>

                <div className="metric-card">
                  <small>ROI</small>
                  <strong>133.15</strong>
                  <span>%</span>
                </div>

              </div>


              <div className="preview-bottom">

                <div className="fake-map">

                  <div className="map-grid"></div>

                  <div className="map-road road-one"></div>
                  <div className="map-road road-two"></div>
                  <div className="map-road road-three"></div>

                  <div className="map-marker">
                    ●
                  </div>

                  <span className="map-label">
                    ANALYZED SITE
                  </span>

                </div>


                <div className="recommendation-panel">

                  <small>FINAL RECOMMENDATION</small>

                  <h3>
                    Hybrid Deployment
                  </h3>

                  <p>
                    Solar and wind resources show complementary
                    potential, supporting a hybrid deployment strategy.
                  </p>

                  <div className="recommendation-score">
                    <span>Solar</span>
                    <div>
                      <i style={{ width: "90%" }}></i>
                    </div>
                    <strong>90</strong>
                  </div>

                  <div className="recommendation-score">
                    <span>Wind</span>
                    <div>
                      <i style={{ width: "70%" }}></i>
                    </div>
                    <strong>70</strong>
                  </div>

                </div>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          WORKFLOW
      ====================================================== */}

      <section
        className="workflow-section"
        id="workflow"
      >

        <div className="section-container">

          <div className="workflow-heading">

            <div className="section-label">
              HOW IT WORKS
            </div>

            <h2>
              Five steps from site
              <span> to strategy.</span>
            </h2>

          </div>


          <div className="workflow-line"></div>

          <div className="workflow-grid">

            {workflow.map((item) => (

              <div
                className="workflow-card"
                key={item.number}
              >

                <div className="workflow-number">
                  {item.number}
                </div>

                <h3>
                  {item.title}
                </h3>

                <p>
                  {item.description}
                </p>

              </div>

            ))}

          </div>

        </div>

      </section>


      {/* =====================================================
          FINAL CTA
      ====================================================== */}

      <section className="final-cta">

        <div className="cta-glow"></div>

        <div className="cta-content">

          <div className="section-label">
            READY TO ANALYZE?
          </div>

          <h2>
            Where should renewable
            <br />
            energy be deployed?
          </h2>

          <p>
            Evaluate a site using resource, geospatial, technical,
            energy and financial intelligence.
          </p>

          <button
            className="primary-button large"
            onClick={startAnalysis}
          >
            Start Site Analysis
            <span>→</span>
          </button>

        </div>

      </section>


      {/* =====================================================
          FOOTER
      ====================================================== */}

      <footer className="landing-footer">

        <div className="footer-grid">

          <div className="footer-brand">

            <div className="brand">
              <span className="brand-mark">SW</span>
              <span>SOLAR-WIND INTEL</span>
            </div>

            <p>
              AI-powered renewable energy site assessment
              and deployment planning.
            </p>

          </div>


          <div>
            <h4>PLATFORM</h4>
            <button onClick={() => scrollTo("platform")}>
              Platform
            </button>
            <button onClick={() => scrollTo("capabilities")}>
              Capabilities
            </button>
            <button onClick={() => scrollTo("workflow")}>
              How It Works
            </button>
          </div>


          <div>
            <h4>INTELLIGENCE</h4>
            <span>Solar</span>
            <span>Wind</span>
            <span>GIS</span>
            <span>Energy</span>
          </div>


          <div>
            <h4>ANALYSIS</h4>
            <button onClick={startAnalysis}>
              Site Analysis
            </button>
            <span>Reports</span>
            <span>Financial Analysis</span>
          </div>

        </div>


        <div className="footer-bottom">
          © 2026 Solar-Wind Deployment Intelligence
        </div>

      </footer>

    </div>
  );
}