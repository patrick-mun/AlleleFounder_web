# Contrats d'intégration avec Effet_fondateur2

**Statut :** frontière décidée, adaptateur non implémenté

**Moteur audité :** paquet `effet-fondateur` 0.1.0, copie locale à la révision
`192614ebe621` sur une branche de travail ; cette copie n'est pas une release à
intégrer tant que son état reproductible n'est pas publié.

## 1. Principe

Le moteur reste autonome et utilisable par sa CLI. AlleleFounder Web ne dépend
que de surfaces publiques : commandes documentées, schémas distribués,
configuration résolue, manifest, audits et artefacts déclarés.

L'adaptateur se situe côté worker. Django enregistre une intention et un
instantané ; il ne lance jamais le moteur dans une vue ou un processus web.

## 2. Identification obligatoire d'une version moteur

Chaque compatibilité web–moteur est décrite par :

- version du paquet ;
- révision source complète ;
- digest de l'image OCI scientifique ;
- version du schéma de configuration ;
- empreinte du lot de schémas publics ;
- inventaire des outils externes produit par le moteur ;
- version de l'adaptateur web.

Une image scientifique est lancée par digest, jamais par un tag mutable en
production. Une nouvelle version moteur passe les tests contractuels avant
d'être autorisée pour de nouveaux runs. Un run existant conserve sa version.

## 3. Ports applicatifs proposés

L'application définit des interfaces stables, sans importer l'implémentation du
moteur :

```text
EngineCompatibility.check()
EngineValidator.validate_configuration(snapshot)
EngineValidator.validate_inputs(snapshot)
EngineRunner.start(run_request)
EngineRunner.inspect(engine_run_id)
EngineRunner.resume(engine_run_id)
EngineArtifacts.import_manifest(engine_run_id)
```

Les types transportent des identifiants, empreintes et références de stockage.
Ils ne transportent pas le contenu génétique dans la file de tâches.

## 4. Contrats produits par le compilateur web

Un `StudySnapshot` compile dans un espace isolé :

| Sortie | Source métier | Contrôle attendu |
|---|---|---|
| Répertoire de sources ACPA | `IndividualSource` + `SourceFile` | Une source par individu, noms sûrs et déterministes, empreintes conservées. |
| `samples.tsv` | `Family`, `Individual`, affectations de source | Colonnes et vocabulaire du schéma `samples_master`; aucun génotype déduit. |
| `variant.yaml` | `TargetVariant` | Assemblage, coordonnée `bp`, REF/ALT et confirmations obligatoires. |
| `genotypes.tsv` | `TargetGenotypeEvidence` | Une ligne par individu, génotype explicite, source et méthode. |
| `pipeline.yaml` | étude + politique exposée et bornée | `schema_version`, cible concordante, chemins internes à l'instantané, étapes autorisées. |
| `snapshot.manifest.json` | ensemble compilé | Version du compilateur, liste triée des fichiers, taille et SHA-256. |

Le compilateur ne copie pas les données dans le dépôt Git. Il matérialise un
espace de travail temporaire ou un préfixe de stockage propre au snapshot. Les
noms de fichiers internes sont générés par l'application et ne proviennent pas
directement d'une entrée navigateur.

## 5. Validation en deux niveaux

### Validation métier locale

Elle donne un retour rapide avant gel : champs requis, cardinalités, filiation,
unicité des codes, présence d'une source, preuve de génotype et autorisations.
Elle ne prétend pas certifier la conformité V2.

### Validation autoritative moteur

Le worker exécute la version épinglée de :

```text
effet-fondateur validate-config <pipeline.yaml>
effet-fondateur validate-samples --table <samples.tsv> --source-root <sources>
```

et les validateurs publics supplémentaires disponibles pour la version ciblée.
Le résultat structuré doit être conservé. Tant que la CLI ne fournit pas une
sortie machine stable pour une validation, l'adaptateur mappe prudemment le code
de sortie et conserve le diagnostic filtré ; il ne parse pas une phrase humaine
pour prendre une décision scientifique.

La validation des génotypes cibles et des contrats croisés devra utiliser une
commande publique du moteur ou un run synthétique de préparation. L'absence
d'une telle commande est un manque de contrat à résoudre avec le dépôt moteur,
pas une autorisation d'importer une fonction privée.

## 6. Demande d'exécution

La tâche interne contient uniquement :

- `analysis_run_id` ;
- `organization_id` opaque ;
- `study_snapshot_id` ;
- identifiant de compatibilité moteur ;
- identifiant de corrélation.

Le worker recharge les objets, revérifie l'autorisation technique, prend un
verrou/idempotency key, résout les références de stockage, recalcule les
empreintes et prépare un dossier de travail non privilégié. Il lance ensuite la
CLI avec une liste d'arguments, sans shell.

## 7. Retour du moteur

L'adaptateur importe, après validation d'intégrité :

- identifiant et état du run ;
- `config.resolved.yaml` et son empreinte ;
- `run_manifest.json` ;
- journal d'événements structuré ;
- pour chaque étape, `stage_outputs.json`, `audit.json` et empreintes ;
- artefacts déclarés et leur classe de sensibilité ;
- décisions manuelles en attente ;
- version et environnement moteur.

Une sortie présente mais non déclarée n'est pas publiée dans l'application. Une
sortie déclarée absente ou dont l'empreinte diffère met l'import en échec.

## 8. États et erreurs

L'état web ne réduit pas les états du moteur :

| Événement moteur/worker | État web | Règle |
|---|---|---|
| tâche acceptée, non démarrée | `QUEUED` | Pas de progression inventée. |
| processus lancé | `RUNNING` | Conserver tentative et horodatage. |
| décision bloquante | `WAITING_DECISION` | Créer/actualiser la `HumanDecision` exacte. |
| code non nul ou intégrité invalide | `FAILED` | Conserver code stable et diagnostic filtré. |
| manifest final valide | `SUCCEEDED` | Seulement après import et contrôle des artefacts requis. |
| étape non évaluée | état d'étape `NOT_EVALUATED` | Ne jamais traduire en réussite. |

Les stderr/stdout bruts sont des artefacts d'exploitation à accès restreint.
Les messages utilisateur emploient des codes stables, indiquent l'étape et
n'exposent ni chemin hôte, ni commande complète avec secret, ni contenu
génétique.

## 9. Reprise et décisions humaines

- Une reprise utilise la même configuration résolue et le même instantané.
- Un changement de paramètre scientifique crée un nouveau snapshot et un
  nouveau run.
- Une demande de reprise est idempotente et verrouillée ; deux workers ne
  reprennent pas simultanément le même run.
- Une décision web référence le type attendu, l'artefact et son SHA-256.
- Le worker compile la décision dans le format moteur prévu, puis démarre une
  nouvelle exécution conforme au contrat ; il ne modifie pas manuellement le
  manifest d'un run.

## 10. Progression du raccordement

1. **Validation de configuration** : adaptateur simulé puis CLI épinglée.
2. **Compilation et validation des entrées** : sorties déterministes et tests
   contractuels sans outil scientifique.
3. **Instantané immuable** : manifest, empreintes, approbation et stockage.
4. **Exécution simulée** : mêmes états et artefacts, aucune commande scientifique.
5. **Moteur réel** : worker scientifique isolé sur données synthétiques.
6. **Suivi et reprise** : import de manifest, décisions et verrouillage.
7. **Publication contrôlée** : permissions d'artefact, rapport et audit.

## 11. Tests contractuels

- Golden files synthétiques pour les quatre entrées V2 et le manifest web.
- Compilation répétée byte-à-byte identique.
- Rejet d'un chemin absolu, `..`, lien symbolique sortant et fichier modifié.
- Rejet d'une cible, d'un individu ou d'une source discordante.
- Test de compatibilité contre l'image moteur exacte, sans PLINK/KING dans la
  suite unitaire.
- Import d'un manifest valide, inconnu, incomplet et altéré.
- Mapping exhaustif des états, y compris `NOT_EVALUATED` et décision bloquante.
- Idempotence de démarrage/reprise et concurrence de deux workers.
- Test garantissant qu'aucune donnée individuelle n'entre dans les journaux ou
  messages de file.

## 12. Interdictions

- Importer `effet_fondateur.stages.*` ou une fonction privée depuis Django.
- Monter le clone de développement du moteur dans le conteneur web de production.
- Utiliser la copie locale non propre comme version d'exécution.
- Réécrire un schéma côté web pour accepter une entrée rejetée par le moteur.
- Considérer un rapport historique de `data/output/` comme une source.
- Relancer le pipeline V1 archivé.
