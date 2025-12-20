# 📊 Projet BI Northwind - Solution Complète

## 🎯 Objectif du Projet

Ce projet présente une solution complète de Business Intelligence (BI) basée sur la célèbre base de données Northwind. Il démontre toutes les étapes d'un pipeline ETL moderne et la création d'un tableau de bord analytique interactif.

### Fonctionnalités principales :
- ✅ Extraction des données depuis des fichiers Excel/CSV (ou depuis une base SQL si nécessaire)
- ✅ Transformation et nettoyage des données avec Python/Pandas
- ✅ Création de métriques analytiques et KPIs
- ✅ Tableau de bord interactif avec visualisations dynamiques
- ✅ Génération de rapports et graphiques exportables

---

## 📁 Structure du Projet

```
Project-BI/
│
├── data/
│   ├── raw/                    # Données sources (Excel/CSV)
│   ├── processed/              # Données transformées (CSV) prêtes pour le reporting
│   └── northwind_analytics.db  # Base analytique SQLite (générée par scripts/load.py)
│
├── scripts/
│   ├── etl_main.py             # Orchestrateur ETL (extrait + transforme + charge)
│   ├── extract.py              # Extraction (depuis Excel/CSV -> data/raw/)
│   ├── transform.py            # Nettoyage / enrichissement -> data/processed/
│   ├── load.py                 # Chargement des CSV transformés vers SQLite + rapports
│   └── dashboard.py            # Dashboard interactif (Dash + Plotly)
│
├── figures/                    # Graphiques générés (statics)
├── reports/                    # Rapports Excel/PDF générés
├── notebooks/                  # Notebooks Jupyter d'analyse
│
├── README.md                   # Ce fichier
└── requirements_windows.txt    # Dépendances Python (Windows)
```

---

## 🚀 Installation et Configuration

### 1. Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Base de données Northwind (SQLite, SQL Server, ou Access)

### 2. Installation des dépendances

```bash
# Cloner ou télécharger le projet
cd Project-BI

# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances (Windows)
pip install -r requirements_windows.txt
```

### 3. Source des données

Ce projet supporte plusieurs sources principales :

- **Fichiers Excel** originaux (ex. `Customers.xlsx`, `Orders.xlsx`, `Products.xlsx`) placés dans `data/`.
- **Fichiers CSV** préexistants dans `data/raw/` (le script `extract.py` peut prendre des CSVs comme entrée).
- **Base SQL** : tables ayant la même structure que les fichiers Excel. Pour charger depuis une base SQL, utilisez l'option `--source sql` et fournissez une SQLAlchemy connection string via `--db-conn`.

Exemples :

```bash
# Extraction depuis une base SQLite
python scripts/extract.py --source sql --db-conn "sqlite:///data/northwind.db"

# Orchestrer tout le pipeline depuis une base SQL
python scripts/etl_main.py --source sql --db-conn "sqlite:///data/northwind.db"

# Exemple SQL Server (ODBC) :
python scripts/extract.py --source sql --db-conn "mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server"
```

> 💡 Si les noms de tables dans la base diffèrent des noms attendus (ex: `customers`, `orders`), vous pouvez adapter le mapping `db_table_map` dans `scripts/extract.py` pour faire correspondre les clés logiques aux noms de table réels.

Placez vos fichiers Excel/CSV dans `data/` (ou `data/raw/`) avant de lancer l'extraction. Le script `load.py` créera ensuite la base SQLite analytique `data/northwind_analytics.db`.


---

## 🎬 Exécution du Projet

### Étape 1 : Extraction des données

```bash
# Extraction depuis les fichiers Excel (défaut)
python scripts/extract.py

# Extraction depuis une base SQL (ex: SQLite)
python scripts/extract.py --source sql --db-conn "sqlite:///data/northwind.db"
```

**Ce que fait ce script :**
- Charge les fichiers Excel depuis `data/` (ou lit CSVs déjà présents dans `data/raw/`).
- Si le fichier `Order Details` est absent, le script génère des lignes de commande **simulées** pour chaque commande. La simulation est **déterministe** (seedée par `OrderID`) et s'appuie sur la liste des produits dans `Products.xlsx`, ce qui permet d'obtenir des métriques stables (ex: **Panier moyen**) entre les exécutions.
- Génère des fichiers CSV dans `data/raw/` (customers.csv, orders.csv, sales_analysis_complete.csv, etc.).

> 💡 Option : si vous préférez que la simulation soit persistée (fichier `data/raw/order_details_simulated.csv`) pour inspection ou réutilisation, je peux ajouter un paramètre pour enregistrer la simulation au lieu de la régénérer à chaque extraction.

**Résultat attendu :**
```
✓ Chargement des fichiers source depuis data/
✓ Fichiers convertis / exportés vers data/raw/ (customers.csv, orders.csv, sales_analysis_complete.csv, ...)
```

---

### Étape 2 : Transformation des données

```bash
python scripts/transform.py
```

**Ce que fait ce script :**
- Charge `data/raw/sales_analysis_complete.csv` (ou `sales_analysis.csv` en fallback).
- Nettoie, enrichit et calcule des composantes temporelles.
- Crée et conserve un indicateur `WasShipped` (basé sur la présence initiale de `ShippedDate` **avant** tout remplissage/post-traitement) pour permettre au dashboard d'identifier correctement les commandes non-livrées.
- Calcule des agrégations (monthly_sales, category_sales, top_products, country_sales, employee_sales, etc.).
- Sauvegarde les outputs CSV dans `data/processed/` (sales_clean.csv, kpis.csv, monthly_sales.csv, ...).

> ⚠️ Remarque : Si vous mettez à jour la logique d'extraction (par ex. simulation des détails de commande), **re-lancez** `python scripts/transform.py` pour régénérer `sales_clean.csv` afin que les nouveaux flags et imputations soient appliqués.

**Résultat attendu :**
```
🧹 Nettoyage des données de ventes...
  • Dates converties
  • Composantes temporelles ajoutées
  • Valeurs manquantes: 150 → 0

📊 Création des métriques agrégées...
  • monthly_sales: 24 lignes
  • category_sales: 8 lignes
  • top_products: 20 lignes
  
💰 KPIs principaux:
  • Revenu total: $1,354,458.59
  • Commandes: 830
  • Clients: 89
```

---

### Étape 3 : Chargement et Dashboard

Vous pouvez charger les données transformées dans une base SQLite et générer un rapport, puis démarrer le dashboard.

```bash
# Lancer le chargement dans SQLite et création de rapports
python scripts/load.py

# (Optionnel) Orchestrer tout le pipeline (extract -> transform -> load)
python scripts/etl_main.py

# Lancer le dashboard (port 8080 par défaut)
python scripts/dashboard.py
```

**Ce que fait ces scripts :**
- `load.py`: charge les CSV transformés dans `data/northwind_analytics.db`, crée des vues et index, et génère un rapport Excel (`reports/rapport_northwind.xlsx`).
- `etl_main.py`: orchestre l'extraction, la transformation et le chargement en séquence.
- `dashboard.py`: démarre un serveur Dash et sert le dashboard interactif sur `http://localhost:8080`.

**Résultat attendu :**
```
🚀 Lancement du dashboard...
📡 Serveur démarré sur http://localhost:8080
💡 Ouvrez votre navigateur à cette adresse
```

Ouvrez votre navigateur et allez à : **http://localhost:8080**

---

## 📊 Indicateurs Clés (KPIs)

Le tableau de bord présente les KPIs suivants :

### KPIs Principaux
1. **💰 Revenu Total** : Somme de toutes les ventes
2. **📦 Nombre de Commandes** : Total des commandes passées
3. **👥 Nombre de Clients** : Clients uniques actifs
4. **📊 Panier Moyen** : Valeur moyenne par commande
5. **🚚 Délai de Livraison Moyen** : En jours

### Visualisations Disponibles

1. **📈 Évolution des ventes mensuelles**
   - Graphique en ligne montrant la tendance temporelle
   - Permet d'identifier la saisonnalité

2. **🎯 Répartition par catégorie**
   - Diagramme circulaire des ventes par catégorie de produits
   - Identifie les catégories les plus rentables

3. **🏆 Top 10 Produits**
   - Graphique à barres horizontales
   - Classement des produits les plus vendus

4. **🌍 Ventes par Pays**
   - Graphique à barres des ventes géographiques
   - Top 15 pays par revenus

5. **👔 Performance des Employés**
   - Comparaison des ventes par employé
   - Nombre de commandes traitées

---

## 🛠️ Choix Techniques

### Bibliothèques Python Utilisées

| Bibliothèque | Usage | Justification |
|-------------|-------|---------------|
| **Pandas** | Manipulation de données | Standard de l'industrie, performant, facile à utiliser |
| **SQLAlchemy** | Connexion BDD | Compatible avec tous types de bases de données |
| **Plotly** | Visualisations | Graphiques interactifs modernes et élégants |
| **Dash** | Dashboard web | Framework Python pour applications web analytiques |
| **NumPy** | Calculs numériques | Optimisé pour les opérations mathématiques |

### Architecture Choisie

**Pipeline ETL Modulaire**
- ✅ Séparation claire Extract / Transform / Load
- ✅ Chaque script peut être exécuté indépendamment
- ✅ Facilite le débogage et la maintenance
- ✅ Permet la réutilisation du code

**Stockage en CSV**
- ✅ Format universel et léger
- ✅ Facile à inspecter et déboguer
- ✅ Compatible avec tous les outils d'analyse
- ✅ Versionnable avec Git

---

## 📈 Analyses Possibles

Ce projet permet de répondre à des questions d'affaires telles que :

1. **Analyse des ventes**
   - Quelle est la tendance des ventes sur la période ?
   - Quels sont les mois les plus rentables ?
   - Y a-t-il une saisonnalité ?

2. **Analyse produits**
   - Quels produits génèrent le plus de revenus ?
   - Quelles catégories sont les plus populaires ?
   - Quel est le taux de réachat ?

3. **Analyse géographique**
   - Quels pays achètent le plus ?
   - Où concentrer les efforts commerciaux ?

4. **Analyse RH**
   - Quels employés sont les plus performants ?
   - Quelle est la charge de travail par employé ?

5. **Analyse logistique**
   - Quel est le délai moyen de livraison ?
   - Y a-t-il des retards significatifs ?

---

## 🎓 Pour Aller Plus Loin

### Améliorations Possibles

1. **Analyse prédictive**
   - Prévision des ventes futures (Machine Learning)
   - Détection d'anomalies

2. **Dashboard avancé**
   - Filtres interactifs par période/catégorie
   - Export de rapports PDF automatisés
   - Alertes en temps réel

3. **Optimisation**
   - Utilisation de bases de données NoSQL (MongoDB)
   - Cache des résultats pour améliorer les performances
   - Parallélisation du traitement

4. **Déploiement**
   - Hébergement sur cloud (AWS, Azure, Heroku)
   - Mise en place d'API REST
   - Automatisation avec Airflow

---

## 🐛 Dépannage

### Problème : Erreur de connexion à la base

**Solution :**
- Si vous utilisez la base SQLite originale Northwind, vérifiez que le fichier `northwind.db` est présent dans `data/`.
- Si vous utilisez le pipeline ETL, vérifiez que `data/northwind_analytics.db` (généré par `load.py`) existe ou exécutez `python scripts/load.py` pour le créer.
- Assurez-vous que les chemins d'accès aux fichiers sont corrects et que vous avez les droits en lecture/écriture.

### Problème : Module introuvable

**Solution :** Assurez-vous que l'environnement virtuel est activé et que les dépendances sont installées :
```bash
pip install -r requirements_windows.txt
```

### Problème : Le dashboard ne s'affiche pas

**Solution :** Vérifiez que le port 8080 n'est pas déjà utilisé. Changez le port si nécessaire :
```python
dashboard.run(debug=True, port=8081)
```

### Problème : Le "Panier moyen" change d'une exécution à l'autre

**Symptôme :** La métrique *AvgOrderValue* varie significativement après chaque exécution de l'ETL (extract/transform/load).

**Cause :** Lorsqu'il n'y a pas de table `Order Details`, le `scripts/extract.py` génère des lignes de commande simulées. Avant la dernière mise à jour, la simulation utilisait un tirage réellement aléatoire, d'où des variations à chaque exécution.

**Solution :** Le comportement a été rendu **déterministe** : la simulation est maintenant seedée par `OrderID` et utilise la liste de produits de `Products.xlsx`, ce qui stabilise la valeur de *Panier moyen* entre exécutions. Si vous souhaitez inspecter ou persister les résultats de la simulation (fichier `data/raw/order_details_simulated.csv`), demandez-moi et j'ajouterai l'option de persistance.

---

## 📚 Ressources Additionnelles

- [Documentation Pandas](https://pandas.pydata.org/docs/)
- [Documentation Plotly](https://plotly.com/python/)
- [Documentation Dash](https://dash.plotly.com/)
- [Base Northwind Officielle](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/northwind-pubs)

---

## 👤 Auteur
Slimani imad zakaria el hadj ··
232331397617 ·· 
Projet Bisnes Intelligence 3eme ingenieur cybersecurity

---

## 📄 Licence

Ce projet est fourni à des fins éducatives. La base de données Northwind est une propriété de Microsoft mise à disposition publiquement.

---

## 🙏 Remerciements

- Microsoft pour la base de données Northwind
- La communauté Python pour les excellentes bibliothèques open-source
- Tous les contributeurs et formateurs

---

