import hashlib
import math
import time
from datetime import datetime
import itertools
import string
import multiprocessing
import queue

ANNEE_COURANTE = str(datetime.now().year)

# ==========================================
# 0. FONCTION DE L'OUVRIER (MULTI-PROCESSING FIXÉ)
# ==========================================
def ouvrier_hachage(queue_travail, hash_cible, boite_aux_lettres, bouton_arret):
    debut = time.time()
    dernier_envoi = 0
    tentatives_locales = 0
    
    # L'ouvrier boucle tant qu'il y a du travail dans la file
    while True:
        if bouton_arret.is_set():
            return
            
        try:
            # Il pioche un paquet de 10 000 mots dans la pile
            paquet_mots = queue_travail.get_nowait()
        except queue.Empty:
            # S'il n'y a plus de paquets, l'ouvrier a fini sa journée !
            return
            
        for mot_de_base in paquet_mots:
            if bouton_arret.is_set():
                return
                
            mutations = generer_mutations(mot_de_base)
            for mot in mutations:
                hash_tester = hashlib.md5(mot.encode('utf-8', errors='ignore')).hexdigest()
                tentatives_locales += 1
                
                if hash_cible == hash_tester:
                    dictionnaire_victoire = {
                        "type": "result", "trouve": True, "candidat": mot, 
                        "mot_base": mot_de_base, "tentatives_locales": tentatives_locales, 
                        "methode": "Dictionnaire + Mutations (Multi-cœurs)"
                    }
                    boite_aux_lettres.put(dictionnaire_victoire)
                    return
            
                if tentatives_locales % 100000 == 0:
                    maintenant = time.time()
                    temps_ecoule = maintenant - debut
                    if maintenant - dernier_envoi >= 0.06:
                        dictionnaire_progression = {
                            "type": "progress", "candidat": mot, 
                            "vitesse": int(tentatives_locales / temps_ecoule) if temps_ecoule > 0 else 0
                        }
                        boite_aux_lettres.put(dictionnaire_progression)
                        dernier_envoi = maintenant


# ==========================================
# 1. ANALYSE THÉORIQUE
# ==========================================
def affichage(mot_de_passe: str) -> dict:
    longueur = len(mot_de_passe)
    hash_md5 = hashlib.md5(mot_de_passe.encode('utf-8', errors='ignore')).hexdigest()
    
    if longueur == 0:
        return {
            "longueur": 0, "minuscule": False, "majuscule": False, 
            "chiffre": False, "car_special": False, "entropie": 0, 
            "temps_CPU": 0, "temps_GPU": 0, "hash_md5": hash_md5
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
        "temps_CPU": nb_possibilites // 5_400_000_000,
        "temps_GPU": nb_possibilites // 82_000_000_000,
        "hash_md5": hash_md5
    }

# ==========================================
# 2. CASSAGE EN TEMPS RÉEL (LE MOTEUR)
# ==========================================
def generer_mutations(mot: str, caracteres_speciaux: list = None) -> list:
    if not mot:
        return []
    
    if caracteres_speciaux is None:
        caracteres_speciaux = ['&', '@', '#', '!']
        
    mot_cap = mot.capitalize()
    mot_leet = mot.lower().replace("a", "@")
    mot_cap_leet = mot_cap.replace("a", "@")
    
    mutations = [mot_cap, mot_leet, mot_cap_leet]
    suffixes = caracteres_speciaux + ["123", "2010!", "2026", "2010"]
    
    for suffixe in suffixes:
        mutations.append(mot + suffixe)
        mutations.append(mot_cap + suffixe)
        mutations.append(mot_leet + suffixe)
        mutations.append(mot_cap_leet + suffixe)
        
    return list(set(mutations))


def generateur_recherche(mot_de_passe_cible: str):
    hash_cible = hashlib.md5(mot_de_passe_cible.encode('utf-8', errors='ignore')).hexdigest()
    tentatives = 0
    debut_global = time.time()
    dernier_envoi = debut_global 
    
    def envoyer_progression(tents, cand):
        """Sous-fonction pour gérer l'envoi des Étapes 1 et 2 proprement"""
        nonlocal dernier_envoi
        if tents % 5000 == 0:
            maintenant = time.time()
            if maintenant - dernier_envoi >= 0.06:
                temps_ecoule = maintenant - debut_global
                vit = int(tents / temps_ecoule) if temps_ecoule > 0 else 0
                dernier_envoi = maintenant
                return {"type": "progress", "tentatives": tents, "candidat": cand, "vitesse": vit}
        return None

    # --- ÉTAPE 1 : FORCE BRUTE PURE (Uniquement si <= 4 caractères) ---
    if len(mot_de_passe_cible) <= 4:
        alphabet = string.ascii_letters + string.digits + string.punctuation 
        for longueur in range(1, 5):
            for tentative_tuple in itertools.product(alphabet, repeat=longueur):
                candidat = "".join(tentative_tuple)
                hash_candidat = hashlib.md5(candidat.encode('utf-8')).hexdigest()
                tentatives += 1
                
                if hash_candidat == hash_cible:
                    yield {"type": "result", "trouve": True, "candidat": candidat, "tentatives": tentatives, "methode": "Force Brute pure"}
                    return
                
                progression = envoyer_progression(tentatives, candidat)
                if progression: yield progression

    # --- ÉTAPE 2 : DICTIONNAIRE PUR ---
    try:
        with open('rockyou.txt', 'r', encoding='utf-8', errors='ignore') as f:
            rang = 0
            for ligne in f:
                rang += 1
                candidat = ligne.strip()
                hash_candidat = hashlib.md5(candidat.encode('utf-8')).hexdigest()
                tentatives += 1
                
                if hash_candidat == hash_cible:
                    yield {
                        "type": "result", "trouve": True, "candidat": candidat, 
                        "tentatives": tentatives, "methode": "Dictionnaire (Mot exact)", "rang": rang 
                    }
                    return 
                    
                progression = envoyer_progression(tentatives, candidat)
                if progression: yield progression
    except FileNotFoundError:
        yield {"type": "error", "message": "Le fichier rockyou.txt est introuvable."}
        return

    # --- ÉTAPE 3 : DICTIONNAIRE + MUTATIONS (USINE MULTI-PROCESSUS FIXÉE) ---
    nb_coeurs = max(1, multiprocessing.cpu_count() - 1) # On demande au PC combien il a de cœurs (ex: 8)
    
    queue_travail = multiprocessing.Queue()
    boite_aux_lettres = multiprocessing.Queue()
    bouton_arret = multiprocessing.Event()
    liste_ouvriers = []
    paquet_actuel = []
    
    tentatives_totales = tentatives 

    try:
        # 1. Le Chef d'Atelier remplit la file d'attente (sans lancer les ouvriers)
        with open('rockyou.txt', 'r', encoding='utf-8', errors='ignore') as f:
            for ligne in f:
                paquet_actuel.append(ligne.strip())
                if len(paquet_actuel) == 100000:
                    queue_travail.put(paquet_actuel)
                    paquet_actuel = [] 
            
            if len(paquet_actuel) > 0:
                queue_travail.put(paquet_actuel)

        # 2. On embauche EXACTEMENT le nombre de cœurs de ton processeur
        for _ in range(nb_coeurs):
            p = multiprocessing.Process(target=ouvrier_hachage, args=(queue_travail, hash_cible, boite_aux_lettres, bouton_arret))
            p.start()
            liste_ouvriers.append(p)

        # 3. Le Réceptionniste (Écoute de la boîte aux lettres - inchangé)
        while True:
            if not any(p.is_alive() for p in liste_ouvriers) and boite_aux_lettres.empty():
                yield {"type": "result", "trouve": False, "tentatives": tentatives_totales}
                break
                
            try:
                message = boite_aux_lettres.get(timeout=0.1)
                
                if message["type"] == "progress":
                    tentatives_totales += 100000 
                    message["tentatives"] = tentatives_totales
                    
                    temps_total = time.time() - debut_global
                    message["vitesse"] = int(tentatives_totales / temps_total) if temps_total > 0 else 0
                    
                elif message.get("trouve") == True:
                    message["tentatives"] = tentatives_totales + message.get("tentatives_locales", 0)
                    bouton_arret.set() 
                    yield message
                    break              
                    
                yield message
                
            except queue.Empty:
                pass
                
    except FileNotFoundError:
        yield {"type": "error", "message": "Le fichier rockyou.txt est introuvable."}
                