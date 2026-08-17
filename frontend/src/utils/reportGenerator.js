import jsPDF from "jspdf";

export function generatePDF(data, location = {}, mapImage = null) {
  if (!data) {
    throw new Error(
      "No analysis data available."
    );
  }

  const pdf = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  });
//... (rest of the file)

  const pageWidth =
    pdf.internal.pageSize.getWidth();

  const pageHeight =
    pdf.internal.pageSize.getHeight();

  const district =
    location.districtName ||
    data.site_information
      ?.resolved_location ||
    "Selected Site";

  const state =
    location.stateName || "";

  const latitude =
    data.site_information?.latitude ??
    location.latitude ??
    "—";

  const longitude =
    data.site_information?.longitude ??
    location.longitude ??
    "—";

  const landArea =
    data.site_information
      ?.available_land_area_km2 ??
    "—";

  const assessment =
    data.deployment_assessment || {};

  const recommendation =
    data.deployment_recommendation || {};

  const technical =
    data.technical_feasibility || {};

  const energy =
    data.energy_yield || {};

  const financial =
    data.financial_analysis || {};

  const formatMoney = (value) => {
    const amount = Number(value || 0).toLocaleString('en-IN', {
      maximumFractionDigits: 0,
    });
    return `INR ${amount}`;
  };

  let y = 20;

  const checkPage = (height = 15) => {
    if (y + height > pageHeight - 18) {
      pdf.addPage();
      y = 20;
    }
  };

  const addHeading = (text) => {
    checkPage(18);

    pdf.setFont(
      "helvetica",
      "bold"
    );

    pdf.setFontSize(14);

    pdf.setTextColor(
      11,
      34,
      55
    );

    pdf.text(text, 15, y);

    y += 8;
  };

  const addLine = (
    label,
    value
  ) => {
    const safeValue =
      value === undefined ||
      value === null ||
      value === ""
        ? "—"
        : String(value);

    const wrapped =
      pdf.splitTextToSize(
        safeValue,
        pageWidth - 70
      );

    const requiredHeight =
      Math.max(
        8,
        wrapped.length * 5 + 3
      );

    checkPage(requiredHeight);

    pdf.setFont(
      "helvetica",
      "bold"
    );

    pdf.setFontSize(9);

    pdf.setTextColor(
      11,
      34,
      55
    );

    pdf.text(
      `${label}:`,
      15,
      y
    );

    pdf.setFont(
      "helvetica",
      "normal"
    );

    pdf.setTextColor(
      70,
      85,
      95
    );

    pdf.text(
      wrapped,
      55,
      y
    );

    y += requiredHeight;
  };

  /* ==========================================================
     HEADER
     ========================================================== */

  pdf.setFillColor(
    11,
    34,
    55
  );

  pdf.rect(
    0,
    0,
    pageWidth,
    34,
    "F"
  );

  pdf.setTextColor(
    255,
    255,
    255
  );

  pdf.setFont(
    "helvetica",
    "bold"
  );

  pdf.setFontSize(18);

  pdf.text(
    "SOLAR-WIND INTELLIGENCE",
    15,
    15
  );

  pdf.setFont(
    "helvetica",
    "normal"
  );

  pdf.setFontSize(9);

  pdf.text(
    "Renewable Energy Site Deployment Assessment",
    15,
    23
  );

  y = 45;

  /* ==========================================================
     MAP IMAGE
     ========================================================== */

  if (mapImage) {
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(14);
    pdf.setTextColor(11, 34, 55);
    pdf.text("SITE MAP", 15, y);
    y += 8;

    checkPage(75);
    pdf.addImage(mapImage, 'PNG', 15, y, pageWidth - 30, 70);
    y += 75;
  }

  /* ==========================================================
     SITE INFORMATION
     ========================================================== */

  addHeading(
    "SITE INFORMATION"
  );

  addLine(
    "District",
    district
  );

  addLine(
    "State",
    state
  );

  addLine(
    "Latitude",
    latitude
  );

  addLine(
    "Longitude",
    longitude
  );

  addLine(
    "Available Land",
    `${landArea} km²`
  );

  y += 5;

  /* ==========================================================
     OVERALL SUITABILITY
     ========================================================== */

  addHeading(
    "DEPLOYMENT SUITABILITY"
  );

  addLine(
    "Overall Score",
    assessment.normalized_score ??
      assessment.overall_score ??
      assessment.score ??
      "—"
  );

  addLine(
    "Classification",
    assessment.recommendation ??
      assessment.suitability ??
      "—"
  );

  y += 5;

  /* ==========================================================
     RENEWABLE POTENTIAL
     ========================================================== */

  addHeading(
    "RENEWABLE POTENTIAL"
  );

  addLine(
    "Recommended Technology",
    recommendation.recommended_technology
  );

  addLine(
    "Recommended Capacity",
    recommendation.recommended_capacity_mw !=
      null
      ? `${recommendation.recommended_capacity_mw} MW`
      : "—"
  );

  addLine(
    "Solar Score",
    assessment.solar_score ??
      "—"
  );

  addLine(
    "Wind Score",
    assessment.wind_score ??
      "—"
  );

  y += 5;

  /* ==========================================================
     TECHNICAL FEASIBILITY
     ========================================================== */

  addHeading(
    "TECHNICAL FEASIBILITY"
  );

  addLine(
    "Status",
    technical.feasibility_status ??
      technical.status ??
      "—"
  );

  addLine(
    "Score",
    technical.feasibility_score ??
      technical.score ??
      "—"
  );

  addLine(
    "Passed",
    technical.hard_constraints_passed ??
      technical.passed ??
      "—"
  );

  addLine(
    "Failed",
    technical.hard_constraints_failed ??
      technical.failed ??
      "—"
  );

  y += 5;

  /* ==========================================================
     ENERGY YIELD
     ========================================================== */

  addHeading(
    "ENERGY YIELD"
  );

  addLine(
    "Technology",
    energy.technology
  );

  addLine(
    "Capacity",
    energy.capacity != null
      ? `${energy.capacity} MW`
      : energy.capacity_mw != null
      ? `${energy.capacity_mw} MW`
      : "—"
  );

  addLine(
    "Annual Energy",
    energy.annual_energy_mwh !=
      null
      ? `${energy.annual_energy_mwh} MWh`
      : "—"
  );

  addLine(
    "Annual Energy GWh",
    energy.annual_energy_gwh !=
      null
      ? `${energy.annual_energy_gwh} GWh`
      : "—"
  );

  addLine(
    "Solar Capacity Factor",
    energy.solar_capacity_factor ??
      "—"
  );

  addLine(
    "Wind Capacity Factor",
    energy.wind_capacity_factor ??
      "—"
  );

  y += 5;

  /* ==========================================================
     FINANCIAL FEASIBILITY
     ========================================================== */

  if (data.financial_analysis) {
    addHeading(
      "FINANCIAL FEASIBILITY"
    );

    addLine(
      "Annual Revenue",
      formatMoney(
        financial.estimated_annual_revenue
      )
    );

    addLine(
      "Project Cost",
      formatMoney(
        financial.estimated_project_cost
      )
    );

    addLine(
      "Payback Period",
      financial.payback_period_years !=
        null
        ? `${financial.payback_period_years} years`
        : "—"
    );

    addLine(
      "ROI",
      financial.roi_percent !=
        null
        ? `${financial.roi_percent}%`
        : "—"
    );

    y += 5;
  }

  /* ==========================================================
     FINAL DEPLOYMENT RECOMMENDATION
     ========================================================== */

  addHeading(
    "FINAL DEPLOYMENT RECOMMENDATION"
  );

  addLine(
    "Technology",
    recommendation.recommended_technology
  );

  addLine(
    "Capacity",
    recommendation.recommended_capacity_mw !=
      null
      ? `${recommendation.recommended_capacity_mw} MW`
      : "—"
  );

  addLine(
    "Expansion Status",
    recommendation.expansion_status
  );

  const remarks =
    recommendation.optimization_remarks ||
    "No additional recommendation remarks were provided.";

  checkPage(25);

  pdf.setFont(
    "helvetica",
    "bold"
  );

  pdf.setFontSize(9);

  pdf.setTextColor(
    11,
    34,
    55
  );

  pdf.text(
    "Recommendation Remarks:",
    15,
    y
  );

  y += 6;

  pdf.setFont(
    "helvetica",
    "normal"
  );

  pdf.setFontSize(10);

  pdf.setTextColor(
    60,
    70,
    80
  );

  const wrappedRemarks =
    pdf.splitTextToSize(
      String(remarks),
      pageWidth - 30
    );

  const remarksHeight =
    wrappedRemarks.length * 5;

  checkPage(
    remarksHeight + 8
  );

  pdf.text(
    wrappedRemarks,
    15,
    y
  );

  y += remarksHeight + 10;

  /* ==========================================================
     SITE LOCATION — ALWAYS LAST
     ========================================================== */

  addHeading(
    "SITE LOCATION"
  );

  addLine(
    "District",
    district
  );

  addLine(
    "State",
    state
  );

  addLine(
    "Coordinates",
    `${latitude}, ${longitude}`
  );

  if (
    location.resolvedAddress
  ) {
    addLine(
      "Resolved Address",
      location.resolvedAddress
    );
  }

  /* ==========================================================
     FOOTERS
     ========================================================== */

  const totalPages =
    pdf.internal.getNumberOfPages();

  for (
    let page = 1;
    page <= totalPages;
    page++
  ) {
    pdf.setPage(page);

    pdf.setDrawColor(
      210,
      220,
      226
    );

    pdf.line(
      15,
      pageHeight - 14,
      pageWidth - 15,
      pageHeight - 14
    );

    pdf.setFont(
      "helvetica",
      "normal"
    );

    pdf.setFontSize(7);

    pdf.setTextColor(
      100,
      110,
      120
    );

    pdf.text(
      "Solar-Wind Deployment Intelligence",
      15,
      pageHeight - 8
    );

    pdf.text(
      `Page ${page} of ${totalPages}`,
      pageWidth - 35,
      pageHeight - 8
    );
  }

  /* ==========================================================
     DOWNLOAD
     ========================================================== */

  const safeDistrict =
    String(district)
      .replace(
        /[^a-z0-9]+/gi,
        "_"
      )
      .replace(
        /^_+|_+$/g,
        ""
      );

  pdf.save(
    `Solar_Wind_Site_Report_${
      safeDistrict || "Analysis"
    }.pdf`
  );
}

export default generatePDF;