import os
import fitz  # PyMuPDF

# Output target directory
OUTPUT_DIR = "D:/Antigravity Workspace/BodhZ_Bid Compliance Project (SIH26100)/data/sample/documents"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --------------------------------------------------
# SYNTHETIC PDF GENERATOR UTILITY
# --------------------------------------------------
def create_pdf(filename: str, title: str, content_lines: list):
    """Generates a clean synthetic PDF with PyMuPDF for document pipeline testing."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size

    # Header title
    page.insert_text((50, 50), title, fontsize=16, color=(0.02, 0.11, 0.24))

    # Content lines
    y = 90
    for line in content_lines:
        page.insert_text((50, y), line, fontsize=11, color=(0.1, 0.1, 0.1))
        y += 22

    path = os.path.join(OUTPUT_DIR, filename)
    doc.save(path)
    doc.close()
    print(f"Generated sample PDF: {path}")


# Generate GST Certificate
create_pdf(
    "GST_Certificate_Sample.pdf",
    "GOVERNMENT OF INDIA - GOODS AND SERVICES TAX REGISTRATION CERTIFICATE",
    [
        "Registration Certificate - FORM GST REG-06",
        "Registration Number (GSTIN): 27ABCDE1234F1Z5",
        "Legal Name: Acme Solutions Pvt Ltd",
        "Trade Name: Acme Solutions",
        "Address: Plot 42, Tech Park, MIDC, Mumbai, Maharashtra 400072",
        "Date of Liability: 01/04/2018",
        "Status: ACTIVE",
        "Taxpayer Type: Regular",
        "Issuing Authority: Commercial Tax Officer, Circle 12"
    ]
)

# Generate Udyam Registration Certificate
create_pdf(
    "Udyam_Registration_Sample.pdf",
    "MINISTRY OF MICRO, SMALL & MEDIUM ENTERPRISES - UDYAM REGISTRATION CERTIFICATE",
    [
        "Udyam Registration Number: UDYAM-MH-12-0098234",
        "Name of Enterprise: Acme Solutions Pvt Ltd",
        "Type of Enterprise: SMALL ENTERPRISE",
        "Major Activity: Services / IT Solutions",
        "Date of Incorporation: 15/05/2015",
        "National Industry Classification (NIC) Code: 62011",
        "Date of Udyam Registration: 10/07/2020",
        "MSME Status: VERIFIED ACTIVE"
    ]
)

# Generate PAN Document
create_pdf(
    "PAN_Card_Sample.pdf",
    "INCOME TAX DEPARTMENT - GOVT OF INDIA",
    [
        "PERMANENT ACCOUNT NUMBER CARD",
        "PAN Number: ABCDE1234F",
        "Name: ACME SOLUTIONS PRIVATE LIMITED",
        "Date of Incorporation: 15/05/2015",
        "Category: Private Limited Company",
        "Status: ACTIVE AND VALIDATED"
    ]
)

# Generate OEM Authorization Letter
create_pdf(
    "OEM_Authorization_Sample.pdf",
    "MANUFACTURER AUTHORIZATION LETTER (OEM AUTHORIZATION)",
    [
        "To: Procurement Officer, GeM Portal",
        "Ref: GeM Tender No. GEM/2026/B/882109",
        "Date: 10/08/2026",
        "Subject: OEM Authorization for Server Infrastructure & Storage",
        "We, Global Tech OEM Corporation, hereby authorize Acme Solutions Pvt Ltd to bid,",
        "supply, install and service Server Infrastructure and Enterprise Storage Systems",
        "against GeM Tender GEM/2026/B/882109.",
        "Authorization Validity: 31/12/2027",
        "Authorized Signatory: Global Tech OEM India Pvt Ltd"
    ]
)
