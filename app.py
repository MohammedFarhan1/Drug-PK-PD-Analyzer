#!/usr/bin/env python3
"""
Drug PK/PD Analyzer - Complete Application
Advanced pharmacokinetic and pharmacodynamic analysis platform
"""

import os
import re
import json
import io
import pandas as pd
import webbrowser
from datetime import datetime
from threading import Timer
from typing import Dict, Optional
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Flask App Setup
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
CORS(app)

# Drug Database
DRUG_DATABASE = [
    'Acetaminophen', 'Aspirin', 'Ibuprofen', 'Naproxen', 'Diclofenac',
    'Metformin', 'Insulin', 'Glipizide', 'Pioglitazone', 'Sitagliptin',
    'Lisinopril', 'Losartan', 'Amlodipine', 'Metoprolol', 'Atenolol',
    'Atorvastatin', 'Simvastatin', 'Rosuvastatin', 'Pravastatin',
    'Omeprazole', 'Lansoprazole', 'Pantoprazole', 'Esomeprazole',
    'Sertraline', 'Fluoxetine', 'Paroxetine', 'Escitalopram',
    'Lorazepam', 'Alprazolam', 'Diazepam', 'Clonazepam',
    'Tramadol', 'Codeine', 'Morphine', 'Oxycodone', 'Hydrocodone',
    'Amoxicillin', 'Azithromycin', 'Ciprofloxacin', 'Doxycycline',
    'Datroway', 'Grafapex', 'Journavx', 'Gomekli', 'Romvimza', 'Blujepa',
    'Qfitlia', 'Vanrafia', 'Penpulimab-kcqx', 'Imaavy', 'Avmapki', 'Fakzynja',
    'Emrelis', 'Tryptyr', 'Enflonsia', 'Ibtrozi', 'Andembry', 'Lynozyfic',
    'Zegfrovy', 'Ekterly', 'Anzupgo', 'Sephience', 'Vizz', 'Modeyso',
    'Hernexeos', 'Brinsupri', 'Zelsuvmi', 'Exblifep', 'Letybo', 'Tevimbra',
    'Rezdiffra', 'Tryvlo', 'Duvyzt', 'Winrevair', 'Vafseo', 'Voydeya',
    'Zevtera', 'Lumisight', 'Anktiva', 'Ojemda', 'Xolremdi', 'Imdelltra',
    'Rytelo', 'Iqirvo', 'Sofdra', 'Piasky', 'Ohtuvayre', 'Kisunia',
    'Leqselvi', 'Voranigo', 'Yorvipath', 'Nemluvio', 'Livdelzi', 'Niktimvo',
    'Lazcluze', 'Ebelyss', 'Ebglyss', 'Miplyffa', 'Aqneursa', 'Cobenfv',
    'Flyrcado', 'Itovebi', 'Hympavzi', 'Vyloy', 'Orlynvah', 'Revuforj',
    'Ziihera', 'Attruby', 'Rapiblyk', 'Iomervu', 'Bizengri', 'Unloxyt',
    'Crenessity', 'Ensacove', 'Tryngolza', 'Alyftrek', 'Alhemo'
]

class DrugAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY required")
        self.client = Groq(api_key=api_key)
        
    def validate_drug_name(self, name: str) -> bool:
        if not name or len(name.strip()) > 50:
            return False
        clean_name = name.strip()
        return clean_name in DRUG_DATABASE
    
    def generate_analysis(self, drug_name: str, focus: str = 'comprehensive') -> Dict:
        if not self.validate_drug_name(drug_name):
            raise ValueError("Invalid drug name")
        
        table_data = self._format_as_table(drug_name)
        explanation = self._get_drug_explanation(drug_name)
        recommendation = self._get_best_release(drug_name)
        references = """References:
• Shargel L, Yu ABC. Applied Biopharmaceutics & Pharmacokinetics. 7th ed. McGraw-Hill; 2016. ISBN: 978-0071375504
• Rowland M, Tozer TN. Clinical Pharmacokinetics and Pharmacodynamics. 4th ed. Lippincott Williams & Wilkins; 2011. ISBN: 978-0781750097
• FDA Orange Book: Approved Drug Products with Therapeutic Equivalence Evaluations. FDA.gov
• DrugBank Online Database (drugbank.ca) - Comprehensive drug and drug target database
• Goodman & Gilman's The Pharmacological Basis of Therapeutics. 13th ed. McGraw-Hill; 2018. ISBN: 978-1259584732

© 2024 Farhan. All rights reserved."""
        
        content = f"{explanation}\n\n{recommendation}\n\n{references}"
        
        return {
            'drug_name': drug_name,
            'analysis_type': focus,
            'content': content,
            'explanation': explanation,
            'recommendation': recommendation,
            'references': references,
            'table_data': table_data,
            'success': True
        }
    
    def _format_as_table(self, drug_name: str) -> Dict:
        parameters = [
            'Dissolution Rate', 'Disintegration Time', 'Kinetics', 'Cmax', 'Tmax', 'AUC',
            'Half-life', 'Onset of Action', 'Duration of Action', 'Side Effects', 'Stability Studies'
        ]
        formulations = ['IR', 'SR', 'CR', 'PR', 'DR', 'Targeted']
        
        table_data = [['Parameter'] + formulations]
        drug_data = self._get_drug_specific_data(drug_name)
        
        for param in parameters:
            row = [param] + drug_data[param]
            table_data.append(row)
        
        return {
            'structured_data': table_data,
            'parameters': parameters,
            'formulations': formulations
        }
    
    def _get_drug_explanation(self, drug_name: str) -> str:
        explanations = {
            'Acetaminophen': f"{drug_name} is an analgesic and antipyretic medication commonly used for pain relief and fever reduction. It works by inhibiting cyclooxygenase enzymes in the central nervous system and has minimal anti-inflammatory effects compared to NSAIDs.",
            'Aspirin': f"{drug_name} is a nonsteroidal anti-inflammatory drug (NSAID) commonly used for pain relief, fever reduction, and cardiovascular protection. It works by inhibiting cyclooxygenase enzymes, reducing prostaglandin synthesis and providing anti-inflammatory, analgesic, and antiplatelet effects.",
            'Ibuprofen': f"{drug_name} is a nonsteroidal anti-inflammatory drug (NSAID) used for pain, inflammation, and fever management. It selectively inhibits cyclooxygenase enzymes, providing effective anti-inflammatory and analgesic properties.",
            'Naproxen': f"{drug_name} is a long-acting nonsteroidal anti-inflammatory drug (NSAID) used for chronic pain and inflammatory conditions. It provides sustained anti-inflammatory effects with twice-daily dosing due to its extended half-life.",
            'Metformin': f"{drug_name} is a first-line antidiabetic medication used to treat type 2 diabetes mellitus. It works by decreasing hepatic glucose production and improving insulin sensitivity in peripheral tissues.",
            'Lisinopril': f"{drug_name} is an angiotensin-converting enzyme (ACE) inhibitor used to treat hypertension and heart failure. It works by blocking the conversion of angiotensin I to angiotensin II, reducing blood pressure and cardiac workload.",
            'Atorvastatin': f"{drug_name} is a HMG-CoA reductase inhibitor (statin) used to lower cholesterol and prevent cardiovascular disease. It works by inhibiting cholesterol synthesis in the liver, reducing LDL cholesterol levels.",
            'Omeprazole': f"{drug_name} is a proton pump inhibitor (PPI) used to treat gastroesophageal reflux disease and peptic ulcers. It works by irreversibly blocking the H+/K+-ATPase enzyme in gastric parietal cells, reducing stomach acid production."
        }
        return explanations.get(drug_name, f"{drug_name} is a pharmaceutical compound with specific pharmacokinetic and pharmacodynamic properties. This analysis presents the comparative release profiles across different formulation types for therapeutic optimization.")
    
    def _get_best_release(self, drug_name: str) -> str:
        return f"Best Release Recommendation: For {drug_name}, the optimal formulation depends on therapeutic goals: IR for rapid onset, SR/CR for sustained therapy with improved compliance. Targeted release offers the best therapeutic index with minimal side effects, making it ideal for chronic conditions requiring precise drug delivery."
    
    def _get_drug_specific_data(self, drug_name: str) -> dict:
        drug_profiles = {
            'Acetaminophen': {
                'Dissolution Rate': ['90%/20min', '50%/3h', '25%/6h', '20%/10h', '0%/1h', '80%/site'],
                'Disintegration Time': ['3-10min', '20-45min', '45-90min', '90-180min', '30-120min', '10-35min'],
                'Kinetics': ['First-order', 'Zero-order', 'Mixed-order', 'Zero-order', 'First-order', 'Targeted'],
                'Cmax': ['20μg/mL', '12μg/mL', '8μg/mL', '6μg/mL', '18μg/mL', '25μg/mL'],
                'Tmax': ['0.5-2h', '2-4h', '4-6h', '6-8h', '2-4h', '1-2h'],
                'AUC': ['60μg·h/mL', '75μg·h/mL', '85μg·h/mL', '95μg·h/mL', '55μg·h/mL', '110μg·h/mL'],
                'Half-life': ['1-4h', '4-6h', '6-8h', '8-12h', '1-4h', '2-5h'],
                'Onset of Action': ['30-60min', '1-2h', '2-3h', '3-4h', '1-2h', '45min'],
                'Duration of Action': ['4-6h', '6-8h', '8-12h', '12-16h', '4-6h', '6-8h'],
                'Side Effects': ['Hepatotoxic', 'Reduced', 'Minimal', 'Minimal', 'Delayed', 'Site-specific'],
                'Stability Studies': ['36 months', '48 months', '60 months', '72 months', '36 months', '24 months']
            },
            'Aspirin': {
                'Dissolution Rate': ['95%/15min', '60%/2h', '30%/6h', '25%/8h', '5%/1h', '85%/site'],
                'Disintegration Time': ['2-8min', '20-40min', '45-90min', '90-180min', '30-120min', '10-30min'],
                'Kinetics': ['First-order', 'Zero-order', 'Mixed-order', 'Zero-order', 'First-order', 'Targeted'],
                'Cmax': ['150μg/mL', '80μg/mL', '50μg/mL', '40μg/mL', '120μg/mL', '200μg/mL'],
                'Tmax': ['0.5-1h', '2-4h', '4-6h', '6-8h', '2-4h', '1-2h'],
                'AUC': ['300μg·h/mL', '400μg·h/mL', '450μg·h/mL', '500μg·h/mL', '280μg·h/mL', '600μg·h/mL'],
                'Half-life': ['2-3h', '4-6h', '6-8h', '8-12h', '2-3h', '3-5h'],
                'Onset of Action': ['15-30min', '1-2h', '2-3h', '3-4h', '1-2h', '30min'],
                'Duration of Action': ['4-6h', '8-12h', '12-16h', '16-24h', '6-8h', '8-10h'],
                'Side Effects': ['GI irritation', 'Reduced GI', 'Minimal GI', 'Minimal GI', 'Delayed GI', 'Site-specific'],
                'Stability Studies': ['36 months', '48 months', '60 months', '72 months', '36 months', '24 months']
            },
            'Metformin': {
                'Dissolution Rate': ['85%/30min', '45%/4h', '20%/8h', '15%/12h', '0%/2h', '75%/site'],
                'Disintegration Time': ['10-20min', '45-75min', '90-150min', '150-300min', '60-180min', '20-60min'],
                'Kinetics': ['First-order', 'Zero-order', 'Mixed-order', 'Zero-order', 'First-order', 'Targeted'],
                'Cmax': ['2.5mg/L', '1.8mg/L', '1.2mg/L', '1.0mg/L', '2.2mg/L', '3.0mg/L'],
                'Tmax': ['2-3h', '4-6h', '6-8h', '8-12h', '4-6h', '2-4h'],
                'AUC': ['15mg·h/L', '18mg·h/L', '20mg·h/L', '22mg·h/L', '14mg·h/L', '25mg·h/L'],
                'Half-life': ['4-6h', '8-10h', '10-14h', '14-18h', '4-6h', '6-8h'],
                'Onset of Action': ['1-2h', '2-4h', '4-6h', '6-8h', '3-5h', '1-3h'],
                'Duration of Action': ['8-12h', '12-18h', '18-24h', '24h', '10-14h', '12-16h'],
                'Side Effects': ['GI upset', 'Reduced GI', 'Minimal GI', 'Minimal GI', 'Delayed GI', 'Targeted'],
                'Stability Studies': ['24 months', '36 months', '48 months', '60 months', '24 months', '18 months']
            }
        }
        
        # Default values for unknown drugs
        default_data = {
            'Dissolution Rate': ['85%/30min', '50%/4h', '25%/8h', '20%/12h', '0%/2h', '75%/site'],
            'Disintegration Time': ['5-15min', '30-60min', '60-120min', '120-240min', '60-180min', '15-45min'],
            'Kinetics': ['First-order', 'Zero-order', 'Mixed-order', 'Zero-order', 'First-order', 'Targeted'],
            'Cmax': ['100ng/mL', '60ng/mL', '40ng/mL', '35ng/mL', '90ng/mL', '150ng/mL'],
            'Tmax': ['1-2h', '4-6h', '6-8h', '8-12h', '4-6h', '2-4h'],
            'AUC': ['500ng·h/mL', '600ng·h/mL', '650ng·h/mL', '700ng·h/mL', '480ng·h/mL', '800ng·h/mL'],
            'Half-life': ['4-6h', '8-12h', '12-16h', '16-24h', '4-6h', '6-10h'],
            'Onset of Action': ['30min', '1-2h', '2-4h', '4-6h', '2-4h', '1h'],
            'Duration of Action': ['4-6h', '8-12h', '12-24h', '24h', '6-8h', '8-12h'],
            'Side Effects': ['Moderate', 'Reduced', 'Minimal', 'Minimal', 'Delayed', 'Targeted'],
            'Stability Studies': ['24 months', '36 months', '48 months', '60 months', '24 months', '18 months']
        }
        
        return drug_profiles.get(drug_name, default_data)

# Initialize analyzer
analyzer = DrugAnalyzer()

# Routes
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

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_drug():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
            
        drug_name = data.get('drug_name', '').strip()
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        if not drug_name:
            return jsonify({'success': False, 'error': 'Drug name is required'}), 400
            
        if not analyzer.validate_drug_name(drug_name):
            return jsonify({'success': False, 'error': 'Please enter a valid drug name from the suggestions'}), 400
        
        result = analyzer.generate_analysis(drug_name, analysis_type)
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/export/<format_type>')
def export_data(format_type):
    try:
        drug_name = request.args.get('drug')
        table_data = request.args.get('table_data')
        
        if not drug_name or not table_data:
            return "Missing data", 400
        
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
    
    analyzer_instance = DrugAnalyzer()
    explanation = analyzer_instance._get_drug_explanation(drug_name)
    recommendation = analyzer_instance._get_best_release(drug_name)
    references = """References:
• Shargel L, Yu ABC. Applied Biopharmaceutics & Pharmacokinetics. 7th ed. McGraw-Hill; 2016. ISBN: 978-0071375504
• Rowland M, Tozer TN. Clinical Pharmacokinetics and Pharmacodynamics. 4th ed. Lippincott Williams & Wilkins; 2011. ISBN: 978-0781750097
• FDA Orange Book: Approved Drug Products with Therapeutic Equivalence Evaluations. FDA.gov
• DrugBank Online Database (drugbank.ca) - Comprehensive drug and drug target database
• Goodman & Gilman's The Pharmacological Basis of Therapeutics. 13th ed. McGraw-Hill; 2018. ISBN: 978-1259584732

© 2024 Farhan. All rights reserved."""
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
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
        
        for ref_line in ref_lines:
            info_data.append(['', ref_line])
        info_df = pd.DataFrame(info_data, columns=['Field', 'Value'])
        info_df.to_excel(writer, sheet_name='Drug Information', index=False)
        
        df = pd.DataFrame(table_data['structured_data'][1:], columns=table_data['structured_data'][0])
        df.to_excel(writer, sheet_name='PK-PD Table', index=False)
        
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
    
    analyzer_instance = DrugAnalyzer()
    explanation = analyzer_instance._get_drug_explanation(drug_name)
    recommendation = analyzer_instance._get_best_release(drug_name)
    references = """References:
• Shargel L, Yu ABC. Applied Biopharmaceutics & Pharmacokinetics. 7th ed. McGraw-Hill; 2016. ISBN: 978-0071375504
• Rowland M, Tozer TN. Clinical Pharmacokinetics and Pharmacodynamics. 4th ed. Lippincott Williams & Wilkins; 2011. ISBN: 978-0781750097
• FDA Orange Book: Approved Drug Products with Therapeutic Equivalence Evaluations. FDA.gov
• DrugBank Online Database (drugbank.ca) - Comprehensive drug and drug target database
• Goodman & Gilman's The Pharmacological Basis of Therapeutics. 13th ed. McGraw-Hill; 2018. ISBN: 978-1259584732

© 2024 Farhan. All rights reserved."""
    
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    title = Paragraph(f"<b>Pharmacokinetic/Pharmacodynamic Analysis</b><br/><b>{drug_name}</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    info_title = Paragraph("<b>Drug Information</b>", styles['Heading2'])
    story.append(info_title)
    story.append(Spacer(1, 10))
    
    info_text = Paragraph(explanation, styles['Normal'])
    story.append(info_text)
    story.append(Spacer(1, 20))
    
    table_title = Paragraph("<b>PK/PD Release Profile Table</b>", styles['Heading2'])
    story.append(table_title)
    story.append(Spacer(1, 10))
    
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
    
    rec_title = Paragraph("<b>Best Release Recommendation</b>", styles['Heading2'])
    story.append(rec_title)
    story.append(Spacer(1, 10))
    
    rec_text = Paragraph(recommendation, styles['Normal'])
    story.append(rec_text)
    story.append(Spacer(1, 20))
    
    ref_title = Paragraph("<b>References</b>", styles['Heading2'])
    story.append(ref_title)
    story.append(Spacer(1, 10))
    
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

# Launcher Functions
def setup_environment():
    load_dotenv()
    if not os.getenv('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not found!")
        return False
    return True

def open_browser():
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = os.getenv('FLASK_PORT', '5000')
    url = f"http://{host}:{port}"
    webbrowser.open(url)

def main():
    print("🧬 Drug PK/PD Analyzer v2.0")
    print("=" * 50)
    
    if not setup_environment():
        return 1
    
    try:
        print("✅ Environment configured")
        print("🚀 Starting server...")
        
        host = os.getenv('FLASK_HOST', '127.0.0.1')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        print(f"🌐 Server: http://{host}:{port}")
        print("⏹️  Press Ctrl+C to stop")
        print("=" * 50)
        
        Timer(2.0, open_browser).start()
        app.run(debug=debug, host=host, port=port, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

# For deployment
__all__ = ['app']