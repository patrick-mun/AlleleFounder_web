# Livraison progressive de l'interface

**Statut :** proposé

Ce document rend explicite le moment où chaque page d'AlleleFounder apparaît.
Il complète le [plan de développement](development_plan.md) et s'appuie sur les
maquettes de `Effet_fondateur2/docs/ui/allelefounder_architecture.html`.

Les maquettes fixent la hiérarchie de l'information, les parcours et les
principes de prudence scientifique. Elles ne fixent pas un logo, des textes
marketing, un domaine public, ni une API. Toutes les données utilisées avant la
porte du lot 9 sont synthétiques.

## Carte des pages par lot

| Lot | Pages réellement livrées | Référence principale |
|---|---|---|
| 0 | Aucune page exécutable | conception des parcours |
| 1 | Accueil technique, erreurs, santé, administration de développement | socle uniquement |
| 2 | Accueil public, demande et décision d'accès, inscription sur invitation, connexion, récupération, MFA, choix d'organisation, cadre applicatif, tableau de bord vide, équipe, compte | figures 4 à 7 |
| 3 | Liste/détail des études, étapes Contexte, Cible et Familles | figure 8 |
| 4 | Étapes Sources et Génotypes, vues de preuve par individu | figure 9 |
| 5 | Vérification, aperçu V2, gel et instantanés | figure 10 |
| 6 | Lancement simulé, liste et suivi des analyses, tableau de bord alimenté | figure 11 |
| 7 | Suivi réel et provenance du moteur épinglé | figure 11 enrichie |
| 8 | Décisions, résultats, artefacts, rapports, notifications et audit | figure 12 |
| 9 | Paramètres et écrans d'exploitation finalisés pour le pilote | parcours qualifiés |

## Parcours principal d'une étude

L'assistant est visible progressivement, mais conserve dès son introduction les
sept repères suivants :

1. Contexte — lot 3 ;
2. Cible — lot 3 ;
3. Familles — lot 3 ;
4. Sources — lot 4 ;
5. Génotypes — lot 4 ;
6. Vérification — lot 5 ;
7. Gel et lancement — gel au lot 5, lancement asynchrone au lot 6.

Une étape future peut être visible comme indisponible avec une explication. Elle
ne doit jamais simuler une capacité qui n'existe pas encore.

## États obligatoires d'une page

Chaque page traite, lorsqu'ils s'appliquent :

- le premier usage et l'état vide, avec une action suivante claire ;
- le chargement partiel sans masquer toute la page ;
- la validation locale et les erreurs serveur ;
- l'accès refusé sans révéler l'existence d'un objet d'une autre organisation ;
- l'indisponibilité temporaire d'un service ;
- le succès et la prochaine action ;
- les conflits de révision ou d'empreinte sans écrasement silencieux.

Les statuts associent un libellé, un signe visuel et une explication. La couleur
seule ne porte jamais l'information.

## Principes de présentation

- famille d'abord pour la constitution de la cohorte ;
- divulgation progressive des détails techniques ;
- unités, hypothèses, exclusions et limites scientifiques visibles ;
- séparation constante entre fait technique, interprétation, décision humaine
  et provenance ;
- aucune donnée individuelle sur le tableau de bord ;
- rendu serveur utilisable au clavier, lisible sur mobile et amélioré
  progressivement ;
- direction visuelle bleu-vert, fond clair, cartes sobres et orange réservé aux
  décisions ou limites, sous réserve de validation de l'identité finale.

## Critère de revue visuelle

Un lot comportant une interface n'est pas clos sur le seul succès des tests
backend. Une revue avec jeu de données synthétique vérifie : parcours complet,
quatre rôles, isolation des organisations, états d'erreur, petit écran,
navigation clavier et cohérence avec la figure de référence. Toute différence
volontaire est documentée dans le registre des décisions.
