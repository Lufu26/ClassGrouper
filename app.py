# app.py
from flask import Flask, render_template, request, session, make_response, redirect, url_for
from fpdf import FPDF
import random

app = Flask(__name__)
# SECRET_KEY is required to use 'session'. In production, change this to a random string.
app.secret_key = 'classgrouper_secret_key'

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # 1. Get data from form
    raw_data = request.form['raw_names']
    try:
        group_size = int(request.form['group_size'])
    except ValueError:
        group_size = 10  # Default fallback

    # 2. Process the text data
    # Split by new line, remove leading/trailing spaces, ignore empty lines
    names_list = [name.strip() for name in raw_data.split('\n') if name.strip()]

    if not names_list:
        return "Error: No names provided", 400

    # 3. Algorithm: Shuffle and Chunk
    random.shuffle(names_list)
    
    groups = []
    # Logic: Slice the list from 0 to 10, 10 to 20, etc.
    for i in range(0, len(names_list), group_size):
        groups.append(names_list[i:i + group_size])

    # 4. Save to session so we can print it later
    session['groups'] = groups
    session['total_students'] = len(names_list)

    return render_template('results.html', groups=groups, total_students=len(names_list))

@app.route('/download-pdf')
def download_pdf():
    # Retrieve groups from session
    groups = session.get('groups', [])
    
    if not groups:
        return redirect(url_for('index'))

    # Initialize PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Class Group Assignments", ln=1, align='C')
    pdf.ln(10)

    # Content
    group_number = 1
    for group in groups:
        # Group Header
        pdf.set_font("Arial", 'B', 12)
        # Light gray background for header
        pdf.set_fill_color(240, 240, 240) 
        pdf.cell(0, 10, txt=f"Group {group_number} ({len(group)} members)", ln=1, align='L', fill=True)
        
        # Names
        pdf.set_font("Arial", size=11)
        for name in group:
            # Clean name to ensure it doesn't break Latin-1 encoding (common FPDF issue)
            clean_name = name.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 8, txt=f"  - {clean_name}", ln=1, align='L')
        
        pdf.ln(5) # Space between groups
        group_number += 1

    # Create response
    # output(dest='S') returns the PDF as a string (latin-1 encoded)
    response_content = pdf.output(dest='S').encode('latin-1')
    
    response = make_response(response_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=class_groups.pdf'
    
    return response

if __name__ == "__main__":
    app.run(debug=True)