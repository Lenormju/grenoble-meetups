# Grenoble Tech Meetups

Calendrier des meetups tech de Grenoble, généré avec [Hugo](https://gohugo.io/) et hébergé sur GitHub Pages.

Site : **[grenoble-meetups.fr](https://grenoble-meetups.fr)** — Flux RSS : **[grenoble-meetups.fr/index.xml](https://grenoble-meetups.fr/index.xml)**

## Développement local

```bash
hugo server                  # serveur de dev avec hot-reload
hugo server --buildFuture    # inclure les événements à venir
hugo --gc --minify           # build de production (→ ./public)
```

Hugo 0.162.0 requis.

## Déploiement

Un push sur `main` déclenche GitHub Actions qui build et déploie sur GitHub Pages. Un cron mensuel relance le build pour mettre à jour la vue "mois courant".

## Ajouter un meetup

Utiliser la commande `/add-meetup` dans Claude Code — elle gère la création de fichiers, le nommage et le front matter automatiquement.
