# Maestro - Frugal'IA 2025 Hackathon

Membres de l’équipe : Andrei, Caroline, Damien, Gabriel, Lionel, Romain, Sophie.

Durée du hackathon : du 15 au 16 novembre 2025.

## Slide-deck

[Slide-deck](assets/MAESTRO.pdf)

## Interface preview

![Interface](assets/interface.png)

## Installation

### Local Development

Run the Gradio app:

```bash
uv run gradio app/main.py
```

### Docker Deployment

The application can be deployed using Docker for easy hosting:

```bash
# Build and run with docker compose
docker compose up --build

# Or run in detached mode
docker compose up -d --build
```

Alternatively, using the Task runner:

```bash
# Run in foreground
task docker

# Run in detached mode
task dockerd
```

The application will be available at `http://localhost:7860`

To view logs:

```bash
docker compose logs -f maestro
```

To stop the service:

```bash
docker compose down
```

## Presentation

Maestro - Orchestrateur est un projet dont l'objectif est de proposer une interface de type orchestrateur ou routeur permettant à un utilisateur de répondre à son besoin avec la solution la plus adaptée et la plus optimisée

Sources:

- [.gitignore](.gitignore): [Python.gitignore](https://github.com/github/gitignore/blob/main/Python.gitignore)
- [uv](https://docs.astral.sh/uv/) setup: [uv-fastapi-example](https://github.com/astral-sh/uv-fastapi-example)

## Developer environment setup

```bash
set -a; source .env; set +a
```

Create virtual environment:

```bash
uv sync
```

Available commands:

```bash
task --list
```

See [Taskfile.yml](Taskfile.yml)
