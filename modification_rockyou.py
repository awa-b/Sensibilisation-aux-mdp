import hashlib
import math
import time

# --- 1. ANALYSE THÉORIQUE ---
def affichage(mot_de_passe):
    longueur = len(mot_de_passe)
    
    if longueur == 0:
        return {
            "longueur": 0, "minuscule": False, "majuscule": False, 
            "chiffre": False, "car_special": False, "entropie": 0, 
            "temps_CPU": 0, "temps_GPU": 0
        }

    minuscule = any(c.islower() for c in mot_de_passe)
    majuscule = any(c.isupper() for c in mot_de_passe)
    chiffre = any(c.isdigit() for c in mot_de_passe)
    car_special = any(not c.isalnum() for c in mot_de_passe)

    taille_alphabet = 0
    if minuscule: taille_alphabet += 26
    if majuscule: taille_alphabet += 26
    if chiffre: taille_alphabet += 10
    if car_special: taille_alphabet += 32
    
    if taille_alphabet == 0: taille_alphabet = 1 

    entropie = int(longueur * math.log2(taille_alphabet))
    nb_possibilites = taille_alphabet ** longueur
    
    return {
        "longueur": longueur,
        "minuscule": minuscule,
        "majuscule": majuscule,
        "chiffre": chiffre,
        "car_special": car_special,
        "entropie": entropie,
        "temps_CPU": nb_possibilites // 5400000000,
        "temps_GPU": nb_possibilites // 82000000000
    }

# --- 2. CASSAGE EN TEMPS RÉEL ---
def generer_mutations(mot_de_base):
    """Génère les 10 mutations les plus courantes et efficaces d'un mot."""
    if not mot_de_base:
        return []
        
    mot_cap = mot_de_base.capitalize()
    
    # L'ordre correspond aux statistiques d'utilisation humaine
    return [
        mot_de_base,                  # 1. Mot original ("soleil")
        mot_cap,                      # 2. Première lettre majuscule ("Soleil")
        mot_de_base + "123",          # 3. Ajout suite de chiffres ("soleil123")
        mot_cap + "123",              # 4. Majuscule + suite de chiffres ("Soleil123")
        mot_de_base + "!",            # 5. Ajout caractère spécial classique ("soleil!")
        mot_cap + "!",                # 6. Majuscule + caractère spécial ("Soleil!")
        mot_de_base + "123!",         # 7. Combo imposé classique ("soleil123!")
        mot_cap + "123!",             # 8. Combo classique + Majuscule ("Soleil123!")
        mot_de_base + "2024",         # 9. Ajout année ("soleil2024")
        mot_cap + "2024!"             # 10. Combo "Parfait" ("Soleil2024!")
    ]

def generateur_recherche(mot_de_passe_cible):
    """
    Teste les mots et leurs 10 mutations en RAM. Yield la progression.
    """
    hash_cible = hashlib.md5(mot_de_passe_cible.encode('utf-8', errors='ignore')).hexdigest()
    tentatives = 0
    debut = time.time()
    
    try:
        with open('rockyou.txt', 'r', encoding='utf-8', errors='ignore') as f:
            for ligne in f:
                mot_de_base = ligne.strip()
                mutations = generer_mutations(mot_de_base)
                
                # On teste les 10 variantes pour ce mot
                for candidat in mutations:
                    hash_candidat = hashlib.md5(candidat.encode('utf-8', errors='ignore')).hexdigest()
                    tentatives += 1
                    
                    # A. SI LE MOT EST TROUVÉ
                    if hash_candidat == hash_cible:
                        yield {
                            "type": "result", 
                            "trouve": True, 
                            "candidat": candidat, 
                            "tentatives": tentatives
                        }
                        return 
                        
                    # B. MISE À JOUR (toutes les 10 000 tentatives pour que le réseau suive la cadence)
                    if tentatives % 10000 == 0:
                        temps_ecoule = time.time() - debut
                        vitesse = int(tentatives / temps_ecoule) if temps_ecoule > 0 else 0
                        yield {
                            "type": "progress", 
                            "tentatives": tentatives, 
                            "candidat": candidat, 
                            "vitesse": vitesse
                        }
                        
    except FileNotFoundError:
        yield {"type": "error", "message": "Le fichier rockyou.txt est introuvable."}
        return
        
    # C. SI LE DICTIONNAIRE ET LES MUTATIONS SONT ÉPUISÉS
    yield {"type": "result", "trouve": False, "tentatives": tentatives}