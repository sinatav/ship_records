import re
import pandas as pd

def extract_date(text):
    if not text:
        return None
    match = re.search(r"\b(\d{1,2}/\d{1,2}/\d{4})\b", str(text))
    return match.group(1) if match else None

def extract_embark_loc(text):
    if not text: return None
    match = re.search(r"(embarqué|rembarqué|fait la campagne|armement)\s+(?:à|au|en|sur)?\s*([\w\s'\-]+)", text.lower())
    return match.group(2).strip() if match else None

def extract_disembark_loc(text):
    if not text: return None
    match = re.search(r"(débarqué|déserté|mort|passé|resté)\s+(?:à|au|en|sur)?\s*([\w\s'\-]+)", text.lower())
    return match.group(2).strip() if match else None

def split_remarks(remarks):
    """Split remarks at 'rembarqué' into multiple legs."""
    if not remarks:
        return [None]
    parts = re.split(r"(?<=rembarqué)", remarks, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]

def extract_embark_loc(text):
    pass

def extract_disembark_loc(text):
    pass

def extract_details(text):
    # Patterns for embarkation
    embark_patterns = {
        'embarqué': {                                                                                           
            'date': r'\b(?:embarqué|rembarqué|embarquée|rembarquée|embarqués|rembarqués|embarquées|rembarquées) (?:(?!\b(?:débarqué|débarquée|débarqués|débarquées|déserté|désertée|désertés|désertées|mort|morte|morts|mortes|passé|passée|passés|passées|resté)\b).)*le (\d{2}/\d{2}/\d{4})(?=\s|\n|$| ---|,)',
            'location': r'\b(?:embarqué|rembarqué|embarquée|rembarquée|embarqués|rembarqués|embarquées|rembarquées) à ([\w\s\'-îÎ]+?)(?=\s+\b(?:mort[es]?|débarqué[es]?|déserté[es]?|passé[es]?|resté[es]?|tombé[es]?)\b| le \d{2}/\d{2}/\d{4}|,| ---|\n|$)'
        },
        'a fait la': {
            'date': r'remplacement du (\d{2}/\d{2}/\d{4})',
            'location': r'\b(?:a|à) fait la campagne de ([\w\s\'-îÎ]+?) à ([\w\s\'-îÎ]+)'
        },
        'supplément': {
            'date': r'\bsupplément à (?!\b(?:débarqué|débarquée|débarqués|débarquées|déserté|désertée|désertés|désertées|mort|morte|morts|mortes|passé|passée|passés|passées)\b)[\w\s\'-îÎ]+? du (\d{2}/\d{2}/\d{4})',
            'location': r'\bsupplément à ([\w\s\'-îÎ]+?) du \d{2}/\d{2}/\d{4}'
        },
        'remplacement': {
            'date': r'\bremplacement (?:au|à)?(?!\b(?:débarqué|débarquée|débarqués|débarquées|déserté|désertée|désertés|désertées|mort|morte|morts|mortes|passé|passée|passés|passées)\b)[\w\s\'-îÎ]+?(?: le| du) (\d{2}/\d{2}/\d{4})',
            'location': r'\bremplacement (?:au|à)? ([\w\s\'-îÎ]+?)(?: en| le| du|\n|,| ---|$)'
        },
        'trouvé': {
            'date': r'\btrouvé[es]? caché[es]? à bord(?:(?!\b(?:débarqué[es]?|déserté[es]?|mort[es]?|passé[es]?)\b)[^\n])*? le (\d{2}/\d{2}/\d{4})',
            'location': r'\btrouvé[es]? caché[es]? à bord (?:après le départ de|le \d{2}/\d{2}/\d{4})\s+((?!\b(?:débarqué[es]?|sert|déserté[es]?|mort[es]?|passé[es]?)\b)[\w\s\'-îÎ]+?)(?=\s+\b(?:le\s+\d{2}/\d{2}/\d{4}|---|,|\n|$|\b(?:débarqué[es]?|sert|déserté[es]?|mort[es]?|passé[es]?)\b))'
        }
    }

    # Patterns for disembarkation
    disembark_patterns = {
        'débarqué': {
            'date': r'\bdébarqué[es]?.*?(?:à|au|furtivement à|malade après être tombé du haut mal à)? (?:désarmement à |malade à |malade et mort à l\'hôpital (?:de|du) |malade à l\'hôpital (?:de|du) )?[\w\s\'-îÎ]+? le (\d{2}/\d{2}/\d{4})',
            'location': r'\bdébarqué[es]? (?:au |à |furtivement à |malade après être tombé du haut mal à )?(?:désarmement à |malade à l\'hôpital (?:de|du) |malade à |malade et mort à l\'hôpital (?:de|du) )?([\w\s\'-îÎ]+?)(?= le \d{2}/\d{2}/\d{4}| ---|,|\n|$| mort[es]?)'
        },
        'déserté': {
            'date': r'\bdéserté[es]? (?:à [\w\s\'-îÎ]+|sur le vaisseau de côte le [\w\s\'-îÎ]+|en [\w\s\'-îÎ]+) le (\d{2}/\d{2}/\d{4})',
            'location': r'\bdéserté[es]? (?:à|en|au départ de) ([\w\s\'-îÎ]+?)(?: le|\n|,| ---|$)'
        },
        'mort en mer': {
            'date': r'\b(?:mort[es]? (?:en mer|noyé en [\w\s\'-îÎ]+|du [\w\s\'-îÎ]+ en [\w\s\'-îÎ]+|à l\'hôpital de [\w\s\'-îÎ]+|à la ration|à [\w\s\'-îÎ]+)|tombé à la mer et mort noyé) le (\d{2}/\d{2}/\d{4})',
            'location': r'\bmort[es]? (?:en mer|à l\'hôpital (?:du|de)|à la ration|à) ([\w\s\'-îÎ]+?)(?= le \d{2}/\d{2}/\d{4})'
        },
        'a fait la': {
            'date': r'levé[es]? du (\d{2}/\d{2}/\d{4})',
            'location': r'\b(?:a|à) fait la campagne de [\w\s\'-îÎ]+? à ([\w\s\'-îÎ]+?)(?=\s*(?:du|le) \d{2}/\d{2}/\d{4}|\s*---|,|en|\n|$)'
        },
        'passé': {
            'date': r'\bpassé[es]? sur la [\w\s\'-îÎ]+ en rade de [\w\s\'-îÎ]+ le (\d{2}/\d{2}/\d{4})',
            'location': r'\bpassé[es]? sur la [\w\s\'-îÎ]+ en rade de ([\w\s\'-îÎ]+)(?=\s+(?:le\s+\d{2}/\d{2}/\d{4}|,| ---|\n|$))'
        },
        'resté': {
            'date': r'\bresté[es]? (?:malade au départ de|malade à l\'hôpital de|à terre au départ de|à terre malade au départ de|à terre malade à|à|en|au départ de) [\w\s\'-îÎ]+? le\s*(\d{2}/\d{2}/\d{4})(?: rejoint|\n|,| ---|$)',
             'location': r'\bresté[es]? (?:malade au départ de|malade à l\'hôpital de|à terre au départ de|à terre malade au départ de|à terre malade à|à|en|au départ de) ([\w\s\'-îÎ]+?)(?: le| rejoint|\n|,| ---|$)'

        }
    }

    # Initialize results
    embark_location = pd.NA
    embark_date = pd.NA
    disembark_location = pd.NA
    disembark_date = pd.NA

    # Initialize match variables
    embark_date_match = None
    embark_location_match = None
    disembark_date_match = None
    disembark_location_match = None

    # Determine which embark patterns to use
    if 'embarqué' in text.lower() or 'rembarqué' in text.lower():
        embark_date_match = re.search(embark_patterns['embarqué']['date'], text, flags=re.IGNORECASE)
        embark_location_match = re.search(embark_patterns['embarqué']['location'], text, flags=re.IGNORECASE)
    elif 'fait la campagne' in text.lower():
        embark_date_match = re.search(embark_patterns['a fait la']['date'], text, flags=re.IGNORECASE)
        embark_location_match = re.search(embark_patterns['a fait la']['location'], text, flags=re.IGNORECASE)
    elif 'supplément' in text.lower():
        embark_date_match = re.search(embark_patterns['supplément']['date'], text, flags=re.IGNORECASE)
        embark_location_match = re.search(embark_patterns['supplément']['location'], text, flags=re.IGNORECASE)
    elif 'remplacement' in text.lower():
        embark_date_match = re.search(embark_patterns['remplacement']['date'], text, flags=re.IGNORECASE)
        embark_location_match = re.search(embark_patterns['remplacement']['location'], text, flags=re.IGNORECASE)
    elif 'trouvé' in text.lower():
        embark_date_match = re.search(embark_patterns['trouvé']['date'], text, flags=re.IGNORECASE)
        embark_location_match = re.search(embark_patterns['trouvé']['location'], text, flags=re.IGNORECASE)        

    # Extract embark information
    if embark_date_match:
        embark_date = embark_date_match.group(1)
    if embark_location_match:
        embark_location = embark_location_match.group(1)

    # Determine which disembark patterns to use
    if 'débarqué' in text.lower():
        disembark_date_match = re.search(disembark_patterns['débarqué']['date'], text, flags=re.IGNORECASE)
        disembark_location_match = re.search(disembark_patterns['débarqué']['location'], text, flags=re.IGNORECASE)
    elif 'déserté' in text.lower():
        disembark_date_match = re.search(disembark_patterns['déserté']['date'], text, flags=re.IGNORECASE)
        disembark_location_match = re.search(disembark_patterns['déserté']['location'], text, flags=re.IGNORECASE)
    elif 'mort' in text.lower():
        disembark_date_match = re.search(disembark_patterns['mort en mer']['date'], text, flags=re.IGNORECASE)
        disembark_location_match = re.search(disembark_patterns['mort en mer']['location'], text, flags=re.IGNORECASE)
    elif 'passé' in text.lower():
        disembark_date_match = re.search(disembark_patterns['passé']['date'], text, flags=re.IGNORECASE)
        disembark_location_match = re.search(disembark_patterns['passé']['location'], text, flags=re.IGNORECASE)
    elif 'fait la campagne' in text.lower():
        disembark_date_match = re.search(disembark_patterns['a fait la']['date'], text, flags=re.IGNORECASE)
        disembark_location_match = re.search(disembark_patterns['a fait la']['location'], text, flags=re.IGNORECASE)
    elif 'resté' in text.lower():
        disembark_date_match = re.search(disembark_patterns['resté']['date'], text, flags=re.IGNORECASE)
        disembark_location_match = re.search(disembark_patterns['resté']['location'], text, flags=re.IGNORECASE)

    # Extract disembark information
    if disembark_date_match:
        disembark_date = disembark_date_match.group(1)
    if disembark_location_match:
        disembark_location = disembark_location_match.group(1)
        if len(disembark_location_match.groups()) > 1 and disembark_location_match.group(2):
            disembark_location += f", {disembark_location_match.group(2)}"
    if 'mort à bord' in text.lower() or 'morte à bord' in text.lower() or 'morts à bord' in text.lower() or 'mortes à bord' in text.lower():
        disembark_location = 'on board'
    elif 'mort en mer' in text.lower() or 'morte en mer' in text.lower() or 'morts en mer' in text.lower() or 'mortes en mer' in text.lower():
        disembark_location = 'at sea'
    if 'née en mer' in text.lower() or 'né en mer' in text.lower() or 'nées en mer' in text.lower() or 'nés en mer' in text.lower():
        embark_location = 'at sea'
    elif 'née à bord' in text.lower() or 'né à bord' in text.lower() or 'nées à bord' in text.lower() or 'nés à bord' in text.lower():
        embark_location = 'on board'
    
            

    return embark_location, embark_date, disembark_location, disembark_date