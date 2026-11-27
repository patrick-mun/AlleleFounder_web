# Migration de la base

Cette procédure s’applique à une version applicative déjà construite et testée.
L’opérateur doit disposer d’une sauvegarde restaurable et d’un accès PostgreSQL
contrôlé. Les variables `DJANGO_*` et `POSTGRES_*` doivent être injectées par le
gestionnaire de secrets de l’environnement.

1. vérifier la version d’image et la sauvegarde associée au déploiement ;
2. afficher le plan avec `python manage.py showmigrations --plan` ;
3. vérifier l’absence de migration inattendue avec
   `python manage.py makemigrations --check --dry-run` ;
4. exécuter `python manage.py migrate --noinput` dans une tâche unique ;
5. exécuter `python manage.py check --deploy` avec les réglages de production ;
6. vérifier `/health/ready/`, puis la page d’accueil.

Une migration ne doit jamais être lancée automatiquement par chaque réplique
web au démarrage.
