---
title: "La concurrence structurée du projet Loom ☕"
description: "José Paumard présente l'API de Concurrence Structurée du projet Loom : les patterns StructuredTaskScope, leur configuration et les stratégies de l'API Joiner."
date: 2026-09-23
time: "19:00"
groups: ["alpesjug"]
location:
  name: "Salesforce"
  address: "29 Bd des Alpes"
  city: "Meylan"
links:
  - url: "https://www.meetup.com/alpesjug/events/316501713/"
---

Le projet Loom a déjà livré les threads virtuels en Java 21 et l'API Scoped Value en Java 25. Il doit encore livrer l'API de Concurrence Structurée, qui est toujours en version preview pour le moment. C'est cet élément qui permettra d'écrire simplement des requêtes asynchrones en parallèle. Pour le moment, résoudre ce problème s'appuie sur les ExecutorService, ou la programmation réactive.

La programmation concurrente structurée apporte de nouveaux patterns, utilisables uniquement sur les threads virtuels. Le modèle de programmation est simple, facilement débuggable. Cette présentation se propose de vous montrer ces patterns, de comprendre comment fonctionnent les objets StructuredTaskScope et comment vous pouvez les configurer. Elle vous montre également les différentes stratégies offertes par l'API Joiner pour gérer les résultats de vos requêtes, et comment vous pouvez créer vos propres Joiners si vous voulez construire vos propres stratégies.

Le conférencier : José est Java Developer Advocate au Java Platform Group chez Oracle. Anciennement maître de conférences à l'Université Sorbonne Paris Nord pendant 28 ans, il est Java Champion, Rockstar JavaOne, speaker régulier dans de nombreuses conférences : Devoxx (France, Belgique, UK), JavaOne, Oracle Code One, DevNexus, JFokus. Il a été consultant en entreprise pendant 25 ans, fortement investi en qualité des applications logicielles et Software Craftsmanship. Il est membre du Paris JUG, co-organisateur du Paris JUG Java Day et de JChateau, unconference annuelle organisée par le Paris JUG. Il contribue au site https://dev.java/, tient le JEP Café sur YouTube, et publie également une série de shorts : Cracking the Java Coding Interview.
