import pygame_menu
import pygame

import random

pygame.init()

#  Constantes
black = [0, 0, 0]
white = [255, 255, 255]
red = [255, 0, 0]
sky = 'lightblue'
WIDTH = 400  # Largeur de la fenêtre pygame
HEIGHT = 500  # Hauteur de la fenêtre pygame
skin1 = 'benoit.png'  # Avatar de base
skin2 = 'benoit_moust.png'  # Unlock après 100 points
font = pygame.font.Font('Eight-Bit Madness.ttf', 20)

#  Screen
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Benoit Jumper')

#  Initialisation du jeu
#  l'axe (x,y) de pygame prends pour valeur (0,0)
#  u point le plus haut à gauche de la fenêtre
background = white

timer = pygame.time.Clock()
fps = 60

avatar = skin1
doodle = pygame.transform.scale(pygame.image.load(avatar), (80, 80))  # On scale l'avatar à la taille de la fenêtre
doodle_x = 165  # Position initiale x
doodle_y = 400  # Position initiale y
platforms = [[175, 480, 70, 10], [265, 370, 70, 10], [175, 260, 70, 10],
             [265, 150, 70, 10], [175, 480, 70, 10], [85, 150, 70, 10]]  # Génération "fixe" des 6 premières plateformes
platforms_wrong = [[85, 370, 70, 10]]  # Plateformes pièges, permet de regler la difficultée
game_over = False

score = 0
high_score = 0
super_jump = 2
score_last = 0

doodle_speed = 3  # Vitesse de déplacement du doodle sur l'axe x
jump = False  # On saute pas
y_change = 0
x_change = 0


def update_platforms(plateform_list, y_pos, change):
    """
    Génération de plateformes dont les positions sont aléatoires
    La liste va être parcourue afin
    :param plateform_list:
    :param y_pos:
    :param change:
    :return plateform_list:
    """
    global score
    global super_jump
    if y_pos < 250 and change < 0:  # Permet le scrolling vertical des plateformes lorsque y est atteint
        for i in range(len(plateform_list)):
            plateform_list[i][1] -= change
    else:
        pass
    for y in range(len(plateform_list)):
        if plateform_list[y][1] > 500:  # Lorsque la plateforme sors de l'écran
            # On réutilise l'item actuel en créant une nouvelle plateforme avec des valeurs x, y random
            # Elles ne touchent pas les côtés de l'écran et nous voulons qu'elles se générent avant l'affichage
            plateform_list[y] = [random.randint(10, 320), random.randint(-50, -10), 70, 10]
            score += 1

    return plateform_list


def update_plateforms_wrong(platforms_list_wrong, y_pos, change):
    if y_pos < 250 and change < 0:  # Permet le scrolling vertical des plateformes lorsque y est atteint
        for i in range(len(platforms_list_wrong)):
            platforms_list_wrong[i][1] -= change
    else:
        pass
    for y in range(len(platforms_list_wrong)):
        if platforms_list_wrong[y][1] > 500:  # Lorsque la plateforme sors de l'écran
            # On réutilise l'item actuel en créant une nouvelle plateforme avec des valeurs x, y random
            # Elles ne touchent pas les côtés de l'écran et nous voulons qu'elles se générent avant l'affichage
            platforms_list_wrong[y] = [random.randint(10, 320), random.randint(-50, -10), 70, 10]

    return platforms_list_wrong


def check_collision(rect_list, ennemies_list, j):
    """
    Vérifie la collision entre une plateforme et le doodle
    :param rect_list:
    :param ennemies_list:
    :param j:
    :return j:
    """
    global doodle_x
    global doodle_y
    global y_change
    global game_over

    for i in range(len(rect_list)):
        #  En cas ce collision du doodle avec un block, la variable jump retourne O et est gérée dans update_doodle
        #  le "body" du doodle est manipulé afin de rentrer en colision avec l'affichage "réel" de celui-ci
        if rect_list[i].colliderect([doodle_x + 5, doodle_y + 70, 70, 10]) and jump is False and y_change > 0:
            j = True
    for y in range(len(ennemies_list)):
        #  En cas ce collision du doodle avec une plateforme rougedddddd, game over
        #  le "body" du doodle est manipulé afin de rentrer en colision avec l'affichage "réel" de celui-ci
        if ennemies_list[y].colliderect([doodle_x + 5, doodle_y + 70, 70, 10]) and jump is False and y_change > 0:
            game_over = True
            doodle_y = 450

    return j


def update_doodle(y_pos):
    """
    Update la position du doodle sur l'axe y
    :param y_pos:
    :return y_pos:
    """
    global jump
    global y_change
    jump_height = 10  # Hauteur du saut
    gravity = .4  # plus la valeur est base, plus l'inertie "gravitationnelle" est bas
    if jump:  # Si collision, le mouvement du saut est effectué
        y_change = -jump_height  # Valeur négative car pour monter dans l'axe y, la valeur de position doit descendre
        jump = False  # On réinitialise la variable pour la prochaine collision
    y_pos += y_change
    y_change += gravity  # La gravité permet au doodle de redescrendre après son saut

    return y_pos


def game_event_manager():
    """
    # Gère les événements pendant la partie
    :return:
    """
    global running
    global y_change
    global x_change
    global super_jump

    paused = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Si on quitte la fenêtre le jeu ne tourne plus...
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:  # On garde la touche pressée
            if event.key == pygame.K_w:  # Pause / Unpause
                paused = True
                if paused is True:  # On bloque la position du doodle en cas de pause
                    y_change = 0
                    x_change = 0
            if event.key == pygame.K_SPACE and game_over:  # Si Game Over + Spacebar : Restart la partie
                restart()
            if event.key == pygame.K_SPACE and game_over is False and super_jump > 0:  # Sinon, lance un super saut
                super_jump -= 1
                y_change = -15
            if event.key == pygame.K_q:  # Touche Q
                x_change = -doodle_speed  # Vers la gauche sur l'axe X
            if event.key == pygame.K_d:  # Touche D
                x_change = doodle_speed  # Vers la droite sur l'axe X

        if event.type == pygame.KEYUP:  # Lors de l'appui/relachement de la touche

            if event.key == pygame.K_q:  # Touche Q
                x_change = 0  # Rien ne se passe, on veux que le personnage soit immobile sur l'axe X
            if event.key == pygame.K_d:  # Touche D
                x_change = 0  # Rien ne se passe, on veux que le personnage soit immobile sur l'axe X


def gamescreen_init():
    """
    Initialise l'écran de jeu avec les différents éléments "fixes" lors du début d'une partie
    :return:
    """
    screen.fill(sky)
    screen.blit(doodle, (doodle_x, doodle_y))  # Position initiale du doodle

    high_score_text = font.render('High Score: ' + str(high_score), True, black, background)  # Affiche le High Score
    screen.blit(high_score_text, (280, 0))

    score_text = font.render('Score: ' + str(score), True, black, background)  # Affiche le Score
    screen.blit(score_text, (320, 20))

    super_jump_text = font.render('Super Jump (spacebar): ' + str(super_jump), True, black,
                                  background)  # Affiche le Super Jump
    screen.blit(super_jump_text, (10, 10))


def game_update():
    """
    Permet d'upate les différents éléments du jeu (doodle, plateforme)
    Detecte les cas de GameOver et empeche les collisions sur les bords de l'écran
    :return:
    """
    global doodle_x
    global doodle_y
    global x_change
    global y_change
    global game_over
    global platforms
    global platforms_wrong

    doodle_x += x_change
    if doodle_y < 440:  # Si le doodle n'est pas en bas de l'écran, sa position est update
        doodle_y = update_doodle(doodle_y)
    else:  # Sinon, la partie est finie
        game_over = True
        y_change = 0
        x_change = 0

    platforms = update_platforms(platforms, doodle_y, y_change)
    platforms_wrong = update_plateforms_wrong(platforms_wrong, doodle_y, y_change)

    if doodle_x < -20:  # Evite les collisions côté droit en remettant le doodle a la position max choisie
        doodle_x = -20
    elif doodle_x > 330:  # Evite les collisions côté gauche en remettant le doodle a la position max choisie
        doodle_x = 330


def doodle_switch():
    """
    Change l'orientation du skin du doodle selon la direction sur l'axe X
    :return:
    """
    global doodle

    if x_change > 0:  # Si on va vers la gauche, le doodle pointera vers la gauche ( le png est dans cet état de base )
        doodle = pygame.transform.scale(pygame.image.load(avatar), (80, 80))
    elif x_change < 0:  # Si on va vers la droite, le doodle pointera vers la droite ( grace à la fonction flip )
        doodle = pygame.transform.flip(pygame.transform.scale(pygame.image.load(avatar), (80, 80)), True, False)

def gameover_txt():
    """
    Affiche un texte lors d'un game over
    :return:
    """
    game_over_text = font.render('Game Over: Spacebar to restart', True, black, background)  # Affiche le Game Over
    screen.blit(game_over_text, (80, 80))


def restart():
    """
    Permet de réinitialiser les variables lors d'un game over
    :return:
    """
    global game_over
    global score
    global doodle_x
    global doodle_y
    global background
    global platforms
    global super_jump
    global score_last
    global platforms_wrong

    game_over = False
    score = 0
    doodle_x = 165
    doodle_y = 400
    background = white
    platforms = [[175, 480, 70, 10], [265, 370, 70, 10], [175, 260, 70, 10],
                 [265, 150, 70, 10], [175, 480, 70, 10], [85, 150, 70, 10]]
    platforms_wrong = [[85, 370, 70, 10]]
    super_jump = 3
    score_last = 0


def play():
    """
    # Fonctionnement du jeu
    :return:
    """
    global jump
    global avatar
    global high_score
    global super_jump
    global score_last

    timer.tick(fps)  # Limite les FPS à 60
    blocks = []  # Génération de la liste des plateformes
    ennemies = []
    scoretrue = False
    gamescreen_init()
    if game_over:  # Affiche le game over si besoin
        gameover_txt()

    for i in range(len(platforms)):  # Fonction permettant de dessiner les plateformes et les ajoutes a la liste
        block = pygame.draw.rect(screen, black, platforms[i], 0, 3)
        blocks.append(block)

# Test d'incrémentation de la difficulté [WIP]
# Théorie : le jeu marche par frame, nous restons donc x frame à score = 10 et le jeu réitère la boucle plusieurs fois
#    if score == 10:
#       scoretrue = True
#       if scoretrue == True:
#            new_plateform_wrong = [random.randint(10, 320), random.randint(-50, -10), 70, 10]
#            platforms_wrong.append(new_plateform_wrong)
#            scoretrue = False

    for y in range(len(platforms_wrong)):
        ennemie = pygame.draw.rect(screen, red, platforms_wrong[y], 0, 3)
        ennemies.append(ennemie)

    game_event_manager()
    jump = check_collision(blocks, ennemies, jump)

    game_update()

    if high_score > 100:  # Swap vers le Benoit à moustache dès que le joueur atteint les 100 de score
        avatar = skin2

    doodle_switch()

    if score > high_score:  # Affiche le meilleur score de la session en cours
        high_score = score
    if score - score_last > 50:  # Offre un bonus super jump tout les 50 de score
        score_last = score
        super_jump += 1

    pygame.display.flip()  # Update l'écran de jeu


def start_the_game():
    """
    S'assure de rester sur l'écran de jeu une fois qu'on lance la partie
    :return:
    """
    while running is True:
        play()


def main_menu():
    """
    Affiche la page de menu
    :return:
    """
    menu = True

    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        themefont = pygame_menu.font.FONT_8BIT
        titlefont = pygame.font.Font('Eight-Bit Madness.ttf', 30)
        montheme = pygame_menu.Theme(  # Theme personnalisé
            background_color=white,  # Couleur du fond
            title_font=titlefont,  # Police du titre
            title_font_color=black,  # Couleur du titre
            title_offset=(100, 100),  # Position du titre
            title_font_size=24,  # Taille de police du titre
            title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,  # Pas de "barre de menu"
            widget_font=themefont,  # Police des widgets
            selection_color=black,  # Couleur lors de l'hovering des widgets
        )

        menu = pygame_menu.Menu('Benoit Jumper !', 400, 500,
                                theme=montheme)  # Utilisation du thème défini plus tôt

        menu.add.button('Play', start_the_game)  # S'assure de lancer la partie et de rester sur l'écran de jeu
        menu.add.button('Quit', pygame_menu.events.EXIT)  # Quitte le jeu

        menu.mainloop(screen)  # On loop sur l'écran de menu


running = True
while running:
    main_menu()

pygame.quit()
