"""
Updated report_generator.py

NOTE:
This is the architectural template. Integrate with your project by importing
calculate_deployment_score and generate_pdf_report.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

from engine.site_information import SiteInformation
from engine.scoring import calculate_deployment_score
from engine.pdf_report_generator import generate_pdf_report

PROJECT_NAME = "Solar Wind Deployment Intelligence"

def generate_report(site: SiteInformation, dataset_results: dict,
                    save_output: bool=True,
                    display_output: bool=True)->dict:

    report = {
        "project": PROJECT_NAME,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "site_information":{
            "requested_location":site.requested_location,
            "resolved_location":site.resolved_location,
            "latitude":site.latitude,
            "longitude":site.longitude,
            "country":site.country,
            "state":site.state,
            "source":site.source,
        },
        "datasets":dataset_results
    }

    report["deployment_assessment"] = calculate_deployment_score(report)

    if save_output:
        outdir = Path("reports") / site.requested_location.strip().lower().replace(" ","_")
        outdir.mkdir(parents=True, exist_ok=True)

        with (outdir/"deployment_report.json").open("w",encoding="utf-8") as f:
            json.dump(report,f,indent=4,ensure_ascii=False)

        generate_pdf_report(report,outdir)

        if display_output:
            print("Saved:", outdir/"deployment_report.json")
            print("Saved:", outdir/"deployment_report.pdf")

    return report
