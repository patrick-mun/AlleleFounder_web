# Instructions de travail — AlleleFounder Web

## Mission du dépôt

Ce dépôt contient le plan de contrôle web d’AlleleFounder. Il gère les comptes,
organisations, études familiales, autorisations, instantanés, analyses, décisions,
artefacts et audits. Les calculs scientifiques appartiennent exclusivement au
moteur voisin `../Effet_fondateur2`.

Le premier déploiement réel visé est une installation mono-établissement sur
l’infrastructure interne du CHU. L’application doit néanmoins rester portable
vers un futur SaaS, sans dépendance obligatoire à un cloud public.

## Références à lire

Avant une modification structurante, lire les documents concernés sous `docs/`
et, pour toute frontière scientifique ou d’exécution, les références du moteur :

- `../Effet_fondateur2/AGENTS.md` ;
- `../Effet_fondateur2/README.md` ;
- `../Effet_fondateur2/SESSION.md` ;
- `../Effet_fondateur2/docs/ui/allelefounder_architecture.html` ;
- `../Effet_fondateur2/docs/ui/allelefounder_infrastructure.md` ;
- `../Effet_fondateur2/docs/security_predeployment.md` ;
- les contrats pertinents sous `../Effet_fondateur2/docs/modules/`.

Le dépôt moteur est une dépendance externe. Ne jamais le modifier, déplacer ou
committer depuis une tâche AlleleFounder Web sans demande explicite.

## Frontières impératives

- Ne recopier dans Django aucune formule, transformation de génotype ou méthode
  scientifique du moteur.
- Ne jamais lancer PLINK, KING, bcftools, SHAPEIT5, Java ou un moteur IBD dans
  une requête HTTP ou dans le processus web.
- Utiliser un worker isolé pour toute exécution du moteur ou d’un outil externe.
- Ne pas importer une fonction privée du moteur comme API d’intégration.
- Épingler la version du moteur et enregistrer version publiée, révision Git et
  digest de l’image scientifique pour chaque run.
- Considérer configuration, instantané, manifest, états et artefacts comme des
  contrats versionnés et vérifiables.
- Ne jamais transformer l’absence d’un résultat en résultat négatif, ni un état
  technique réussi en conclusion scientifique.
- Ne jamais déduire un génotype du statut clinique, du groupe, de la famille ou
  du génotype d’un apparenté.

## Données et sécurité

- Utiliser uniquement des données synthétiques jusqu’à autorisation explicite
  après clôture de la porte de sécurité.
- Ne jamais copier de donnée depuis `../Effet_fondateur2/data/`.
- Ne jamais versionner de donnée génétique, résultat de run, secret, jeton,
  sauvegarde ou URL signée.
- Ne pas journaliser de génotype, contenu de fichier, identité de participant,
  secret ou chemin physique sensible.
- Conserver les fichiers génétiques hors de PostgreSQL. La base ne porte que
  des métadonnées, identifiants opaques, tailles et empreintes.
- Résoudre l’organisation et l’autorisation côté serveur pour chaque objet,
  téléchargement et tâche. Un identifiant fourni par le navigateur n’est
  jamais une preuve d’accès.
- Refuser les chemins absolus, `..`, séparateurs inattendus et liens symboliques
  aux frontières de stockage et de matérialisation.
- Traiter la future checklist de sécurité web et celle du moteur comme
  bloquantes avant toute donnée réelle ou exposition publique.

## Méthode de travail

- Commencer par `git status` et préserver toutes les modifications existantes.
- Travailler par petits lots vérifiables et utiliser `apply_patch` pour les
  fichiers texte.
- Ne créer aucun commit et ne pousser aucune branche sans demande explicite.
- N’ajouter aucune dépendance sans justification, borne de version et analyse
  de sa place en production, développement ou test.
- Mettre à jour la documentation et le registre de décisions lorsqu’un contrat,
  une frontière ou une décision structurante change.
- Distinguer explicitement dans les documents : **décidé**, **proposé**,
  **ouvert** et **interdit**.

## Conventions de code

- Python 3.12, noms explicites, annotations de types et fonctions courtes.
- Séparer vues, formulaires, services métier, sélecteurs de lecture et
  adaptateurs externes. Les vues ne portent pas les règles d’autorisation ou de
  compilation à elles seules.
- Définir un modèle utilisateur personnalisé avant la première migration.
- Garder les dates en UTC et appliquer le fuseau de l’utilisateur à l’affichage.
- Favoriser les contraintes PostgreSQL pour les invariants locaux et des
  services transactionnels pour les invariants multi-objets.
- Publier une tâche uniquement après validation de la transaction métier.
- Rendre les tâches idempotentes ou distinguer explicitement leurs tentatives.

## Tests attendus

- Tester le comportement observable, les erreurs et les cas limites.
- Tester chaque rôle et l’isolation entre au moins deux organisations.
- Tester qu’une URL, une recherche, un compteur, un téléchargement et une tâche
  ne révèlent aucun objet d’une autre organisation.
- Tester les migrations depuis la dernière version publiée et leur compatibilité
  de retour arrière lorsqu’elle est requise.
- Simuler les services externes et le moteur dans les tests unitaires.
- Ne lancer aucune commande scientifique réelle dans la suite ordinaire.
- Utiliser des répertoires temporaires et des fixtures entièrement synthétiques.
- Vérifier que les journaux de test ne contiennent ni secret, ni génotype, ni
  identité de participant.

## Validation proportionnée

Pour un lot documentaire :

- `git diff --check` ;
- vérification des liens et cohérence avec les contrats cités ;
- `git status --short`.

Pour un lot Django, ajouter au minimum les contrôles de format, types, tests
ciblés, migrations et contrôles de déploiement documentés par le lot. Signaler
les validations non exécutées et leur raison.
