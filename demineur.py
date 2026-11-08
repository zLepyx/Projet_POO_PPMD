import numpy as np
import sys



# une case de la grille
class Case:
    def __init__(self, estMine, estDecouverte, drapeauPlace, nbMinesVoisines):
        self.estMine = estMine                  # True si la case contient une mine
        self.estDecouverte = estDecouverte      # True si le joueur a ouvert la case
        self.drapeauPlace = drapeauPlace        # True si le joueur a mis un drapeau
        self.nbMinesVoisines = nbMinesVoisines  # nombre de mines dans les 8 cases autour

    # ce qu'on affiche pour la case
    def __str__(self):
        if self.drapeauPlace:
            return "⚑"
        if not self.estDecouverte:
            return " "
        if self.estMine:
            return "*"
        if self.nbMinesVoisines == 0:
            return " "
        return str(self.nbMinesVoisines)






# le plateau de jeu : un tableau de cases
class Grille:
    def __init__(self, nbLignes, nbColonnes, nbMines):
        self.nbLignes = nbLignes
        self.nbColonnes = nbColonnes
        self.nbMines = nbMines
        self.minesPlacees = False          # les mines sont placées au premier clic
        self.mineExplosee = False          # True si le joueur a ouvert une mine
        self.nbDrapeauxBienPlaces = 0      # drapeaux posés sur une vraie mine
        self.nbDrapeauxBienPlaces = 0

        # Création d'une grille vide (sans mines) pour l'instant afin que le joueur
        # choisisse sa case de départ sans tomber directement sur une mine...

        self.cases = np.zeros((nbLignes, nbColonnes), dtype=object)

        for i in range(nbLignes):
            for j in range(nbColonnes):
                self.cases[i, j] = Case(False, False, False, 0)



    # place les mines au hasard, jamais sur la case du premier clic
    def placerMines(self, numeroLignePremierClic, numeroColonnePremierClic):

        # numéros de toutes les cases sauf celle du premier clic
        numeros = np.arange(self.nbLignes * self.nbColonnes)
        numeroClic = numeroLignePremierClic * self.nbColonnes + numeroColonnePremierClic
        numeros = numeros[numeros != numeroClic]


        # tirage de nbMines numéros distincts
        numerosMines = np.random.default_rng().choice(numeros, size=self.nbMines, replace=False)

        for i in range(self.nbLignes):
            for j in range(self.nbColonnes):
                self.cases[i, j].estMine = (i * self.nbColonnes + j) in numerosMines


        # Placement des numéros dans la grille
        for i in range(self.nbLignes):
            for j in range(self.nbColonnes):
                if not self.cases[i, j].estMine:
                    self.cases[i, j].nbMinesVoisines = self.calculerMinesVoisines(i, j)

        self.minesPlacees = True

    # compte les mines autour d'une case
    def calculerMinesVoisines(self, numeroLigne, numeroColonne):

        # calcul du numéro qui va signifier le nombre de mines adjacents a lui (ses 8 cases autour de lui)
        compteur = 0
        for i in range(numeroLigne - 1, numeroLigne + 2):
            for j in range(numeroColonne - 1, numeroColonne + 2):
                if i == numeroLigne and j == numeroColonne:      # on ne compte pas la case elle-même
                    continue
                if 0 <= i < self.nbLignes and 0 <= j < self.nbColonnes:   # on reste dans la grille
                    if self.cases[i, j].estMine:
                        compteur += 1
        return compteur



    # ouvre une case
    def revelerCase(self, numeroLigne, numeroColonne):

        case = self.cases[numeroLigne, numeroColonne]

        # déjà ouverte ou protégée par un drapeau : on ne fait rien
        if case.estDecouverte or case.drapeauPlace:
            return

        case.estDecouverte = True

        # c'est une mine : perdu
        if case.estMine:
            self.mineExplosee = True
            return

        # aucune mine autour : on ouvre aussi les voisines
        if case.nbMinesVoisines == 0:
            self.propagerRevelation(numeroLigne, numeroColonne)

    # premier clic : ouvre la case et ses voisines sans mine
    def revelerPremiereCase(self, numeroLigne, numeroColonne):

        # la case cliquée et ses voisines qui ne sont pas des mines
        self.revelerCase(numeroLigne, numeroColonne)

        for i in range(numeroLigne - 1, numeroLigne + 2):
            for j in range(numeroColonne - 1, numeroColonne + 2):
                if 0 <= i < self.nbLignes and 0 <= j < self.nbColonnes:
                    if not self.cases[i, j].estMine:
                        self.revelerCase(i, j)

    # ouvre les 8 cases autour d'une case
    def propagerRevelation(self, numeroLigne, numeroColonne):

        for i in range(numeroLigne - 1, numeroLigne + 2):
            for j in range(numeroColonne - 1, numeroColonne + 2):
                if i == numeroLigne and j == numeroColonne:
                    continue
                if 0 <= i < self.nbLignes and 0 <= j < self.nbColonnes:
                    self.revelerCase(i, j)

    # clic sur un chiffre : ouvre les voisines si assez de drapeaux autour
    def revelerVoisinesAutomatiquement(self, numeroLigne, numeroColonne):

        # seulement sur une case déjà découverte
        if not self.cases[numeroLigne, numeroColonne].estDecouverte:
            return

        # nombre de drapeaux posés autour (le joueur ne sait pas s'ils sont bien placés)
        compteur = 0
        for i in range(numeroLigne - 1, numeroLigne + 2):
            for j in range(numeroColonne - 1, numeroColonne + 2):
                if 0 <= i < self.nbLignes and 0 <= j < self.nbColonnes:
                    if self.cases[i, j].drapeauPlace:
                        compteur += 1

        # autant de drapeaux que le chiffre : on révèle les voisines sans drapeau
        # (revelerCase ignore déjà les cases avec un drapeau)
        if self.cases[numeroLigne, numeroColonne].nbMinesVoisines == compteur:
            self.propagerRevelation(numeroLigne, numeroColonne)



    # pose un drapeau et compte s'il est sur une mine
    def placerDrapeau(self, numeroLigne, numeroColonne):
        self.cases[numeroLigne, numeroColonne].drapeauPlace = True

        if self.cases[numeroLigne, numeroColonne].estMine:
            self.nbDrapeauxBienPlaces += 1

    # enlève un drapeau et met le compteur à jour
    def retirerDrapeau(self, numeroLigne, numeroColonne):
        self.cases[numeroLigne, numeroColonne].drapeauPlace = False

        if self.cases[numeroLigne, numeroColonne].estMine:
            self.nbDrapeauxBienPlaces -= 1

    # True si chaque mine a un drapeau et qu'il n'y a pas de drapeau en trop
    def tousLesDrapeauxBienPlaces(self):

        # nombre total de drapeaux posés 
        nbDrapeaux = 0
        for i in range(self.nbLignes):
            for j in range(self.nbColonnes):
                if self.cases[i, j].drapeauPlace:
                    nbDrapeaux += 1

        # toutes les mines ont un drapeau et aucun drapeau n'est en trop
        # sinon il suffirait de mettre des drapeaux partout pour gagner...
        return self.nbDrapeauxBienPlaces == self.nbMines and nbDrapeaux == self.nbMines

    # ouvre toutes les cases qui ne sont pas des mines
    def revelerCasesSansMine(self):
        for i in range(self.nbLignes):
            for j in range(self.nbColonnes):
                if not self.cases[i, j].estMine:
                    self.cases[i, j].estDecouverte = True

    # True si toutes les cases sans mine sont ouvertes
    def estGagnee(self):

        # gagné quand toutes les cases qui ne sont pas des mines sont découvertes
        for i in range(self.nbLignes):
            for j in range(self.nbColonnes):
                if not self.cases[i, j].estMine and not self.cases[i, j].estDecouverte:
                    return False
        return True

    # ouvre toute la grille 
    def revelerToutesLesCases(self):
        for i in range(self.nbLignes):
            for j in range(self.nbColonnes):
                self.cases[i, j].estDecouverte = True


    # affichage de la grille ligne par ligne
    def __str__(self):

        texte = ""

        for i in range(self.nbLignes):
            texteLigne = ""
            for j in range(self.nbColonnes):

                texteLigne += str(self.cases[i, j]) + " "

            texte = texte + texteLigne + "\n"

        return texte






# la partie gère les clics du joueur et la fin du jeu
class Demineur:
    def __init__(self, difficulte):
        self.difficulte = difficulte      
        self.partieTerminee = False        # True quand la partie est fini
        self.partieGagnee = False          # True si le joueur a gagné
        self.grille = None                 # la grille sera créé au démarrage


    # lance une nouvelle partie
    def demarrerPartie(self):
        self.creerGrille()

    # crée la grille selon la difficulté (tailles du démineur de Google)
    def creerGrille(self):
        coefs = {"facile": 1, "moyen": 1.75, "difficile": 2.5}
        coef = coefs[self.difficulte]

        nbLignes = int(8 * coef)
        nbColonnes = int(10 * coef)
        nbMines = int(10 * coef ** 2.5)

        self.grille = Grille(nbLignes, nbColonnes, nbMines)


    # clic gauche du joueur sur une case
    def clicGauche(self, numeroLigne, numeroColonne):
        if self.partieTerminee:
            return

        # au premier clic on place les mines puis on ouvre
        if not self.grille.minesPlacees:
            self.grille.placerMines(numeroLigne, numeroColonne)
            self.grille.revelerPremiereCase(numeroLigne, numeroColonne)

        # clic sur un chiffre déjà ouvert
        elif self.grille.cases[numeroLigne, numeroColonne].estDecouverte:
            self.grille.revelerVoisinesAutomatiquement(numeroLigne, numeroColonne)

        # clic sur une case cachée
        else:
            self.grille.revelerCase(numeroLigne, numeroColonne)
            self.grille.revelerVoisinesAutomatiquement(numeroLigne, numeroColonne)

        self.verifierFinPartie()

    # au clic droit du joueur pose ou enlève un drapeau
    def clicDroit(self, numeroLigne, numeroColonne):
        if self.partieTerminee:
            return

        # tant que les mines ne sont pas placées, un clic droit compte comme le premier clic
        if not self.grille.minesPlacees:
            self.clicGauche(numeroLigne, numeroColonne)
            return

        case = self.grille.cases[numeroLigne, numeroColonne]

        # pas de drapeau sur une case ouverte
        if case.estDecouverte:
            return

        if not case.drapeauPlace:
            self.grille.placerDrapeau(numeroLigne, numeroColonne)
        else:
            self.grille.retirerDrapeau(numeroLigne, numeroColonne)

        # si toutes les mines sont trouvées on dévoile le reste de la grille
        if self.grille.tousLesDrapeauxBienPlaces():
            self.grille.revelerCasesSansMine()

        self.verifierFinPartie()


    # regarde si la partie est perdue ou gagnée
    def verifierFinPartie(self):
        if self.grille.mineExplosee:
            self.partieTerminee = True
        elif self.grille.estGagnee():
            self.partieTerminee = True
            self.partieGagnee = True







if __name__ == "__main__":

    # test
    demineur = Demineur("facile")
    demineur.demarrerPartie()
    grille = demineur.grille

    print(grille)




