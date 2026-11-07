# Points des maisons de Poudlard

Application Django en français pour consulter et gérer les points de Gryffondor, Serpentard, Serdaigle et Poufsouffle. Les pages publiques demandent un code partagé ; l'administration Django utilise ses propres comptes.

## Développement local

Prérequis : Python 3.10 ou plus récent.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY='cle-locale-a-remplacer'
export ACCESS_CODE='code-local'
python manage.py migrate
python manage.py runserver
```

Ouvrir http://127.0.0.1:8000/ et saisir la valeur de `ACCESS_CODE`. Pour l'administration, créer un compte avec `python manage.py createsuperuser`, puis se connecter sur `/gestion-hp-admin/`.

## Modifier les actions

Le fichier [`config/actions.json`](./config/actions.json) est relu à chaque affichage et à chaque envoi d'action. Modifiez le JSON (le champ `points` accepte des entiers négatifs), puis enregistrez-le. En déploiement, après avoir récupéré sa modification par Git, un simple Reload de l'application suffit ; il n'est pas nécessaire de redémarrer les processus séparément. Un fichier absent ou invalide affiche un message explicite sur la page de la maison.

## Images et fond

Les logos actuels sont dans `static/img/`. L'application utilise les fichiers suivants :

- Gryffondor : `gryffindor.webp`
- Serpentard : `slytherin.jpeg`
- Serdaigle : `ravenclaw.webp`
- Poufsouffle : `hufflepuff.webp`

Les images peuvent être au format JPEG, PNG ou WebP : le nom de fichier stocké pour chaque maison doit correspondre au nom exact du fichier dans `static/img/`. Il est également possible de modifier ce nom dans l'administration Django, dans la fiche de la maison. Le dossier est conservé dans Git par `.gitkeep`. Le fond parchemin est fait en CSS (dégradés beige, bordure et ombre) ; aucune image de fond n'est requise. Si vous fournissez un `parchemin.jpg`, le CSS pourra être adapté pour l'utiliser.

## Déploiement gratuit sur PythonAnywhere

Les étapes ci-dessous supposent le nom de compte PythonAnywhere `monpseudo` et le dépôt `https://github.com/VOTRE_COMPTE/VOTRE_DEPOT.git`. Remplacez ces valeurs par les vôtres partout. Vérifiez que la version Python choisie est disponible sur votre compte ; la procédure ci-dessous utilise Python 3.10, également compatible avec les dépendances du projet.

1. Dans une console Bash PythonAnywhere, clonez le dépôt :

   ```bash
   cd ~
   git clone https://github.com/VOTRE_COMPTE/VOTRE_DEPOT.git poudlard
   cd ~/poudlard
   ```

2. Créez l'environnement et installez les dépendances :

   ```bash
   mkvirtualenv --python=python3.10 monenv
   pip install -r ~/poudlard/requirements.txt
   ```

3. Dans l'onglet **Web**, choisissez **Add a new web app**, confirmez le domaine gratuit `monpseudo.pythonanywhere.com`, puis **Manual configuration** et la même version Python que celle de l'environnement (3.10).

4. Dans l'onglet **Web**, renseignez le chemin du code `/home/monpseudo/poudlard` et le chemin du virtualenv `/home/monpseudo/.virtualenvs/monenv`. Ouvrez le fichier WSGI depuis le lien proposé dans l'onglet et remplacez son contenu par le bloc suivant. Remplacez la clé secrète et le code d'accès par des valeurs longues et uniques ; ne les ajoutez jamais au dépôt Git.

   ```python
   import os
   import sys

   path = "/home/monpseudo/poudlard"
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ["SECRET_KEY"] = "REMPLACER-PAR-UNE-CLE-SECRETE-ALEATOIRE"
   os.environ["DEBUG"] = "False"
   os.environ["ACCESS_CODE"] = "REMPLACER-PAR-UN-CODE-PARTAGE-UNIQUE"
   os.environ["ALLOWED_HOSTS"] = "monpseudo.pythonanywhere.com"
   os.environ["ADMIN_URL"] = "gestion-hp-admin/"
   os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poudlard.settings")

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

5. Dans une console Bash PythonAnywhere :

   ```bash
   workon monenv
   cd ~/poudlard
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic
   ```

6. Dans l'onglet **Web** > **Static files**, ajoutez :
   - URL : `/static/`
   - Directory : `/home/monpseudo/poudlard/staticfiles`

7. Cliquez sur **Reload** dans l'onglet **Web**.

8. Pour publier une mise à jour :

   ```bash
   cd ~/poudlard
   git pull
   workon monenv
   python manage.py migrate
   python manage.py collectstatic
   ```

   Les commandes `migrate` et `collectstatic` ne sont nécessaires que si la mise à jour concerne respectivement les modèles/migrations ou les fichiers statiques. Cliquez ensuite sur **Reload**. Une modification de `config/actions.json` récupérée par `git pull` ne demande qu'un **Reload**.

`db.sqlite3` est ignorée par Git et n'est pas versionnée. La base et les points restent donc sur PythonAnywhere et ne sont pas écrasés par un `git pull`.

### Vérifications après déploiement

Depuis un terminal, remplacez le domaine par le vôtre :

```bash
curl -i https://monpseudo.pythonanywhere.com/robots.txt
curl -sSI https://monpseudo.pythonanywhere.com/ | grep -i '^X-Robots-Tag:'
```

La première commande doit renvoyer `User-agent: *` puis `Disallow: /`. La seconde doit afficher `X-Robots-Tag: noindex, nofollow, noarchive, nosnippet`. La page d'accueil peut rediriger vers la saisie du code si la session n'est pas encore ouverte.

## Checklist finale

- [ ] Déploiement PythonAnywhere terminé et application rechargée.
- [ ] `SECRET_KEY`, `DEBUG=False`, `ACCESS_CODE` et `ALLOWED_HOSTS` configurés dans le fichier WSGI.
- [ ] Superutilisateur créé et administration accessible sur `/gestion-hp-admin/`.
- [ ] Code partagé demandé sur les pages publiques ; points ajoutés et retraits inscrits dans l'historique.
- [ ] `robots.txt`, l'en-tête `X-Robots-Tag` et la balise robots HTML vérifiés.
- [ ] Les quatre images fournies déposées sous les noms attendus dans `static/img/`.
