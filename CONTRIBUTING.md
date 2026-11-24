# Contribuer

Un évènement manque, ou une info est incorrecte ? Il y a trois façons d'aider, de la plus simple à la plus directe. Les deux premières ne demandent aucune compétence technique.

- **Envoyer un mail** à [contact@grenoble-meetups.fr](mailto:contact@grenoble-meetups.fr).
- **Ouvrir un ticket** avec le [formulaire](https://github.com/Lenormju/grenoble-meetups/issues/new/choose) : il demande le nom, la date, le lieu et le lien.
- **Faire la modification vous-même**, par une *pull request*. Le détail est plus bas.

Toute contribution est relue avant d'être publiée.

## Quels évènements sont acceptés ?

- Ils ont lieu **dans l'agglomération grenobloise**. Pas de Lyon, ni d'ailleurs.
- Ils sont **publics**.
- Ils sont autour de la tech : développement, données, sécurité, jeux vidéo, product, etc.
- Un **lien** vers la page de l'évènement ou l'inscription est fortement recommandé : il permet de vérifier l'information et aide les participants.

Ce n'est pas obligatoirement un meetup : conférences, ateliers, soirées et appels à contributions ont leur place.

## Corriger un évènement

1. Ouvrez la page de l'évènement sur le site.
2. Cliquez sur **Faites la modification**, en bas de page. GitHub ouvre le fichier dans son éditeur.
3. Modifiez, puis proposez la modification. GitHub crée la *pull request* pour vous.

Pour un évènement annulé, ajoutez `cancelled: true` juste au-dessus de `title:`. La page reste accessible, mais il disparaît du calendrier.

## Ajouter un évènement

Créez `content/meetups/AAAA-MM/AAAA-MM-JJ-mot-cle.md`, par exemple `content/meetups/2026-12/2026-12-10-python-grenoble.md`.

- Le dossier est celui du mois de l'évènement.
- Le nom du fichier commence par la date, suivie d'un identifiant de 1 à 4 mots, en minuscules, sans accents, séparés par des tirets.

Contenu minimal :

```yaml
---
title: "Nom de l'évènement 🎤"
description: "Une phrase qui résume l'évènement."
startDate: "2026-12-10"
startTime: "19:00"
location:
  name: "La Casemate"
  address: "1 Place Saint-Laurent, Grenoble"
links:
  - url: "https://..."
---
```

- `startTime` accepte une heure (`19:00`) ou un moment de la journée (`midi`, `après-midi`, `soir`) quand l'heure n'est pas encore connue.
- Les champs facultatifs (`endDate`, `endTime`, `price`, `groups`, `location.details`…) sont à imiter depuis les fichiers existants du même dossier.
- Si le fichier est invalide, la publication échoue et le message d'erreur indique le fichier et la valeur en cause.

## Tester en local (facultatif)

Avec [Hugo](https://gohugo.io/installation/) (version 0.162.0) :

```bash
hugo server
```

Le site est alors disponible sur `http://localhost:1313`.
