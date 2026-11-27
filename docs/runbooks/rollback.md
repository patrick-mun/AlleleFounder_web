# Retour arrière du lot 1

Avant une mise en production, vérifier sur une copie synthétique que les
migrations concernées sont réversibles. Pour revenir à une migration donnée :

1. retirer le trafic de la version défaillante ;
2. conserver les journaux techniques et relever la migration courante avec
   `python manage.py showmigrations` ;
3. déployer le code compatible avec l’état cible ;
4. exécuter `python manage.py migrate <application> <migration_cible>` dans une
   tâche unique ;
5. remettre en service seulement après réussite de `/health/ready/`.

Si Django signale une migration irréversible, ou si des données pourraient être
perdues, arrêter la procédure et restaurer la sauvegarde testée selon le plan
institutionnel. Le volume PostgreSQL local du compose n’est pas une sauvegarde.
