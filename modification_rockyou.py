import pathlib as pt

fichier_original = pt.Path("/usr/share/wordlists/rockyou.txt")
fichier_alterer = pt.Path("custom_test.txt")

var = ['&','@','#','']

with open(fichier_original,mode="r",encoding='latin-1') as src, open(fichier_alterer,mode='w',encoding='latin-1') as des :
   for element in src:
      mot_de_passe = element.strip()
      for i in var :
         nouveau_mot = mot_de_passe + i
         mot_final = nouveau_mot + '\n'
         des.write(mot_final)

      



