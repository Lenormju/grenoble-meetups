# Newsletter LinkedIn

Préparer la newsletter LinkedIn mensuelle pour les meetups de Grenoble : sanity check du contenu, texte du post, carousel, texte Slack.

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
- URL = premier lien **non-LinkedIn** du front matter. Si le seul lien disponible est un post
  LinkedIn, le prendre quand même — en dernier recours c'est mieux que rien. Si l'événement n'a
  aucun lien, **omettre la ligne d'URL** : ne jamais se replier sur la page de l'événement sur
  grenoble-meetups.fr, la ligne de clôture du post y renvoie déjà
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

## 4. Carousel

Le visuel du post est un **carousel PDF** uploadé sur LinkedIn : une slide de vue d'ensemble du mois, puis une slide par jour ayant des événements.

### Lancement

Il n'y a **rien à éditer** — tout est lu depuis `content/meetups/YYYY-MM/`. Le mois est un argument :

```bash
cd calendar_generators
uv run --with playwright --with pyyaml --with img2pdf python3 gen_carousel.py --month 2026-10
```

Premier lancement sur une machine neuve, une seule fois (~115 Mo) :

```bash
uv run --with playwright python3 -m playwright install chromium
```

### Sorties

Dans `calendar_generators/`, toutes gitignorées (ce sont des artefacts, régénérables en quelques secondes) :

- `carousel_<mois>_<année>_NN.png` — les slides
- `carousel_<mois>_<année>.pdf` — **c'est ce fichier qu'on uploade sur LinkedIn**

### Ce qu'il faut savoir

- **Relancer le script après toute modification du contenu du mois.** Le carousel est un instantané ; un événement ajouté après coup n'y sera pas.
- Un événement **multi-jours** (`endDate`) s'étale sur toutes ses journées dans la grille de la slide 1, mais n'a **qu'une seule carte**, avec sa plage (`1 → 3 octobre`) dans la ligne meta — pas N slides quasi identiques.
- Un événement **sans `location`** affiche « Lieu annoncé prochainement » (constante `LOCATION_TBA`). Sans danger, puisqu'on ne génère un carousel que pour un mois à venir.
- Le rendu passe par Chromium (Playwright), donc les emojis sont en couleur et le CSS est du vrai CSS — contrairement à l'image calendrier, qui passe par Pillow.

### Image calendrier (optionnelle)

`gen_calendar.py --month YYYY-MM` produit encore le PNG carré mono-image, même source de données. Il ne fait plus partie de la newsletter, mais reste utile pour un usage ponctuel. Notes techniques si tu y touches :

- Pillow seul ne rend pas les emojis → `pilmoji` obligatoire (via `uv run --with pilmoji`)
- `pilmoji` doit envelopper **tout** le rendu texte dans `with Pilmoji(img) as p:` ; les formes (rectangles) restent avec `draw`
- La mesure du texte pour le word-wrap utilise toujours `draw.textbbox()` (pas `pilmoji`) — c'est correct car les dimensions de texte sans emoji suffisent pour l'estimation
- `SHORT_LABELS` permet de raccourcir à la main un titre qui déborde de sa cellule
- L'erreur Pyright sur `Image.new('RGB', ..., "#ffffff")` est un faux positif — ignorer

---

## 5. Texte Slack

À générer **après** la publication du post LinkedIn : le texte cite son URL, qui doit d'abord être renseignée dans `linkedinPost` du `_index.md` du mois. Si `linkedinPost` est absent, le signaler et laisser la ligne en placeholder.

### Template

```
Meetups de Grenoble du mois de [Mois] :

site https://grenoble-meetups.fr/
post LinkedIn : [URL de linkedinPost]
sinon voici la liste complète (à date) :
[jour] [DD] [à HH:MM | midi | soir] : [Titre sans emoji] [:code_slack:]
[jour] [DD] ...
```

Règles :
- Mois **capitalisé et sans l'année** (`Juillet`, `Septembre`)
- `site` sans deux-points ; `post LinkedIn :` avec deux-points entourés d'espaces
- Une ligne par événement, **aucune ligne vide entre les événements** (bloc compact)
- **Ordre chronologique, y compris à l'intérieur d'une même journée** (`jeudi 09 à 12h` avant `jeudi 09 à 19h`)
- Mêmes règles de date/heure que le post LinkedIn : `à 19h`, `à 18h30`, pas de `à` avant `midi` / `soir`
- Titre **complet** (pas la version courte du calendrier), sans son emoji, suivi du **code court Slack** de cet emoji
- Ni URL par événement, ni ligne de contexte, ni hashtag — contrairement au post LinkedIn

### Conversion des emojis en codes Slack

| Emoji | Code Slack |
|---|---|
| 🤖 | `:robot_face:` |
| 🎤 | `:microphone:` |
| 🎮 | `:video_game:` |
| 🛡️ | `:shield:` |
| 💬 | `:speech_balloon:` |
| 📖 | `:book:` |
| 🐟 | `:fish:` |
| 🌍 | `:earth_africa:` |
| 🔧 | `:wrench:` |
| 📱 | `:iphone:` |
| 🧪 | `:test_tube:` |
| 🍽️ | `:knife_fork_plate:` |
| 🧍 | `:standing_person:` |

Attention aux pièges : `:robot_face:` (pas `:robot:`), `:iphone:` pour 📱, `:knife_fork_plate:` pour 🍽️. Pour un emoji absent de cette table, vérifier son nom Slack sur emojipedia plutôt que de le deviner — un code invalide s'affiche en texte brut dans Slack.
