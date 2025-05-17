import re

def extract_text_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        return text, []
    except Exception as e:
        return '', [str(e)]

def classify_legal_issue(text):
    text = text.lower()
    if 'eviction' in text or 'landlord' in text:
        return 'Landlord-Tenant'
    elif 'credit' in text or 'equifax' in text:
        return 'Credit Dispute'
    elif 'human rights' in text:
        return 'Human Rights'
    elif 'police' in text or 'abuse' in text:
        return 'Police Misconduct'
    elif 'child' in text or 'CAS' in text:
        return 'Child Protection'
    elif 'small claims' in text:
        return 'Small Claims'
    return 'General Legal Issue'

def score_merit(text, legal_issue):
    base_score = 50
    if legal_issue.lower() in text.lower():
        return 90
    elif len(text.split()) > 300:
        return 75
    return base_score

def select_form(legal_issue, province):
    form_map = {
        'Landlord-Tenant': {
            'court': 'Landlord and Tenant Board',
            'form_name': 'T2 - Application About Tenant Rights'
        },
        'Credit Dispute': {
            'court': 'Federal Privacy Commissioner',
            'form_name': 'PIPEDA Complaint Form'
        },
        'Human Rights': {
            'court': 'Human Rights Tribunal',
            'form_name': 'HRTO Form 1 - Application'
        },
        'Police Misconduct': {
            'court': 'Office of the Independent Police Review Director',
            'form_name': 'OIPRD Complaint Form'
        },
        'Child Protection': {
            'court': 'Family Court',
            'form_name': 'Form 33B - Protection Application'
        },
        'Small Claims': {
            'court': 'Small Claims Court',
            'form_name': 'Plaintiff’s Claim (Form 7A)'
        },
        'General Legal Issue': {
            'court': 'Provincial Court',
            'form_name': 'General Filing Form'
        }
    }
    return form_map.get(legal_issue, form_map['General Legal Issue'])
