# Modèle métier initial

**Statut :** proposé pour validation avant migrations

**Principe :** le domaine web décrit la préparation et la traçabilité ; il ne
reproduit pas le modèle scientifique interne du moteur.

## 1. Vue des dépendances

```text
User ──< Membership >── Organization
                           │
                           ├──< Study ──1 TargetVariant
                           │      │
                           │      ├──< Family ──< Individual
                           │      │                  │
                           │      │                  ├──0..1 IndividualSource >── SourceFile
                           │      │                  └──0..1 TargetGenotypeEvidence
                           │      │
                           │      └──< StudySnapshot ──< AnalysisRun
                           │                               │
                           │                               ├──< AnalysisStep
                           │                               └──< HumanDecision
                           │
                           ├──< Artifact
                           └──< AuditEvent
```

`SourceFile`, `StudySnapshot`, `AnalysisRun`, `Artifact` et `AuditEvent` portent
également une relation directe vers `Organization` afin de rendre le filtrage
de sécurité explicite et vérifiable, même si l'organisation peut être retrouvée
par une autre relation.

## 2. Entités d'identité et d'autorisation

### User

- Identité applicative, adresse électronique normalisée et vérifiée, état du
  compte et préférences non sensibles.
- Ne porte aucun rôle global donnant implicitement accès aux études.
- Un compte peut appartenir à plusieurs organisations.

### Organization

- Frontière de tenant et de gouvernance.
- Possède un identifiant public opaque, un nom, un état et des paramètres non
  secrets.
- La suppression physique n'est pas prévue dans le premier produit ; une
  désactivation conserve l'audit et bloque les nouveaux accès.

### Membership

- Joint `User` et `Organization` avec un rôle parmi `ADMIN`, `ANALYST`,
  `REVIEWER`, `READER` et un état d'invitation/activation.
- Unicité `(organization, user)`.
- Toute modification de rôle produit un événement d'audit.
- La séparation des tâches « auteur d'une proposition / relecteur » est une
  règle de service, pas un nouveau rôle implicite.

## 3. Constitution d'une étude

### Study

- Appartient à une organisation et possède un code métier unique dans celle-ci.
- Contient le contexte, l'assemblage, le statut de brouillon et une révision
  courante.
- Une étude gelée reste consultable ; une correction crée une nouvelle révision
  et un nouvel instantané.

### TargetVariant

- Relation un-à-un avec `Study` pour le périmètre autosomique mono-variant V2.
- Conserve gène, chromosome, position en `bp`, REF, ALT, assemblage, transcrit,
  HGVS optionnels, identifiants et confirmations de référence/annotation.
- Aucune valeur de cible n'est codée dans le logiciel.
- Les études multi-variants, mitochondriales, X/Y ou structurales exigent un
  nouveau contrat ; elles ne seront pas introduites par des champs ambigus.

### Family

- Appartient à une étude ; `family_code` devient le futur `FID` après validation
  et échappement déterministe.
- Unicité `(study, family_code)`.
- Un contrôle non apparenté est une famille unitaire, ce qui évite un second
  modèle de participant.

### Individual

- Appartient à une famille et, par elle, à une étude et une organisation.
- Possède un `individual_code` stable, un futur `IID`, le sexe selon le
  vocabulaire du moteur, un statut clinique descriptif, un groupe et des
  métadonnées de lot nécessaires au contrat.
- `father` et `mother` sont optionnels et doivent référencer des individus de la
  même famille ; une personne ne peut être son propre ancêtre.
- Unicité de `individual_code`, `sample_id` et du couple futur `(FID, IID)` dans
  l'étude.
- Le statut clinique et le groupe ne sont jamais une source de génotype.

## 4. Sources et preuves

### SourceFile

- Représente un fichier génétique dans un stockage externe : clé opaque,
  empreinte SHA-256, taille, type déclaré/détecté, état de validation et niveau
  de sensibilité.
- Ne contient ni chemin absolu fourni par l'utilisateur, ni blob en base.
- Un fichier téléversé est d'abord en quarantaine ; il n'est affectable qu'après
  validation technique minimale.

### IndividualSource

- Association explicite entre un `Individual` et un `SourceFile`.
- Cardinalité initiale : zéro ou une source active par individu, et une source
  active affectée à au plus un individu dans une étude.
- Conserve l'acteur, la date et le mode d'affectation. Une suggestion issue d'un
  dépôt multiple n'est active qu'après confirmation humaine.
- Un remplacement désactive l'association antérieure sans modifier le fichier
  ou l'historique.

### TargetGenotypeEvidence

- Relation zéro-ou-un active par individu et par révision d'étude.
- Contient le génotype diploïde explicite (`REF/REF`, `REF/ALT`, `ALT/ALT` ou
  valeur manquante autorisée par le contrat), la source individuelle, la méthode
  de mesure, la date, le statut de vérification et l'acteur.
- La provenance clinique ou le groupe sont interdits comme origine.
- Les anciennes preuves ne sont pas écrasées : une correction crée une nouvelle
  version et invalide les aperçus non gelés concernés.

## 5. Gel et analyses

### StudySnapshot

- Capture immuable d'une révision complète de l'étude.
- Conserve la version du contrat, les empreintes des objets sources, les
  artefacts compilés, le résultat de validation et l'approbation de gel.
- Une seule charge canonique produit toujours les mêmes octets compilés ; les
  fichiers texte imposent encodage UTF-8, ordre des lignes et fin de ligne.
- États proposés : `COMPILING`, `INVALID`, `READY_FOR_REVIEW`, `APPROVED`,
  `SUPERSEDED`.
- Un instantané approuvé n'est jamais modifié. Tout changement produit un nouvel
  instantané.

### AnalysisRun

- Référence exactement un `StudySnapshot` approuvé.
- Conserve initiateur, état, dates, identifiant de run moteur, version du paquet,
  révision Git, digest de l'image scientifique et empreinte de configuration.
- États web proposés : `QUEUED`, `STARTING`, `RUNNING`, `WAITING_DECISION`,
  `FAILED`, `SUCCEEDED`, `CANCEL_REQUESTED`, `CANCELLED`.
- `CANCELLED` ne sera activé qu'après existence d'un protocole worker/moteur
  sûr ; l'UI ne l'invente pas.

### AnalysisStep

- Représente fidèlement une étape déclarée dans le manifest du moteur.
- Unicité `(analysis_run, engine_stage_id)`.
- Conserve état moteur, criticité, tentative, signature, dates, code d'erreur et
  références aux audits. Les sorties brutes ne sont pas recopiées en colonnes
  métier.
- `NOT_EVALUATED` est distinct de `SUCCEEDED` et de `SKIPPED`.

### HumanDecision

- Porte le type de décision déclaré par le contrat moteur, l'objet exact revu,
  son empreinte, le verdict, le rôle du relecteur, la date et une justification
  structurée.
- Une décision n'est valide que pour l'empreinte affichée au relecteur.
- Le premier produit n'a pas de verdict générique « forcer ».
- Selon la politique à valider, l'auteur de la proposition ne peut pas approuver
  sa propre décision sensible.

## 6. Artefacts et audit

### Artifact

- Métadonnée d'un objet stocké : organisation, propriétaire logique, type,
  taille, SHA-256, classe de sensibilité, clé opaque, version de contrat et état
  de publication.
- Un artefact n'est téléchargeable qu'après autorisation serveur et émission
  d'un accès court, ou diffusion contrôlée par Django.
- Un fichier présent dans le stockage mais non publié par un contrat n'est pas
  un artefact scientifique.

### AuditEvent

- Journal append-only d'une action importante : acteur technique, organisation,
  action, type et identifiant opaque de cible, résultat, date, adresse réseau
  réduite selon politique et identifiant de corrélation.
- Ne contient aucun génotype, identité de participant, contenu de fichier,
  secret ou journal scientifique brut.
- Les événements de sécurité et les audits scientifiques restent liés mais ne
  sont pas confondus.

## 7. Invariants transversaux

1. Toute lecture ou écriture d'un objet tenanté vérifie l'organisation.
2. Un `StudySnapshot` et un `AnalysisRun` appartiennent à la même organisation
   que l'étude source.
3. Un run ne peut référencer qu'un instantané `APPROVED`.
4. Toute décision référence une empreinte immuable et un contrat connu.
5. Une source génétique active n'est jamais partagée silencieusement entre deux
   individus.
6. Une preuve de génotype est explicite et indépendante du statut clinique.
7. Les suppressions métier sensibles sont logiques ; les politiques de purge
   physique restent à définir avec le cadre institutionnel.
8. Les transitions d'état passent par des services explicites et sont testées.

## 8. Points ouverts non bloquants pour les premières migrations

- Durées de conservation et processus de purge : à arbitrer avec DSI, DPO et
  juridique avant données réelles.
- Politique exacte de double contrôle pour chaque type de décision : à fermer
  avant le lot 8.
- Vocabulaires d'affichage clinique : le stockage doit rester aligné sur les
  vocabulaires V2, sans conversion implicite.
- Historique temporel générique ou tables de versions ciblées : commencer par
  des versions ciblées pour les preuves et instantanés, réévaluer après le lot 4.
