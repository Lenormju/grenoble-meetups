# Image sociale / `image` des données structurées

Implémenté. Le fonctionnement au quotidien est documenté dans `CLAUDE.md` (section « Social
cards ») ; cette note garde le pourquoi des choix et les liens de vérification.

## Ce qui a été fait

Chaque page a une card 1200 × 630 générée par Hugo au build, servie à la fois comme `og:image` /
`twitter:image` (`layouts/partials/seo.html`) et comme `image` du JSON-LD `Event`
(`layouts/meetups/single.html`). `twitter:card` est passé de `summary` à `summary_large_image`.

Trois gabarits : un par événement (date, titre, groupe organisateur), un par mois
(« Septembre 2026 · 10 événements »), un par défaut pour le reste.

## Les deux usages, et leur poids réel

1. **`og:image`** — le gain concret. Avant, un partage sur LinkedIn ou Mastodon produisait un
   aperçu sans visuel : `seo.html` n'émettait aucun `og:image` et les pages ne contiennent aucune
   image à repêcher.
2. **Données structurées `Event`** — lève l'avertissement Search Console « Missing field image ».
   Le champ est recommandé, pas requis, et l'affichage des résultats enrichis n'est jamais
   garanti. C'est le bénéfice secondaire, pas le moteur de la décision.

Aucun réseau social ne lit le JSON-LD ; Google ne lit pas l'`og:image`. Deux consommateurs
distincts qui pointent ici vers le même fichier.

## Contraintes qui ont dicté la conception

**Format** — Google indexe le SVG, mais les consommateurs d'`og:image` non. PNG, donc.

**Dimensions** — 1200 × 630 satisfait tout le monde : au-dessus des minimums LinkedIn (640 × 360),
Facebook (200 × 200) et X (300 × 157), et au-dessus des seuils Google (720 px de large,
50 000 pixels). Sous le minimum d'une plateforme, elle ne refuse pas l'image, elle bascule sur la
petite vignette carrée.

**Ratios multiples** — Google recommande de fournir 16:9, 4:3 et 1:1 dans un tableau. Non fait
volontairement : ces ratios ne servent qu'aux résultats enrichis, jamais aux réseaux sociaux, et
peuvent s'ajouter plus tard sans rien remettre en cause.

**Génération native Hugo plutôt qu'un script Python en CI** — trois raisons : les cards se
régénèrent depuis le contenu à chaque build, `hugo server` montre les vraies images en local, et
le nommage par hash de Hugo produit une nouvelle URL à chaque modification, ce qui contourne les
caches LinkedIn et Google au lieu de les subir. `calendar_generators/` n'était pas réutilisable :
ce sont des scripts Pillow copiés-collés mois par mois, avec les données en dur.

## Vérification

- Test des résultats enrichis : https://search.google.com/test/rich-results
- Validateur schema.org : https://validator.schema.org/
- Aperçu LinkedIn (permet aussi de forcer le rafraîchissement du cache) :
  https://www.linkedin.com/post-inspector/

## Sources

- [Event structured data](https://developers.google.com/search/docs/appearance/structured-data/event)
- [Image SEO Best Practices](https://developers.google.com/search/docs/appearance/google-images)
- [Structured data general guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
