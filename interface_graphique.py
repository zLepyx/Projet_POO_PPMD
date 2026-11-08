import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QComboBox, QGridLayout, QLayout

from demineur import Demineur


# la fenêtre du jeu
class Fenetre(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        # la partie en cours
        self.demineur = Demineur("facile")
        self.demineur.demarrerPartie()

        # menu pour choisir la difficulté
        self.choixDifficulte = QComboBox()
        self.choixDifficulte.addItems(["facile", "moyen", "difficile"])
        self.choixDifficulte.currentTextChanged.connect(self.changerDifficulte)

        # bouton pour relancer une partie
        self.boutonRecommencer = QPushButton("Recommencer")
        self.boutonRecommencer.clicked.connect(self.recommencer)



        # la grille de boutons 
        self.grilleLayout = QGridLayout()

        # tout est empilé de haut en bas
        layout = QVBoxLayout()


        # texte d'information 
        self.labelInfo = QLabel("Cliquez sur une case pour démarrer la partie")
        self.labelInfo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.choixDifficulte)
        layout.addWidget(self.labelInfo)
        layout.addWidget(self.boutonRecommencer)

        layout.addLayout(self.grilleLayout)


        # la fenêtre prend la taille de la grille
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)

        # cases collées les unes aux autres
        self.grilleLayout.setSpacing(0)

        self.construireGrille()




        self.setWindowTitle("Démineur")
        self.show()



    # nouvelle partie : nouveau démineur et nouveau boutons
    def nouvellePartie(self, difficulte):
        self.demineur = Demineur(difficulte)
        self.demineur.demarrerPartie()

        # on enlève les anciens boutons
        for ligne in self.boutons:
            for bouton in ligne:
                self.grilleLayout.removeWidget(bouton)
                bouton.deleteLater()

        self.choixDifficulte.setEnabled(True)
        self.construireGrille()
        self.actualiser()

    # bouton Recommencer : nouvelle partie avec la même difficulté
    def recommencer(self):
        self.nouvellePartie(self.choixDifficulte.currentText())

    # crée un bouton pour chaque case de la grille
    def construireGrille(self):
        grille = self.demineur.grille
        self.boutons = []                      # tableau de boutons

        for i in range(grille.nbLignes):
            ligneBoutons = []
            for j in range(grille.nbColonnes):
                bouton = BoutonCase(i, j)
                bouton.setStyleSheet("background-color: #a0a0a0")
                bouton.clicGauche.connect(self.clicGaucheSurCase)    # clic gauche
                bouton.clicDroit.connect(self.clicDroitSurCase)      # clic droit 

                self.grilleLayout.addWidget(bouton, i, j)
                ligneBoutons.append(bouton)
            self.boutons.append(ligneBoutons)



    # menu de difficulté changé : nouvelle grille
    def changerDifficulte(self, texte):
        self.demineur = Demineur(texte)
        self.demineur.demarrerPartie()

        for ligne in self.boutons:
            for bouton in ligne:
                self.grilleLayout.removeWidget(bouton)
                bouton.deleteLater()
        self.construireGrille()

    # le joueur fait un clic gauche sur la case
    def clicGaucheSurCase(self, ligneclique , coloneclique):
        self.demineur.clicGauche(ligneclique , coloneclique)

        self.actualiser()

    # le joueur fait un clic droit sur la case
    def clicDroitSurCase(self, ligneclique , coloneclique):
        self.demineur.clicDroit(ligneclique , coloneclique)
        self.actualiser()

    # met à jour l'affichage à partir de la grille
    def actualiser(self):
        grille = self.demineur.grille

        # compte les drapeaux posés
        nbDrapeauxPlaces = 0
        for i in range(grille.nbLignes):
            for j in range(grille.nbColonnes):
                if grille.cases[i, j].drapeauPlace:
                    nbDrapeauxPlaces += 1

        self.labelInfo.setText("Drapeaux restants : " + str(grille.nbMines - nbDrapeauxPlaces))



        # on ne change pas de difficulté pendant une partie
        if grille.minesPlacees:
            self.choixDifficulte.setEnabled(False)
        if self.demineur.partieTerminee:
            self.choixDifficulte.setEnabled(True)

        # texte et couleur de chaque bouton
        for i in range(grille.nbLignes):
            for j in range(grille.nbColonnes):
                case = grille.cases[i, j]
                bouton = self.boutons[i][j]

                bouton.setText(str(case))

                if case.estDecouverte:
                    bouton.setStyleSheet("background-color: #e5e5e5")    # découverte
                else:
                    bouton.setStyleSheet("background-color: #a0a0a0")    # cachée




        # fin de partie
        if self.demineur.partieTerminee:
            # gagné
            if self.demineur.partieGagnee:
                self.labelInfo.setText("Tu as gagné !")


                self.demineur.grille.revelerToutesLesCases()
                for i in range(grille.nbLignes):
                    for j in range(grille.nbColonnes):
                        case = grille.cases[i, j]
                        bouton = self.boutons[i][j]

                        bouton.setText(str(case))

                        if case.nbDrapeauxBienPlaces:
                            bouton.setStyleSheet("background-color: #f70000")
                        if case.estDecouverte:
                            bouton.setStyleSheet("background-color: #e5e5e5")


            # perdu on montre toutes les mines en rouge
            else:
                self.labelInfo.setText("Tu as perdu !")
                self.demineur.grille.revelerToutesLesCases()
                for i in range(grille.nbLignes):
                    for j in range(grille.nbColonnes):
                        case = grille.cases[i, j]
                        bouton = self.boutons[i][j]

                        bouton.setText(str(case))


                        if case.estMine:
                            bouton.setStyleSheet("background-color: #f70000")

                        if case.estDecouverte and not case.estMine:
                            bouton.setStyleSheet("background-color: #e5e5e5")


# un bouton de la grille qui sait quelle case il représente
class BoutonCase(QPushButton):
    clicGauche = pyqtSignal(int, int)     
    clicDroit = pyqtSignal(int, int)     

    def __init__(self, ligneclique, coloneclique):
        QPushButton.__init__(self, " ")
        self.ligneclique = ligneclique                        # numéro de ligne
        self.coloneclique = coloneclique                        # numéro de colonne
        self.setFixedSize(40, 40)

    # quand on clique 
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicGauche.emit(self.ligneclique, self.coloneclique)
        elif event.button() == Qt.RightButton:
            self.clicDroit.emit(self.ligneclique, self.coloneclique)





# lance la fenêtre du jeu
if __name__ == "__main__":


    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    fen = Fenetre()

    app.exec_()



