from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
import os


def generate_executive_summary(result, filename, user):
    os.makedirs("storage/sanitized", exist_ok=True)
    output_path = f"storage/sanitized/executive_summary_{filename}.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    pink = HexColor("#e91e8c")
    dark = HexColor("#1a1a2e")

    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        textColor=pink,
        fontSize=24,
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        "heading",
        parent=styles["Heading2"],
        textColor=dark,
        fontSize=14,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=6
    )

    story = []

    # title
    story.append(Paragraph("PII Sanitization Executive Summary", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    story.append(Paragraph(f"Processed by: {user}", body_style))
    story.append(Paragraph(f"File: {filename}", body_style))
    story.append(Spacer(1, 20))

    # risk score section
    story.append(Paragraph("Risk Assessment", heading_style))
    risk_color = {
        "LOW": "#28a745",
        "MEDIUM": "#ffc107",
        "HIGH": "#fd7e14",
        "CRITICAL": "#dc3545"
    }.get(result["risk_level"], "#gray")

    risk_data = [
        ["Metric", "Value"],
        ["Risk Score", f"{result['risk_score']}/100"],
        ["Risk Level", result["risk_level"]],
        ["PII Items Found", str(len(result["pii_found"]))],
        ["Attack Vectors", str(len(result["attack_vectors"]))],
        ["Compliance Violations", str(len(result["compliance_flags"]))]
    ]
    risk_table = Table(risk_data, colWidths=[3*inch, 3*inch])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pink),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 1, dark),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [HexColor("#f8f9fa"), white]),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 20))

    # PII found section
    story.append(Paragraph("PII Detected", heading_style))
    if result["pii_found"]:
        pii_data = [["Type", "Value", "Confidence"]]
        for pii in result["pii_found"]:
            pii_data.append([
                pii["type"],
                pii["value"][:30] +
                "..." if len(pii["value"]) > 30 else pii["value"],
                f"{int(pii['confidence']*100)}%"
            ])
        pii_table = Table(pii_data, colWidths=[2*inch, 3*inch, 1*inch])
        pii_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), pink),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 1, dark),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [HexColor("#f8f9fa"), white]),
            ("PADDING", (0, 0), (-1, -1), 6)
        ]))
        story.append(pii_table)
    story.append(Spacer(1, 20))

    # attack vectors section
    story.append(Paragraph("Attack Vectors Detected", heading_style))
    if result["attack_vectors"]:
        for vector in result["attack_vectors"]:
            story.append(Paragraph(f"• {vector}", body_style))
    else:
        story.append(
            Paragraph("No critical attack vectors detected.", body_style))
    story.append(Spacer(1, 20))

    # attack narrative
    story.append(Paragraph("Security Analysis", heading_style))
    story.append(Paragraph(result["attack_narrative"], body_style))
    story.append(Spacer(1, 20))

    # compliance section
    story.append(Paragraph("Compliance Violations", heading_style))
    if result["compliance_flags"]:
        for flag in result["compliance_flags"]:
            story.append(Paragraph(f"• {flag}", body_style))
    else:
        story.append(
            Paragraph("No compliance violations detected.", body_style))

    doc.build(story)
    return output_path
