"""
pdf_report_generator.py

Skeleton implementation.

Install:
pip install reportlab

TODO:
Use reportlab.platypus.SimpleDocTemplate, Table, Paragraph and Spacer.
Render:
- Project
- Site Information
- Dataset summaries
- Deployment Assessment
- Recommendation

Output:
deployment_report.pdf
"""

from pathlib import Path
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def generate_pdf_report(report:dict, output_directory:Path)->None:
    pdf = output_directory/"deployment_report.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(pdf))
    story=[]

    story.append(Paragraph("<b>Solar Wind Deployment Intelligence</b>",styles["Title"]))
    story.append(Spacer(1,12))

    site = report["site_information"]
    story.append(Paragraph(f"Location: {site['resolved_location']}",styles["Heading2"]))
    story.append(Paragraph(f"Latitude: {site['latitude']}",styles["BodyText"]))
    story.append(Paragraph(f"Longitude: {site['longitude']}",styles["BodyText"]))
    story.append(Spacer(1,12))

    assess = report.get("deployment_assessment",{})
    story.append(Paragraph("<b>Deployment Assessment</b>",styles["Heading2"]))
    for k,v in assess.items():
        if isinstance(v,(str,int,float)):
            story.append(Paragraph(f"{k}: {v}",styles["BodyText"]))

    doc.build(story)
