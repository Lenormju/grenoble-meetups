# Newsletter LinkedIn

Préparer la newsletter LinkedIn mensuelle pour les meetups de Grenoble : sanity check du contenu, texte du post, image calendrier.

---

## 1. Quel mois ?

Si l'utilisateur ne précise pas, utiliser le mois **suivant** (la newsletter est publiée en début de mois pour le mois en cours, mais préparée avant).

Le contenu du mois cible est dans `content/meetups/YYYY-MM/`.

---

## 2. Sanity check

Lire tous les fichiers du mois. Vérifier pour chaque événement **actif** (non `cancelled: true`) :

| Champ | Règle |
|---|---|
| `description` | Présente et non vide |
| `links` | Au moins un lien — ou note explicite que c'est intentionnel |
| Chaque lien | A un `label` (sinon le site l'affiche mal) |
| `time` | Renseigné (`HH:MM`, `midi`, `après-midi`, ou `soir`) |
| `title` | Se termine par un emoji |
| `location.address` | Présente si `location.name` est renseigné |
| Fichier | Nom = `YYYY-MM-DD-slug.md`, date cohérente avec le front matter |

Signaler également :
- Les événements multi-jours sans `endDate`
- Les doublons potentiels (même titre, même date)
- Le `_index.md` du mois (doit exister avec `title` et `date`)

Présenter les résultats sous forme de tableau : OK / ⚠️ à vérifier / ❌ bloquant.

---

## 3. Texte du post LinkedIn

### Format par événement

```
📅 [jour] [DD] [à HH:MM | midi | soir] : [Titre sans emoji] [emoji]
[Une ligne de contexte si l'event le mérite — facultatif]
[URL principale]
```

Règles :
- **Ordre chronologique**, annulés exclus
- `à` entre le numéro de jour et une heure numérique (`mercredi 01 à 19h`)
- Pas de `à` avant `midi` / `soir` (`jeudi 02 midi`)
- Si un workshop se répète plusieurs fois dans le mois, lister chaque occurrence séparément (sans mentionner "2ème session" ou numérotation)
- URL = premier lien non-LinkedIn du front matter
- Pas de `hashtag#`, juste `#grenoble_meetups`

### Structure du post

```
[Intro contextuelle — ton décontracté, référence à la saison ou à l'actualité]

📅 ...
[URL]

📅 ...
...

Retrouvez tous les détails sur https://grenoble-meetups.fr

#grenoble_meetups
```

### Exemples d'intros

- Juillet : *"Juillet démarre, voici les meetups tech à Grenoble avant la trêve estivale 🌞"*
- Septembre : *"La rentrée approche, les meetups aussi 👇"*
- Janvier : *"Bonne année ! Voici les premiers meetups tech grenoblois de 2027 👇"*

---

## 4. Image calendrier

### Script existant

Les scripts sont dans `calendar_generators/gen_calendar_MOIS.py`. Si le script du mois n'existe pas, le créer en copiant le script du mois précédent et en adaptant :

- `MONTH` — numéro du mois
- `events` — dict `{jour: ["Libellé court"]}` (événements actifs uniquement, emojis inclus)
- `HOLIDAYS` — jours fériés du mois (ex: `{14}` pour le 14 juillet)
- `DENSE_DAYS` — jours avec 2+ événements (police réduite)
- titre, footer, nom du fichier de sortie

Le fichier PNG est sauvegardé dans le **répertoire courant** (pas de chemin absolu).

### Lancement

```bash
cd calendar_generators
uv run --with pilmoji python3 gen_calendar_MOIS.py
```

### Notes techniques

- Pillow seul ne rend pas les emojis → `pilmoji` obligatoire (via `uv run --with pilmoji`)
- `pilmoji` doit envelopper **tout** le rendu texte dans `with Pilmoji(img) as pilmoji:` ; les formes (rectangles) restent avec `draw`
- La mesure du texte pour le word-wrap utilise toujours `draw.textbbox()` (pas `pilmoji`) — c'est correct car les dimensions de texte sans emoji suffisent pour l'estimation
- L'erreur Pyright sur `Image.new('RGB', ..., "#ffffff")` est un faux positif — ignorer
