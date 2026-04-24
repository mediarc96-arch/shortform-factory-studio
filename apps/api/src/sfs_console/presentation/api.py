from __future__ import annotations

from fastapi import FastAPI, HTTPException

from sfs_console.application import (
    BuildProductionRequestMarkdown,
    ListWorkspaceSnapshot,
    ValidateDeliveryReadiness,
)
from sfs_console.config import Settings
from sfs_console.infrastructure import FileSystemWorkspaceScanner
from sfs_console.presentation.schemas import (
    CharacterResponse,
    DeliveryReadinessResponse,
    EpisodeResponse,
    FormatProfileResponse,
    HealthResponse,
    ProductionRequestPreviewRequest,
    ProductionRequestPreviewResponse,
    WorkspaceSnapshotResponse,
)


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    scanner = FileSystemWorkspaceScanner(resolved_settings.workspace_root)

    app = FastAPI(title="SFS Console API", version="0.1.0")

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service=resolved_settings.service_name)

    @app.get("/workspace", response_model=WorkspaceSnapshotResponse)
    def workspace() -> WorkspaceSnapshotResponse:
        snapshot = ListWorkspaceSnapshot(scanner).execute()
        return WorkspaceSnapshotResponse.from_domain(snapshot)

    @app.get("/episodes", response_model=list[EpisodeResponse])
    def episodes() -> list[EpisodeResponse]:
        snapshot = ListWorkspaceSnapshot(scanner).execute()
        return [EpisodeResponse.from_domain(episode) for episode in snapshot.episodes]

    @app.get("/characters", response_model=list[CharacterResponse])
    def characters() -> list[CharacterResponse]:
        snapshot = ListWorkspaceSnapshot(scanner).execute()
        return [CharacterResponse.from_domain(character) for character in snapshot.characters]

    @app.get("/formats", response_model=list[FormatProfileResponse])
    def formats() -> list[FormatProfileResponse]:
        snapshot = ListWorkspaceSnapshot(scanner).execute()
        return [FormatProfileResponse.from_domain(profile) for profile in snapshot.formats]

    @app.post("/requests/production/preview", response_model=ProductionRequestPreviewResponse)
    def production_request_preview(
        request: ProductionRequestPreviewRequest,
    ) -> ProductionRequestPreviewResponse:
        try:
            markdown = BuildProductionRequestMarkdown().execute(request.to_draft())
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

        return ProductionRequestPreviewResponse(
            request_type=request.request_type,
            episode_slug=request.episode_slug,
            markdown=markdown,
        )

    @app.get("/episodes/{episode_slug}/delivery-readiness", response_model=DeliveryReadinessResponse)
    def delivery_readiness(episode_slug: str) -> DeliveryReadinessResponse:
        snapshot = ListWorkspaceSnapshot(scanner).execute()
        episode = next(item for item in snapshot.episodes if item.slug == episode_slug)
        character = next(
            (item for item in snapshot.characters if item.slug == episode.character_slug),
            None,
        )
        readiness = ValidateDeliveryReadiness().execute(
            episode,
            character_has_rights=bool(character and character.has_rights),
        )
        return DeliveryReadinessResponse.from_domain(readiness)

    return app


app = create_app()
