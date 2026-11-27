# AlleleFounder Web

Interface web Django du logiciel AlleleFounder.

Ce dépôt accueillera le plan de contrôle de l’application : comptes,
organisations, études familiales, autorisations, orchestration des analyses et
historique. Les calculs scientifiques restent dans le moteur autonome
[Effet_fondateur2](https://github.com/patrick-mun/Effet_fondateur2).

## Statut

Le lot 1 fournit le socle Django : PostgreSQL obligatoire, utilisateur
personnalisé par courriel, configuration stricte, page d’accueil, pages d’erreur,
sondes de vivacité et disponibilité, journaux JSON filtrés et image OCI.
L’authentification complète, les organisations, les études et le raccordement
au moteur scientifique appartiennent aux lots suivants.

Le lot 0 de conception est documenté dans [`docs/`](docs/README.md) :

- architecture, frontières et découpage des applications ;
- modèle métier initial et invariants multi-organisation ;
- contrats d’intégration progressifs avec le moteur ;
- plan de développement en lots avec tests et critères de sortie.

La cible initiale de déploiement est une installation institutionnelle sur
l’infrastructure interne du CHU. L’architecture devra rester portable vers une
éventuelle offre SaaS ultérieure.

## Principes initiaux

- ne pas recopier la logique scientifique du moteur dans Django ;
- raccorder le moteur par des contrats et versions explicites ;
- utiliser uniquement des données synthétiques pendant la construction ;
- séparer les requêtes web des traitements scientifiques asynchrones ;
- ne jamais versionner de donnée génétique, de secret ou de résultat de run.

## Développement

Python 3.12 est requis. PostgreSQL reste obligatoire en local et en test : il
n’existe aucun repli SQLite.

```bash
cp .env.example .env
python3.12 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements/development.txt
.venv/bin/pip install --no-deps -e .
docker compose --env-file .env -f infra/compose/compose.yaml up -d db
set -a && source .env && set +a
export POSTGRES_HOST=127.0.0.1 POSTGRES_PORT=55432
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Les contrôles ordinaires sont :

```bash
.venv/bin/ruff format --check .
.venv/bin/ruff check .
.venv/bin/python manage.py test
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
```

Les règles de contribution et contrôles de sécurité sont définis dans
[`AGENTS.md`](AGENTS.md). Les procédures d’exploitation minimales sont sous
[`docs/runbooks/`](docs/runbooks/).
