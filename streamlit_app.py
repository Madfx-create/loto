import streamlit as st
import random
import pandas as pd
import io
from collections import Counter

st.set_page_config(page_title="Swiss Lotto Stratégie", layout="wide")

# CONFIGURATION DE BASE DE LA GRILLE
COLONNES = {
    1: {1, 7, 13, 19, 25, 31, 37},
    2: {2, 8, 14, 20, 26, 32, 38},
    3: {3, 9, 15, 21, 27, 33, 39},
    4: {4, 10, 16, 22, 28, 34, 40},
    5: {5, 11, 17, 23, 29, 35, 41},
    6: {6, 12, 18, 24, 30, 36, 42}
}

LIGNES = {
    1: set(range(1, 7)),
    2: set(range(7, 13)),
    3: set(range(13, 19)),
    4: set(range(19, 25)),
    5: set(range(25, 31)),
    6: set(range(31, 37)),
    7: set(range(37, 43))
}

CENTRE = {8, 9, 10, 11, 14, 15, 16, 17, 20, 21, 22, 23, 26, 27, 28, 29, 32, 33, 34, 35}
POURTOUR = set(range(1, 43)) - CENTRE

DIAGONALES = [
    {1, 8, 15, 22, 29, 36}, {2, 9, 16, 23, 30, 37}, {3, 10, 17, 24, 31, 38},
    {4, 11, 18, 25, 32, 39}, {5, 12, 19, 26, 33, 40}, {6, 13, 20, 27, 34, 41},
    {6, 11, 16, 21, 26, 31}, {12, 17, 22, 27, 32, 37}
]

# SOCLE FIXE EXTRAIT DU PDF
SOCLE_16_BASES = [2, 5, 9, 12, 14, 17, 20, 23, 26, 28, 31, 34, 35, 38, 39, 41]

def valide_criteres_grille(grille):
    cols_occupees = [sum(1 for n in grille if n in COLONNES[c]) for c in COLONNES]
    cols_actives = [count for count in cols_occupees if count > 0]
    if len(cols_actives) != 4 or cols_actives.count(2) != 2:
        return False
        
    pairs = sum(1 for n in grille if n % 2 == 0)
    if pairs not in:
        return False

    lignes_occupees = sum(1 for l in LIGNES if any(n in LIGNES[l] for n in grille))
    if lignes_occupees not in:
        return False

    nb_centre = sum(1 for n in grille if n in CENTRE)
    nb_pourtour = sum(1 for n in grille if n in POURTOUR)
    if not (2 <= nb_centre <= 3 and 3 <= nb_pourtour <= 4):
        return False

    gauche = sum(1 for n in grille if any(n in COLONNES[c] for c in [1, 2, 3]))
    droite = 6 - gauche
    if not (2 <= gauche <= 4 and 2 <= droite <= 4):
        return False

    terminales = [n % 10 for n in grille]
    if max(Counter(terminales).values()) < 2:
        return False

    grille_triee = sorted(list(grille))
    paires_consecutives = 0
    for i in range(len(grille_triee) - 1):
        if grille_triee[i+1] - grille_triee[i] == 1:
            paires_consecutives += 1
    for i in range(len(grille_triee) - 2):
        if grille_triee[i+2] - grille_triee[i+1] == 1 and grille_triee[i+1] - grille_triee[i] == 1:
            return False
    if paires_consecutives > 1:
        return False

    basse = sum(1 for n in grille if 1 <= n <= 21)
    haute = 6 - basse
    if not (2 <= basse <= 4 and 2 <= haute <= 4):
        return False

    for diag in DIAGONALES:
        if sum(1 for n in grille if n in diag) > 3:
            return False

    if not (117 <= sum(grille) <= 153):
        return False

    somme_chiffres = sum(sum(int(digit) for digit in str(n)) for n in grille)
    if not (28 <= somme_chiffres <= 45):
        return False

    return True

st.title("🎰 Système Stratégique Swiss Loto")
st.subheader("Générateur indépendant (Anti-Oubli)")

st.sidebar.header("🔥 Vos critères de la semaine")
chauds_input = st.sidebar.text_input("Numéros Chauds (séparés par des virgules)", "8, 5, 24, 9, 17")
froids_input = st.sidebar.text_input("Numéros Froids (séparés par des virgules)", "31, 33, 38, 42, 15")

try:
    NUMEROS_CHAUDS = [int(x.strip()) for x in chauds_input.split(",") if x.strip().isdigit()]
    NUMEROS_FROIDS = [int(x.strip()) for x in froids_input.split(",") if x.strip().isdigit()]
except:
    st.sidebar.error("Veuillez vérifier le format des numéros.")

if st.button("🚀 Générer un lot de 8 grilles parfaites"):
    pool_bases = SOCLE_16_BASES * 2
    random.shuffle(pool_bases)
    lot = []
    idx_base = 0
    
    for g_idx in range(8):
        grille_valide = False
        for _ in range(5000):
            chauds_dispo = [n for n in NUMEROS_CHAUDS if n not in pool_bases[idx_base:idx_base+4]]
            froids_dispo = [n for n in NUMEROS_FROIDS if n not in pool_bases[idx_base:idx_base+4] and n not in chauds_dispo]
            if not chauds_dispo or not froids_dispo:
                break
            num_chaud = random.choice(chauds_dispo)
            num_froid = random.choice(froids_dispo)
            bases_grille = pool_bases[idx_base:idx_base+4]
            candidat_grille = set(bases_grille + [num_chaud, num_froid])
            if len(candidat_grille) == 6 and valide_criteres_grille(candidat_grille):
                conflit = any(len(candidat_grille.intersection(set(g))) > 3 for g in lot)
                if not conflit:
                    lot.append(sorted(list(candidat_grille)))
                    idx_base += 4
                    grille_valide = True
                    break
        if not grille_valide:
            break

    if len(lot) == 8:
        st.success("✅ Lot de 8 grilles généré avec succès en respectant 100% de vos critères !")
        df = pd.DataFrame(lot, columns=[f"Num {i}" for i in range(1, 7)])
        df.index = [f"Grille {i}" for i in range(1, 9)]
        st.table(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Grilles')
        st.download_button(label="📥 Télécharger le fichier Excel", data=output.getvalue(), file_name="grilles_swiss_loto.xlsx", mime="application/vnd.ms-excel")
    else:
        st.error("❌ Les contraintes géographiques sont très strictes. Modifiez un peu vos numéros chauds/froids ou réessayez en cliquant à nouveau sur le bouton.")
