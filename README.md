# .Remade By Cyb3rtech

## 📄 Description

Bot lookdb remade by cyb3rtech
  discord : @antidatabreach 

## 📁 Configuration du Bot

### 1. Mettre le Token du Bot

Pour commencer, vous devez ajouter le token de votre bot dans le fichier `lookdb-remade.py`.

```python
# lookdb-remade.py
token = 'votre-token-ici'
```

### 2. Créer les Dossiers Requis

Assurez-vous de créer les dossiers nécessaires pour le bon fonctionnement du bot :

```bash
dump
database
```

### 3. Ajouter les IDs des Personnes à Blacklister

Si vous souhaitez blacklister certaines personnes de la recherche lookup, ajoutez leurs IDs dans le fichier `lookdb-remade.py`.

```python
# bls.txt
id 1
id 2
id 3
...
```

## 🚀 Utilisation

Pour démarrer le bot, exécutez simplement le fichier `lookdb-remade.py` :

```bash
python lookdb-remade.py
```

Le bot devrait maintenant être en ligne et opérationnel !

## 🛠️ Dépannage

### Problèmes Courants

- **Erreur de Token** : Assurez-vous que le token du bot est correct et qu'il est bien placé dans le fichier `lookdb-remade.py`.
- **Dossiers Manquants** : Vérifiez que les dossiers `dump` et `database` existent et ont les permissions nécessaires.
