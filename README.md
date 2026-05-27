# Moteur Autonome - Surveillance Flotte Véhicules

**Auteur :** MAHENDRARAJAH Partheepan  
**Formation :** Mastère Product Manager – Studi  
**Module :** Bloc 3 – Industrialisation & Cycle de vie solution digitale

---

## Description

Moteur Python de surveillance en temps réel d'une flotte de camions, avec deux modules indépendants :

| Module | Algorithme | Input | Output |
|--------|-----------|-------|--------|
| ZFE (Geo) | Ray Casting + Bounding Box | `lyon_polygon.json`, `truck_gps.json` | Log `[ALERT ZFE]` |
| Safety (Physics) | Filtrage moyenneur + Seuil 2.5G | `accelerometer_data.csv` | `daily_score.json` |

---

## Structure du projet

```
moteur-autonome/
├── engine.py                    # Moteur principal
├── daily_score.json             # Output généré par le moteur
├── README.md
└── data/
    ├── lyon_polygon.json        # Polygone ZFE Lyon (GeoJSON simplifié)
    ├── truck_gps.json           # Positions GPS des camions
    └── accelerometer_data.csv  # Données accéléromètre (1200 échantillons)
```

---

## Procédure de test en local

### Prérequis
- Python 3.8+
- Aucune dépendance externe (stdlib uniquement : `json`, `csv`, `math`, `logging`)

### Installation & Lancement

```bash
# 1. Cloner le dépôt
git clone https://github.com/pmahendted-ops/studi-mastere-pm.git
cd studi-mastere-pm

# 2. Lancer le moteur
python3 engine.py
```

### Résultats attendus

```
[ALERT ZFE] TRK-001 en ZFE 'ZFE Lyon Centre' | pos=(45.758, 4.834)
[ALERT ZFE] TRK-002 en ZFE 'ZFE Lyon Centre' | pos=(45.755, 4.833)
...
[FREINAGE VIOLENT] TRK-001 2025-01-15T08:02:00 | 2.90G
[FREINAGE VIOLENT] TRK-002 2025-01-15T08:32:00 | 3.32G
...
-> daily_score.json généré
```

---

## Algorithmes

### Module 1 : ZFE – Ray Casting + Bounding Box

**Problème :** Déterminer si un camion est à l'intérieur d'une zone polygonale (ZFE).

**Algorithme Ray Casting (Shimrat, 1962) :**  
On lance un rayon horizontal depuis le point testé vers +∞. On compte le nombre d'intersections avec les arêtes du polygone. Si impair → point intérieur.

```
Point P = (lat, lon)
Pour chaque arête [Vi, Vj] du polygone :
    Si le rayon horizontal depuis P croise [Vi, Vj] :
        inverser le flag "inside"
Retourner inside
```

**Optimisation Bounding Box :**  
Avant le Ray Casting (O(n)), on vérifie en O(1) si le point est dans le rectangle englobant minimal. Si non → on court-circuite immédiatement, économisant n comparaisons.

```
Bounding Box = {min_lat, max_lat, min_lon, max_lon}
Si P ∉ BBox → retourner False (pas besoin de Ray Casting)
Sinon → lancer Ray Casting
```

### Module 2 : Safety – Filtrage/Seuil accéléromètre

**Problème :** Détecter les freinages violents (> 2.5G) dans un signal bruité.

**Pipeline :**

```
1. Lecture CSV → vecteurs (ax, ay, az) en G
2. Magnitude vectorielle : |a| = √(ax² + ay² + az²)
3. Filtre moyenneur glissant (fenêtre 5 pts) → atténue le bruit HF
4. Seuillage : si |a|_filtré > 2.5G → FREINAGE VIOLENT
5. Scoring : score = max(0, 100 - nb_events × 10)
```

**Format `daily_score.json` :**
```json
{
  "date": "2025-01-15",
  "threshold_g": 2.5,
  "scores": {
    "TRK-001": {
      "score": 70,
      "total_events": 3,
      "max_deceleration_g": 3.34,
      "risk_level": "MEDIUM",
      "events": [...]
    }
  }
}
```
