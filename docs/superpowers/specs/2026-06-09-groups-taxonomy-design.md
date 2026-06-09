# Design : Taxonomie Groupes

**Date :** 2026-06-09  
**Statut :** Approuvé

## Contexte

Le site liste des événements tech grenoblois organisés par mois. Certains groupes organisent des événements récurrents (Human Talks, SICP, CARA-Beer, Hackerspace…). Il n'existe actuellement aucun moyen de naviguer par groupe ou de filtrer les événements d'un mois par organisateur.

## Cas d'usage couverts

- **A — Navigation par groupe** : cliquer sur un groupe affiche tous ses événements (passés et futurs) sur une page dédiée.
- **C — Filtre sur la page mois** : des tags cliquables au-dessus du calendrier permettent de n'afficher que les événements d'un groupe.

## Modèle de données

### Front matter des événements

```yaml
groups: ["humantalks"]                      # standard — un seul groupe
groups: ["securimag", "hackerspace"]        # co-organisation (rare)
```

Le champ `groups` est obligatoire. Tout événement doit appartenir à au moins un groupe.

### Structure `content/groups/`

```
content/groups/
  humantalks/_index.md
  sicp/_index.md
  hackerspace/_index.md
  cara-beer/_index.md
  ...
```

Chaque `_index.md` contient au minimum :

```yaml
---
title: "Human Talks Grenoble"
---
```

Optionnellement une description courte et/ou un lien vers le site/Meetup.com du groupe.

### Configuration Hugo

```toml
# hugo.toml
[taxonomies]
  group = "groups"
```

Génère automatiquement :
- `/groups/` — liste de tous les groupes
- `/groups/humantalks/` — tous les événements de ce groupe

## Pages de groupe

**Layout :** `layouts/groups/list.html`

Contenu :
- Titre du groupe
- Liste d'événements triée chronologiquement : futurs en premier (croissant), puis passés (décroissant)
- Chaque ligne : date + titre + lien vers la page événement
- Pas de calendrier grille — liste simple adaptée à la vue multi-mois

**Layout index :** `layouts/groups/terms.html`

Contenu : liste de tous les groupes avec le nombre d'événements associés.

## Filtre par groupe sur la page mois

### Rendu HTML

Chaque carte événement reçoit un attribut `data-groups` :

```html
<div class="event-card" data-groups="humantalks">…</div>
<div class="event-card" data-groups="securimag hackerspace">…</div>
```

Au-dessus du calendrier, une rangée de tags générée depuis les groupes présents dans le mois :

```html
<div class="group-filters">
  <button class="group-tag active" data-filter="all">Tous</button>
  <button class="group-tag" data-filter="humantalks">Human Talks Grenoble</button>
  <button class="group-tag" data-filter="sicp">SICP / Grenoble Coding Workshop</button>
  …
</div>
```

Les tags apparaissent dès qu'il y a au moins un groupe dans le mois.

### Comportement JS

- Par défaut : tous les événements visibles, tag "Tous" actif
- Clic sur un tag groupe → seuls les événements de ce groupe visibles, les autres à `opacity: 0.2`
- Clic sur le même tag actif → retour à "tous visibles"
- Clic sur un autre tag → bascule vers ce groupe
- Clic sur "Tous" → réinitialise

Implémentation JS pur, sans dépendance externe. Toggle de classe CSS sur les cartes.

Le nom affiché dans le tag est le `title` du `_index.md` du groupe (pas le slug).

## Skill `add-meetup`

Le skill est mis à jour pour :

1. Demander le(s) groupe(s) lors de la saisie de l'événement
2. Générer le champ `groups:` dans le front matter
3. Vérifier que chaque groupe référencé a un `content/groups/<slug>/_index.md` — si absent, le créer avec un titre placeholder à compléter

Le champ `groups` est obligatoire dans le workflow d'ajout.

## Fichiers à créer / modifier

| Fichier | Action |
|---|---|
| `hugo.toml` | Ajouter `[taxonomies]` avec `group = "groups"` |
| `content/groups/<slug>/_index.md` | Créer pour chaque groupe existant |
| `layouts/groups/list.html` | Créer (page groupe) |
| `layouts/groups/terms.html` | Créer (liste des groupes) |
| `layouts/partials/month-calendar.html` | Ajouter `data-groups` sur les cartes + rendre les tags |
| `layouts/meetups/list.html` | Idem si les tags doivent apparaître sur `/meetups/YYYY-MM/` |
| `static/style.css` | Styles pour `.group-filters` et `.group-tag` |
| Tous les événements existants | Ajouter `groups:` dans le front matter |
| Skill `add-meetup` | Ajouter étape groupe + création auto du `_index.md` |
