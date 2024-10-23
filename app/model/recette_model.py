class Recette:
    def __init__(self, nom, ingredient):
        self.nom = nom
        self.ingredient = ingredient

    def __str__(self):
        return f'{self.nom}, {self.ingredient}'