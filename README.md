# POC GML Edge IoT

## Lancer le test

```bash
python poc_gml_improved.py
```

Le script lit `data_geo.json` et `accelerometer_data.csv`, affiche les alertes ZFE, puis génère `daily_score.json`.

## Ce qui est testé

- Optimisation Bounding Box avant Ray Casting.
- Détection Point in Polygon.
- Détection de freinage violent par magnitude/seuil.
- Export JSON exploitable pour scoring assurance.
