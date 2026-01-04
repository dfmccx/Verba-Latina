import streamlit as st
import requests
import random
import os

# Load from secret if available, fallback to sidebar
API_KEY = os.getenv("GROK_API_KEY")
if not API_KEY:
    st.warning("Secret 'GROK_API_KEY' not found—entering in sidebar (secure for this session). Add to Secrets for permanent no-entry.")
    API_KEY = st.sidebar.text_input("Grok API Key", type="password")
    if not API_KEY:
        st.error("Enter your Grok API key in sidebar to generate entries.")
        st.stop()

API_URL = "https://api.x.ai/v1/chat/completions"

# Updated prompt – Definition first after header, extra spacing
PROMPT_TEMPLATE = """
Generate a high-quality Latin dictionary entry for the query: "{query}"

Determine if the query is Latin (any form) or English and set direction accordingly (Latin → English or English → Latin).

Follow this EXACT structure and style. Do not deviate.

Start directly with the main lemma or phrase as the top header (bold with macrons if applicable):

#### **main lemma or phrase**

Then:

**Definition**: [detailed definition with notes]

**Part of Speech**: [e.g., Verb (1st conjugation) or Noun (3rd declension)]

**Gender**: Masculine/Feminine/Neuter (only for nouns/adjectives; omit for verbs)

**Stem**: [exact stem(s)]

**Pronunciation (Classical)**: [lemma] /[IPA with ˈ for primary stress only, macrons for long vowels, breve ˘ for short vowels in IPA only]/ ([notes]) – use macrons for long vowels elsewhere, NO breve symbols outside IPA

**Frequency**: [brief note, e.g., Very high – common in poetry]

[Conjugation or declension tables – always 3 columns: Person/Case (bold), Form, English Example. Use STRICTLY LITERAL English examples, e.g., 'peace (subject)' for nominative, 'of peace' for genitive, 'to/for peace' for dative – no contextual sentences. Split verb tenses into separate tables with **Tense Name** as bold heading, noun singular/plural into separate tables with **Singular Declension** and **Plural Declension** as bold headings – no side-scrolling. For nouns, ALWAYS order cases exactly: Nominative, Vocative, Accusative, Genitive, Dative, Ablative]

**Infinitive**: [if verb]

**Imperative**: [if verb]

**Gerundive**: [if relevant, e.g., for names like Amanda]

**Etymology**: [detailed]

**Common English Derivatives**: [list]

**Related Words/Concepts**: [bold Latin words with translations]

**Classical Examples**: 
  - [Author, Work reference]: "[Latin quote]" ("[English translation]").
  - Exactly 3 examples with accurate citations and literal translations.

Add an extra newline after each bold section for clarity and spacing. Use macrons correctly. Be accurate, professional, and comprehensive. Include multiple senses/words if needed for English queries. For phrases, treat the phrase as the main lemma and provide explanation, origin, and examples.
"""

# Only Latin words and phrases for random entry
wotd_options = [
    "amo", "bellum", "puella", "rex", "felix", "domus", "gladius", "iustitia", 
    "amicus", "deus", "via", "sum", "fero", "audio", "scribo", "lego", "imperator", 
    "res publica", "carpe diem", "veni vidi vici", "alea iacta est", "memento mori", 
    "et tu brute", "senatus populusque romanus", "fortuna", "aeternus", "virtus", 
    "pax", "libertas"
]

st.set_page_config(page_title="Verba Latina", layout="centered")

# Serif font CSS + aesthetic improvements
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Times New Roman', Times, serif !important;
        line-height: 1.8 !important;
    }
    h1 {
        font-size: 3em !important;
        font-weight: bold !important;
        text-align: center !important;
        margin-bottom: 0.2em !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2) !important;
    }
    .subtitle {
        font-size: 1.5em !important;
        font-style: italic !important;
        text-align: center !important;
        color: #666666 !important;
        margin-bottom: 1.5em !important;
    }
    table {
        border-collapse: collapse !important;
        width: 100% !important;
        margin: 1em 0 !important;
    }
    th, td {
        border: 1px solid #ddd !important;
        padding: 12px !important;
        text-align: left !important;
    }
    th {
        background-color: #e0e0e0 !important;
        color: #000 !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# Persistent theme using localStorage
st.markdown("""
<script>
    const getTheme = () => localStorage.getItem("verba_latina_theme") || "Light";
    const setTheme = (theme) => localStorage.setItem("verba_latina_theme", theme);

    // Load saved theme on start
    const savedTheme = getTheme();
    if (savedTheme === "Dark") {
        document.body.classList.add("dark-mode");
    }

    // Save theme on change (Streamlit will rerun on selectbox change)
</script>
""", unsafe_allow_html=True)

# Theme selector – default to saved or Light
default_mode = "Light"
# To get the saved theme, we use a placeholder (Streamlit can't read JS directly, but we can default to Light and save on change)
mode = st.sidebar.selectbox("Theme", ["Light", "Dark"], index=0 if default_mode == "Light" else 1)

# Save theme on change
st.markdown(f"""
<script>
    setTheme("{mode}");
</script>
""", unsafe_allow_html=True)

# Apply theme styles
if mode == "Dark":
    st.markdown("""
    <style>
        .stApp {background-color: #0e1117 !important; color: #fafafa !important;}
        .css-1v0mbdj {background-color: #262730 !important;}
        .stTextInput > div > div > input {background-color: #333 !important; color: #fff !important;}
        .stButton > button {background-color: #444 !important; color: #fff !important;}
        th {background-color: #444 !important; color: #fff !important;}
        td {border-color: #555 !important;}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp {background-color: #ffffff !important; color: #000000 !important;}
        .css-1v0mbdj {background-color: #f0f2f6 !important;}
        .stTextInput > div > div > input {background-color: #fff !important; color: #000 !important;}
        .stButton > button {background-color: #f0f0f0 !important; color: #000 !important;}
        th {background-color: #e0e0e0 !important; color: #000 !important;}
    </style>
    """, unsafe_allow_html=True)

# Title and subtitle
st.markdown("<h1>Verba Latina</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>The Ultimate English-Latin Dictionary</p>", unsafe_allow_html=True)
st.markdown("A comprehensive bidirectional resource for Latin and English. Entries are generated dynamically with precise morphological, etymological, and classical detail.")

# Pages list
pages = ["Home", "About Latin", "History of Latin", "Pronunciation Guide", "Declensions Overview", "Conjugations Overview", "Common Phrases"]

# Initialize session state for page
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Sidebar navigation
st.sidebar.header("Menu")
index = pages.index(st.session_state.page)
page = st.sidebar.radio("Navigation", pages, index=index)

# Update page if changed
if page != st.session_state.page:
    st.session_state.page = page
    st.rerun()

current_page = st.session_state.page

# Cache generation for performance
@st.cache_data(ttl=3600)
def generate_entry_cached(user_query):
    prompt = PROMPT_TEMPLATE.format(query=user_query)

    payload = {
        "messages": [
            {"role": "system", "content": "You are an expert Latin scholar generating precise, structured dictionary entries. Prioritize factual accuracy from classical sources (Lewis & Short, Allen & Greenough). Follow the format exactly."},
            {"role": "user", "content": prompt}
        ],
        "model": "grok-4-1-fast-reasoning",
        "temperature": 0.0,
        "max_tokens": 4096
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"], None
    except Exception as e:
        return None, f"Error: {str(e)} – Check key or internet connection."

def display_entry(user_query):
    entry, error = generate_entry_cached(user_query)

    if error:
        st.error(error)
        if st.button("Retry"):
            st.rerun()
        return

    st.markdown(entry)

if current_page == "Home":
    query = st.text_input("Enter Latin (any form) or English word/phrase:", placeholder="e.g., amavi, gladium, love, justice")

    if query:
        with st.spinner("⏳ *Patientia virtus est...*"):
            display_entry(query)
    else:
        wotd = random.choice(wotd_options)
        st.markdown("<h3><em>Entrata Aleatoria</em></h3>", unsafe_allow_html=True)
        with st.spinner("⏳ *Patientia virtus est...*"):
            display_entry(wotd)

else:
    # Back to Home at top
    if st.button("Back to Home", key="back_top"):
        st.session_state.page = "Home"
        st.rerun()

    if current_page == "About Latin":
        st.title("About Latin")
        st.markdown("""
Latin is the language of ancient Rome, but its influence extends far beyond the fall of the Empire. Often called the "mother tongue" of the Romance languages (Italian, French, Spanish, Portuguese, Romanian), it shaped much of European vocabulary, law, science, and philosophy.

Why learn Latin today? It sharpens analytical thinking—deciphering complex grammar trains the mind like few other pursuits. It unlocks direct access to foundational texts: Cicero's orations, Virgil's poetry, Augustine's confessions, or medieval philosophy. Scientific and medical terminology is rooted in Latin (e.g., *homo sapiens*, *cardiovascular*). Even English derives about 60% of its vocabulary from Latin (directly or via French).

Latin is not "dead"—it lives in liturgy, mottoes, legal phrases, and academic traditions. Learning it connects you to two millennia of human thought, from the Republic to the Renaissance.

Whether you're reading Caesar's war commentaries or inscriptions on ancient coins, Latin rewards curiosity with depth and beauty.
""")

    elif current_page == "History of Latin":
        st.title("History of Latin")
        st.markdown("""
Latin originated in the region around Rome (Latium) in the 8th–7th century BCE, as part of the Italic branch of Indo-European languages. Early inscriptions (like the Praenestine fibula, c. 600 BCE) show its archaic form.

Classical Latin (1st century BCE–1st century CE) was refined by writers like Cicero and Virgil during the Golden Age. This is the Latin taught today—elegant, structured, and literary.

After Rome's fall (476 CE), Latin evolved into the Romance languages in everyday speech, but remained the lingua franca of educated Europe. Medieval Latin (used in churches, universities, and science) was more flexible. Renaissance humanists revived Classical style.

From the 17th–19th centuries, Latin was the language of scholarship (Newton wrote in Latin). It persists in the Catholic Church, law ("habeas corpus"), and taxonomy.

Today, Latin is experiencing a revival—spoken fluently by enthusiasts, taught in schools, and used in new compositions. It is a bridge to the past and a key to understanding Western civilization.
""")

    elif current_page == "Pronunciation Guide":
        st.title("Pronunciation Guide")
        st.markdown("""
The Classical pronunciation (restored from ancient evidence) is standard in academic settings. It differs from Ecclesiastical (Church) Latin, which is more Italian-like.

**Vowels**  
Short vowels are crisp: a as in "cat", e as in "bet", i as in "bit", o as in "cot", u as in "put".  
Long vowels (marked with macrons) are held longer: ā as in "father", ē as in "they", ī as in "machine", ō as in "go", ū as in "rule".

**Diphthongs**  
ae as "eye", oe as "oy" in "boy", au as "ow" in "house".

**Consonants**  
c and g always hard (k, g)—no "ch" or "j" sounds.  
v = "w" (vinum = "wee-noom").  
i between vowels = "y" (maior = "my-or").  
r is trilled. s is always "s" (never "z").

**Stress**  
Penultimate syllable if long; otherwise antepenultimate. Example: amīcus (a-MEE-kus).

Practice with phrases: "Veni, vidi, vici" (WAY-nee, WEE-dee, WEE-kee).
""")

    elif current_page == "Declensions Overview":
        st.title("Declensions Overview")
        st.markdown("""
Latin nouns are grouped into five declensions based on stem endings. Gender is fixed (masculine, feminine, neuter).

**1st Declension** (mostly feminine, -a stem): puella, puellae ("girl").  
**2nd Declension** (masculine/neuter, -o stem): dominus, dominī ("lord"); bellum, bellī ("war").  
**3rd Declension** (all genders, consonant/i-stem): pax, pacis ("peace", feminine); rex, rēgis ("king", masculine); corpus, corporis ("body", neuter).  
**4th Declension** (masculine/neuter, -u stem): manus, manūs ("hand", feminine); cornu, cornūs ("horn", neuter).  
**5th Declension** (mostly feminine, -e stem): rēs, reī ("thing"); diēs, diēī ("day", masculine in some uses).

Gender is learned with the noun—it's fixed. Some nouns are irregular (e.g., domus mixes 4th and 2nd).

**The Six Cases and Their Functions**  
Latin uses cases to show a noun's role in the sentence (replacing word order/prepositions in English). Here are the main uses, with examples from **puella** ("girl"):

- **Nominative**: Subject of the verb ("who/what does the action").  
  Puella currit. ("The girl runs.")

- **Vocative**: Direct address ("O [noun]!").  
  Puella, venī! ("Girl, come!")

- **Accusative**: Direct object ("what receives the action") or motion toward (with some prepositions).  
  Puellam videō. ("I see the girl.")

- **Genitive**: Possession ("of [noun]") or partitive ("some of").  
  Liber puellae. ("The book of the girl" / "The girl's book.")

- **Dative**: Indirect object ("to/for [noun]") or benefit/possession.  
  Puellae librum dō. ("I give the book to the girl.")

- **Ablative**: Means/instrument ("by/with/from [noun]"), separation, or accompaniment (often with prepositions).  
  Cum puellā ambulō. ("I walk with the girl.")

Cases allow flexible word order—meaning comes from endings, not position. Mastering them unlocks Latin's precision and beauty.
""")

    elif current_page == "Conjugations Overview":
        st.title("Conjugations Overview")
        st.markdown("""
Verbs change form (conjugate) for person, number, tense, mood, and voice. There are four regular conjugations, identified by infinitive ending.

**1st Conjugation** (-āre): amāre ("to love") – long ā throughout.

**2nd Conjugation** (-ēre, stress on stem): vidēre ("to see") – long ē in stem.

**3rd Conjugation** (-ere, short e): legere ("to read") – variable stem vowels.

**4th Conjugation** (-īre): audīre ("to hear") – long ī before -re.

Irregular verbs include sum (to be), ferō (to carry), eō (to go), volō (to want).

Principal parts (four forms) provide stems for all tenses: e.g., amō, amāre, amāvī, amātum.

Tenses express time (present, past, future) and aspect (completed vs. ongoing). Moods include indicative (statements), subjunctive (possibility, wish), imperative (commands).

Mastering conjugations unlocks Latin's precision and elegance in expression.
""")

    elif current_page == "Common Phrases":
        st.title("Common Phrases")
        st.markdown("""
Latin phrases endure in English and modern culture. Here are some classics with context:

- *Carpe diem* (Horace): "Seize the day" – embrace the present.

- *Veni, vidi, vici* (Julius Caesar): "I came, I saw, I conquered" – report of swift victory.

- *Alea iacta est* (Caesar): "The die is cast" – an irreversible decision.

- *Memento mori*: "Remember that you must die" – stoic reminder of mortality.

- *Et tu, Brute?* (Shakespeare/Caesar): "And you, Brutus?" – betrayal by a friend.

- *Senātus Populusque Rōmānus* (SPQR): "The Senate and People of Rome" – symbol of the Republic.

- *In vīnō vēritās*: "In wine, there is truth" – alcohol loosens tongues.

- *Cogitō, ergō sum* (Descartes): "I think, therefore I am" – foundation of philosophy.

These expressions capture Roman wit, philosophy, and drama.
""")

    # Back to Home at bottom
    if st.button("Back to Home", key="back_bottom"):
        st.session_state.page = "Home"
        st.rerun()