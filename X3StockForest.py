import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

# Charger les données
file_path = "mouvements_stock.csv"
data = pd.read_csv(file_path, sep=';', low_memory=False)

# Prétraitement des données
data['Quantite_PCU'] = pd.to_numeric(data['Quantite_PCU'].str.replace(',', '.'), errors='coerce')
data['Quantite_STU'] = pd.to_numeric(data['Quantite_STU'].str.replace(',', '.'), errors='coerce')
data['Date_Mouvement'] = pd.to_datetime(data['Date_Mouvement'], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')

# Trier et calculer les caractéristiques
data = data.sort_values(by=['Article', 'Date_Mouvement'])
data['Délai_entre_mouvements'] = data.groupby('Article')['Date_Mouvement'].diff().dt.days.fillna(0)
data['Variation_Quantite'] = data.groupby('Article')['Quantite_PCU'].diff().fillna(0)
data['Moyenne_mobile_Quantite'] = data.groupby('Article')['Quantite_PCU'].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
data['Variation_Pourcentage'] = data.groupby('Article')['Quantite_PCU'].pct_change().fillna(0)
data['Heure_Mouvement'] = data['Date_Mouvement'].dt.hour

# Gestion des valeurs manquantes et infinies
stat_cols = ['Type_Statistique_0', 'Type_Statistique_1', 'Type_Statistique_2', 'Type_Statistique_3', 'Type_Statistique_4']
data[stat_cols] = data[stat_cols].fillna('ZZZZZ')
numeric_cols = ['Quantite_PCU', 'Quantite_STU', 'Délai_entre_mouvements', 'Variation_Quantite', 'Moyenne_mobile_Quantite', 'Variation_Pourcentage', 'Heure_Mouvement']
data[numeric_cols] = data[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(0)

# Sélectionner les features
cat_cols = ['Type_Piece', 'Type_Mouvement'] + stat_cols
features = numeric_cols + cat_cols

# Créer un pipeline de prétraitement
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
    ])

# Créer un pipeline avec prétraitement et Isolation Forest
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('iforest', IsolationForest(contamination=0.01, random_state=42, n_estimators=100))
])

# Entraîner le modèle
pipeline.fit(data[features])

# Prédire les anomalies
data['anomaly_score'] = pipeline.decision_function(data[features])
data['anomalie'] = pipeline.predict(data[features])

# Visualiser la distribution des scores d'anomalie
plt.figure(figsize=(10, 6))
plt.hist(data['anomaly_score'], bins=50)
plt.xlabel('Score d\'anomalie')
plt.ylabel('Fréquence')
plt.title('Distribution des scores d\'anomalie')
plt.show()

# Filtrer les anomalies
anomalies = data[data['anomalie'] == -1]

# Définir le seuil dans tous les cas
seuil = np.percentile(data['anomaly_score'], 5)  # Les 5% les plus anormaux

print(f"Nombre d'anomalies détectées : {len(anomalies)}")
if len(anomalies) > 0:
    print(anomalies.head())
else:
    print("Aucune anomalie détectée avec la méthode directe. Utilisation du seuil ajusté...")
    anomalies = data[data['anomaly_score'] <= seuil]
    print(f"Nombre d'anomalies après ajustement : {len(anomalies)}")
    print(anomalies.head())

# Exporter les résultats
if len(anomalies) > 0:
    anomalies.to_csv('anomalies_detectees.csv', index=False)
    print("Fichier 'anomalies_detectees.csv' créé avec succès.")
else:
    print("Aucune anomalie à exporter.")

# Afficher des statistiques supplémentaires
print("\nStatistiques des scores d'anomalie:")
print(data['anomaly_score'].describe())

# Visualiser la distribution des scores d'anomalie avec le seuil
plt.figure(figsize=(10, 6))
plt.hist(data['anomaly_score'], bins=50)
plt.axvline(x=seuil, color='r', linestyle='--', label='Seuil d\'anomalie')
plt.xlabel('Score d\'anomalie')
plt.ylabel('Fréquence')
plt.title('Distribution des scores d\'anomalie avec seuil')
plt.legend()
plt.show()

# Afficher les 10 anomalies les plus significatives
if len(anomalies) > 0:
    print("\nLes 10 anomalies les plus significatives :")
    print(anomalies.sort_values('anomaly_score').head(10))

# Analyse supplémentaire par type de mouvement
print("\nRépartition des anomalies par type de mouvement :")
print(anomalies['Type_Mouvement'].value_counts(normalize=True))

# Analyse temporelle des anomalies
anomalies['Date_Mouvement'] = pd.to_datetime(anomalies['Date_Mouvement'])
anomalies['Mois'] = anomalies['Date_Mouvement'].dt.to_period('M')
anomalies_par_mois = anomalies.groupby('Mois').size()

plt.figure(figsize=(12, 6))
anomalies_par_mois.plot(kind='bar')
plt.title('Nombre d\'anomalies par mois')
plt.xlabel('Mois')
plt.ylabel('Nombre d\'anomalies')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()