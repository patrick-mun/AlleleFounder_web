# Architecture applicative initiale

## 1. Compréhension du produit

**Décidé.** AlleleFounder Web est le plan de contrôle du pipeline scientifique
V2 : il organise les utilisateurs, organisations, études familiales, droits,
preuves, instantanés, analyses, décisions, artefacts et audits. Il ne devient
pas une seconde implémentation du pipeline.

Le parcours d’étude reste « famille d’abord » : contexte, variant cible,
familles et individus, sources par individu, preuves de génotype, vérification,
puis gel et lancement. La première cible réelle est une instance mono-CHU ; le
modèle conserve néanmoins une organisation explicite afin de tester l’isolation
et de permettre une évolution ultérieure.

## 2. Frontières techniques

### Décidé

- monolithe Django modulaire, Python 3.12, PostgreSQL et rendu HTML serveur ;
- HTMX seulement lorsqu’il améliore une interaction locale ;
- plan web et plan de calcul séparés ;
- worker isolé avant toute exécution scientifique réelle ;
- stockage abstrait pour sources, instantanés et artefacts ;
- configuration et secrets injectés ;
- releases sous images OCI immuables, identifiées par digest ;
- logique métier dans des services testables, indépendants des vues ;
- organisation résolue côté serveur et filtrage systématique de tous les objets.

### Interdit

- frontend JavaScript séparé sans nouvelle décision d’architecture ;
- microservices métier pendant les premiers lots ;
- blob génétique dans PostgreSQL ou fichier durable sur le conteneur web ;
- import de fonctions privées du moteur ;
- appel d’un outil scientifique depuis une requête HTTP ;
- socket Docker, terminal ou commande libre accessibles au service web ;
- clé primaire ou `organization_id` reçu du navigateur utilisé seul comme
  contrôle d’accès.

## 3. Arborescence proposée

L’arborescence n’est pas encore créée ; elle guide l’initialisation du lot 1.

```text
AlleleFounder_web/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── manage.py
├── src/
│   └── allelefounder/
│       ├── config/                 réglages, URLs, ASGI et WSGI
│       ├── accounts/               utilisateur, invitations, MFA et sessions
│       ├── organizations/          organisations, membres, rôles et contexte
│       ├── studies/                études, variants, familles et individus
│       ├── evidence/               sources et preuves de génotype cible
│       ├── snapshots/              compilation, validation et gel
│       ├── analyses/               runs, étapes, tentatives et décisions
│       ├── artifacts/              métadonnées et contrôle d’accès au stockage
│       ├── audit/                  événements d’audit non sensibles
│       ├── integration/            ports et adaptateurs Effet_fondateur2
│       ├── common/                 primitives réellement partagées
│       ├── templates/
│       └── static/
├── tests/
│   ├── factories/                  objets synthétiques uniquement
│   ├── integration/
│   └── system/
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── domain_model.md
│   ├── engine_integration.md
│   ├── development_plan.md
│   ├── decisions.md
│   └── adr/                        décisions futures numérotées
├── infra/                          ajouté progressivement au lot 1
│   ├── docker/
│   ├── compose/
│   ├── environments/
│   └── runbooks/
└── scripts/                        commandes de développement non métier
```

Le paquet `integration` contient des interfaces et adaptateurs ; il ne contient
ni modèles scientifiques, ni implémentation des étapes V2. Les commandes Django
restent dans l’application propriétaire de leur comportement plutôt que dans
un dossier global de scripts.

## 4. Découpage des applications Django

| Application | Responsabilité | Dépendances autorisées principales |
|---|---|---|
| `accounts` | utilisateur personnalisé, activation et sécurité du compte | Django auth ; adaptateur MFA retenu plus tard |
| `organizations` | organisations, appartenances, rôles, contexte actif | `accounts`, `audit` |
| `studies` | contexte, cible, familles, individus, révisions | `organizations`, `audit` |
| `evidence` | fichiers sources, association aux individus, preuves de génotype | `studies`, `artifacts`, `audit` |
| `snapshots` | prévisualisation déterministe, validation, approbation et gel | `studies`, `evidence`, `artifacts`, `integration` |
| `analyses` | runs, étapes, tentatives, décisions et états | `snapshots`, `artifacts`, `integration`, `audit` |
| `artifacts` | métadonnées, empreintes, sensibilité, accès logique au stockage | `organizations`, `audit` |
| `audit` | événements append-only et export autorisé | `accounts`, référence opaque aux objets |
| `integration` | ports du moteur, formats de transfert et adaptateurs worker | aucun import depuis les vues |
| `common` | identifiants, temps, erreurs et utilitaires transversaux minimaux | aucune logique métier propriétaire |

Les dépendances circulaires sont évitées par des services et des identifiants
opaques. `audit` ne devient pas un entrepôt de payloads métier. Un événement
d’audit peut conserver le type et l’identifiant opaque d’une cible, mais pas son
génotype ni son contenu.

## 5. Flux principal

```text
Utilisateur autorisé
  -> brouillon Study
  -> familles / individus / cible
  -> sources et preuves explicites
  -> aperçu compilé et constats de validation
  -> approbation liée à une empreinte
  -> StudySnapshot immuable
  -> AnalysisRun
  -> tâche interne après commit
  -> worker et adaptateur du moteur
  -> manifest / étapes / artefacts contrôlés
  -> décisions humaines et publication autorisée
```

Une modification postérieure au gel crée une nouvelle révision et un nouvel
instantané. Elle ne modifie jamais un run existant.

## 6. Tenancy et autorisations

**Décidé.** Le premier modèle utilise un schéma PostgreSQL partagé avec une
frontière `Organization` explicite. Tous les agrégats métier portant une donnée
d’organisation possèdent une relation directe vers l’organisation, même si elle
pourrait être déduite par une jointure. Cette redondance contrôlée facilite les
contraintes, les sélecteurs et l’audit d’isolation.

Les lectures passent par des sélecteurs exigeant le contexte d’organisation ;
les écritures passent par des services qui revérifient appartenance, rôle et
état. Les tâches reçoivent des identifiants internes, rechargent elles-mêmes
l’organisation, puis vérifient les relations avant tout accès au stockage.

## 7. Déploiement

Le développement local peut utiliser `.venv`. La qualification d’une release
utilise une image applicative et, à partir du raccordement réel, une image
scientifique distincte. Le proxy est l’unique entrée réseau. Les migrations
sont exécutées par un job unique, jamais au démarrage de chaque réplique web.

Les choix concrets de broker, stockage, coffre de secrets et plateforme CHU
restent des adaptateurs avec une échéance définie dans `decisions.md`.
