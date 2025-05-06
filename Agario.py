import pygame
import random
import math
import sys
import time


pygame.init()
largeur_ecran, hauteur_ecran = 800, 600
ecran = pygame.display.set_mode((largeur_ecran, hauteur_ecran))
pygame.display.set_caption("Hagra.io")
clock = pygame.time.Clock()


logo = pygame.image.load("logoo.png")
logo = pygame.transform.scale(logo, (400, 200))

BLANC = (255, 255, 255)
VERT = (0, 255, 0)
ROUGE = (255, 0, 0)
NOIR = (0, 0, 0)
GRIS = (200, 200, 200)
COULEURS_ENNEMIS = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (128, 0, 128)]


TAILLE_MAP = 3000  
INTERVALLE_REGEN = 20000  
DERNIERE_REGEN = 0
TEMPS_RESPAWN = 3  


pseudo = ""
saisie_active = False
font = pygame.font.SysFont(None, 32)
font_petit = pygame.font.SysFont(None, 24)
font_grande = pygame.font.SysFont(None, 72)


joueur_pos = [TAILLE_MAP // 2, TAILLE_MAP // 2]
joueur_rayon = 20
joueur_couleur = VERT
vitesse = 4
score_joueur = joueur_rayon * 10
joueur_vivant = True
temps_mort = 0


nombre_ennemis = 4
ennemis = []
for i in range(nombre_ennemis):
    x = random.randint(0, TAILLE_MAP)
    y = random.randint(0, TAILLE_MAP)
    rayon = random.randint(15, 30)
    vitesse_ennemi = random.uniform(1.5, 2.5)
    ennemis.append({
        "pos": [x, y],
        "rayon": rayon,
        "couleur": COULEURS_ENNEMIS[i % len(COULEURS_ENNEMIS)],
        "vitesse": vitesse_ennemi,
        "cible": [random.randint(0, TAILLE_MAP), random.randint(0, TAILLE_MAP)],
        "nom": f"Ennemi {i+1}",
        "score": rayon * 10,  
        "vivant": True,
        "temps_mort": 0
    })


nombre_particules_min = 30
nombre_particules_max = 80
particules = []

def generer_particules():
    global particules
    particules = []
    nombre = random.randint(nombre_particules_min, nombre_particules_max)
    for _ in range(nombre):
        x = random.randint(0, TAILLE_MAP)
        y = random.randint(0, TAILLE_MAP)
        rayon = random.randint(3, 7)
        particules.append([x, y, rayon])

generer_particules()


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def dessiner_quadrillage(offset_x, offset_y):
    espace = 50  
    start_x = -(offset_x % espace)
    start_y = -(offset_y % espace)
    
    
    for x in range(int(start_x), largeur_ecran, espace):
        pygame.draw.line(ecran, GRIS, (x, 0), (x, hauteur_ecran), 1)
    
    
    for y in range(int(start_y), hauteur_ecran, espace):
        pygame.draw.line(ecran, GRIS, (0, y), (largeur_ecran, y), 1)

def convertir_coordonnees(pos, joueur_pos):
    """Convertit les coordonnées absolues en coordonnées relatives à l'écran"""
    return [pos[0] - joueur_pos[0] + largeur_ecran // 2, pos[1] - joueur_pos[1] + hauteur_ecran // 2]

def dessiner():
    ecran.fill(BLANC)
    
    if joueur_vivant:
        
        offset_x = joueur_pos[0] - largeur_ecran // 2
        offset_y = joueur_pos[1] - hauteur_ecran // 2
        
        
        dessiner_quadrillage(offset_x, offset_y)
        
        
        for p in particules:
            pos_ecran = convertir_coordonnees(p[:2], joueur_pos)
            if 0 <= pos_ecran[0] <= largeur_ecran and 0 <= pos_ecran[1] <= hauteur_ecran:
                pygame.draw.circle(ecran, ROUGE, (int(pos_ecran[0]), int(pos_ecran[1])), p[2])
        
        
        for ennemi in ennemis:
            if ennemi["vivant"]:
                pos_ecran = convertir_coordonnees(ennemi["pos"], joueur_pos)
                if (-ennemi["rayon"] <= pos_ecran[0] <= largeur_ecran + ennemi["rayon"] and 
                    -ennemi["rayon"] <= pos_ecran[1] <= hauteur_ecran + ennemi["rayon"]):
                    pygame.draw.circle(ecran, ennemi["couleur"], (int(pos_ecran[0]), int(pos_ecran[1])), ennemi["rayon"])
                    
                    texte = font_petit.render(ennemi["nom"], True, NOIR)
                    ecran.blit(texte, (pos_ecran[0] - texte.get_width() // 2, pos_ecran[1] - ennemi["rayon"] - 20))
        
       
        pygame.draw.circle(ecran, joueur_couleur, (largeur_ecran // 2, hauteur_ecran // 2), joueur_rayon)
        
       
        if pseudo:
            texte = font_petit.render(pseudo, True, NOIR)
            ecran.blit(texte, (largeur_ecran // 2 - texte.get_width() // 2, hauteur_ecran // 2 - joueur_rayon - 20))
    else:
        
        texte_mort = font_grande.render("YOU DIED", True, ROUGE)
        ecran.blit(texte_mort, (largeur_ecran // 2 - texte_mort.get_width() // 2, hauteur_ecran // 2 - 50))
        
        temps_restant = max(0, TEMPS_RESPAWN - (time.time() - temps_mort))
        texte_respawn = font.render(f"Respawn in: {int(temps_restant)}s", True, NOIR)
        ecran.blit(texte_respawn, (largeur_ecran // 2 - texte_respawn.get_width() // 2, hauteur_ecran // 2 + 50))
    
    
    afficher_leaderboard()
    
    pygame.display.flip()

def afficher_leaderboard():
    
    scores = []
    if pseudo and joueur_vivant:
        scores.append((pseudo, score_joueur))
    for ennemi in ennemis:
        if ennemi["vivant"]:
            scores.append((ennemi["nom"], ennemi["score"]))
    
   
    scores.sort(key=lambda x: x[1], reverse=True)
    
   
    x_pos = largeur_ecran - 200
    y_pos = 20
    pygame.draw.rect(ecran, (220, 220, 220, 128), (x_pos - 10, y_pos - 10, 190, len(scores) * 30 + 20))
    
    titre = font_petit.render("Classement:", True, NOIR)
    ecran.blit(titre, (x_pos, y_pos))
    y_pos += 30
    
    for nom, score in scores:
        texte = font_petit.render(f"{nom}: {score}", True, NOIR)
        ecran.blit(texte, (x_pos, y_pos))
        y_pos += 25

def menu_demarrage():
    global pseudo, saisie_active
    
    en_menu = True
    input_rect = pygame.Rect(largeur_ecran // 2 - 100, hauteur_ecran // 2 + 50, 200, 32)
    
    while en_menu:
        ecran.fill(BLANC)
        
        
        ecran.blit(logo, (largeur_ecran // 2 - logo.get_width() // 2, 100))
        
        
        titre = font.render("Entrez votre pseudo:", True, NOIR)
        ecran.blit(titre, (largeur_ecran // 2 - titre.get_width() // 2, hauteur_ecran // 2))
        
        
        pygame.draw.rect(ecran, (200, 200, 200) if not saisie_active else (240, 240, 240), input_rect, 2)
        texte_saisie = font.render(pseudo, True, NOIR)
        ecran.blit(texte_saisie, (input_rect.x + 5, input_rect.y + 5))
        
        
        btn_rect = pygame.Rect(largeur_ecran // 2 - 50, hauteur_ecran // 2 + 100, 100, 40)
        pygame.draw.rect(ecran, (0, 200, 0), btn_rect)
        texte_btn = font.render("Jouer", True, BLANC)
        ecran.blit(texte_btn, (btn_rect.x + btn_rect.width // 2 - texte_btn.get_width() // 2, 
                              btn_rect.y + btn_rect.height // 2 - texte_btn.get_height() // 2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    saisie_active = True
                else:
                    saisie_active = False
                
                if btn_rect.collidepoint(event.pos) and pseudo:
                    en_menu = False
            
            if event.type == pygame.KEYDOWN and saisie_active:
                if event.key == pygame.K_RETURN:
                    en_menu = False if pseudo else None
                elif event.key == pygame.K_BACKSPACE:
                    pseudo = pseudo[:-1]
                else:
                    if len(pseudo) < 15:  
                        pseudo += event.unicode
        
        clock.tick(60)

def deplacer_ennemis():
    for ennemi in ennemis:
        if not ennemi["vivant"]:
            
            if time.time() - ennemi["temps_mort"] > TEMPS_RESPAWN:
                ennemi["vivant"] = True
                ennemi["pos"] = [random.randint(0, TAILLE_MAP), random.randint(0, TAILLE_MAP)]
                ennemi["rayon"] = 20
                ennemi["score"] = ennemi["rayon"] * 10
                ennemi["cible"] = [random.randint(0, TAILLE_MAP), random.randint(0, TAILLE_MAP)]
            continue
        
        
        if distance(ennemi["pos"], ennemi["cible"]) < 5 or random.random() < 0.01:
            ennemi["cible"] = [random.randint(0, TAILLE_MAP), random.randint(0, TAILLE_MAP)]
        
        
        dx = ennemi["cible"][0] - ennemi["pos"][0]
        dy = ennemi["cible"][1] - ennemi["pos"][1]
        dist = math.hypot(dx, dy)
        if dist != 0:
            ennemi["pos"][0] += ennemi["vitesse"] * dx / dist
            ennemi["pos"][1] += ennemi["vitesse"] * dy / dist
        
        
        ennemi["pos"][0] = max(ennemi["rayon"], min(TAILLE_MAP - ennemi["rayon"], ennemi["pos"][0]))
        ennemi["pos"][1] = max(ennemi["rayon"], min(TAILLE_MAP - ennemi["rayon"], ennemi["pos"][1]))

def gerer_collisions():
    global particules, joueur_rayon, score_joueur, joueur_vivant, temps_mort
    
    if not joueur_vivant:
        
        if time.time() - temps_mort > TEMPS_RESPAWN:
            joueur_vivant = True
            joueur_pos[0] = random.randint(0, TAILLE_MAP)
            joueur_pos[1] = random.randint(0, TAILLE_MAP)
            joueur_rayon = 20
            score_joueur = joueur_rayon * 10
        return
    
    
    nouvelles_particules = []
    for p in particules:
        pos_p_ecran = convertir_coordonnees(p[:2], joueur_pos)
        dist = distance((largeur_ecran // 2, hauteur_ecran // 2), pos_p_ecran)
        
        if dist < joueur_rayon + p[2]:
            joueur_rayon += 0.2  # Grossit quand il mange
            score_joueur = joueur_rayon * 10
        else:
            nouvelles_particules.append(p)
    particules = nouvelles_particules
    
    
    for ennemi in ennemis:
        if not ennemi["vivant"]:
            continue
            
        nouvelles_particules = []
        for p in particules:
            if distance(ennemi["pos"], p[:2]) < ennemi["rayon"] + p[2]:
                ennemi["rayon"] += 0.15  
                ennemi["score"] = ennemi["rayon"] * 10
            else:
                nouvelles_particules.append(p)
        particules = nouvelles_particules
    
    
    for ennemi in ennemis:
        if not ennemi["vivant"]:
            continue
            
        dist = distance(joueur_pos, ennemi["pos"])
        if dist < joueur_rayon + ennemi["rayon"]:
            if joueur_rayon > ennemi["rayon"] * 1.1:  # Le joueur doit être significativement plus gros
                # Le joueur mange l'ennemi
                joueur_rayon += ennemi["rayon"] * 0.5
                score_joueur = joueur_rayon * 10
                ennemi["vivant"] = False
                ennemi["temps_mort"] = time.time()
            elif ennemi["rayon"] > joueur_rayon * 1.1:  # L'ennemi doit être significativement plus gros
                # L'ennemi mange le joueur
                ennemi["rayon"] += joueur_rayon * 0.5
                ennemi["score"] = ennemi["rayon"] * 10
                joueur_vivant = False
                temps_mort = time.time()
    
    
    for i in range(len(ennemis)):
        for j in range(i+1, len(ennemis)):
            ennemi1 = ennemis[i]
            ennemi2 = ennemis[j]
            
            if not ennemi1["vivant"] or not ennemi2["vivant"]:
                continue
                
            dist = distance(ennemi1["pos"], ennemi2["pos"])
            if dist < ennemi1["rayon"] + ennemi2["rayon"]:
                if ennemi1["rayon"] > ennemi2["rayon"] * 1.1:
                    # Ennemi1 mange ennemi2
                    ennemi1["rayon"] += ennemi2["rayon"] * 0.5
                    ennemi1["score"] = ennemi1["rayon"] * 10
                    ennemi2["vivant"] = False
                    ennemi2["temps_mort"] = time.time()
                elif ennemi2["rayon"] > ennemi1["rayon"] * 1.1:
                    # Ennemi2 mange ennemi1
                    ennemi2["rayon"] += ennemi1["rayon"] * 0.5
                    ennemi2["score"] = ennemi2["rayon"] * 10
                    ennemi1["vivant"] = False
                    ennemi1["temps_mort"] = time.time()


menu_demarrage()


en_cours = True
DERNIERE_REGEN = pygame.time.get_ticks()

while en_cours:
    temps_actuel = pygame.time.get_ticks()
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False
    
    if joueur_vivant:
        
        souris_x, souris_y = pygame.mouse.get_pos()
        dx = souris_x - largeur_ecran // 2
        dy = souris_y - hauteur_ecran // 2
        dist = math.hypot(dx, dy)
        
        if dist != 0:
            
            vitesse_effective = vitesse * (20 / joueur_rayon) if joueur_rayon > 20 else vitesse
            
            
            new_x = joueur_pos[0] + vitesse_effective * dx / dist
            new_y = joueur_pos[1] + vitesse_effective * dy / dist
            
            joueur_pos[0] = max(joueur_rayon, min(TAILLE_MAP - joueur_rayon, new_x))
            joueur_pos[1] = max(joueur_rayon, min(TAILLE_MAP - joueur_rayon, new_y))
    
    
    deplacer_ennemis()
    
    
    gerer_collisions()
    
    
    if temps_actuel - DERNIERE_REGEN > INTERVALLE_REGEN:
        generer_particules()
        DERNIERE_REGEN = temps_actuel
    
    dessiner()

pygame.quit()