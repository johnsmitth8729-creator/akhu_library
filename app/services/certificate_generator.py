"""PDF certificate generation for competition winners."""

from __future__ import annotations

import os

from flask import current_app

from app import db
from app.models import CompetitionCertificate
from app.utils.datetime import now_local


def generate_certificate_pdf(cert: CompetitionCertificate) -> str:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas
    except ImportError:
        return ""

    user = cert.user
    competition = cert.competition
    rel_dir = os.path.join("uploads", "certificates")
    abs_dir = os.path.join(current_app.static_folder, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)

    filename = f"cert_{cert.verification_code}.pdf"
    abs_path = os.path.join(abs_dir, filename)
    rel_path = f"{rel_dir}/{filename}"

    c = canvas.Canvas(abs_path, pagesize=landscape(A4))
    width, height = landscape(A4)

    c.setFillColor(colors.HexColor("#0B3B6F"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#D4AF37"))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 2.2 * cm, "AKHU Library")

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 4 * cm, "Certificate of Achievement")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 5.2 * cm, "This certifies that")

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 6.4 * cm, user.fullname if user else "Participant")

    c.setFont("Helvetica", 13)
    c.drawCentredString(
        width / 2,
        height - 7.6 * cm,
        f"placed #{cert.position} in \"{competition.title}\"",
    )
    c.drawCentredString(
        width / 2,
        height - 8.6 * cm,
        f"Score: {cert.score} ({cert.percentage:.1f}%)",
    )

    issued = cert.issued_at or now_local()
    c.setFont("Helvetica", 11)
    c.drawCentredString(
        width / 2,
        2.5 * cm,
        f"Issued {issued.strftime('%d %B %Y')}  ·  Verify: {cert.verification_code}",
    )

    c.save()

    cert.pdf_path = rel_path
    db.session.commit()
    return rel_path
