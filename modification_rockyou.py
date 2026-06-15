import hashlib
import math



var = ['&','@','#']

def fichier_mutation(fichier_original):
   with open(fichier_original,mode="r",encoding='utf-8', errors='ignore') as src, open("fichier_alterer.txt",mode='w',encoding='utf-8') as des :
      for element in src:
         mot_de_passe = element.strip()
         for i in var :
            nouveau_mot = mot_de_passe + i
            mot_final = nouveau_mot + '\n'
            des.write(mot_final)
   return "fichier_alterer.txt"


def hashFilename(filename,fichier_destination):
   with open(filename, 'r',encoding='utf-8', errors='ignore' ) as f, open(fichier_destination, 'w') as g:
      for line in f:
         s = line.rstrip('\n')
         digest = hashlib.md5(s.encode()).hexdigest()
         g.write(f"{s}:{digest}\n")
   return fichier_destination

      
#affichage

def convertir_temps(temps_seconde):

    if temps_seconde == 0:
        return "moins d'une seconde"
    
    secondes = 0
    minutes = 0
    heures = 0
    jour = 0
    mois = 0
    annee = 0
    
    minutes = temps_seconde // 60
    secondes = temps_seconde % 60
    if minutes >=60:
        heures = minutes //60
        minutes = minutes % 60
       
        if heures >=24:
            jour = heures //24
            heures = heures % 24

            if jour >=30:
                mois = jour // 30
                jour = jour % 30

                if mois >=12:
                    annee = mois //12
                    mois = mois % 12
    

    
    return f"{annee} ans {mois} mois {jour} jours {heures}heures {minutes} minutes {secondes} secondes "



def affichage(mot_de_passe):
    longueur = len(mot_de_passe)

    minuscule = any(c.islower() for c in mot_de_passe)
    majuscule = any(c.isupper() for c in mot_de_passe)
    chiffre = any(c.isdigit() for c in mot_de_passe)
    car_special = any(not c.isalnum() for c in mot_de_passe)


    taille_alphabet = 0
    if minuscule:
        taille_alphabet +=26
    if majuscule:
        taille_alphabet +=26
    if chiffre:
        taille_alphabet +=10
    if car_special:
        taille_alphabet += 32

    entropie = int(longueur * math.log2(taille_alphabet))

    nb_possibilites = taille_alphabet ** longueur

    
    return {
        "longueur": longueur,
        "minuscule": minuscule,
        "majuscule": majuscule,
        "chiffre": chiffre,
        "car_special": car_special,
        "entropie": entropie,
        "temps_CPU": convertir_temps(nb_possibilites // 5400000000),
        "temps_GPU": convertir_temps(nb_possibilites // 82000000000),
        "temps_cluster": convertir_temps(nb_possibilites // (82000000000*25))
    }
            

#recherche dans les fichiers 

def hacher_mdp_md5(mot_de_passe):
   return hashlib.md5(mot_de_passe.encode()).hexdigest()

def recherche_hash(mot_de_passe,file):
    hash = hacher_mdp_md5(mot_de_passe)

    with open(file, 'r') as f:
      for ligne in f:
         candidat, hash_candidat = ligne.strip().rsplit(':',1)
         if hash_candidat == hash :
            return {"trouve": True, "candidat": candidat} 
    
    with open('fichier_alterer_hasher.txt', 'r') as f:
        for ligne in f:
            if not ligne.strip():
                continue
        
            candidat, hash_candidat = ligne.strip().rsplit(':',1)
            if hash_candidat == hash :
                return {"trouve": True, "candidat": candidat}
    return {"trouve": False}    




if __name__ == '__main__':
   
   hashFile = hashFilename("rockyou.txt","hash_rockyou.txt")
   file_mod = fichier_mutation("rockyou.txt")
   
   file_mod1 = hashFilename(file_mod, "hash_altere.txt")

   recherche_hash("binta@205",hashFile)