import streamlit as st
from fpdf import FPDF
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw
from num2words import num2words

# Custom CSS for Dark and Light Blue Theme with Reduced st.title Font Size
st.markdown("""
    <style>
    .stApp {
        background-color: #333d5b;
        color: #FFFFFF;
    }
    /* Targeting the specific class for st.title */
    div[data-testid="stMarkdownContainer"] h1 {
        color: #FFFFFF;
        text-align: center;
        font-family: '', sans-serif;
        font-size: 28px !important; /* Reduced font size for st.title with higher specificity */
    }
    h2 {
        color: #93C5FD;
        font-family: 'Arial', sans-serif;
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stNumberInput > div > div > input {
        background-color: #FFFFFF;
        color: #1E3A8A;
        border-radius: 8px;
        border: 2px solid #60A5FA;
    }
    .stButton > button {
        background-color: #232935;
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        padding: 0.5em 1em;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #3B82F6;
    }
    .stDownloadButton > button {
        background-color: #232935;
        color: #FFFFFF;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    .stDownloadButton > button:hover {
        background-color: #3B82F6;
    }
    .stForm {
        background-color: #232935;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Function to make the logo circular and resize it to 70x70 pixels
def process_logo(logo_file):
    img = Image.open(logo_file).convert("RGBA")
    img = img.resize((70, 70), Image.Resampling.LANCZOS)
    mask = Image.new("L", (70, 70), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 70, 70), fill=255)
    img.putalpha(mask)
    temp_path = "temp_logo.png"
    img.save(temp_path, "PNG")
    return temp_path

# Function to generate invoice PDF (unchanged)
def create_invoice(company_name, customer_name, address, items, total_amount, date, invoice_number, text_color, header_color, bg_color, logo_path=None):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_fill_color(*bg_color)
    pdf.rect(0, 0, 210, 297, 'F')

    if logo_path:
        try:
            logo_x = (210 - 18.5) / 2
            pdf.image(logo_path, x=logo_x, y=8, w=18.5)
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(*text_color)
            pdf.set_xy(0, 20)
            pdf.cell(210, 25, company_name, ln=False, align='C')
            pdf.set_xy(0.1, 20.1)
            pdf.cell(210, 25, company_name, ln=True, align='C')
            pdf.ln(8)
        except Exception as e:
            pdf.set_font('Arial', '', 10)
            pdf.cell(200, 10, f"Error loading logo: {str(e)}", ln=True, align='L')
    else:
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(*text_color)
        pdf.set_xy(0, 8)
        pdf.cell(210, 10, company_name, ln=False, align='C')
        pdf.set_xy(0.1, 8.1)
        pdf.cell(210, 10, company_name, ln=True, align='C')
        pdf.ln(8)

    pdf.set_font('Arial', 'B', 18)
    pdf.set_xy(0, pdf.get_y())
    pdf.cell(210, 10, 'INVOICE', ln=True, align='C')
    pdf.line(90, pdf.get_y() - 1, 120, pdf.get_y() - 1)

    pdf.set_font('Arial', 'B', 12)
    pdf.ln(15)
    pdf.cell(100, 6, f"Invoice Number: {invoice_number}")
    pdf.set_xy(160, pdf.get_y())
    pdf.cell(50, 6, f"Date: {date}", align='L')
    pdf.ln(7)

    pdf.set_font('Arial', '', 12)
    pdf.cell(100, 6, f"Customer Name: {customer_name}", ln=True)
    pdf.cell(100, 6, f"Address: {address}", ln=True)

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(*header_color)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, 'Item', border=1, align='C', fill=True)
    pdf.cell(30, 10, 'Quantity', border=1, align='C', fill=True)
    pdf.cell(30, 10, 'Price', border=1, align='C', fill=True)
    pdf.cell(30, 10, 'Total', border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(*text_color)
    pdf.set_fill_color(*bg_color)
    total = 0
    for item in items:
        pdf.cell(100, 10, item['name'], border=1, align='L')
        pdf.cell(30, 10, str(item['quantity']), border=1, align='C')
        pdf.cell(30, 10, f"${item['price']:.2f}", border=1, align='C')
        item_total = item['quantity'] * item['price']
        pdf.cell(30, 10, f"${item_total:.2f}", border=1, align='C')
        pdf.ln()
        total += item_total

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, 'Total Amount Due:', border=1)
    pdf.cell(30, 10, f"${total:.2f}", border=1, align='C')
    pdf.ln()
    pdf.set_font('Arial', 'B', 12)
    total_in_words = num2words(total, to='currency', currency='USD').replace(' and ', ' ')
    pdf.cell(200, 10, f"Amount in Words: {total_in_words.capitalize()}", ln=True)
    
    return pdf

# Function to download the PDF
def download_invoice(pdf):
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buf = BytesIO()
    buf.write(pdf_bytes)
    buf.seek(0)
    return buf

# Streamlit App Interface
st.title('CUSTOMIZABLE INVOICE GENERATOR BY MERCHANTSONS')

# Company Name and Logo
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input('Company Name')
with col2:
    uploaded_logo = st.file_uploader("Upload Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
logo_path = None
if uploaded_logo is not None:
    logo_path = process_logo(uploaded_logo)
    st.success("Logo uploaded and processed successfully!")

# Customer Info and Invoice Details
col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input('Customer Name')
with col2:
    invoice_number = st.text_input('Invoice Number')
st.subheader("Customer Address")
address = st.text_area('Customer Address')
date = st.date_input('Invoice Date')

# Color selection
st.subheader("Customize Colors")
text_color = st.color_picker("Pick Text Color", "#FFFFFF")
header_color = st.color_picker("Pick Table Header Color", "#60A5FA")
bg_color = st.color_picker("Pick Invoice Background Color", "#1E3A8A")

# Convert hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

text_color_rgb = hex_to_rgb(text_color)
header_color_rgb = hex_to_rgb(header_color)
bg_color_rgb = hex_to_rgb(bg_color)

# Initialize session state for items
if 'item_list' not in st.session_state:
    st.session_state.item_list = []

# Add Items Block with Dynamic Display
st.subheader('Add Items')
with st.form(key='items_form'):
    col1, col2, col3 = st.columns(3)
    with col1:
        item_name = st.text_input('Item Name')
    with col2:
        quantity = st.number_input('Quantity', min_value=1)
    with col3:
        price = st.number_input('Price ($)', min_value=0.01, format="%.2f")
    add_item_button = st.form_submit_button('Add Item')
    
    if add_item_button and item_name:
        st.session_state.item_list.append({'name': item_name, 'quantity': quantity, 'price': price})
        st.success(f"Item '{item_name}' added!")

# Display added items within the same block
if st.session_state.item_list:
    st.markdown("### Added Items:")
    for i, item in enumerate(st.session_state.item_list):
        st.write(f"- {item['name']} | Quantity: {item['quantity']} | Price: ${item['price']:.2f} | Total: ${item['quantity'] * item['price']:.2f}")

# Generate Invoice Button
if st.button('Generate Invoice'):
    if company_name and customer_name and address and invoice_number and st.session_state.item_list:
        pdf = create_invoice(
            company_name=company_name,
            customer_name=customer_name,
            address=address,
            items=st.session_state.item_list,
            total_amount=0,
            date=str(date),
            invoice_number=invoice_number,
            text_color=text_color_rgb,
            header_color=header_color_rgb,
            bg_color=bg_color_rgb,
            logo_path=logo_path
        )
        buf = download_invoice(pdf)
        st.download_button(
            label="Download Invoice as PDF",
            data=buf,
            file_name=f"Invoice_{invoice_number}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Please fill in all fields and add at least one item.")