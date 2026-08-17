import React, { useMemo, useState } from "react";
import html2canvas from "html2canvas";
import MapView from "../components/MapView";
import SuitabilityCard from "../components/SuitabilityCard";
import RenewablePotential from "../components/RenewablePotential";
import TechnicalAssessment from "../components/TechnicalAssessment";
import EnergyYield from "../components/EnergyYield";
import { analyzeSite } from "../api/analysis";
import { generatePDF } from "../utils/reportGenerator";
import "../styles/analysis.css";
import "./AnalysisPage.css";

const TOTAL_STEPS = 5;

const AnalysisPage = () => {
  const [step, setStep] = useState(1);
  const [locationMode, setLocationMode] = useState("name");

  const [locationName, setLocationName] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [landArea, setLandArea] = useState("");
  const [usedLandArea, setUsedLandArea] = useState("0");

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisStage, setAnalysisStage] = useState(0);
  const [error, setError] = useState(null);

  const [locationLoading, setLocationLoading] = useState(false);
  const [locationError, setLocationError] = useState("");

  const steps = [
    {
      number: "01",
      title: "Site Location",
      description:
        "Define where the renewable project will be assessed.",
    },
    {
      number: "02",
      title: "Site Resources",
      description:
        "Specify the land available for deployment.",
    },
    {
      number: "03",
      title: "Data Analysis",
      description:
        "Evaluate solar, wind, terrain, environment and infrastructure.",
    },
    {
      number: "04",
      title: "Suitability Score",
      description:
        "Calculate the overall deployment suitability.",
    },
    {
      number: "05",
      title: "Deployment Plan",
      description:
        "Review energy, technical and financial recommendations.",
    },
  ];

  const analysisStages = [
    "Validating site coordinates",
    "Analysing solar resource",
    "Analysing wind resource",
    "Assessing terrain and infrastructure",
    "Evaluating environmental conditions",
    "Calculating deployment suitability",
    "Generating deployment recommendation",
  ];

  const progress = useMemo(
    () =>
      Math.round(
        ((step - 1) / (TOTAL_STEPS - 1)) * 100
      ),
    [step]
  );

  const resetAnalysis = () => {
    setStep(1);
    setData(null);
    setLoading(false);
    setAnalysisStage(0);
    setError(null);
    setLocationError("");
    setLocationName("");
    setLatitude("");
    setLongitude("");
    setLandArea("");
    setUsedLandArea("0");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const resolveLocation = async () => {
    const query = locationName.trim();

    if (!query) {
      setLocationError(
        "Enter a location before continuing."
      );
      return false;
    }

    setLocationLoading(true);
    setLocationError("");

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&countrycodes=in&q=${encodeURIComponent(
          query
        )}`,
        {
          headers: {
            Accept: "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          "Unable to contact the location service."
        );
      }

      const results = await response.json();

      if (!results.length) {
        throw new Error(
          "Location could not be found. Try a city, district or region name."
        );
      }

      const result = results[0];

      setLatitude(result.lat);
      setLongitude(result.lon);

      return true;
    } catch (err) {
      setLocationError(
        err?.message ||
          "Unable to resolve the location."
      );

      return false;
    } finally {
      setLocationLoading(false);
    }
  };

  const validateStepOne = async () => {
    if (locationMode === "name") {
      return await resolveLocation();
    }

    const lat = Number(latitude);
    const lng = Number(longitude);

    if (
      !Number.isFinite(lat) ||
      lat < -90 ||
      lat > 90
    ) {
      setLocationError(
        "Latitude must be between -90 and 90."
      );

      return false;
    }

    if (
      !Number.isFinite(lng) ||
      lng < -180 ||
      lng > 180
    ) {
      setLocationError(
        "Longitude must be between -180 and 180."
      );

      return false;
    }

    setLocationError("");

    return true;
  };

  const validateStepTwo = () => {
    const available = Number(landArea);
    const used = Number(usedLandArea || 0);

    if (
      !Number.isFinite(available) ||
      available <= 0
    ) {
      setError(
        "Available land area must be greater than 0 km²."
      );

      return false;
    }

    if (!Number.isFinite(used) || used < 0) {
      setError(
        "Used land area cannot be negative."
      );

      return false;
    }

    if (used > available) {
      setError(
        "Used land area cannot exceed available land area."
      );

      return false;
    }

    setError(null);

    return true;
  };

  const nextStep = async () => {
    setError(null);

    if (step === 1) {
      const valid = await validateStepOne();

      if (!valid) {
        return;
      }
    }

    if (step === 2) {
      const valid = validateStepTwo();

      if (!valid) {
        return;
      }
    }

    setStep((current) =>
      Math.min(
        current + 1,
        TOTAL_STEPS
      )
    );
  };

  const previousStep = () => {
    setError(null);
    setLocationError("");

    setStep((current) =>
      Math.max(current - 1, 1)
    );
  };

  const handleAnalyse = async () => {
    if (!validateStepTwo()) {
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysisStage(0);
    setStep(3);

    const requestData = {
      latitude: Number(latitude),
      longitude: Number(longitude),
      available_land_area_km2: Number(
        landArea
      ),
      used_land_area_km2: Number(
        usedLandArea || 0
      ),
    };

    try {
      setAnalysisStage(1);

      const result = await analyzeSite(
        requestData
      );

      setAnalysisStage(
        analysisStages.length - 1
      );

      setData(result);
      setStep(5);
    } catch (err) {
      setError(
        err?.message ||
          "Site analysis failed. Please try again."
      );

      setStep(2);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(Number(value || 0));

  /*
   * ---------------------------------------------------------
   * RESULT PAGE
   * ---------------------------------------------------------
   */

  if (data) {
    const recommendation =
      data.deployment_recommendation || {};

    const technology =
      recommendation.recommended_technology ||
      recommendation.recommended_tech ||
      recommendation.technology ||
      "N/A";

    const capacity =
      recommendation.capacity_mw ??
      recommendation.recommended_capacity_mw ??
      data.energy_yield?.installed_capacity_mw ??
      data.energy_yield?.capacity_mw ??
      null;

    const expansionStatus =
      recommendation.expansion_status ||
      recommendation.expansion_assessment ||
      "N/A";

    const recommendationRemarks =
      recommendation.remarks ||
      recommendation.recommendation_reason ||
      recommendation.reason ||
      "The site assessment has generated a deployment recommendation based on the evaluated renewable resources, terrain, infrastructure and technical feasibility.";

    return (
      <div className="analysis-container">

        {/* ==================================================
            HEADER
        ================================================== */}

        <header className="analysis-header">
          <div>
            <span className="analysis-kicker">
              SOLAR-WIND INTELLIGENCE
            </span>

            <h1>
              Deployment Analysis
            </h1>

            <p>
              Site assessment and
              renewable-energy deployment
              planning.
            </p>
          </div>

          <button
            className="secondary-btn"
            onClick={resetAnalysis}
          >
            New Analysis
          </button>
        </header>

        <main className="results-container">

          {/* ==================================================
              COMPLETED BANNER
          ================================================== */}

          <div className="completed-banner">
            <div>
              <span className="status-dot" />
              ANALYSIS COMPLETE
            </div>

            <span>
              Site assessment successfully
              generated
            </span>
          </div>

          {/* ==================================================
              SITE OVERVIEW
          ================================================== */}

          <section className="results-grid">

            <div className="result-card site-overview">

              <span className="result-label">
                SITE OVERVIEW
              </span>

              <h2>
                {data.site_information
                  ?.resolved_location ||
                  locationName ||
                  "Selected Site"}
              </h2>

              <div className="overview-details">

                <div>
                  <span>
                    LATITUDE
                  </span>

                  <strong>
                    {
                      data.site_information
                        ?.latitude
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    LONGITUDE
                  </span>

                  <strong>
                    {
                      data.site_information
                        ?.longitude
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    LAND AREA
                  </span>

                  <strong>
                    {
                      data.site_information
                        ?.available_land_area_km2
                    }{" "}
                    km²
                  </strong>
                </div>

              </div>
            </div>

            <SuitabilityCard
              assessment={
                data.deployment_assessment
              }
            />

          </section>

          {/* ==================================================
              RENEWABLE POTENTIAL
          ================================================== */}

          <section className="result-section">

            <div className="section-heading">

              <span>01</span>

              <div>
                <small>
                  RESOURCE INTELLIGENCE
                </small>

                <h2>
                  Renewable Potential
                </h2>
              </div>

            </div>

            <RenewablePotential
              assessment={
                data.deployment_assessment
              }
              deployment={
                data.deployment_recommendation
              }
            />

          </section>

          {/* ==================================================
              TECHNICAL FEASIBILITY
          ================================================== */}

          <section className="result-section">

            <div className="section-heading">

              <span>02</span>

              <div>
                <small>
                  TECHNICAL ASSESSMENT
                </small>

                <h2>
                  Technical Feasibility
                </h2>
              </div>

            </div>

            <TechnicalAssessment
              tech={
                data.technical_feasibility
              }
            />

          </section>

          {/* ==================================================
              ENERGY YIELD
          ================================================== */}

          <section className="result-section">

            <div className="section-heading">

              <span>03</span>

              <div>
                <small>
                  ENERGY FORECASTING
                </small>

                <h2>
                  Energy Yield
                </h2>
              </div>

            </div>

            <EnergyYield
              yieldData={
                data.energy_yield
              }
            />

          </section>

          {/* ==================================================
              MAP
          ================================================== */}

          <section className="result-section map-result">

            <div className="section-heading">

              <span>04</span>

              <div>
                <small>
                  GEOSPATIAL INTELLIGENCE
                </small>

                <h2>
                  Site Location
                </h2>
              </div>

            </div>

            <MapView
              latitude={
                data.site_information
                  ?.latitude
              }
              longitude={
                data.site_information
                  ?.longitude
              }
              locationName={
                data.site_information
                  ?.resolved_location ||
                locationName
              }
            />

          </section>

          {/* ==================================================
              FINANCIAL ANALYSIS
          ================================================== */}

          {data.financial_analysis && (
            <section className="result-section finance-result">

              <div className="section-heading">

                <span>05</span>

                <div>
                  <small>
                    INVESTMENT INTELLIGENCE
                  </small>

                  <h2>
                    Financial Feasibility
                  </h2>
                </div>

              </div>

              <div className="finance-grid">

                <div>
                  <span>
                    ANNUAL REVENUE
                  </span>

                  <strong>
                    {formatCurrency(
                      data.financial_analysis
                        ?.estimated_annual_revenue
                    )}
                  </strong>
                </div>

                <div>
                  <span>
                    PROJECT COST
                  </span>

                  <strong>
                    {formatCurrency(
                      data.financial_analysis
                        ?.estimated_project_cost
                    )}
                  </strong>
                </div>

                <div>
                  <span>
                    PAYBACK PERIOD
                  </span>

                  <strong>
                    {
                      data.financial_analysis
                        ?.payback_period_years
                    }{" "}
                    years
                  </strong>
                </div>

                <div>
                  <span>
                    ROI
                  </span>

                  <strong>
                    {
                      data.financial_analysis
                        ?.roi_percent
                    }
                    %
                  </strong>
                </div>

              </div>

            </section>
          )}

          {/* ==================================================
              FINAL RECOMMENDATION
          ================================================== */}

          <section className="recommendation-result">

            <div className="section-heading light">

              <span>06</span>

              <div>
                <small>
                  FINAL DECISION
                </small>

                <h2>
                  Deployment Recommendation
                </h2>
              </div>

            </div>

            <div className="recommendation-details">

              {/* Main recommendation */}

              <div className="recommendation-main">

                <span className="recommendation-main-label">
                  FINAL RECOMMENDATION
                </span>

                <h3>
                  {technology === "HYBRID"
                    ? "Hybrid Solar-Wind Deployment"
                    : technology === "SOLAR"
                    ? "Solar Energy Deployment"
                    : technology === "WIND"
                    ? "Wind Energy Deployment"
                    : technology}
                </h3>

                <p>
                  {recommendationRemarks}
                </p>

              </div>

              {/* Recommendation metrics */}

              <div className="recommendation-grid">

                <div>
                  <span>
                    RECOMMENDED TECHNOLOGY
                  </span>

                  <strong>
                    {technology}
                  </strong>
                </div>

                <div>
                  <span>
                    RECOMMENDED CAPACITY
                  </span>

                  <strong>
                    {capacity !== null &&
                    capacity !== undefined &&
                    capacity !== ""
                      ? `${capacity} MW`
                      : "—"}
                  </strong>
                </div>

                <div>
                  <span>
                    EXPANSION STATUS
                  </span>

                  <strong>
                    {expansionStatus}
                  </strong>
                </div>

              </div>

            </div>

          </section>

          {/* ==================================================
              ACTIONS
          ================================================== */}

          <div className="result-actions">

            <button
              className="secondary-btn"
              onClick={resetAnalysis}
            >
              ← Start New Analysis
            </button>

            <button
              className="primary-btn"
              onClick={async () => {
                try {
                  let mapImage = null;
                  const mapElement = document.querySelector('.site-map-wrapper');
                  if (mapElement) {
                    const canvas = await html2canvas(mapElement, { useCORS: true, allowTaint: true });
                    mapImage = canvas.toDataURL("image/png");
                  }
                  generatePDF(data, { resolvedLocation: locationName || data.site_information?.resolved_location }, mapImage);
                } catch {
                  setError(
                    "Unable to generate the PDF report. Please try again."
                  );
                }
              }}
            >
              ↓ Download PDF Report
            </button>

          </div>

          {error && (
            <div className="inline-error">
              {error}
            </div>
          )}

        </main>

      </div>
    );
  }

  /*
   * ---------------------------------------------------------
   * INPUT / WIZARD PAGE
   * ---------------------------------------------------------
   */

  return (
    <div className="analysis-container">

      {/* ==================================================
          HEADER
      ================================================== */}

      <header className="analysis-header">

        <div>

          <span className="analysis-kicker">
            SOLAR-WIND INTELLIGENCE
          </span>

          <h1>
            Site Assessment
          </h1>

          <p>
            Evaluate. Model. Deploy Smarter.
          </p>

        </div>

        <div className="header-status">

          <span className="status-dot" />

          ANALYSIS PLATFORM

        </div>

      </header>

      {/* ==================================================
          WIZARD
      ================================================== */}

      <main className="wizard-shell">

        <section className="wizard-intro">

          <span className="analysis-kicker">
            RENEWABLE ENERGY ASSESSMENT
          </span>

          <h2>
            Define the site before we
            analyse it.
          </h2>

          <p>
            Complete each phase in
            sequence. Your inputs are
            passed to the existing
            analysis engine without
            changing the backend
            workflow.
          </p>

        </section>

        {/* ==================================================
            STEPPER
        ================================================== */}

        <nav
          className="stepper"
          aria-label="Analysis phases"
        >

          {steps.map(
            (item, index) => {

              const stepNumber =
                index + 1;

              const active =
                stepNumber === step;

              const completed =
                stepNumber < step;

              return (
                <React.Fragment
                  key={item.number}
                >

                  <button
                    type="button"
                    className={`step-item ${
                      active
                        ? "active"
                        : ""
                    } ${
                      completed
                        ? "completed"
                        : ""
                    }`}
                    onClick={() => {
                      if (completed) {
                        setStep(
                          stepNumber
                        );
                      }
                    }}
                    disabled={
                      !completed &&
                      !active
                    }
                  >

                    <span className="step-number">
                      {item.number}
                    </span>

                    <span className="step-copy">

                      <strong>
                        {item.title}
                      </strong>

                      <small>
                        {
                          item.description
                        }
                      </small>

                    </span>

                  </button>

                  {index <
                    steps.length -
                      1 && (
                    <span className="step-line" />
                  )}

                </React.Fragment>
              );
            }
          )}

        </nav>

        {/* ==================================================
            LOADING
        ================================================== */}

        {loading ? (

          <section className="analysis-running">

            <div className="loader-ring" />

            <span className="analysis-kicker">
              LIVE SITE ANALYSIS
            </span>

            <h2>
              Analysing your site
            </h2>

            <p>
              The platform is
              evaluating renewable
              resources, terrain,
              environmental conditions
              and infrastructure.
            </p>

            <div className="analysis-progress">

              <div
                className="analysis-progress-bar"
                style={{
                  width: `${Math.max(
                    12,
                    ((analysisStage +
                      1) /
                      analysisStages.length) *
                      100
                  )}%`,
                }}
              />

            </div>

            <div className="analysis-pipeline">

              {analysisStages.map(
                (
                  stageName,
                  index
                ) => (

                  <div
                    key={stageName}
                    className={`pipeline-item ${
                      index <=
                      analysisStage
                        ? "done"
                        : ""
                    }`}
                  >

                    <span>
                      {index <=
                      analysisStage
                        ? "✓"
                        : String(
                            index + 1
                          ).padStart(
                            2,
                            "0"
                          )}
                    </span>

                    {stageName}

                  </div>

                )
              )}

            </div>

          </section>

        ) : (

          <>

            {/* ==================================================
                STEP 1
            ================================================== */}

            {step === 1 && (

              <section className="phase-card">

                <div className="phase-heading">

                  <span className="phase-number">
                    01
                  </span>

                  <div>

                    <span className="analysis-kicker">
                      PHASE 01
                    </span>

                    <h2>
                      Define Site Location
                    </h2>

                    <p>
                      Tell us where the
                      renewable-energy
                      project will be
                      assessed.
                    </p>

                  </div>

                </div>

                <div className="field-block">

                  <label>
                    LOCATION METHOD
                  </label>

                  <div className="mode-switch">

                    <button
                      type="button"
                      className={
                        locationMode ===
                        "name"
                          ? "selected"
                          : ""
                      }
                      onClick={() => {
                        setLocationMode(
                          "name"
                        );

                        setLocationError(
                          ""
                        );
                      }}
                    >
                      Location Name
                    </button>

                    <button
                      type="button"
                      className={
                        locationMode ===
                        "coordinates"
                          ? "selected"
                          : ""
                      }
                      onClick={() => {
                        setLocationMode(
                          "coordinates"
                        );

                        setLocationError(
                          ""
                        );
                      }}
                    >
                      Coordinates
                    </button>

                  </div>

                </div>

                {locationMode ===
                "name" ? (

                  <div className="field-block">

                    <label htmlFor="locationName">
                      LOCATION
                    </label>

                    <input
                      id="locationName"
                      value={
                        locationName
                      }
                      onChange={(
                        event
                      ) =>
                        setLocationName(
                          event.target
                            .value
                        )
                      }
                      placeholder="e.g. Krishnagiri, Tamil Nadu"
                      autoComplete="off"
                    />

                    <small className="field-help">
                      The location will
                      be converted to
                      coordinates before
                      analysis.
                    </small>

                  </div>

                ) : (

                  <div className="field-grid">

                    <div className="field-block">

                      <label htmlFor="latitude">
                        LATITUDE
                      </label>

                      <input
                        id="latitude"
                        type="number"
                        step="any"
                        value={
                          latitude
                        }
                        onChange={(
                          event
                        ) =>
                          setLatitude(
                            event.target
                              .value
                          )
                        }
                        placeholder="12.5152"
                      />

                    </div>

                    <div className="field-block">

                      <label htmlFor="longitude">
                        LONGITUDE
                      </label>

                      <input
                        id="longitude"
                        type="number"
                        step="any"
                        value={
                          longitude
                        }
                        onChange={(
                          event
                        ) =>
                          setLongitude(
                            event.target
                              .value
                          )
                        }
                        placeholder="78.0093"
                      />

                    </div>

                  </div>

                )}

                {locationError && (
                  <div className="form-error">
                    {locationError}
                  </div>
                )}

                <div className="phase-actions">

                  <span>
                    Step 1 of 5
                  </span>

                  <button
                    className="primary-btn"
                    onClick={nextStep}
                    disabled={
                      locationLoading
                    }
                  >
                    {locationLoading
                      ? "Resolving Location..."
                      : "Continue →"}
                  </button>

                </div>

              </section>

            )}

            {/* ==================================================
                STEP 2
            ================================================== */}

            {step === 2 && (

              <section className="phase-card">

                <div className="phase-heading">

                  <span className="phase-number">
                    02
                  </span>

                  <div>

                    <span className="analysis-kicker">
                      PHASE 02
                    </span>

                    <h2>
                      Define Site Resources
                    </h2>

                    <p>
                      Specify the land
                      available for
                      renewable-energy
                      deployment.
                    </p>

                  </div>

                </div>

                <div className="resource-summary">

                  <span>
                    SELECTED SITE
                  </span>

                  <strong>
                    {locationName ||
                      `${latitude}, ${longitude}`}
                  </strong>

                </div>

                <div className="field-grid">

                  <div className="field-block">

                    <label htmlFor="landArea">
                      AVAILABLE LAND FOR
                      DEPLOYMENT (km²)
                    </label>

                    <input
                      id="landArea"
                      type="number"
                      min="0.01"
                      step="any"
                      value={landArea}
                      onChange={(
                        event
                      ) =>
                        setLandArea(
                          event.target
                            .value
                        )
                      }
                      placeholder="e.g. 1"
                    />

                    <small className="field-help">
                      Total land area
                      available for the
                      renewable-energy
                      project.
                    </small>

                  </div>

                  <div className="field-block">

                    <label htmlFor="usedLandArea">
                      CURRENTLY USED LAND
                      (km²)
                    </label>

                    <input
                      id="usedLandArea"
                      type="number"
                      min="0"
                      step="any"
                      value={
                        usedLandArea
                      }
                      onChange={(
                        event
                      ) =>
                        setUsedLandArea(
                          event.target
                            .value
                        )
                      }
                      placeholder="0"
                    />

                    <small className="field-help">
                      Optional. Leave as
                      0 if the site is
                      currently unused.
                    </small>

                  </div>

                </div>

                {error && (
                  <div className="form-error">
                    {error}
                  </div>
                )}

                <div className="phase-actions">

                  <button
                    className="secondary-btn"
                    onClick={
                      previousStep
                    }
                  >
                    ← Back
                  </button>

                  <div>

                    <span>
                      Step 2 of 5
                    </span>

                    <button
                      className="primary-btn"
                      onClick={
                        handleAnalyse
                      }
                    >
                      Start Site Analysis →
                    </button>

                  </div>

                </div>

              </section>

            )}

            {/* ==================================================
                READY STATE
            ================================================== */}

            {step >= 3 &&
              !loading && (

                <section className="analysis-ready">

                  <div className="ready-icon">
                    ✓
                  </div>

                  <span className="analysis-kicker">
                    SITE INPUTS READY
                  </span>

                  <h2>
                    Ready to run the
                    assessment
                  </h2>

                  <p>
                    Location and land
                    constraints are
                    validated. Start the
                    existing analysis
                    engine to calculate
                    the deployment
                    assessment.
                  </p>

                  <div className="ready-summary">

                    <div>

                      <span>
                        LOCATION
                      </span>

                      <strong>
                        {locationName ||
                          `${latitude}, ${longitude}`}
                      </strong>

                    </div>

                    <div>

                      <span>
                        LAND AREA
                      </span>

                      <strong>
                        {landArea} km²
                      </strong>

                    </div>

                  </div>

                  <button
                    className="primary-btn"
                    onClick={
                      handleAnalyse
                    }
                  >
                    Run Full Analysis →
                  </button>

                  {error && (
                    <div className="form-error">
                      {error}
                    </div>
                  )}

                </section>

              )}

          </>

        )}

      </main>

    </div>
  );
};

export default AnalysisPage;