import streamlit as st
import re

def parse_bibliography(bib_text):
    """Transformă lista de bibliografie într-un dicționar { '1': 'Text...' }"""
    bib_dict = {}
    # Curățăm textul și căutăm linii care încep cu un număr
    lines = bib_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Match pentru: "1 Adler Y..." sau "1\tAdler Y..."
        match = re.match(r'^(\d+)\s+(.*)', line)
        if match:
            num, content = match.groups()
            bib_dict[num] = content
    return bib_dict

def extract_referenced_numbers(section_text, bib_keys):
    """
    Identifică numerele de referință prin 3 metode:
    1. Paranteze [1] sau (1)
    2. Numere lipite de cuvinte (ex: myocarditis27)
    3. Numere de sine stătătoare care există în bibliografie
    """
    found_numbers = set()
    
    # Metoda 1: Paranteze pătrate sau rotunde [1, 2-5] sau (1, 2)
    bracket_matches = re.findall(r'[\(\[]([\d\s,\-]+)[\)\]]', section_text)
    for match in bracket_matches:
        # Gestionăm intervale de tip 10-12
        if '-' in match:
            parts = re.findall(r'\d+', match)
            if len(parts) >= 2:
                try:
                    start, end = int(parts[0]), int(parts[-1])
                    for n in range(start, end + 1):
                        if str(n) in bib_keys: found_numbers.add(str(n))
                except: pass
        # Gestionăm liste de tip 1, 2, 3
        nums = re.findall(r'\d+', match)
        for n in nums:
            if n in bib_keys: found_numbers.add(n)

    # Metoda 2: Numere lipite de litere (frecvent la copy-paste din PDF, ex: "disease27")
    attached_matches = re.findall(r'[a-zA-Z](\d+)', section_text)
    for n in attached_matches:
        if n in bib_keys:
            found_numbers.add(n)

    # Metoda 3: Orice număr de sine stătător care se potrivește cu o cheie din bib
    # (Excludem anii probabili 2020-2025 pentru a evita alarmele false, dacă nu sunt referințe)
    standalone_nums = re.findall(r'\b\d{1,3}\b', section_text)
    for n in standalone_nums:
        if n in bib_keys:
            found_numbers.add(n)
            
    return found_numbers

def split_sections(text):
    # Split pe titluri de tip 1. , 1.1 , 2.1.1
    pattern = r'\n(?=\d+\.\s|\d+\.\d+\s|\d+\.\d+\.\d+\s)'
    sections = re.split(pattern, text)
    return [s.strip() for s in sections if s.strip()]

def main():
    st.set_page_config(page_title="ESC 2025 Fixer", layout="wide")
    st.title("🫀 ESC 2025: Referințe Fix")
    
    col1, col2 = st.columns(2)
    with col1:
        guide_text = st.text_area("1. Textul Ghidului:", height=300)
    with col2:
        biblio_input = st.text_area("2. Bibliografia (Toată lista):", height=300)

    if st.button("Procesează"):
        if not guide_text or not biblio_input:
            st.warning("Te rog introdu datele.")
            return

        bib_dict = parse_bibliography(biblio_input)
        sections = split_sections(guide_text)
        
        st.info(f"Am găsit {len(sections)} secțiuni și {len(bib_dict)} referințe în bibliografie.")

        for i, section in enumerate(sections):
            # Extracție numere folosind cheile de bibliografie existente
            ref_numbers = extract_referenced_numbers(section, bib_dict.keys())
            
            # Construim lista de referințe pentru acest paragraf
            current_bib_list = []
            for n in sorted(list(ref_numbers), key=int):
                current_bib_list.append(f"[{n}] {bib_dict[n]}")
            
            bib_output = "\n".join(current_bib_list) if current_bib_list else "Nu s-au găsit referințe în acest text."

            with st.expander(f"Paragraful {i+1}: {section[:100]}..."):
                prompt = f"""Acționează ca un expert cardiolog și utilizator avansat de Obsidian. Analizează textul următor din Ghidul ESC 2025 (IMPS) și creează o pagină Obsidian formatată astfel:
YAML Header: Include id (format ESC-IMPS-X.X-Nume), type: guideline-section, guideline: ESC IMPS 2025, domain, section, tags, și linked_paragraphs.
Structură:
Folosește un callout > [!abstract] Overview pentru un rezumat scurt.
Tradu in romana textul cu si insereaza referintele (care sa fie mentionate la finalul paginii)
Folosește subtitluri clare (H2, H3).
Foloseste stilizare si emoji pentru a scoate in evidenta lucrurile importante
Linking Logic: Oriunde apare o referință numerică în text (ex: [27]), înlocuiește-o cu un link de tipul [[ESC-IMPS-AUTHOR-YEAR]]. Identifică autorul și anul din bibliografia furnizată.
Limba: Traduce explicațiile în limba română, păstrând termenii medicali consacrați.

---
TEXTUL SECȚIUNII:
{section}

---
LISTA DE REFERINȚE RELEVANTE:
{bib_output}
"""
                st.code(prompt, language="markdown")

if __name__ == "__main__":
    main()
