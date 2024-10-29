# Wolof Bridge

**Wolof-Bridge** est un projet conçu pour interagir avec un modèle de données en traduisant des questions et des réponses en langue Wolof. Ce projet utilise l'api de traduction google pour traduire une question en Wolof vers la langue comprise par le modèle de données, interroger le modèle, puis traduire la réponse finale en Wolof.

## Objectifs du projet

- **Traduction bidirectionnelle** entre le Wolof et une langue supportée par le modèle.
- **Interaction fluide** avec le modèle de données pour obtenir des réponses adaptées en Wolof.
- **Automatisation** de la traduction et de l'interrogation en utilisant CrewAI.

## Prérequis

1. **Python 3.8+**
2. **Clé d'API de traduction google**
3. **Clé d'API groq**

## Installation

Clonez le dépôt et installez les dépendances :

```bash
git clone https://github.com/dofbi/Wolof-Bridge.git
cd Wolof-Bridge
pip install -r requirements.txt
```

## Utilisation

Pour démarrer le projet, exécutez simplement `main.py` avec une question en Wolof :

```bash
python main.py
```

