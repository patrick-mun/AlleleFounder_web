# Plan de développement par lots

**Statut :** proposé

**Règle :** chaque lot est petit, vérifiable et livrable sans anticiper les
dépendances du lot suivant. Aucune donnée réelle avant la porte du lot 9.

Les pages visibles ne sont pas repoussées à la fin du projet. Elles commencent
au lot 2 et évoluent avec le domaine qu'elles présentent. Le détail des écrans,
de leurs états et des maquettes de référence est tenu dans
[`ui_delivery_plan.md`](ui_delivery_plan.md).

## Contrôles transversaux de chaque lot

- `git diff --check` et état Git inspecté.
- Tests ciblés avant la suite élargie.
- Tests d'isolation entre organisations pour tout nouvel objet exposé.
- Tests des quatre rôles pour toute nouvelle action.
- Aucune donnée génétique, identité réelle, sortie de run ou secret versionné.
- Documentation et journal de décisions mis à jour si un contrat change.
- Dépendances externes simulées dans les tests unitaires.
- Pour toute page ajoutée : états vide, chargement, erreur, accès refusé et
  succès traités lorsqu'ils s'appliquent.
- Navigation au clavier, intitulés accessibles, contraste, adaptation mobile et
  absence d'information portée par la couleur seule vérifiés.
- Revue visuelle avec des données exclusivement synthétiques contre la maquette
  de référence du lot ; les textes, le logo et le nom de domaine restent à
  valider et ne sont pas recopiés comme des contrats.

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

### Pages visibles

Aucune. Ce lot définit les parcours et les maquettes ; il ne livre pas encore
d'interface exécutable.

## Lot 1 — socle Django, PostgreSQL et santé

**Statut :** terminé et vérifié le 27 novembre 2026.

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

### Pages visibles

- page technique d'accueil confirmant que l'application répond ;
- administration Django réservée au développement ;
- pages d'erreur minimales et endpoints de santé.

Ces écrans valident uniquement le socle. Ils ne constituent ni l'accueil public
ni l'interface finale d'AlleleFounder.

### Validation de clôture

- 14 tests Django, Ruff, `check` et `check --deploy` réussis ;
- migrations appliquées sur PostgreSQL 18.7 et disponibilité vérifiée ;
- image construite, exécutée sous l’UID non privilégié `10001` et Gunicorn
  démarré sans erreur ;
- fichiers statiques collectés à la construction, CSS de l’administration servi
  en HTTP 200 avec compression gzip ;
- vivacité, disponibilité, page d’accueil et administration vérifiées dans le
  compose local.

## Lot 2 — comptes, MFA, organisations et autorisations

**Statut :** terminé et vérifié le 27 novembre 2026.

### Livrables

- demande d'accès publique, décision administrative, invitation privée,
  validation d'adresse, MFA obligatoire et récupération.
- `Organization`, `Membership` et quatre rôles.
- résolution serveur de l'organisation active et services d'autorisation.
- audit des invitations, connexions, MFA et changements de rôle.

### Pages et parcours visibles

- accueil public : objectif, fonctionnement général, sécurité, documentation et
  accès à la connexion ;
- demande d'accès, confirmation de réception et file de décision réservée aux
  administrateurs de plateforme ;
- connexion, récupération de compte, activation d'une invitation et validation
  de l'adresse professionnelle ;
- configuration et challenge MFA, alternatives passkey/code de récupération et
  affichage unique des codes de secours ;
- sélection de l'organisation active lorsqu'un compte en possède plusieurs ;
- première version du cadre applicatif authentifié : navigation, organisation
  active, notifications et compte ;
- tableau de bord dans son état vide, avec actions autorisées selon le rôle ;
- équipe : membres, invitations et rôles ; compte : profil, sécurité et sessions ;
- page de service indisponible distinguant application, maintenance et services
  asynchrones lorsqu'ils seront introduits.

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

L'accueil, l'activation sur invitation, le MFA et le cadre applicatif sont
utilisables sur ordinateur et mobile et reprennent la hiérarchie des figures 4
à 7 de la maquette, sans prétendre livrer encore les études ou analyses.

### Validation de clôture

- 43 tests Django réussis sur PostgreSQL, dont demande sans création de compte,
  décision administrative, inscription par passkey, invitation expirée, compte
  désactivé, MFA obligatoire, isolation de deux organisations, matrice des
  quatre rôles, réauthentification et protection du dernier administrateur ;
- Ruff, `check`, `check --deploy` et absence de migration manquante vérifiés ;
- Prettier CSS, html-validate, Stylelint et contrôles complémentaires du skill
  `web-code-conventions` réussis sans erreur ni avertissement de lint ;
- image reconstruite, migrations appliquées et Gunicorn exécuté sous l'UID non
  privilégié `10001` ; accueil, connexion, CSS, vivacité et disponibilité
  servis en HTTP 200 ;
- e-mails locaux capturés par Mailpit sans dépendre d'un serveur SMTP externe ;
- accueil revu à 1 440 px et connexion revue en mise en page étroite à 500 px,
  sans débordement ; les données présentées restent synthétiques.

## Lot 3 — études, variants, familles et individus

### Livrables

- `Study`, `TargetVariant`, `Family`, `Individual` et parcours étapes 1 à 3.
- validations autosomiques, codes stables, filiation et révisions de brouillon.
- liste/détail d'études filtrées par organisation.

### Pages et parcours visibles

- liste des études avec recherche, filtres, état vide et création ;
- détail d'une étude avec synthèse et historique de brouillon ;
- assistant étape 1 « Contexte » ;
- assistant étape 2 « Cible » ;
- assistant étape 3 « Familles », organisé famille d'abord, avec membres,
  filiations, identifiants stables et indicateurs de complétude ;
- navigation entre étapes conservant le brouillon et signalant un conflit de
  révision sans écraser silencieusement les changements.

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

La page Familles correspond fonctionnellement à la figure 8 : elle montre les
membres par famille et la complétude attendue, mais n'invente encore aucune
source ni preuve de génotype.

## Lot 4 — sources et preuves de génotype

### Livrables

- interface de stockage, quarantaine, `SourceFile`, `IndividualSource` et
  `TargetGenotypeEvidence`.
- dépôt multiple avec confirmation explicite des affectations.
- parcours étapes 4 et 5, sans validation scientifique réelle.

### Pages et parcours visibles

- assistant étape 4 « Sources » : dépôt simple ou multiple, quarantaine,
  contrôle de format et association explicite fichier-individu ;
- confirmation manuelle des associations proposées, sans validation silencieuse ;
- assistant étape 5 « Génotypes » : saisie/import de la preuve cible, origine,
  statut et diagnostic par individu ;
- vues Sources et Génotypes de l'étude avec états dépôt en cours, rejeté,
  indisponible, à confirmer et validé techniquement.

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

L'association des sources reprend la figure 9 et rend toujours visibles la
famille, l'individu concerné, l'empreinte calculée et l'action de confirmation.

## Lot 5 — compilation et validation des entrées V2

### Livrables

- compilateur déterministe pour `samples.tsv`, `variant.yaml`, `genotypes.tsv`
  et `pipeline.yaml`.
- aperçu lisible, diagnostics locaux et adaptateur de validation moteur simulé.
- `StudySnapshot` avec manifest et empreintes.

### Pages et parcours visibles

- assistant étape 6 « Vérification » : synthèse familles/individus/sources/
  génotypes, erreurs bloquantes, avertissements et liens de correction ;
- aperçu lisible et téléchargement contrôlé des quatre entrées V2 générées ;
- assistant étape 7 « Gel » : comparaison de l'empreinte revue, approbation et
  création de l'instantané immuable ;
- liste et détail des instantanés avec version, auteur, date, manifest,
  provenance et statut de validation.

Le bouton de lancement scientifique reste indisponible dans ce lot : le gel est
réel, mais l'exécution asynchrone arrive au lot 6.

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

La revue reprend la figure 10 : elle distingue clairement les objets métier,
les fichiers générés, les limites et les blocages avant gel.

## Lot 6 — analyses asynchrones simulées

### Livrables

- file de tâches choisie, worker applicatif séparé et adaptateur moteur factice.
- `AnalysisRun`, `AnalysisStep`, idempotence, suivi et erreurs simulées.
- vues de suivi sans polling agressif ; HTMX peut être introduit ici.

### Pages et parcours visibles

- activation de l'action « Lancer » depuis un instantané approuvé ;
- liste des analyses avec filtres, étude, version, auteur, dates et état ;
- détail d'une analyse simulée avec progression, étapes, tentatives, prochaine
  action et diagnostic sûr ;
- tableau de bord alimenté par les études, analyses et actions synthétiques ;
- états en attente, en cours, réussi, échoué et bloqué, avec reprise lorsque le
  contrat la permet et sans promesse d'annulation.

### Tests

- livraison double, retry, timeout, perte du worker et ordre d'événements.
- deux demandes concurrentes sur le même run.
- transitions autorisées/interdites et conservation des tentatives.
- panne de file, de stockage et de base simulée.
- aucun traitement long dans une requête HTTP.

### Critère de sortie

Les scénarios succès, échec, blocage et reprise synthétiques sont observables,
idempotents et cohérents après redémarrage du worker.

Le suivi correspond à la figure 11 : libellé, icône et explication accompagnent
chaque état ; la couleur n'est jamais le seul signal.

## Lot 7 — adaptateur vers le moteur réel

### Livrables

- image scientifique épinglée par digest et matrice de compatibilité.
- validation CLI puis lancement réel depuis le worker isolé.
- import contrôlé du manifest, des audits et artefacts synthétiques.

### Pages et parcours visibles

- mêmes pages qu'au lot 6, désormais alimentées par le moteur épinglé ;
- provenance technique visible : version, digest, instantané, tentatives et
  contrôles d'intégrité ;
- diagnostic utilisateur limité aux informations sûres, avec identifiant de
  corrélation pour le support ; aucun journal brut sensible n'est exposé.

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

### Pages et parcours visibles

- file des décisions attendues et dossier de preuve associé ;
- détail d'une décision avec réauthentification, empreinte, auteur, rôle,
  commentaire, effet et caractère immuable ;
- détail d'analyse complet : Synthèse, Étapes, Décisions, Résultats, Artefacts,
  Rapport et Provenance ;
- résultats structurés par domaines disponibles, notamment Parenté, Population
  et IBD, sans transformer un statut technique en conclusion scientifique ;
- téléchargement autorisé des artefacts et circuit de revue/publication du
  rapport ;
- notifications et audit filtrés par organisation et droits.

### Tests

- décision sur mauvaise empreinte, double approbation et conflit auteur/relecteur.
- reprise concurrente et changement de configuration refusés.
- artefact d'une autre organisation, sensible ou non déclaré refusé.
- HTML/SVG/PDF malveillant ou altéré traité selon la politique.
- `NOT_EVALUATED` visible et jamais transformé en succès.

### Critère de sortie

Les décisions et reprises respectent les contrats V2 ; un rapport n'est publié
qu'après contrôles d'intégrité, autorisation et revue prévues.

La présentation des résultats reprend la figure 12 : faits, statut
d'interprétation, limites, commentaires humains et provenance restent séparés.

## Lot 9 — préparation du pilote CHU et revue de sécurité

### Livrables

- choix DSI documentés : plateforme, identité, PostgreSQL, stockage, sauvegarde,
  supervision, responsabilités et procédures d'incident.
- revue RSSI/DPO/juridique et politique de conservation.
- checklist de sécurité entièrement reprise avec preuve ou blocage explicite.
- restauration, rotation des secrets, mise à jour et retour arrière testés.

### Pages et parcours visibles

- paramètres d'organisation réellement retenus pour le pilote ;
- informations de service et de maintenance sans détail sensible ;
- écrans d'indisponibilité, expiration de session et récupération vérifiés dans
  les conditions d'exploitation cibles ;
- aide, sécurité du compte et mentions institutionnelles finalisées selon les
  validations DSI, RSSI, DPO et juridiques.

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

Le lot 1 étant clos, préparer le lot 2 en validant la bibliothèque MFA et le
parcours d'invitation. La première livraison visible doit couvrir l'accueil
public, l'activation du compte, le MFA, la sélection d'organisation et le cadre
applicatif avec tableau de bord vide. Le choix du stockage peut rester ouvert
jusqu'avant le lot 4 et celui de la file jusqu'au lot 6.
