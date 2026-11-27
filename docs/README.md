# Conception d’AlleleFounder Web

Ce dossier constitue la source de vérité de conception du plan de contrôle web.
Les contrats scientifiques restent dans le dépôt `Effet_fondateur2`.

## Documents

- [Architecture applicative](architecture.md) : frontières, arborescence et
  découpage Django.
- [Modèle métier](domain_model.md) : objets, relations, invariants et cycles de
  vie.
- [Intégration du moteur](engine_integration.md) : contrats, progression et
  règles d’exécution.
- [Plan de développement](development_plan.md) : petits lots, tests et portes
  de sortie.
- [Livraison progressive de l'interface](ui_delivery_plan.md) : pages livrées
  par lot, états obligatoires et correspondance avec les maquettes.
- [Audit et décisions](decisions.md) : décisions acquises, propositions,
  questions ouvertes et échéances.
- [Profil des conventions web](conventions-profile.md) : règles HTML/CSS/JS et
  niveau d’automatisation appliqué.
- [Procédures d’exploitation](runbooks/) : migration et retour arrière minimal.

## Statuts employés

- **Décidé** : contrainte acceptée pour le produit et à respecter par les lots
  suivants.
- **Proposé** : choix de conception recommandé, à confirmer avant le lot qui le
  rend coûteux à changer.
- **Ouvert** : décision non prise, avec son échéance et son effet bloquant.
- **Interdit** : option incompatible avec la frontière scientifique, la
  sécurité ou le déploiement retenu.

## Autorité des sources

En cas de divergence :

1. les schémas et contrats versionnés du moteur définissent ses entrées et
   sorties exécutables ;
2. les documents `docs/modules/` du moteur définissent leur interprétation ;
3. ce dossier définit le domaine et l’orchestration web ;
4. les maquettes du moteur définissent la référence de parcours et de hiérarchie
   visuelle retenue pour le prototype, mais ne constituent ni une API ni une
   identité graphique définitive.

Une divergence est documentée puis résolue par une évolution explicite du bon
contrat. Elle ne doit pas être compensée par une conversion silencieuse.
