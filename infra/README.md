# Infrastructure du lot 1

Le fichier `compose/compose.yaml` fournit PostgreSQL 18.7 et l’application web
pour le développement et les tests d’intégration. Les images de base sont
épinglées par digest. Ce compose n’est pas une définition de production CHU.
La construction collecte les fichiers statiques versionnés ; WhiteNoise les
sert ensuite depuis le processus Gunicorn.

## Démarrage local

```bash
cp .env.example .env
docker compose --env-file .env -f infra/compose/compose.yaml up -d db
set -a && source .env && set +a
export POSTGRES_HOST=127.0.0.1 POSTGRES_PORT=55432
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

## Exécution complète dans Docker

```bash
docker compose --env-file .env -f infra/compose/compose.yaml up -d db
docker compose --env-file .env -f infra/compose/compose.yaml build web
docker compose --env-file .env -f infra/compose/compose.yaml \
  run --rm web python manage.py migrate --noinput
docker compose --env-file .env -f infra/compose/compose.yaml up -d web
```

L’application est ensuite accessible sur `http://localhost:8000` et PostgreSQL
sur `127.0.0.1:55432` depuis le poste. Entre conteneurs, PostgreSQL reste sur
`db:5432`.

Ne jamais réutiliser les valeurs d’exemple hors d’un poste de développement.
Les opérations de migration et de retour arrière sont décrites dans
`docs/runbooks/`.
