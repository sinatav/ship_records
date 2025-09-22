def classify_embark(text):
    if not text: return 309
    t = text.lower()
    if "armement" in t or "embarqué" in t or "fait la campagne" in t: return 301
    if "remplacement" in t or "supplément" in t: return 302
    if "renversement" in t or "vient" in t: return 303
    if "clandestin" in t or "caché" in t: return 304
    if "né" in t: return 305
    if "rembarqué" in t: return 306
    if "resté" in t: return 308
    return 309

def classify_disembark(text, emb_loc=None, disemb_loc=None):
    if not text: return 309
    t = text.lower()
    if emb_loc and disemb_loc and emb_loc == disemb_loc: return 301
    if "passé" in t: return 303
    if "déserté" in t or "fugitif" in t or "échapé" in t: return 304
    if "mort" in t: return 305
    if "malade" in t or "hôpital" in t: return 306
    if "prise" in t: return 307
    if "resté" in t: return 308
    return 302
