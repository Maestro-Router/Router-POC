from duckduckgo_search import DDGS

from app.tasks.base import Task


def _resolver(query: str) -> str:
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=5)

        if not results:
            return "Pas de résultats trouvés pour la requête."

        # Format results with title and URL
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Pas de titre')
            url = result.get('href', '')
            snippet = result.get('body', '')

            formatted_results.append(
                f"{i}. {title}\n"
                f"   URL: {url}\n"
                f"   {snippet[:150]}{'...' if len(snippet) > 150 else ''}"
            )

        return "Voici quelques liens pertinents :\n\n" + "\n\n".join(formatted_results)

    except Exception as e:
        return f"Erreur lors de la recherche : {str(e)}"


task = Task(
    name="Recherche Web",
    description=(
        "Rechercher sur le web et renvoyer un ensemble concis de résultats pertinents avec liens sources. "
        "Conçu pour extraire et présenter des extraits factuels, des références fiables et des URL soutenant les requêtes utilisateur. "
        "Entrée : question ou demande d'information de l'utilisateur ; "
        "Sortie : liste classée d'extraits courts avec URL source. "
        "Cas particuliers : requêtes ambiguës, demandes de données personnelles ou contenus payants. "
        "Le résolveur doit privilégier les domaines de qualité et inclure le contexte des extraits lorsque possible. "
        "Exemple : Donne-moi la biographie de Victor Hugo"
    ),
    resolver=_resolver,
)
