from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from sfs_console.application import (
    BuildProductionRequestMarkdown,
    CreateCharacterTemplate,
    IssueDeliveryToken,
    ListWorkspaceSnapshot,
    RevokeDeliveryToken,
    ResolveDeliveryPackage,
    SaveProductionRequest,
    SendProductionRequestToPaperclip,
    ValidateDeliveryReadiness,
)
from sfs_console.config import Settings
from sfs_console.infrastructure import (
    FileSystemCharacterWriter,
    FileSystemWorkspaceScanner,
    InMemorySfsStore,
    PaperclipIssueHttpClient,
    PostgresSfsStore,
)
from sfs_console.presentation.schemas import (
    AuditLogResponse,
    CharacterCreateRequest,
    CharacterResponse,
    CharacterTemplateResponse,
    DeliveryTokenCreateRequest,
    DeliveryPackageResponse,
    DeliveryTokenResponse,
    DeliveryReadinessResponse,
    EpisodeResponse,
    FormatProfileResponse,
    HealthResponse,
    OpsComponentResponse,
    OpsHealthResponse,
    ProductionRequestPreviewRequest,
    ProductionRequestPreviewResponse,
    ProductionRequestResponse,
    WorkspaceSnapshotResponse,
)


def create_app(
    settings: Settings | None = None,
    store: InMemorySfsStore | PostgresSfsStore | None = None,
) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    scanner = FileSystemWorkspaceScanner(resolved_settings.workspace_root)
    persistence = store or _build_store(resolved_settings)
    persistence.initialize()
    character_writer = FileSystemCharacterWriter(resolved_settings.workspace_root)
    paperclip = _build_paperclip_client(resolved_settings)

    app = FastAPI(title="SFS Console API", version="0.1.0")

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=resolved_settings.service_name,
            persistence="postgres" if resolved_settings.database_url else "memory",
        )

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

    @app.get("/requests/production", response_model=list[ProductionRequestResponse])
    def production_requests() -> list[ProductionRequestResponse]:
        return [
            ProductionRequestResponse.from_domain(record)
            for record in persistence.list_production_requests()
        ]

    @app.post("/requests/production", response_model=ProductionRequestResponse)
    def create_production_request(
        request: ProductionRequestPreviewRequest,
    ) -> ProductionRequestResponse:
        try:
            record = SaveProductionRequest(persistence, persistence).execute(request.to_draft())
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return ProductionRequestResponse.from_domain(record)

    @app.post(
        "/requests/production/{request_id}/paperclip",
        response_model=ProductionRequestResponse,
    )
    def send_production_request_to_paperclip(request_id: str) -> ProductionRequestResponse:
        if not paperclip:
            raise HTTPException(status_code=503, detail="Paperclip integration is not configured")
        try:
            record = SendProductionRequestToPaperclip(persistence, persistence, paperclip).execute(
                request_id
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return ProductionRequestResponse.from_domain(record)

    @app.post("/characters", response_model=CharacterTemplateResponse)
    def create_character(request: CharacterCreateRequest) -> CharacterTemplateResponse:
        try:
            result = CreateCharacterTemplate(character_writer, persistence).execute(request.to_draft())
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return CharacterTemplateResponse.from_domain(result)

    @app.get("/episodes/{episode_slug}/delivery-readiness", response_model=DeliveryReadinessResponse)
    def delivery_readiness(episode_slug: str) -> DeliveryReadinessResponse:
        snapshot = ListWorkspaceSnapshot(scanner).execute()
        episode = next((item for item in snapshot.episodes if item.slug == episode_slug), None)
        if not episode:
            raise HTTPException(status_code=404, detail="episode not found")
        character = next(
            (item for item in snapshot.characters if item.slug == episode.character_slug),
            None,
        )
        readiness = ValidateDeliveryReadiness().execute(
            episode,
            character_has_rights=bool(character and character.has_rights),
        )
        return DeliveryReadinessResponse.from_domain(readiness)

    @app.get("/deliveries/tokens", response_model=list[DeliveryTokenResponse])
    def delivery_tokens() -> list[DeliveryTokenResponse]:
        return [
            DeliveryTokenResponse.from_domain(record)
            for record in persistence.list_delivery_tokens()
        ]

    @app.post("/deliveries/tokens", response_model=DeliveryTokenResponse)
    def create_delivery_token(request: DeliveryTokenCreateRequest) -> DeliveryTokenResponse:
        try:
            result = IssueDeliveryToken(scanner, persistence, persistence).execute(
                episode_slug=request.episode_slug,
                expires_in_hours=request.expires_in_hours,
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return DeliveryTokenResponse.from_domain(result.record, token=result.token)

    @app.post("/deliveries/tokens/{token_id}/revoke", response_model=DeliveryTokenResponse)
    def revoke_delivery_token(token_id: str) -> DeliveryTokenResponse:
        try:
            record = RevokeDeliveryToken(persistence, persistence).execute(token_id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return DeliveryTokenResponse.from_domain(record)

    @app.get("/public/deliveries/{token}", response_model=DeliveryPackageResponse)
    def public_delivery_package(token: str) -> DeliveryPackageResponse:
        try:
            package = ResolveDeliveryPackage(scanner, persistence).execute(token)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return DeliveryPackageResponse.from_domain(package, token=token)

    @app.get("/public/deliveries/{token}/files/{asset_key}")
    def public_delivery_asset(token: str, asset_key: str) -> FileResponse:
        try:
            asset = ResolveDeliveryPackage(scanner, persistence).get_asset(token, asset_key)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return FileResponse(
            path=asset.path,
            media_type=asset.content_type,
            filename=asset.path.name,
        )

    @app.get("/audit-logs", response_model=list[AuditLogResponse])
    def audit_logs() -> list[AuditLogResponse]:
        return [AuditLogResponse.from_domain(entry) for entry in persistence.list_audit_logs()]

    @app.get("/ops/health", response_model=OpsHealthResponse)
    def ops_health() -> OpsHealthResponse:
        components = [
            OpsComponentResponse(key="workspace", status="ok", detail=str(resolved_settings.workspace_root)),
            OpsComponentResponse(
                key="database",
                status="ok" if resolved_settings.database_url else "degraded",
                detail="postgres" if resolved_settings.database_url else "memory fallback",
            ),
            OpsComponentResponse(
                key="paperclip",
                status="ok" if paperclip else "degraded",
                detail="configured" if paperclip else "not configured",
            ),
            OpsComponentResponse(
                key="scanner",
                status="ok",
                detail=f"{len(scanner.scan().episodes)} episodes indexed",
            ),
        ]
        status = "ok" if all(item.status == "ok" for item in components[:2]) else "degraded"
        return OpsHealthResponse(status=status, components=components)

    return app


def _build_store(settings: Settings) -> InMemorySfsStore | PostgresSfsStore:
    if settings.database_url:
        return PostgresSfsStore(settings.database_url)
    return InMemorySfsStore()


def _build_paperclip_client(settings: Settings) -> PaperclipIssueHttpClient | None:
    if not (
        settings.paperclip_base_url
        and settings.paperclip_api_token
        and settings.paperclip_company_id
    ):
        return None
    return PaperclipIssueHttpClient(
        base_url=settings.paperclip_base_url,
        api_token=settings.paperclip_api_token,
        company_id=settings.paperclip_company_id,
        project_id=settings.paperclip_project_id,
    )


app = create_app()
