import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime
from textwrap import wrap

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Civil Plaint Generator – Kerala", layout="centered")
st.title("⚖️ Civil Plaint Generator (Kerala)")

# --------------------------------------------------
# COURT DETAILS
# --------------------------------------------------
st.subheader("Court Details")
court_name = st.text_input("Name of the Court *")
court_location = st.text_input("Court Location *")

# --------------------------------------------------
# PARTY DETAILS
# --------------------------------------------------
st.subheader("Plaintiff Details")
plaintiff_name = st.text_input("Plaintiff Name *")
plaintiff_age = st.text_input("Plaintiff Age *")
plaintiff_address = st.text_area("Plaintiff Address *")

st.subheader("Defendant Details")
defendant_name = st.text_input("Defendant Name *")
defendant_age = st.text_input("Defendant Age *")
defendant_address = st.text_area("Defendant Address *")

# --------------------------------------------------
# ADVOCATE DETAILS (VAKALATH STYLE)
# --------------------------------------------------
st.subheader("Advocate Details")
advocate_name = st.text_input("Advocate Name *")
advocate_enrollment = st.text_input("Enrollment Number *")
advocate_address = st.text_area("Advocate Office Address *")

# --------------------------------------------------
# CONTRACT DETAILS
# --------------------------------------------------
st.subheader("Contract Details")
contract_type = st.text_input("Type of Contract *")
agreement_date = st.date_input("Agreement Date *")
total_amount = st.text_input("Total Contract Amount (₹) *")
advance_paid = st.text_input("Advance Paid (₹)")
breach_date = st.date_input("Date of Breach *")

# --------------------------------------------------
# DYNAMIC FACTS
# --------------------------------------------------
st.subheader("Facts of the Case")

if "facts" not in st.session_state:
    st.session_state.facts = [""]

for i in range(len(st.session_state.facts)):
    st.session_state.facts[i] = st.text_area(
        f"Fact {i + 1} *",
        st.session_state.facts[i],
        height=90
    )

if st.button("➕ Add Another Fact"):
    st.session_state.facts.append("")

# --------------------------------------------------
# OTHER LEGAL SECTIONS
# --------------------------------------------------
st.subheader("Jurisdiction")
jurisdiction_reason = st.text_area("Reason for Jurisdiction *")

st.subheader("Claim Details")
claim_amount = st.text_input("Claim Amount (₹) *")
interest_rate = st.text_input("Interest Rate (% per annum) *")

st.subheader("Relief Sought")
relief_requested = st.text_area("Relief Requested *")

st.subheader("Verification")
verification_place = st.text_input("Place *")
verification_date = st.date_input("Date", datetime.date.today())

# --------------------------------------------------
# COURT FEE (SIMPLIFIED KERALA RULE – ACADEMIC)
# --------------------------------------------------
def calculate_court_fee(amount):
    try:
        amount = float(amount)
        if amount <= 100000:
            return amount * 0.075
        elif amount <= 500000:
            return amount * 0.05
        else:
            return amount * 0.03
    except:
        return None

court_fee = calculate_court_fee(claim_amount)

# --------------------------------------------------
# VALIDATION
# --------------------------------------------------
def validate_fields():
    missing = []

    required_fields = {
        "Court Name": court_name,
        "Court Location": court_location,
        "Plaintiff Name": plaintiff_name,
        "Plaintiff Age": plaintiff_age,
        "Plaintiff Address": plaintiff_address,
        "Defendant Name": defendant_name,
        "Defendant Age": defendant_age,
        "Defendant Address": defendant_address,
        "Advocate Name": advocate_name,
        "Advocate Enrollment": advocate_enrollment,
        "Advocate Address": advocate_address,
        "Contract Type": contract_type,
        "Total Amount": total_amount,
        "Claim Amount": claim_amount,
        "Interest Rate": interest_rate,
        "Jurisdiction Reason": jurisdiction_reason,
        "Relief Requested": relief_requested,
        "Verification Place": verification_place
    }

    for label, value in required_fields.items():
        if not value.strip():
            missing.append(label)

    if not any(f.strip() for f in st.session_state.facts):
        missing.append("At least one Fact")

    if court_fee is None:
        missing.append("Valid Claim Amount for Court Fee")

    return missing

# --------------------------------------------------
# PDF GENERATION (FIXED: WRAPPING + MULTI-PAGE)
# --------------------------------------------------
def generate_pdf(draft_text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    left_margin = 50
    right_margin = 50
    top_margin = height - 50
    bottom_margin = 50

    text = pdf.beginText()
    text.setTextOrigin(left_margin, top_margin)
    text.setFont("Times-Roman", 11)

    for paragraph in draft_text.split("\n"):
        if paragraph.strip() == "":
            text.textLine("")
            continue

        wrapped_lines = wrap(paragraph, 95)

        for line in wrapped_lines:
            if text.getY() <= bottom_margin:
                pdf.drawText(text)
                pdf.showPage()
                text = pdf.beginText()
                text.setTextOrigin(left_margin, top_margin)
                text.setFont("Times-Roman", 11)

            text.textLine(line)

    pdf.drawText(text)
    pdf.save()
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# GENERATE BUTTON
# --------------------------------------------------
if st.button("📄 Generate Civil Plaint (PDF)"):

    missing_fields = validate_fields()

    if missing_fields:
        st.error("Please fill all mandatory fields before generating the plaint.")
        st.write("❌ Missing / Invalid:")
        st.write(missing_fields)

    else:
        facts_text = ""
        count = 1
        for fact in st.session_state.facts:
            if fact.strip():
                facts_text += f"{count}. {fact}\n"
                count += 1

        draft = f"""
BEFORE THE HON’BLE COURT OF {court_name}, {court_location}

CIVIL SUIT FOR BREACH OF CONTRACT

Plaintiff:
{plaintiff_name}, aged about {plaintiff_age} years,
Residing at {plaintiff_address}

Defendant:
{defendant_name}, aged about {defendant_age} years,
Residing at {defendant_address}

Filed through Counsel:
{advocate_name}
Advocate, Enrollment No: {advocate_enrollment}
Office: {advocate_address}

--------------------------------------------------

1. FACTS OF THE CASE
{facts_text}

2. CAUSE OF ACTION
The cause of action arose on {breach_date} due to breach of contract by the defendant.

3. JURISDICTION
This Hon’ble Court has jurisdiction because {jurisdiction_reason}.

4. VALUATION & COURT FEE
The suit is valued at Rs.{claim_amount}.
Court fee paid under Kerala Court Fees Act: Rs.{court_fee:.2f}

5. CLAIM
The plaintiff claims Rs.{claim_amount} with interest at {interest_rate}% per annum.

6. RELIEF SOUGHT
{relief_requested}

7. VERIFICATION
I, {plaintiff_name}, verify that the contents of this plaint are true to my knowledge.

Verified at {verification_place}
On {verification_date}

Plaintiff
"""

        pdf_file = generate_pdf(draft)

        st.success("Civil Plaint Generated Successfully")
        st.download_button(
            label="⬇️ Download Civil Plaint PDF",
            data=pdf_file,
            file_name="Civil_Plaint_Breach_of_Contract_Kerala.pdf",
            mime="application/pdf"
        )
