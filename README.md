# AlleleFounder Web

Interface web Django du logiciel AlleleFounder.

Ce dépôt accueillera le plan de contrôle de l’application : comptes,
organisations, études familiales, autorisations, orchestration des analyses et
historique. Les calculs scientifiques restent dans le moteur autonome
[Effet_fondateur2](https://github.com/patrick-mun/Effet_fondateur2).

## Statut

Les lots 1 et 2 fournissent le socle Django et le premier parcours produit :
PostgreSQL obligatoire, demande publique examinée par un administrateur,
invitation privée, inscription par le demandeur, adresse vérifiée et MFA
obligatoire. Le demandeur choisit une passkey ou un mot de passe complété par
une application de codes. Les organisations restent isolées avec quatre rôles.

Les études et le raccordement au moteur scientifique appartiennent aux lots
suivants. Les fichiers statiques versionnés sont collectés dans l’image et
servis par WhiteNoise derrière Gunicorn.

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
n’existe aucun repli SQLite. Node.js 20 ou ultérieur sert uniquement aux
contrôles HTML/CSS.

```bash
cp .env.example .env
python3.12 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements/development.txt
.venv/bin/pip install --no-deps -e .
npm ci
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
DJANGO_SETTINGS_MODULE=allelefounder.config.settings.test \
  .venv/bin/python manage.py test
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
npm run lint:web
```

## Premier accès local

L’inscription libre reste fermée. Après `createsuperuser`, démarrer le compose
complet puis suivre le même parcours qu’un utilisateur :

1. ouvrir `http://localhost:8000/demande-acces/` et transmettre une demande ;
2. consulter l’accusé de réception dans Mailpit sur
   `http://localhost:8025/` ;
3. se connecter avec le superutilisateur puis ouvrir
   `http://localhost:8000/administration/demandes-acces/` ;
4. choisir une organisation existante ou en créer une par son nom, attribuer le
   rôle, puis accepter la demande ;
5. ouvrir dans Mailpit le lien d’activation reçu ;
6. renseigner l’identité et choisir une passkey ou un mot de passe avec TOTP.

Le lien personnel valide l’adresse de courriel. L’administrateur décide de
l’organisation et du rôle, mais ne crée pas le profil à la place du demandeur.

En production, `DJANGO_MFA_ENCRYPTION_KEY` doit être une clé distincte de
`DJANGO_SECRET_KEY`. Le serveur SMTP, les hôtes autorisés, l’origine CSRF et les
identifiants PostgreSQL sont également obligatoires.

Pour exécuter l’ensemble dans Docker :

```bash
docker compose --env-file .env -f infra/compose/compose.yaml up -d db mailpit
docker compose --env-file .env -f infra/compose/compose.yaml build web
docker compose --env-file .env -f infra/compose/compose.yaml \
  run --rm web python manage.py migrate --noinput
docker compose --env-file .env -f infra/compose/compose.yaml up -d web mailpit
```

Les règles de contribution et contrôles de sécurité sont définis dans
[`AGENTS.md`](AGENTS.md). Les procédures d’exploitation minimales sont sous
[`docs/runbooks/`](docs/runbooks/).
