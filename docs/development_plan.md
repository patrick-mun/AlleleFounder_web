# Plan de développement par lots

**Statut :** proposé

**Règle :** chaque lot est petit, vérifiable et livrable sans anticiper les
dépendances du lot suivant. Aucune donnée réelle avant la porte du lot 9.

## Contrôles transversaux de chaque lot

- `git diff --check` et état Git inspecté.
- Tests ciblés avant la suite élargie.
- Tests d'isolation entre organisations pour tout nouvel objet exposé.
- Tests des quatre rôles pour toute nouvelle action.
- Aucune donnée génétique, identité réelle, sortie de run ou secret versionné.
- Documentation et journal de décisions mis à jour si un contrat change.
- Dépendances externes simulées dans les tests unitaires.

## Lot 0 — règles, conception et contrats

### Livrables

- `AGENTS.md` adapté au dépôt web.
- Architecture, modèle métier, frontière moteur et plan par lots.
- Registre des décisions bloquantes et arborescence proposée.

### Tests et vérifications

- Contrôle des liens et noms de documents.
- Concordance avec les contrats V2 audités.
- Relecture explicite des catégories décidé/proposé/ouvert/interdit.
- `git diff --check`.

### Critère de sortie

Le propriétaire du produit valide les trois décisions qui bloquent leur lot,
ou accepte qu'elles restent ouvertes jusqu'à la date indiquée. Aucun projet
Django n'est créé dans ce lot.

## Lot 1 — socle Django, PostgreSQL et santé

**Statut :** implémenté ; construction OCI à rejouer avec un démon Docker actif.

### Livrables

- Projet Django Python 3.12, configuration par environnement et modèle `User`
  personnalisé avant toute migration métier.
- PostgreSQL pour développement/test d'intégration.
- pages d'erreur minimales, journalisation structurée sans données sensibles,
  vivacité et disponibilité distinctes.
- image applicative OCI, procédure de migration et retour arrière minimal.

### Tests

- `django check` et contrôle de déploiement adapté à la CI.
- migration depuis une base vide, puis aller/retour des migrations réversibles.
- disponibilité avec PostgreSQL présent/absent ; vivacité indépendante.
- démarrage avec configuration invalide et secret manquant refusé proprement.
- construction reproductible de l'image et exécution non privilégiée.

### Critère de sortie

Une page synthétique et les contrôles de santé fonctionnent sur PostgreSQL ;
aucun SQLite implicite, stockage génétique ou moteur scientifique n'est requis.

## Lot 2 — comptes, MFA, organisations et autorisations

### Livrables

- invitation privée, validation d'adresse, MFA obligatoire et récupération.
- `Organization`, `Membership` et quatre rôles.
- résolution serveur de l'organisation active et services d'autorisation.
- audit des invitations, connexions, MFA et changements de rôle.

### Tests

- activation, invitation expirée, compte désactivé, TOTP et récupération.
- réauthentification avant action sensible.
- matrice complète rôle × action.
- accès inter-organisation par URL, formulaire, requête directe et
  téléchargement simulé refusé sans fuite d'existence.
- changement concurrent du dernier administrateur géré atomiquement.

### Critère de sortie

Deux organisations synthétiques restent isolées dans toutes les vues et
services ; aucun accès métier n'est possible sans MFA et adhésion active.

## Lot 3 — études, variants, familles et individus

### Livrables

- `Study`, `TargetVariant`, `Family`, `Individual` et parcours étapes 1 à 3.
- validations autosomiques, codes stables, filiation et révisions de brouillon.
- liste/détail d'études filtrées par organisation.

### Tests

- unicités en base et erreurs de formulaire.
- parent hors famille, auto-parenté, cycle généalogique et sexe inconnu permis
  selon le contrat.
- variant incomplet ou discordant avec l'assemblage refusé au gel.
- familles multiples et familles unitaires.
- matrice des rôles et isolation tenant sur chaque vue/service.

### Critère de sortie

Une étude synthétique multi-familles représente sans ambiguïté FID/IID,
parents et cible, sans fichier ni génotype inféré.

## Lot 4 — sources et preuves de génotype

### Livrables

- interface de stockage, quarantaine, `SourceFile`, `IndividualSource` et
  `TargetGenotypeEvidence`.
- dépôt multiple avec confirmation explicite des affectations.
- parcours étapes 4 et 5, sans validation scientifique réelle.

### Tests

- taille/extension/type/empreinte, fichier vide, contenu malformé synthétique.
- chemins absolus, traversée, séparateurs interdits et liens symboliques.
- une source affectée à deux individus et remplacement concurrent refusés.
- origine clinique/groupe rejetée comme preuve de génotype.
- stockage et analyse antivirus simulés ; pannes et reprises contrôlées.
- aucune charge sensible dans logs, audit ou file.

### Critère de sortie

Chaque individu possède au plus une source active et une preuve explicite
traçable ; les blobs sont hors PostgreSQL et non accessibles par chemin direct.

## Lot 5 — compilation et validation des entrées V2

### Livrables

- compilateur déterministe pour `samples.tsv`, `variant.yaml`, `genotypes.tsv`
  et `pipeline.yaml`.
- aperçu lisible, diagnostics locaux et adaptateur de validation moteur simulé.
- `StudySnapshot` avec manifest et empreintes.

### Tests

- golden files et répétabilité byte-à-byte.
- propriétés/cas limites des codes, allèles, coordonnées `bp` et vocabulaires.
- absence d'une source/preuve, discordance d'individu ou variante.
- tests contractuels contre la version épinglée des schémas du moteur.
- mutation après aperçu invalide le candidat snapshot.
- approbation impossible sur une empreinte différente.

### Critère de sortie

Un snapshot synthétique approuvé est immuable et validé par les contrats publics
épinglés ; aucune commande scientifique n'est lancée.

## Lot 6 — analyses asynchrones simulées

### Livrables

- file de tâches choisie, worker applicatif séparé et adaptateur moteur factice.
- `AnalysisRun`, `AnalysisStep`, idempotence, suivi et erreurs simulées.
- vues de suivi sans polling agressif ; HTMX peut être introduit ici.

### Tests

- livraison double, retry, timeout, perte du worker et ordre d'événements.
- deux demandes concurrentes sur le même run.
- transitions autorisées/interdites et conservation des tentatives.
- panne de file, de stockage et de base simulée.
- aucun traitement long dans une requête HTTP.

### Critère de sortie

Les scénarios succès, échec, blocage et reprise synthétiques sont observables,
idempotents et cohérents après redémarrage du worker.

## Lot 7 — adaptateur vers le moteur réel

### Livrables

- image scientifique épinglée par digest et matrice de compatibilité.
- validation CLI puis lancement réel depuis le worker isolé.
- import contrôlé du manifest, des audits et artefacts synthétiques.

### Tests

- tests contractuels avec la version exacte du moteur.
- commandes sans shell, utilisateur non privilégié, ressources et réseau bornés.
- manifest valide, incomplet, inconnu et empreinte altérée.
- échecs de PLINK/KING/bcftools simulés au niveau de l'adaptateur ; un test
  d'intégration synthétique réel séparé.
- absence d'import de fonctions privées du moteur.

### Critère de sortie

Un run synthétique du moteur est lancé hors HTTP, sa version/digest sont
enregistrés et seuls ses artefacts validés deviennent visibles.

## Lot 8 — suivi, reprise, décisions, artefacts et rapports

### Livrables

- synchronisation robuste des étapes, `HumanDecision`, reprise et tentatives.
- autorisation des téléchargements et publication contrôlée des rapports.
- séparation faits, commentaires, limites et état de revue.

### Tests

- décision sur mauvaise empreinte, double approbation et conflit auteur/relecteur.
- reprise concurrente et changement de configuration refusés.
- artefact d'une autre organisation, sensible ou non déclaré refusé.
- HTML/SVG/PDF malveillant ou altéré traité selon la politique.
- `NOT_EVALUATED` visible et jamais transformé en succès.

### Critère de sortie

Les décisions et reprises respectent les contrats V2 ; un rapport n'est publié
qu'après contrôles d'intégrité, autorisation et revue prévues.

## Lot 9 — préparation du pilote CHU et revue de sécurité

### Livrables

- choix DSI documentés : plateforme, identité, PostgreSQL, stockage, sauvegarde,
  supervision, responsabilités et procédures d'incident.
- revue RSSI/DPO/juridique et politique de conservation.
- checklist de sécurité entièrement reprise avec preuve ou blocage explicite.
- restauration, rotation des secrets, mise à jour et retour arrière testés.

### Tests

- test de restauration sur environnement isolé.
- scans de dépendances, image, secrets et configuration ; analyse des licences.
- tests d'autorisation et session de sécurité ciblée.
- test de charge prudent sans donnée réelle.
- exercice de rollback et indisponibilité d'une dépendance.
- validation que journaux, sauvegardes et supervision ne contiennent aucune
  donnée génétique individuelle.

### Critère de sortie

La porte sécurité est signée par les responsables compétents et aucun contrôle
bloquant n'est seulement « reporté ». Sans cette preuve, le produit reste limité
aux données synthétiques, même si les lots fonctionnels sont terminés.

## Prochaine action recommandée

Valider la conception et retenir pour le lot 1 la ligne Django/MFA. Ensuite
seulement, initialiser le projet avec le modèle utilisateur personnalisé,
PostgreSQL, les contrôles de santé et les premiers tests de migrations. Le choix
du stockage peut rester ouvert jusqu'avant le lot 4 et celui de la file jusqu'au
lot 6.
