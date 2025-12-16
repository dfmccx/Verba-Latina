import streamlit as st
import requests
import random

# Your Grok API key (enter in sidebar)
API_KEY = st.sidebar.text_input("Grok API Key", type="password")
API_URL = "https://api.x.ai/v1/chat/completions"

# Exact prompt template – locked to our finalized format
PROMPT_TEMPLATE = """
Generate a high-quality Latin dictionary entry for the query: "{query}"

Determine if the query is Latin (any form) or English and set direction accordingly (Latin → English or English → Latin).

Follow this EXACT structure and style. Do not deviate.

### Primary Translations ({direction})
[Appropriate primary translations with bold Latin words, parenthetical explanations, principal parts for verbs or genitive for nouns, and stems at the end of each line]

Then numbered sections for each major word:

#### [Lemma] ([Part of Speech] – [English])
- **Part of Speech**: [e.g., Verb (1st conjugation) or Noun (3rd declension)]
- **Gender**: Masculine/Feminine/Neuter (only for nouns/adjectives; omit for verbs)
- **Stem**: [exact stem(s)]
- **Pronunciation (Classical)**: [lemma] /[IPA]/ ([notes])
- **Frequency**: [brief note, e.g., Very high – common in poetry]
- **Definition**: [detailed definition with notes]

[Conjugation or declension tables – always 3 columns: Person/Case (bold), Form, English Example. Split verb tenses into separate tables, noun singular/plural into separate tables – no side-scrolling]

- **Infinitive**: [if verb]
- **Imperative**: [if verb]
- **Gerundive**: [if relevant, e.g., for names like Amanda]
- **Etymology**: [detailed]
- **Common English Derivatives**: [comma-separated list]
- **Related Words/Concepts**: [bold Latin words with translations]
- **Classical Examples**: 
  - [Author, Work reference]: "[Latin quote]" ("[English translation]").
  - Exactly 3 examples with accurate citations and literal translations.

Use macrons correctly. Be accurate, professional, and comprehensive. Include multiple senses/words if needed for English queries.
"""

# Word of the Day options
wotd_options = [
    "amo", "bellum", "puella", "rex", "felix", "domus", "gladius", "iustitia", "love", "war", 
    "justice", "sword", "girl", "king", "house", "friend", "god", "road", "be"
]

st.title("📖 Ultima Latin Dictionary")
st.markdown("**The ultimate bidirectional Latin resource—AI-powered with Grok.** Type naturally (no macrons/case needed). Full details inside the app!")

query = st.text_input("Enter Latin (any form) or English word/phrase:", placeholder="e.g., amavi, gladium, love, justice")

def generate_entry(user_query):
    if not API_KEY:
        return "⚠️ Please enter your Grok API key in the sidebar to generate entries."
    
    # Rough direction detection – AI will handle accurately
    is_latin = any(c in "āēīōūȳĀĒĪŌŪȲ" for c in user_query) or user_query.lower() in [w.lower() for w in wotd_options if w.isalpha()]
    direction = "Latin → English" if is_latin else "English → Latin"
    
    prompt = PROMPT_TEMPLATE.format(query=user_query, direction=direction)
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are an expert Latin scholar generating precise, structured dictionary entries. Follow the format exactly."},
            {"role": "user", "content": prompt}
        ],
        "model": "grok-4-1-fast-reasoning",  # Grok 4.1 Thinking Mode – best for structured output
        "temperature": 0.1,  # Very low for maximum consistency with our format
        "max_tokens": 4096
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        with st.spinner("Generating entry with Grok 4.1..."):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)} – Check API key, internet, or try again."

if query:
    entry = generate_entry(query)
    st.markdown(entry)
else:
    wotd = random.choice(wotd_options)
    st.header(f"🌟 Word of the Day: **{wotd.capitalize()}**")
    entry = generate_entry(wotd)
    st.markdown(entry)

st.caption("❤️ Powered by Grok API (grok-4-1-fast-reasoning). Entries follow our custom high-quality format. Costs pennies per query!")