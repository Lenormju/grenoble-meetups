---
title: "bash, un tout petit LLM et la naissance d'un agent de code 🤖"
description: "Philippe Charrière montre en direct la plus petite boucle d'agent possible : un LLM local de 12B paramètres, un seul outil bash et un agent de code qui naît sous nos yeux."
startDate: "2026-10-27"
startTime: "19:00"
endTime: "21:00"
groups: ["alpesjug"]
location:
  name: "Salesforce"
  address: "29 Bd des Alpes"
  city: "Meylan"
links:
  - url: "https://www.meetup.com/alpesjug/events/317009119/"
    label: "S'inscrire"
---

L'an dernier, nous avions parlé de comment faire tourner des LLMs en local et les principes de base des applications d'IA générative. Cette fois-ci, allons un peu plus loin et voyons ce qu'est l'agent loop.

Les agents de code ont l'air magiques. Mais en fait ils ont un cœur étonnamment réduit : une boucle, un modèle de langage et… un shell.

Nous allons voir ce cœur fonctionner en direct. Nous donnons à un petit LLM local (plus ou moins 12B de paramètres, tournant sur Docker Model Runner … ou autre chose) un seul outil intégré, bash, et nous le regardons se transformer en assistant de développement. Il liste les fichiers, fait des grep dans le dépôt, lance les tests, appelle une API avec curl, passe le résultat dans jq… tout seul, parce que le modèle connaît déjà ces outils en ligne de commande. Et quand il ne les connaît pas ? Il lance --help et se débrouille (ou tout au moins il essaie).

Nous verrons à l'œuvre la plus petite boucle d'agent possible : le modèle choisit la commande à exécuter, l'agent l'exécute, lui renvoie le résultat, et ainsi de suite jusqu'à ce que le modèle réponde.

Des démos en direct, peu/pas de slides, et du code que vous pourrez lancer dès ce soir (ok c'est du Go, pas du Java, mais c'est reproductible facilement).

Nous parlerons aussi de ce qu'est devenu ce début d'agent, comment il a évolué pour devenir un véritable outil (dédié aux modèles locaux). Ce sera l'occasion d'expliquer à quels moments je l'utilise pour de vrai (et mes conclusions sur les modèles locaux). Ce sera aussi l'occasion de parler de SBX (pourquoi sécuriser des agents de code) mais aussi d'ACP (Agent Client Protocol), et là on parlera un peu de Java (notamment grâce à Emmanuel Hugonnet).

Le conférencier : Philippe Charrière, Principal Solution Architect chez Docker. Précédemment Strategic Senior CSM & CSE chez GitLab. Passionné par le développement en Go, JavaScript et Java (un peu de Rust et de Python). Une addiction forte à tout ce qui touche à WebAssembly et à l'IA générative.
