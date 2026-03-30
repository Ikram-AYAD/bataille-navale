# bataille_navale_pygame_fr_v4.py
import pygame
import sys
import random
import time

# ---------- Configuration ----------
FPS = 30
TAILLE_CASE = 36
MARGE = 20
ESPACE_GRILLES = 80
HAUTEUR_TITRE = 80
LARGEUR_FENETRE = MARGE*2 + TAILLE_CASE*10*2 + ESPACE_GRILLES
HAUTEUR_FENETRE = HAUTEUR_TITRE + MARGE + TAILLE_CASE*10 + 80

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (0, 120, 200)
BLEU_FONCE = (0, 80, 150)
ROUGE = (200, 0, 0)
VERT = (0, 160, 0)
VERT_CLAIR = (150, 220, 150)
ROUGE_CLAIR = (255, 180, 180)
GRIS_FONCE = (120, 120, 120)

# Bateaux
BATEAUX = [
    ("Porte-avion", 5),
    ("Cuirassé", 4),
    ("Frégate", 3),
    ("Sous-marin", 3),
    ("Torpilleur", 2)
]

ORIENTATIONS_SOUS_MARIN = ["haut", "bas", "gauche", "droite"]

# ---------- Fonctions de grille ----------
def creer_grille():
    return [[" "] * 11 for _ in range(11)]

def case_dans_grille(lig, col):
    return 1 <= lig <= 10 and 1 <= col <= 10

def emplacement_valide(grille, lig, col, taille, orientation):
    if orientation == "H" and col + taille - 1 > 10:
        return False
    if orientation == "V" and lig + taille - 1 > 10:
        return False
    for i in range(taille):
        r = lig if orientation == "H" else lig + i
        c = col + i if orientation == "H" else col
        if grille[r][c] != " ":
            return False
    return True

def emplacement_valide_sous_marin(grille, lig, col, orientation):
    if orientation not in ORIENTATIONS_SOUS_MARIN:
        return False
    if orientation == "haut":
        coords = [(lig, col-1), (lig, col), (lig, col+1), (lig-1, col)]
    elif orientation == "bas":
        coords = [(lig, col-1), (lig, col), (lig, col+1), (lig+1, col)]
    elif orientation == "gauche":
        coords = [(lig-1, col), (lig, col), (lig+1, col), (lig, col-1)]
    elif orientation == "droite":
        coords = [(lig-1, col), (lig, col), (lig+1, col), (lig, col+1)]
    else:
        return False
    for (r, c) in coords:
        if not case_dans_grille(r, c) or grille[r][c] != " ":
            return False
    return True

def placer_bateau(grille, lig, col, taille, orientation, nom):
    positions = []
    if nom == "Sous-marin":
        if orientation == "haut":
            coords = [(lig, col-1), (lig, col), (lig, col+1), (lig-1, col)]
        elif orientation == "bas":
            coords = [(lig, col-1), (lig, col), (lig, col+1), (lig+1, col)]
        elif orientation == "gauche":
            coords = [(lig-1, col), (lig, col), (lig+1, col), (lig, col-1)]
        elif orientation == "droite":
            coords = [(lig-1, col), (lig, col), (lig+1, col), (lig, col+1)]
        else:
            return []
        for (r, c) in coords:
            grille[r][c] = "O"
            positions.append((r, c))
    else:
        if orientation == "H":
            for i in range(taille):
                r = lig
                c = col + i
                grille[r][c] = "O"
                positions.append((r, c))
        else:
            for i in range(taille):
                r = lig + i
                c = col
                grille[r][c] = "O"
                positions.append((r, c))
    return positions

def placer_bateau_joueur(lig, col):
    global index_bateau, orientation, flotte_joueur, message
    nom, taille = BATEAUX[index_bateau]
    if nom == "Sous-marin":
        orientation = "haut"
        if not emplacement_valide_sous_marin(grille_joueur, lig, col, orientation):
            message = "Chevauchement ou hors grille (sous-marin)."
            return
        flotte_joueur[nom] = placer_bateau(grille_joueur, lig, col, taille, orientation, nom)
        orientation = "H"  # réinitialise orientation pour le prochain bateau
    else:
        if orientation not in ("H", "V"):
            message = "Orientation invalide pour ce bateau."
            return
        if not emplacement_valide(grille_joueur, lig, col, taille, orientation):
            message = "Chevauchement ou hors grille."
            return
        flotte_joueur[nom] = placer_bateau(grille_joueur, lig, col, taille, orientation, nom)
    index_bateau += 1
    if index_bateau < len(BATEAUX):
        message = f"{nom} placé. Place {BATEAUX[index_bateau][0]} ({BATEAUX[index_bateau][1]})."
    else:
        message = "Tous les bateaux sont placés !"
        demarrer_partie()

def placer_bateaux_bot(grille):
    flotte = {}
    for nom, taille in BATEAUX:
        place = False
        while not place:
            ori = random.choice(["H", "V"])
            lig = random.randint(1, 10)
            col = random.randint(1, 10)
            if nom == "Sous-marin":
                ori_s = random.choice(ORIENTATIONS_SOUS_MARIN)
                if emplacement_valide_sous_marin(grille, lig, col, ori_s):
                    flotte[nom] = placer_bateau(grille, lig, col, taille, ori_s, nom)
                    place = True
            else:
                if emplacement_valide(grille, lig, col, taille, ori):
                    flotte[nom] = placer_bateau(grille, lig, col, taille, ori, nom)
                    place = True
    return flotte

# ---------- Coordonnées ----------
def coin_grille(joueur):
    x = MARGE
    if not joueur:
        x += TAILLE_CASE*10 + ESPACE_GRILLES
    y = HAUTEUR_TITRE + MARGE + 40
    return x, y

def pixel_vers_case(x, y, joueur):
    gx, gy = coin_grille(joueur)
    if x < gx or y < gy:
        return None
    relx = x - gx
    rely = y - gy
    col = relx // TAILLE_CASE + 1
    lig = rely // TAILLE_CASE + 1
    if 1 <= col <= 10 and 1 <= lig <= 10:
        return int(lig), int(col)
    return None

# ---------- Initialisation pygame ----------
pygame.init()
ecran = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
pygame.display.set_caption("Bataille Navale")
horloge = pygame.time.Clock()
police = pygame.font.SysFont(None, 22)
police_grande = pygame.font.SysFont(None, 32)

# ---------- États du jeu ----------
grille_joueur = creer_grille()
grille_bot = creer_grille()
grille_bot_visible = creer_grille()
flotte_joueur = {}
flotte_bot = {}
etat = "placement"
index_bateau = 0
orientation = "H"
apercu_case = None
message = "Place tes bateaux."
tour_joueur = True
derniere_action = time.time()
delai_bot = 1.2

# IA du bot
cases_a_tester = []
derniers_touches = []
direction_courante = None

# ---------- Fonctions de jeu ----------
def demarrer_partie():
    global flotte_bot, etat, message
    flotte_bot = placer_bateaux_bot(grille_bot)
    etat = "jeu"
    message = "La bataille commence !"

def verifier_coule(grille, flotte, lig, col):
    for nom, positions in flotte.items():
        if (lig, col) in positions:
            if all(grille[r][c] == "X" for r, c in positions):
                return nom
    return None

def tirer_joueur(lig, col):
    """
    Retourne :
    - "touché" si tir touche un bateau
    - "coulé" si bateau coulé
    - "raté" si rien
    - "deja" si case déjà tirée
    """
    global message
    if grille_bot_visible[lig][col] in ["X", "-"]:
        message = "Déjà tiré ici."
        return "deja"
    if grille_bot[lig][col] == "O":
        grille_bot[lig][col] = "X"
        grille_bot_visible[lig][col] = "X"
        nom_coule = verifier_coule(grille_bot, flotte_bot, lig, col)
        if nom_coule:
            message = f"Touché ! {nom_coule} coulé !"
            return "coulé"
        else:
            message = "Touché !"
            return "touché"
    else:
        grille_bot[lig][col] = "-"
        grille_bot_visible[lig][col] = "-"
        message = "Raté."
        return "raté"

def tirer_bot():
    global message, cases_a_tester, derniers_touches, direction_courante
    if cases_a_tester:
        lig, col = cases_a_tester.pop(0)
    else:
        lig, col = random.randint(1, 10), random.randint(1, 10)
        while grille_joueur[lig][col] in ["X", "-"]:
            lig, col = random.randint(1, 10), random.randint(1, 10)
    if grille_joueur[lig][col] == "O":
        grille_joueur[lig][col] = "X"
        nom_coule = verifier_coule(grille_joueur, flotte_joueur, lig, col)
        message = f"Bot tire {chr(col+64)}{lig} --- Touché !"
        if nom_coule:
            message += f" Ton {nom_coule} est coulé !"
            derniers_touches.clear()
            cases_a_tester.clear()
            direction_courante = None
        else:
            derniers_touches.append((lig, col))
            if len(derniers_touches) >= 3:
                rs = [r for r, _ in derniers_touches]
                cs = [c for _, c in derniers_touches]
                if len(set(rs)) == 1:
                    direction_courante = "H"
                elif len(set(cs)) == 1:
                    direction_courante = "V"
                else:
                    direction_courante = None
            voisins = []
            for (tr, tc) in derniers_touches:
                autour = [(tr-1, tc), (tr+1, tc), (tr, tc-1), (tr, tc+1)]
                for (r, c) in autour:
                    if case_dans_grille(r, c) and grille_joueur[r][c] not in ["X", "-"]:
                        if (r, c) not in cases_a_tester:
                            voisins.append((r, c))
            cases_a_tester.extend(voisins)
        return True
    else:
        grille_joueur[lig][col] = "-"
        message = f"Bot tire {chr(col+64)}{lig} --- Raté."
        return False

# ---------- Dessin des lignes rouges de bateaux coulés ----------
def dessiner_bateau_coule(surface, positions, nom_bateau, joueur):
    if len(positions) < 2:
        return
    gx, gy = coin_grille(joueur)
    rects = [pygame.Rect(gx + (c - 1) * TAILLE_CASE, gy + (r - 1) * TAILLE_CASE,
                         TAILLE_CASE, TAILLE_CASE) for (r, c) in positions]
    points = {pos: rect.center for pos, rect in zip(positions, rects)}

    # ----------- Sous-marin en T -----------
    if nom_bateau == "Sous-marin":
        rows = [r for r, _ in positions]
        cols = [c for _, c in positions]
        centre = None
        for (r, c) in positions:
            if rows.count(r) == 2 or cols.count(c) == 2:
                centre = (r, c)
                break
        cx, cy = centre
        horiz = [(r, c) for (r, c) in positions if r == cx]
        horiz = sorted(horiz, key=lambda x: x[1])
        pygame.draw.line(surface, ROUGE, points[horiz[0]], points[horiz[-1]], 6)
        vert = [(r, c) for (r, c) in positions if c == cy]
        vert = sorted(vert, key=lambda x: x[0])
        pygame.draw.line(surface, ROUGE, points[vert[0]], points[vert[-1]], 6)
        return

    # ----------- Bateaux normaux (ligne simple) -----------
    sorted_points = sorted(points.values(), key=lambda p: (p[0], p[1]))
    pygame.draw.lines(surface, ROUGE, False, sorted_points, 6)

# Affichage
def dessiner_grille(surface, grille, joueur, montrer=False):
    gx, gy = coin_grille(joueur)
    for r in range(1, 11):
        for c in range(1, 11):
            rect = pygame.Rect(gx+(c-1)*TAILLE_CASE, gy+(r-1)*TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
            if joueur and montrer and grille[r][c] == "O":
                pygame.draw.rect(surface, VERT_CLAIR, rect)
            else:
                pygame.draw.rect(surface, BLANC, rect)
            pygame.draw.rect(surface, NOIR, rect, 1)
            val = grille[r][c]
            if val == "X":
                pygame.draw.line(surface, ROUGE, rect.topleft, rect.bottomright, 3)
                pygame.draw.line(surface, ROUGE, rect.topright, rect.bottomleft, 3)
            elif val == "-":
                pygame.draw.circle(surface, GRIS_FONCE, rect.center, TAILLE_CASE//6, 2)
    flotte = flotte_joueur if joueur else flotte_bot
    for nom, positions in flotte.items():
        if all(grille[r][c] == "X" for r, c in positions):
            dessiner_bateau_coule(surface, positions, nom, joueur)

def dessiner_apercu(surface, lig, col, taille, orientation):
    if not lig or not col:
        return
    gx, gy = coin_grille(True)
    nom, _ = BATEAUX[index_bateau]
    coords = []
    if nom == "Sous-marin":
        if orientation not in ORIENTATIONS_SOUS_MARIN:
            orientation = "haut"
        if orientation == "haut":
            coords = [(lig, col-1), (lig, col), (lig, col+1), (lig-1, col)]
        elif orientation == "bas":
            coords = [(lig, col-1), (lig, col), (lig, col+1), (lig+1, col)]
        elif orientation == "gauche":
            coords = [(lig-1, col), (lig, col), (lig+1, col), (lig, col-1)]
        elif orientation == "droite":
            coords = [(lig-1, col), (lig, col), (lig+1, col), (lig, col+1)]
    else:
        for i in range(taille):
            r = lig if orientation == "H" else lig + i
            c = col + i if orientation == "H" else col
            coords.append((r, c))
    valide = all(case_dans_grille(r, c) and grille_joueur[r][c] == " " for r, c in coords)
    couleur = VERT_CLAIR if valide else ROUGE_CLAIR
    for (r, c) in coords:
        if not case_dans_grille(r, c):
            continue
        rect = pygame.Rect(gx+(c-1)*TAILLE_CASE, gy+(r-1)*TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
        pygame.draw.rect(surface, couleur, rect)
        pygame.draw.rect(surface, NOIR, rect, 1)

def dessiner_interface(surface, tour_joueur):
    pygame.draw.rect(surface, BLEU_FONCE, (0, 0, LARGEUR_FENETRE, HAUTEUR_TITRE))
    titre = "BATAILLE NAVALE"
    surf = police_grande.render(titre, True, BLANC)
    rect = surf.get_rect(center=(LARGEUR_FENETRE//2, HAUTEUR_TITRE//2))
    surface.blit(surf, rect)
    pygame.draw.rect(surface, BLEU, (0, HAUTEUR_TITRE, LARGEUR_FENETRE, 40))
    texte_tour = "Joueur 1, à vous !" if tour_joueur else "Au tour de l'ordinateur..."
    surf = police.render(texte_tour, True, BLANC)
    rect = surf.get_rect(center=(LARGEUR_FENETRE//2, HAUTEUR_TITRE+20))
    surface.blit(surf, rect)
    pygame.draw.rect(surface, BLANC, (MARGE, HAUTEUR_FENETRE-40, LARGEUR_FENETRE-2*MARGE, 30))
    surf = police.render(message, True, NOIR)
    surface.blit(surf, (MARGE+5, HAUTEUR_FENETRE-37))

def tous_coules(grille):
    for r in range(1, 11):
        for c in range(1, 11):
            if grille[r][c] == "O":
                return False
    return True

# ---------- Boucle principale ----------
def boucle_principale():
    global orientation, apercu_case, etat, message, tour_joueur, derniere_action
    en_jeu = True
    while en_jeu:
        horloge.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                en_jeu = False
                break
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    en_jeu = False
                    break
                if ev.key == pygame.K_r and etat == "placement" and index_bateau < len(BATEAUX):
                    nom_bateau, _ = BATEAUX[index_bateau]
                    if nom_bateau == "Sous-marin":
                        if orientation not in ORIENTATIONS_SOUS_MARIN:
                            orientation = "haut"
                        else:
                            i = ORIENTATIONS_SOUS_MARIN.index(orientation)
                            orientation = ORIENTATIONS_SOUS_MARIN[(i + 1) % 4]
                    else:
                        orientation = "V" if orientation == "H" else "H"

            # Placement des bateaux
            if ev.type == pygame.MOUSEBUTTONDOWN and etat == "placement" and ev.button == 1:
                pos = ev.pos
                case = pixel_vers_case(pos[0], pos[1], True)
                if case:
                    lig, col = case
                    placer_bateau_joueur(lig, col)

            # Tir du joueur
            elif ev.type == pygame.MOUSEBUTTONDOWN and etat == "jeu" and tour_joueur and ev.button == 1:
                pos = ev.pos
                case = pixel_vers_case(pos[0], pos[1], False)
                if case:
                    lig, col = case
                    resultat = tirer_joueur(lig, col)
                    if tous_coules(grille_bot):
                        message = "Victoire ! Tous les bateaux ennemis coulés !"
                        etat = "fin"
                    elif resultat in ["raté", "deja"]:
                        # seul dans ce cas, le tour passe au bot
                        tour_joueur = False
                        derniere_action = time.time()
                    # sinon, si touché ou coulé, le joueur rejoue automatiquement

            # Aperçu placement
            elif ev.type == pygame.MOUSEMOTION and etat == "placement" and index_bateau < len(BATEAUX):
                pos = ev.pos
                apercu_case = pixel_vers_case(pos[0], pos[1], True)

        # --- Tour du bot ---
        if etat == "jeu" and not tour_joueur:
            if time.time() - derniere_action > delai_bot:
                bot_tir = tirer_bot()
                if tous_coules(grille_joueur):
                    message = "Défaite ! Tous tes bateaux sont coulés."
                    etat = "fin"
                elif not bot_tir:
                    # seul dans ce cas, le tour passe au joueur
                    tour_joueur = True
                else:
                    # bot touche, il rejoue automatiquement après petit délai
                    derniere_action = time.time() + 0.6

        # --- Affichage ---
        ecran.fill(BLEU)
        dessiner_interface(ecran, tour_joueur)
        dessiner_grille(ecran, grille_joueur, True, montrer=True)
        dessiner_grille(ecran, grille_bot_visible, False, montrer=False)
        if etat == "placement" and index_bateau < len(BATEAUX) and apercu_case:
            nom, taille = BATEAUX[index_bateau]
            lig, col = apercu_case
            dessiner_apercu(ecran, lig, col, taille, orientation)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

# Lancement
if __name__ == "__main__":
    boucle_principale()
