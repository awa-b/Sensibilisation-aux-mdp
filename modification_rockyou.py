import hashlib
import math



var = ['&','@','#','']

def fichier_mutation(fichier_original):
   with open(fichier_original,mode="r",encoding='utf-8', errors='ignore') as src, open("fichier_alterer.txt",mode='w',encoding='utf-8') as des :
      for element in src:
         mot_de_passe = element.strip()
         for i in var :
            nouveau_mot = mot_de_passe + i
            mot_final = nouveau_mot + '\n'
            des.write(mot_final)
   return "fichier_alterer.txt"


def hashFilename(filename):
   with open(filename, 'r',encoding='utf-8', errors='ignore' ) as f, open("fichier_hasher.txt", 'w') as g:
      for line in f:
         s = line.rstrip('\n')
         digest = hashlib.md5(s.encode()).hexdigest()
         g.write(f"{s} {digest}\n")
   return "fichier_hasher.txt"

      
#affichage

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

    temps_cassage_CPU = nb_possibilites // 5400000000
    temps_cassage_GPU = nb_possibilites // 82000000000
    #pour un cluster de 25 GPU
    temps_cassage_cluster = nb_possibilites // (82000000000*25)


    print("La longueur de votre mot de passe est:", longueur)

    print("Les classes de caractère utilisées sont: ")
    if minuscule :
        print("Minuscules")
    if majuscule:
        print("Majuscule")
    if chiffre :
        print("Chiffres")
    if car_special:
        print("Caractère spécial")

    print(f"L'entropie estimée de votre mot de passe est: {entropie}")

    print("Le temps de cassage estimé est : ")
    print(f"Pour un PC portable normal : {temps_cassage_CPU}")
    print(f"Pour une station de gaming avec GPU(RTX 4090): {temps_cassage_GPU}")
    print(f"Pour un cluster d'attaquant professionnel : {temps_cassage_cluster}")
            

#recherche dans les fichiers 

def hacher_mdp_md5(mot_de_passe):
   return hashlib.md5(mot_de_passe.encode()).hexdigest()

def recherche_hash(mot_de_passe):
   hash = hacher_mdp_md5(mot_de_passe)

   with open('fichier_hasher.txt', 'r') as f:
      for ligne in f:
         candidat, hash_candidat = ligne.strip().split(' ')
         if hash_candidat == hash :
            print(f"HAHAAAA ton mot de passe est '{mot_de_passe}', 😝😝😝 trouve quelque chose de mieux ")
            return  
    
   with open('fichier_alterer.txt', 'r') as f:
      for ligne in f:
         candidat, hash_candidat = ligne.strip().split(' ')
         if hash_candidat == hash :
            print(f"HAHAAAA ton mot de passe est '{mot_de_passe}', 😝😝😝 trouve quelque chose de mieux ")
            return
         else: 
            print("pas trouvé!")

   print("Ton mot de passe a l'air robuste nous n'avons pas pu le trouver")



if __name__ == '__main__':

   hashFile =hashFilename("mdp.txt")

   
   file_mod =hashFilename(fichier_mutation("mdp.txt"))

   print(recherche_hash("23Jinshisama@"))