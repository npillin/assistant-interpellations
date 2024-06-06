##############################
# Simple password protection #
##############################

import hmac
import streamlit as st


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Mot de passe", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Mot de passe incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.



########################
# Packages and API key #
########################

st.set_page_config(layout="wide")

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

import os
os.environ['OPENAI_API_KEY'] = st.secrets["apikey"]



##############
# Parameters #
##############

# Questions field
quest_label = "Questions posées dans le cadre de l'intervention :"

# Info field
infos_label = "Informations permettant de répondre aux questions :"

# Structure field
structure_default = """
- Contexte
- Réponse aux questions
- Conclusion
"""

# Prompt template
template = """
Vous êtes un assistant IA dont le rôle est de rédiger un document basé sur les informations dans votre contexte.
Le document que vous rédigez est une réponse du Conseil d'Etat.
Vous répondez au Grand Conseil et représentez le Conseil d'Etat.
Dans le document, vous répondez aux questions posées par le Grand Conseil, qui sont listée ci-dessous.
Pour répondre à ces questions, vous vous basez sur les informations fournies ci-dessous.
Vous utilisez un ton formel.
Rédigez un texte de {n_words} mots environ en utilisant la structure fournie.
       
Questions : {questions}

Informations : {infos}

Structure : {structure}
"""



###################
# Langchain setup #
###################

llm = ChatOpenAI(model_name='gpt-4o')

prompt_template = PromptTemplate(
    input_variables=['n_words', 'questions', 'infos', 'structure'],
    template=template
)

prompt_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)

def gen_text(): # Returns the generated text
    draft = prompt_chain.run(n_words=n_words, questions=questions, infos=infos, structure=structure)
    return draft



#################
# App framework #
#################

st.title("Assistant Interventions+")

st.subheader("Questions et informations pertinentes pour y répondre")
questions = st.text_area(label=quest_label, height=300)
infos = st.text_area(label=infos_label, height=300)

st.subheader("Proposition de texte")
with st.expander("Structure (à modifier au besoin...)"):
    structure = st.text_area(label="", value=structure_default, height=150)
n_words = st.slider("Nombre approximatif de mots à générer (une page contient 600 à 700 mots)", 100, 3000, 650)
if st.button("Genérer"):
    text = gen_text()
    st.write(text)
