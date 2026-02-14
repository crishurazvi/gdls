import streamlit as st
import re

def split_sections(text):
    # Regex pentru a detecta titluri de secțiuni (ex: 1. Introduction, 2.1. Diagnosis)
    # Caută un număr la început de rând urmat de punct și spațiu
    pattern = r'\n(?=\d+\.\s|\d+\.\d+\s|\d+\.\d+\.\d+\s)'
    sections = re.split(pattern, text)
    return [s.strip() for s in sections if s.strip()]

def main():
    st.set_page_config(page_title="ESC 2025 to Obsidian Prompt", layout="wide")
    
    st.title("🫀 ESC Guideline Splitter pentru Obsidian")
    st.markdown("""
    Această aplicație împarte ghidul în secțiuni și pregătește prompturile pentru AI. 
    Lipește textul ghidului și bibliografia mai jos.
    """)

    col1, col2 = st.columns(2)

    with col1:
        guide_text = st.text_area("1. Lipește textul Ghidului ESC aici:", height=400, placeholder="Ex: 2.1 Definition of hypertension...")
    
    with col2:
        biblio_text = st.text_area("2. Lipește lista de Referințe (Bibliografia) aici:", height=400, placeholder="Ex: [27] Williams B, et al. ESC Guidelines 2018...")

    if st.button("Procesează Ghidul"):
        if not guide_text:
            st.error("Te rog să introduci textul ghidului.")
            return

        sections = split_sections(guide_text)
        
        st.success(f"Am identificat {len(sections)} secțiuni.")
        
        st.divider()

        for i, section in enumerate(sections):
            # Extragere titlu (prima linie) pentru afișare în expander
            first_line = section.split('\n')[0][:100]
            
            with st.expander(f"Secțiunea {i+1}: {first_line}"):
                
                # Construcția promptului final
                full_prompt = f"""Acționează ca un expert cardiolog și utilizator avansat de Obsidian. Analizează textul următor din Ghidul ESC 2025 (IMPS) și creează o pagină Obsidian formatată astfel:
YAML Header: Include id (format ESC-IMPS-X.X-Nume), type: guideline-section, guideline: ESC IMPS 2025, domain, section, tags, și linked_paragraphs.
Structură:
Folosește un callout > [!abstract] Overview pentru un rezumat scurt.
Tradu in romana textul cu si insereaza referintele (care sa fie mentionate la finalul paginii)
Folosește subtitluri clare (H2, H3).
Foloseste stilizare si emoji pentru a scoate in evidenta lucrurile importante
Linking Logic: Oriunde apare o referință numerică în text (ex: [27]), înlocuiește-o cu un link de tipul [[ESC-IMPS-AUTHOR-YEAR]]. Identifică autorul și anul din bibliografia pe care o voi furniza sau din context.
Limba: Traduce explicațiile în limba română, păstrând termenii medicali consacrați.

Iată textul secțiunii:
{section}

Iată lista de referințe pentru a genera linkurile corect:
{biblio_text if biblio_text else "Nu a fost furnizată bibliografie."}"""

                # Buton de copy-paste
                st.code(full_prompt, language="markdown")
                st.button(f"Copiază Prompt Secțiunea {i+1}", on_click=None, key=f"btn_{i}")

if __name__ == "__main__":
    main()
