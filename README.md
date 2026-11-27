# AlleleFounder Web

Interface web Django du logiciel AlleleFounder.

Ce dépôt accueillera le plan de contrôle de l’application : comptes,
organisations, études familiales, autorisations, orchestration des analyses et
historique. Les calculs scientifiques restent dans le moteur autonome
[Effet_fondateur2](https://github.com/patrick-mun/Effet_fondateur2).

## Statut

Le projet est en phase d’initialisation. Aucun composant Django ni raccordement
au moteur scientifique n’est encore implémenté.

La première cible de déploiement est une installation institutionnelle sur
l’infrastructure interne du CHU. L’architecture devra rester portable vers une
éventuelle offre SaaS ultérieure.

## Principes initiaux

- ne pas recopier la logique scientifique du moteur dans Django ;
- raccorder le moteur par des contrats et versions explicites ;
- utiliser uniquement des données synthétiques pendant la construction ;
- séparer les requêtes web des traitements scientifiques asynchrones ;
- ne jamais versionner de donnée génétique, de secret ou de résultat de run.
