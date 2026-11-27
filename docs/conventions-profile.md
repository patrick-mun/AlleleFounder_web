# Profil des conventions web

## Référence

- Skill : `web-code-conventions`
- Révision appliquée : `44ac8e8e3f17e3c5f57ee88b805d0df89225e65d`
- Périmètre actuel : gabarits HTML Django du lot 1

## Choix du projet

- langue des pages : français (`fr`) ;
- titres : `Page — AlleleFounder` ;
- gabarits : `src/allelefounder/templates/` ;
- HTML sémantique, un seul `h1` par page, sans style ni script embarqué ;
- commentaires de section au format `<!-- ── NOM ── -->` ;
- aucun CSS ou JavaScript applicatif n’est introduit dans le lot 1.

## Outillage

Le contrôle initial a trouvé Node.js, mais aucun `package.json`, Prettier ou
html-validate dans le dépôt. Le lot 1 ne comportant que des gabarits minimaux,
ces règles sont vérifiées manuellement. La chaîne Node sera ajoutée avec les
premiers actifs CSS/JavaScript ; aucun contrôle automatisé HTML n’est revendiqué
avant cette étape.
