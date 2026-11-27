# Profil des conventions web

## Référence

- Skill : `web-code-conventions`
- Révision appliquée : `44ac8e8e3f17e3c5f57ee88b805d0df89225e65d`
- Périmètre actuel : gabarits HTML et styles Django à partir du lot 2

## Choix du projet

- langue des pages : français (`fr`) ;
- titres : `Page — AlleleFounder` ;
- gabarits : `src/allelefounder/templates/` ;
- HTML sémantique, un seul `h1` par page, sans style ni script embarqué ;
- commentaires de section au format `<!-- ── NOM ── -->` ;
- CSS sous `src/allelefounder/static/allelefounder/css/` ;
- découpage : `tokens.css`, puis `base.css`, sans CSS embarqué ;
- approche responsive avec requêtes `max-width` ;
- aucun JavaScript applicatif tant qu'une interaction native suffit.

## Dérogations

- `HTML-VALIDATE-DJANGO-01` : `attribute-allowed-values` est désactivée, car le
  validateur ne reconnaît pas les valeurs Django telles que
  `for="{{ field.id_for_label }}"`. La présence et la correspondance des
  libellés restent contrôlées par les tests de rendu et la relecture.
- `HTML-VALIDATE-DJANGO-02` : `long-title` est désactivée, car le validateur
  compte les balises de bloc Django comme du texte. Le format et la longueur
  des titres rendus restent vérifiés en revue de page.

## Outillage

La chaîne Node est versionnée à partir du lot 2. La commande de contrôle est
`npm run lint:web`. Elle exécute Prettier, html-validate, Stylelint et les
contrôles complémentaires fournis par le skill.

Les gabarits Django ne passent pas dans Prettier : son parseur HTML peut couper
les balises `{% ... %}` et produire un template invalide. Ils sont contrôlés
par html-validate, les contrôles complémentaires, la compilation Django et une
relecture manuelle. Prettier reste obligatoire pour CSS et outillage JavaScript.

Le contrôle de code mort ignore `helptext` et `errorlist`, classes générées à
l'exécution par les formulaires Django et django-allauth.
