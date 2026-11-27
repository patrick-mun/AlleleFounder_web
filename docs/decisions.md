# Audit de conception et registre des décisions

**Date de l’audit :** 27 novembre 2026

## 1. Documents audités

L’audit initial a couvert `AGENTS.md`, `README.md`, `SESSION.md`, le dossier
d’architecture HTML, le contrat d’infrastructure, la checklist de sécurité et
les contrats V2 relatifs à l’orchestrateur, aux métadonnées, aux sources ACPA,
à la conversion, au variant cible, au gel des cohortes et au rapport. Les
schémas `samples_master`, `target_variant_metadata`,
`target_variant_genotypes` et `run_manifest`, ainsi que la CLI publique, ont
été vérifiés pour distinguer les intentions des interfaces réellement exposées.

## 2. Résultat de l’audit

Les documents convergent sur les points structurants : famille d’abord,
génotype explicite, provenance, instantanés immuables, décisions liées aux
empreintes, séparation web/worker, stockage hors base et prudence scientifique.
Ils suffisent pour concevoir le socle sans choisir aujourd’hui l’infrastructure
finale du CHU.

Les écarts à ne pas masquer sont :

- les maquettes décrivent parfois des capacités futures comme un parcours
  continu, alors que l’annulation, le verrou de reprise et plusieurs étapes de
  production ne sont pas encore contractés par le moteur ;
- la CLI publique valide la configuration et `samples.master.tsv`, mais ne
  fournit pas encore de commande autonome observée pour valider le couple cible
  et génotypes ;
- l’architecture historique regroupe plusieurs responsabilités dans `studies`
  et `analyses`; le découpage proposé ici isole preuves, instantanés et
  intégration pour limiter leur couplage ;
- les états produit, file de tâches, manifest V2 et interprétation scientifique
  sont différents et doivent rester stockés séparément ;
- l’approbation du registre est actuellement encodée dans la configuration
  avant un nouveau run, tandis que certaines décisions suivantes portent sur
  des artefacts de run. Le modèle web doit accepter ces deux portées.

## 3. Décidé

- Python 3.12.16, Django 5.2.19 LTS et dépendances résolues avec `pip-tools` ;
- PostgreSQL 18.7 pour l’environnement conteneurisé du lot 1 ;
- configuration par variables d’environnement validées strictement, sans repli
  SQLite ;
- WhiteNoise 6.12.0 pour servir les fichiers statiques collectés dans l’image
  applicative Gunicorn ;
- Django modulaire, PostgreSQL, rendu serveur et Python 3.12.
- Utilisateur personnalisé avant la première migration.
- Schéma partagé avec `Organization` comme frontière obligatoire et testée.
- Installation mono-CHU initiale, architecture portable sans cloud public
  obligatoire.
- Un fichier source génétique par individu pour le contrat ACPA courant.
- Une preuve explicite et sourcée du génotype cible par individu au gel.
- Instantanés, runs, décisions et artefacts immuables par version.
- Worker séparé pour le moteur et les outils scientifiques.
- Images applicative et scientifique distinctes lors du raccordement réel.
- Données synthétiques uniquement jusqu’à clôture de la porte de sécurité.

## 4. Proposé

- paquet source sous `src/allelefounder/` ;
- applications Django séparées `studies`, `evidence`, `snapshots`, `analyses`,
  `artifacts`, `audit` et `integration` ;
- révision courante explicite sur `Study`, avec nouvel instantané immuable à
  chaque gel ; une table de révision séparée sera introduite seulement si les
  parcours du lot 3 en démontrent le besoin ;
- compilation déterministe dans des services purs, puis validation autoritative
  via l’adaptateur de la version épinglée du moteur ;
- invitation privée, adresse vérifiée et MFA pour le premier pilote ;
- identifiants internes opaques dans les tâches et les URLs ;
- faux adaptateur moteur jusqu’au lot 6 inclus.

## 5. Décisions réellement bloquantes

### Décisions clôturées lors de l’initialisation du lot 1

| Décision | Proposition | Pourquoi elle bloque |
|---|---|---|
| Version Django et résolution des dépendances | Django 5.2.19 LTS et `pip-tools` 7.7.0, fichiers verrouillés avec empreintes | détermine le squelette, les réglages et la politique de maintenance |
| Nom du paquet Python et modèle utilisateur | `allelefounder`, utilisateur personnalisé par courriel | très coûteux à changer après les premières migrations |
| Convention de configuration | variables/fichiers injectés, validation stricte au démarrage | conditionne tous les environnements et tests |

Le nom de paquet et le modèle utilisateur sont retenus dans cette conception.
Ces trois décisions sont désormais implémentées. Le modèle utilisateur est créé
par la migration initiale `accounts.0001_initial` avant toute migration métier.

### Avant les lots ultérieurs

| Échéance | Décision bloquante |
|---|---|
| Lot 2 | bibliothèque MFA/invitation et stratégie d’intégration future au SSO CHU |
| Lot 4 | backend objet initial, chiffrement, tailles, formats et rétention des imports |
| Lot 5 | entrée publique supportée pour valider toutes les entrées V2 compilées |
| Lot 6 | broker, sémantique de livraison, verrouillage et contrat de reprise |
| Lot 7 | digest de l’image scientifique, manifeste de build et limites de ressources |
| Préproduction | PostgreSQL, coffre de secrets, TLS, courrier et observabilité institutionnels |
| Données réelles | RPO/RTO, conservation, suppression, responsabilités et validations de sécurité/juridiques |

## 6. Ouvert mais non bloquant aujourd’hui

- nom public et identité visuelle définitive ;
- import familial en masse au-delà du dépôt multiple confirmé ;
- SSO institutionnel exact ;
- plateforme de conteneurs ou machines virtuelles du CHU ;
- quotas commerciaux, facturation et inscription publique ;
- API publique ;
- suppression définitive et durée de conservation ;
- annulation d’un run scientifique.

## 7. Interdit par l’architecture

- modifier ou copier une méthode scientifique dans Django ;
- déduire un génotype depuis une caractéristique clinique ou familiale ;
- exécuter le pipeline dans le processus web ;
- considérer une fonction privée du moteur comme contrat public ;
- conserver des blobs génétiques dans PostgreSQL ;
- rendre un chemin physique ou une URL signée durable visible dans l’audit ;
- réécrire un instantané, un run, une décision ou un artefact publié ;
- présenter `READY_FOR_SCIENTIFIC_REVIEW` comme preuve d’effet fondateur ;
- utiliser des données réelles avant clôture documentée des portes de sécurité.

## 8. Recommandation de passage au lot 1

Faire relire et accepter ce lot 0, puis ouvrir un lot 1 limité à la sélection
documentée des versions, au squelette Django, au modèle utilisateur vide, à
PostgreSQL et aux contrôles de santé. Ne pas commencer simultanément
l’authentification complète, les études ou le raccordement du moteur.
