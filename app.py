import streamlit as st
import re

def parse_bibliography(bib_text):
    """Transformă lista lungă de bibliografie într-un dicționar { '1': 'Text referință...' }"""
    bib_dict = {}
    # Caută linii care încep cu un număr urmat de tab sau spațiu
    lines = bib_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Match pentru formatul: "1\tAdler Y..." sau "1 Adler Y..."
        match = re.match(r'^(\d+)\s+(.*)', line)
        if match:
            num, content = match.groups()
            bib_dict[num] = content
    return bib_dict

def extract_referenced_numbers(section_text):
    """Identifică toate numerele de referință dintr-un text (ex: [1], [2, 3], [10-12])"""
    # Găsește numere în paranteze pătrate [12] sau [1, 2, 45] sau [12-15]
    found_numbers = set()
    
    # Pattern pentru numere în paranteze [ ]
    bracket_matches = re.findall(r'\[([\d\s,\-]+)\]', section_text)
    for match in bracket_matches:
        # Split după virgulă sau liniuță
        parts = re.split(r'[,\-]', match)
        for part in parts:
            part = part.strip()
            if part.isdigit():
                found_numbers.add(part)
                
    # Opțional: Căutăm și numere simple care ar putea fi referințe (dacă nu sunt în paranteze)
    # Dar limităm căutarea la numerele care apar des ca referințe pentru a evita confuzia cu datele clinice
    # De obicei ESC folosește paranteze pătrate.
    
    return found_numbers

def split_sections(text):
    """Împarte ghidul pe secțiuni bazat pe numerotare (ex: 1. , 1.1. , etc)"""
    pattern = r'\n(?=\d+\.\s|\d+\.\d+\s|\d+\.\d+\.\d+\s)'
    sections = re.split(pattern, text)
    return [s.strip() for s in sections if s.strip()]

def main():
    st.set_page_config(page_title="ESC 2025 Obsidian Pro", layout="wide")
    
    st.title("🫀 ESC 2025 Smart Splitter & Bib-Filter")
    st.markdown("Împarte ghidul în paragrafe și extrage automat **doar bibliografia relevantă** pentru fiecare secțiune.")

    col1, col2 = st.columns(2)
    with col1:
        guide_text = st.text_area("1. Textul Ghidului ESC:", height=300)
    with col2:
        biblio_input = st.text_area("2. Lista completă de Referințe (toate cele 676):", height=300)

    if st.button("Generează Prompt-uri"):
        if not guide_text or not biblio_input:
            st.error("Te rog completează ambele câmpuri.")
            return

        # Pas 1: Procesăm bibliografia totală
        full_bib_dict = parse_bibliography(biblio_input)
        
        # Pas 2: Împărțim ghidul pe secțiuni
        sections = split_sections(guide_text)
        
        st.success(f"Ghid împărțit în {len(sections)} secțiuni. Bibliografie procesată: {len(full_bib_dict)} intrări.")

        for i, section in enumerate(sections):
            # Pas 3: Identificăm ce numere de referință sunt în această secțiune
            ref_numbers = extract_referenced_numbers(section)
            
            # Pas 4: Filtrăm bibliografia doar pentru aceste numere
            relevant_bib = []
            # Sortăm numerele pentru ordine în afișare
            for num in sorted(list(ref_numbers), key=int):
                if num in full_bib_dict:
                    relevant_bib.append(f"{num} {full_bib_dict[num]}")
            
            bib_text_for_prompt = "\n".join(relevant_bib) if relevant_bib else "Nu s-au identificat referințe specifice în acest paragraf."

            # Prima linie a secțiunii pentru titlu
            first_line = section.split('\n')[0][:80]

            with st.expander(f"Secțiunea {i+1}: {first_line}"):
                final_prompt = f"""Acționează ca un expert cardiolog și utilizator avansat de Obsidian. Analizează textul următor din Ghidul ESC 2025 (IMPS) și creează o pagină Obsidian formatată astfel:
YAML Header: Include id (format ESC-IMPS-X.X-Nume), type: guideline-section, guideline: ESC IMPS 2025, domain, section, tags, și linked_paragraphs.
Structură:
Folosește un callout > [!abstract] Overview pentru un rezumat scurt.
Tradu in romana textul cu si insereaza referintele (care sa fie mentionate la finalul paginii)
Folosește subtitluri clare (H2, H3).
Foloseste stilizare si emoji pentru a scoate in evidenta lucrurile importante
Linking Logic: Oriunde apare o referință numerică în text (ex: [27]), înlocuiește-o cu un link de tipul [[ESC-IMPS-AUTHOR-YEAR]]. Identifică autorul și anul din bibliografia pe care o voi furniza sau din context.
Limba: Traduce explicațiile în limba română, păstrând termenii medicali consacrați.

Iată textul secțiunii:
[START TEXT SECȚIUNE]
{section}
[END TEXT SECȚIUNE]

Iată lista de referințe RELEVANTE pentru această secțiune pentru a genera linkurile corect:
[START BIBLIOGRAFIE]
{bib_text_for_prompt}
[END BIBLIOGRAFIE]"""

                st.code(final_prompt, language="markdown")
                st.button(f"Copiază Prompt {i+1}", key=f"copy_{i}")

if __name__ == "__main__":
    main()
