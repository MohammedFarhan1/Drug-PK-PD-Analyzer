from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import io
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from core import DrugAnalyzer, DRUG_DATABASE

import os
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
CORS(app)

# Initialize analyzer
analyzer = DrugAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/drugs/search')
def search_drugs():
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])
    
    matches = [drug for drug in DRUG_DATABASE if query in drug.lower()][:10]
    return jsonify(matches)

@app.route('/api/analyze', methods=['POST'])
def analyze_drug():
    try:
        data = request.get_json()
        drug_name = data.get('drug_name', '').strip()
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        if not analyzer.validate_drug_name(drug_name):
            return jsonify({'success': False, 'error': 'Invalid drug name'}), 400
        
        result = analyzer.generate_analysis(drug_name, analysis_type)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Analysis failed'}), 500

@app.route('/api/export/<format_type>')
def export_data(format_type):
    try:
        drug_name = request.args.get('drug')
        table_data = request.args.get('table_data')
        
        if not drug_name or not table_data:
            return "Missing data", 400
        
        # Parse table data from JSON string
        import json
        parsed_data = json.loads(table_data)
        
        if format_type == 'excel':
            return export_excel(drug_name, parsed_data)
        elif format_type == 'pdf':
            return export_pdf(drug_name, parsed_data)
        else:
            return "Invalid format", 400
            
    except Exception as e:
        return "Export failed", 500

def export_excel(drug_name: str, table_data: dict):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{drug_name.replace(' ', '_')}_pk_pd_{timestamp}.xlsx"
    
    # Get additional data
    analyzer_instance = DrugAnalyzer()
    explanation = analyzer_instance._get_drug_explanation(drug_name)
    recommendation = analyzer_instance._get_best_release(drug_name)
    references = """References:
• Shargel L, Yu ABC. Applied Biopharmaceutics & Pharmacokinetics. 7th ed. McGraw-Hill; 2016. ISBN: 978-0071375504
• Rowland M, Tozer TN. Clinical Pharmacokinetics and Pharmacodynamics. 4th ed. Lippincott Williams & Wilkins; 2011. ISBN: 978-0781750097
• FDA Orange Book: Approved Drug Products with Therapeutic Equivalence Evaluations. FDA.gov
• DrugBank Online Database (drugbank.ca) - Comprehensive drug and drug target database
• Goodman & Gilman's The Pharmacological Basis of Therapeutics. 13th ed. McGraw-Hill; 2018. ISBN: 978-1259584732"""
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Create info sheet
        # Split references into separate rows
        ref_lines = [line.strip() for line in references.split('\n') if line.strip()]
        
        info_data = [
            ['Drug Information', ''],
            ['Drug Name', drug_name],
            ['Description', explanation],
            ['', ''],
            ['Best Release Recommendation', ''],
            ['Recommendation', recommendation],
            ['', ''],
            ['References', '']
        ]
        
        # Add each reference as a separate row
        for ref_line in ref_lines:
            info_data.append(['', ref_line])
        info_df = pd.DataFrame(info_data, columns=['Field', 'Value'])
        info_df.to_excel(writer, sheet_name='Drug Information', index=False)
        
        # Create PK/PD table sheet
        df = pd.DataFrame(table_data['structured_data'][1:], columns=table_data['structured_data'][0])
        df.to_excel(writer, sheet_name='PK-PD Table', index=False)
        
        # Format worksheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = max(len(str(cell.value)) for cell in column)
                worksheet.column_dimensions[column[0].column_letter].width = min(max_length + 5, 50)
    
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def export_pdf(drug_name: str, table_data: dict):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{drug_name.replace(' ', '_')}_pk_pd_{timestamp}.pdf"
    
    # Get additional data
    analyzer_instance = DrugAnalyzer()
    explanation = analyzer_instance._get_drug_explanation(drug_name)
    recommendation = analyzer_instance._get_best_release(drug_name)
    references = """References:
• Shargel L, Yu ABC. Applied Biopharmaceutics & Pharmacokinetics. 7th ed. McGraw-Hill; 2016. ISBN: 978-0071375504
• Rowland M, Tozer TN. Clinical Pharmacokinetics and Pharmacodynamics. 4th ed. Lippincott Williams & Wilkins; 2011. ISBN: 978-0781750097
• FDA Orange Book: Approved Drug Products with Therapeutic Equivalence Evaluations. FDA.gov
• DrugBank Online Database (drugbank.ca) - Comprehensive drug and drug target database
• Goodman & Gilman's The Pharmacological Basis of Therapeutics. 13th ed. McGraw-Hill; 2018. ISBN: 978-1259584732"""
    
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"<b>Pharmacokinetic/Pharmacodynamic Analysis</b><br/><b>{drug_name}</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Drug Information
    info_title = Paragraph("<b>Drug Information</b>", styles['Heading2'])
    story.append(info_title)
    story.append(Spacer(1, 10))
    
    info_text = Paragraph(explanation, styles['Normal'])
    story.append(info_text)
    story.append(Spacer(1, 20))
    
    # PK/PD Table
    table_title = Paragraph("<b>PK/PD Release Profile Table</b>", styles['Heading2'])
    story.append(table_title)
    story.append(Spacer(1, 10))
    
    # Create table
    table = Table(table_data['structured_data'])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Best Release Recommendation
    rec_title = Paragraph("<b>Best Release Recommendation</b>", styles['Heading2'])
    story.append(rec_title)
    story.append(Spacer(1, 10))
    
    rec_text = Paragraph(recommendation, styles['Normal'])
    story.append(rec_text)
    story.append(Spacer(1, 20))
    
    # References
    ref_title = Paragraph("<b>References</b>", styles['Heading2'])
    story.append(ref_title)
    story.append(Spacer(1, 10))
    
    # Split references into bullet points
    ref_lines = references.split('\n')
    for line in ref_lines:
        if line.strip():
            ref_text = Paragraph(line, styles['Normal'])
            story.append(ref_text)
            story.append(Spacer(1, 6))
    
    doc.build(story)
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error="Server error"), 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=debug_mode, host=host, port=port)
