from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_pdf(result):

    filename = "startup_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)

    width, height = letter
    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, y, "Startup Validation Report")
    y -= 40

    c.setFont("Helvetica", 10)

    for key, value in result.items():

        # Section title
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, key.upper())
        y -= 20

        c.setFont("Helvetica", 10)

        lines = str(value).split("\n")

        for line in lines:

            if y < 50:  # create new page
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50

            c.drawString(50, y, line)
            y -= 15

        y -= 20

    c.save()

    return filename