INSERT INTO Recette (nom, ingredient) VALUES
('Poulet au beurre', 'Poulet, Beurre, Oignon, Ail, Gingembre, Crème épaisse, Sauce tomate, Garam masala, Cumin'),
('Gâteau au chocolat', 'Chocolat, Farine, Sucre, Beurre, Oeufs, Levure chimique, Sel'),
('Lasagne végétarienne', 'Pâtes à lasagne, Sauce tomate, Fromage ricotta, Épinards, Fromage mozzarella, Courgettes, Ail'),
('Pizza Margherita', 'Pâte à pizza, Sauce tomate, Mozzarella, Basilic frais, Huile d'/'olive, Sel'),
('Curry de pois chiches', 'Pois chiches, Lait de coco, Pâte de curry, Tomates concassées, Épinards, Oignon, Ail, Gingembre'),
('Salade César', 'Laitue romaine, Croûtons, Parmesan, Poulet grillé, Sauce César, Anchois, Citron'),
('Soupe à l'/'oignon', 'Oignon, Bouillon de boeuf, Vin blanc, Beurre, Farine, Pain, Fromage gruyère'),
('Tacos au poisson', 'Tortillas, Poisson, Chou rouge, Crème aigre, Coriandre, Citron vert, Piment jalapeño'),
('Crêpes sucrées', 'Farine, Sucre, Lait, Oeufs, Beurre, Vanille, Sirop d'/'érable'),
('Riz sauté aux légumes', 'Riz, Carottes, Petits pois, Oignons verts, Sauce soja, Oeufs, Huile de sésame, Gingembre');

SELECT *
FROM Recette
WHERE ingredient LIKE '%Poulet%';


CREATE TABLE IF NOT EXISTS Recette (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        ingredient TEXT)