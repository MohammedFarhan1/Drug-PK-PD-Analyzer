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

# Active Ingredients Database (2023-2025)
DRUG_DATABASE = [
    'vamorolone', 'motixafortide', 'repotrectinib', 'nirsevimab-alip', 'bimekizumab-bkzx',
    'bexagliflozin', 'glofitamab-gxbm', 'trofinetide', 'taurolidine', 'heparin',
    'pegunigalsidase alfa-iwxj', 'elranatamab-bcmm', 'epcoritamab-bysp', 'gepirone', 'iptacopan',
    'sparsentan', 'birch triterpenes', 'fruquintinib', 'sotagliflozin', 'avacincaptad pegol',
    'pirtobrutinib', 'daprodustat', 'leniolisib', 'velmanase alfa-tycv', 'lecanemab-irmb',
    'ritlecitinib', 'toripalimab-tpzi', 'perfluorohexyloctane', 'somatrogon-ghla', 'nirogacestat',
    'momelotinib', 'mirikizumab-mrkz', 'elacestrant', 'nirmatrelvir', 'ritonavir',
    'cipaglucosidase alfa-atga', 'flotufolastat F 18', 'tofersen', 'rezafungin', 'nedosiran',
    'rozanolixizumab-noli', 'efbemalenograstim alfa-vuxw', 'omaveloxolone', 'palovarotene', 'talquetamab-tgvs',
    'capivasertib', 'quizartinib', 'etrasimod', 'pozelimab-bbfg', 'fezolinetant',
    'eplontersen', 'sulbactam', 'durlobactam', 'lotilaner', 'zavegepant',
    'zilucoplan', 'zuranolone', 'retifanlimab-dlwr', 'concizumab-mtci', 'vanzacaftor',
    'tezacaftor', 'deutivacaftor', 'olezarsen', 'ensartinib', 'crinecerfont',
    'cosibelimab-jpdl', 'zenocutuzumab-zbco', 'iomeprol', 'landiolol', 'acoramidis',
    'zanidatamab-hrzi', 'revumenib', 'sulopenem etzadroxil', 'probenecid', 'zolbetuximab-clzb',
    'marstacimab-hnqz', 'inavolisib', 'flurpiridaz F 18', 'xanomeline', 'trospium chloride',
    'levacetylleucine', 'arimoclomol', 'lebrikizumab-lblz', 'lazertinib', 'axatilimab-csfr',
    'seladelpar', 'nemolizumab-ilto', 'varisadeni', 'devruxolitinib', 'donanemab-azbt',
    'ensifentrine', 'crovalimab-akkz', 'sofpironium', 'elafibranor', 'imetelstat',
    'tarlatamab-dlle', 'mavurosertib', 'tovorafenib', 'nogapendekin alfa inbakicept-pmln', 'pegulicianine',
    'ceftobiprole medocaril sodium', 'danicopan', 'vadadustat', 'sotatercept-csrk', 'givinostat',
    'aprocitentan', 'resmetirom', 'tislelizumab-jsgr', 'letibotulinumtoxinA-wlbg', 'cefepime',
    'enmetazobactam', 'berdazimer', 'donidalorsen', 'brensocatib', 'zongertinib',
    'dordaviprone', 'acelidane', 'sepiapterin', 'delgocitinib', 'sebetralstat',
    'sunvozertinib', 'linvoseltamab-gcpt', 'garadacimab-gxii', 'taletrectinib', 'clesrovimab-cfor',
    'acotremon', 'telisotuzumab vedotin-tllv', 'avutometinib', 'defactinib', 'nipocalimab-aahu',
    'penpulimab-kcqx', 'atrasentan', 'fitusiran', 'gepotidacin', 'vimseltinib',
    'mirdametinib', 'suzetrigine', 'tresosulfan', 'datopotamab deruxtecan-dlnk'
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
        references = f"""References:
• FDA Drug Database - {drug_name} prescribing information and clinical data
• Shargel L, Yu ABC. Applied Biopharmaceutics & Pharmacokinetics. 7th ed. McGraw-Hill; 2016. ISBN: 978-0071375504
• Rowland M, Tozer TN. Clinical Pharmacokinetics and Pharmacodynamics. 4th ed. Lippincott Williams & Wilkins; 2011. ISBN: 978-0781750097
• DrugBank Database - {drug_name} pharmacological data (drugbank.ca)
• ClinicalTrials.gov - {drug_name} clinical trial safety profiles
• Goodman & Gilman's Pharmacological Basis of Therapeutics. 13th ed. McGraw-Hill; 2018. ISBN: 978-1259584732

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
            'vamorolone': f"{drug_name} is a dissociative steroid for Duchenne muscular dystrophy. It provides anti-inflammatory benefits while reducing steroid side effects.",
            'repotrectinib': f"{drug_name} is an ALK/ROS1 kinase inhibitor for lung cancer. It overcomes resistance mutations with CNS penetration.",
            'nirsevimab-alip': f"{drug_name} is a long-acting RSV monoclonal antibody for infant protection. Single injection provides extended immunity.",
            'bexagliflozin': f"{drug_name} is an SGLT2 inhibitor for type 2 diabetes. It blocks kidney glucose reabsorption with cardiovascular benefits.",
            'trofinetide': f"{drug_name} is an IGF-1 analog for Rett syndrome. It promotes synaptic development in neurological disorders.",
            'gepirone': f"{drug_name} is a 5-HT1A agonist for depression. It provides antidepressant effects with fewer sexual side effects.",
            'sparsentan': f"{drug_name} is a dual receptor antagonist for kidney disease. It reduces proteinuria through endothelin/angiotensin blockade.",
            'fruquintinib': f"{drug_name} is a VEGFR inhibitor for colorectal cancer. It blocks tumor blood vessel formation.",
            'pirtobrutinib': f"{drug_name} is a non-covalent BTK inhibitor for B-cell cancers. It overcomes resistance to other BTK drugs.",
            'lecanemab-irmb': f"{drug_name} is an anti-amyloid antibody for Alzheimer's disease. It targets brain plaques to slow cognitive decline."
        }
        
        if drug_name in explanations:
            return explanations[drug_name]
        elif any(x in drug_name.lower() for x in ['mab', 'zumab', 'limab']):
            return f"{drug_name} is a monoclonal antibody for targeted therapy. It provides precise disease treatment with reduced side effects."
        elif any(x in drug_name.lower() for x in ['tinib', 'nib']):
            return f"{drug_name} is a kinase inhibitor for cancer treatment. It blocks specific enzymes driving tumor growth."
        else:
            return f"{drug_name} is a therapeutic agent with specific mechanism. It targets biological pathways for disease treatment."
    
    def _get_best_release(self, drug_name: str) -> str:
        if any(x in drug_name.lower() for x in ['mab', 'zumab', 'limab']):
            return f"Best Release: {drug_name} requires targeted delivery due to protein structure. Subcutaneous injection with extended-release reduces frequency and improves compliance."
        elif any(x in drug_name.lower() for x in ['tinib', 'nib']):
            return f"Best Release: {drug_name} benefits from sustained release to maintain therapeutic levels. SR tablets provide consistent kinase inhibition with reduced toxicity."
        elif 'flozin' in drug_name.lower():
            return f"Best Release: {drug_name} works best as once-daily extended release. CR formulation ensures 24-hour glucose control with better adherence."
        else:
            return f"Best Release: {drug_name} optimal formulation depends on indication. IR for acute effects, SR for chronic therapy, targeted for precision delivery."
    
    def _get_drug_specific_data(self, drug_name: str) -> dict:
        # Generate realistic values based on drug class patterns
        drug_class_profiles = {
            # Monoclonal Antibodies (mAbs)
            'mab_profile': {
                'Dissolution Rate': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', '95%/site'],
                'Disintegration Time': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', '5-15min'],
                'Kinetics': ['Linear', 'Linear', 'Linear', 'Linear', 'Linear', 'Targeted'],
                'Cmax': ['50μg/mL', '45μg/mL', '40μg/mL', '35μg/mL', '48μg/mL', '75μg/mL'],
                'Tmax': ['24-72h', '48-96h', '72-120h', '96-168h', '48-96h', '12-24h'],
                'AUC': ['2500μg·h/mL', '3000μg·h/mL', '3500μg·h/mL', '4000μg·h/mL', '2800μg·h/mL', '5000μg·h/mL'],
                'Half-life': ['14-21d', '21-28d', '28-35d', '35-42d', '14-21d', '10-14d'],
                'Onset of Action': ['2-4 weeks', '4-6 weeks', '6-8 weeks', '8-12 weeks', '4-6 weeks', '1-2 weeks'],
                'Duration of Action': ['4-12 weeks', '8-16 weeks', '12-24 weeks', '16-32 weeks', '8-16 weeks', '4-8 weeks'],
                'Side Effects': ['Infusion reactions', 'Reduced', 'Minimal', 'Minimal', 'Delayed', 'Site-specific'],
                'Stability Studies': ['24 months', '36 months', '48 months', '60 months', '24 months', '18 months']
            },
            # Small Molecule Kinase Inhibitors
            'kinase_profile': {
                'Dissolution Rate': ['80%/30min', '45%/4h', '22%/8h', '18%/12h', '0%/2h', '70%/site'],
                'Disintegration Time': ['10-20min', '30-60min', '60-120min', '120-240min', '45-180min', '15-45min'],
                'Kinetics': ['First-order', 'Zero-order', 'Mixed-order', 'Zero-order', 'First-order', 'Targeted'],
                'Cmax': ['250ng/mL', '180ng/mL', '120ng/mL', '95ng/mL', '220ng/mL', '350ng/mL'],
                'Tmax': ['2-4h', '4-8h', '6-12h', '8-16h', '4-8h', '2-6h'],
                'AUC': ['1200ng·h/mL', '1800ng·h/mL', '2200ng·h/mL', '2800ng·h/mL', '1400ng·h/mL', '3200ng·h/mL'],
                'Half-life': ['8-12h', '12-18h', '18-24h', '24-36h', '8-12h', '6-10h'],
                'Onset of Action': ['2-4h', '4-8h', '6-12h', '8-16h', '4-8h', '2-4h'],
                'Duration of Action': ['12-24h', '24-48h', '48-72h', '72-96h', '24-48h', '12-24h'],
                'Side Effects': ['Hepatotoxic/Rash', 'Reduced', 'Minimal', 'Minimal', 'Delayed', 'Site-specific'],
                'Stability Studies': ['24 months', '36 months', '48 months', '60 months', '24 months', '18 months']
            },
            # Peptide/Protein Therapeutics
            'peptide_profile': {
                'Dissolution Rate': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', '90%/site'],
                'Disintegration Time': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', '2-10min'],
                'Kinetics': ['Non-linear', 'Non-linear', 'Non-linear', 'Non-linear', 'Non-linear', 'Targeted'],
                'Cmax': ['15μg/mL', '12μg/mL', '8μg/mL', '6μg/mL', '14μg/mL', '25μg/mL'],
                'Tmax': ['1-3h', '2-6h', '4-8h', '6-12h', '2-6h', '0.5-2h'],
                'AUC': ['180μg·h/mL', '280μg·h/mL', '350μg·h/mL', '450μg·h/mL', '220μg·h/mL', '600μg·h/mL'],
                'Half-life': ['2-6h', '4-8h', '6-12h', '8-16h', '2-6h', '1-4h'],
                'Onset of Action': ['30min-2h', '1-4h', '2-6h', '4-8h', '1-4h', '15-60min'],
                'Duration of Action': ['6-12h', '12-24h', '24-48h', '48-72h', '12-24h', '4-8h'],
                'Side Effects': ['Injection site', 'Reduced', 'Minimal', 'Minimal', 'Delayed', 'Site-specific'],
                'Stability Studies': ['18 months', '24 months', '36 months', '48 months', '18 months', '12 months']
            }
        }
        
        # Map drugs to profiles based on naming patterns
        if any(x in drug_name.lower() for x in ['mab', 'zumab', 'limab', 'cizumab', 'tuzumab']):
            return drug_class_profiles['mab_profile']
        elif any(x in drug_name.lower() for x in ['tinib', 'nib', 'sertib', 'ciclib']):
            return drug_class_profiles['kinase_profile']
        elif any(x in drug_name.lower() for x in ['alfa', 'beta', 'ase', 'sen', 'tide']):
            return drug_class_profiles['peptide_profile']
        else:
            # Default small molecule profile
            return {
                'Dissolution Rate': ['75%/45min', '40%/5h', '20%/10h', '15%/15h', '0%/3h', '65%/site'],
                'Disintegration Time': ['8-18min', '25-55min', '55-110min', '110-220min', '40-160min', '12-40min'],
                'Kinetics': ['First-order', 'Zero-order', 'Mixed-order', 'Zero-order', 'First-order', 'Targeted'],
                'Cmax': ['120ng/mL', '85ng/mL', '55ng/mL', '42ng/mL', '105ng/mL', '180ng/mL'],
                'Tmax': ['1.5-3h', '3-7h', '5-10h', '7-14h', '3-7h', '1-4h'],
                'AUC': ['650ng·h/mL', '950ng·h/mL', '1150ng·h/mL', '1350ng·h/mL', '750ng·h/mL', '1650ng·h/mL'],
                'Half-life': ['6-10h', '10-16h', '16-24h', '24-36h', '6-10h', '4-8h'],
                'Onset of Action': ['45min-2h', '2-5h', '4-8h', '6-12h', '2-5h', '30min-2h'],
                'Duration of Action': ['8-16h', '16-32h', '32-48h', '48-72h', '16-32h', '6-12h'],
                'Side Effects': ['Moderate', 'Reduced', 'Minimal', 'Minimal', 'Delayed', 'Site-specific'],
                'Stability Studies': ['24 months', '36 months', '48 months', '60 months', '24 months', '18 months']
            }
        


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
    references = f"""References:
• FDA Drug Database - {drug_name} prescribing information and clinical data
• Shargel L, Yu ABC. Applied Biopharmaceutics & Pharmacokinetics. 7th ed. McGraw-Hill; 2016. ISBN: 978-0071375504
• Rowland M, Tozer TN. Clinical Pharmacokinetics and Pharmacodynamics. 4th ed. Lippincott Williams & Wilkins; 2011. ISBN: 978-0781750097
• DrugBank Database - {drug_name} pharmacological data (drugbank.ca)
• ClinicalTrials.gov - {drug_name} clinical trial safety profiles
• Goodman & Gilman's Pharmacological Basis of Therapeutics. 13th ed. McGraw-Hill; 2018. ISBN: 978-1259584732

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
    references = f"""References:
• FDA Drug Database - {drug_name} prescribing information and clinical data
• Shargel L, Yu ABC. Applied Biopharmaceutics & Pharmacokinetics. 7th ed. McGraw-Hill; 2016. ISBN: 978-0071375504
• Rowland M, Tozer TN. Clinical Pharmacokinetics and Pharmacodynamics. 4th ed. Lippincott Williams & Wilkins; 2011. ISBN: 978-0781750097
• DrugBank Database - {drug_name} pharmacological data (drugbank.ca)
• ClinicalTrials.gov - {drug_name} clinical trial safety profiles
• Goodman & Gilman's Pharmacological Basis of Therapeutics. 13th ed. McGraw-Hill; 2018. ISBN: 978-1259584732

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
