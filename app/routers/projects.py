from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import optional_api_key
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate, EstimateOut
from app.services.project_service import project_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    _api_key: str = Depends(optional_api_key),
) -> ProjectOut:
    """Save a new project with its idea and currency."""
    try:
        return await project_service.create_project(payload)
    except Exception as exc:
        logger.error("Create project error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create project.") from exc


@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(
    _api_key: str = Depends(optional_api_key),
) -> list[ProjectOut]:
    """List all saved projects."""
    try:
        return await project_service.list_projects()
    except Exception as exc:
        logger.error("List projects error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list projects.") from exc


@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: int,
    _api_key: str = Depends(optional_api_key),
) -> ProjectOut:
    """Get a specific project by ID."""
    result = await project_service.get_project(project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.patch("/projects/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    _api_key: str = Depends(optional_api_key),
) -> ProjectOut:
    """Update a project's name or status."""
    result = await project_service.update_project(project_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    _api_key: str = Depends(optional_api_key),
):
    """Delete a project and all its estimates."""
    deleted = await project_service.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found.")


@router.get("/projects/{project_id}/estimates", response_model=list[EstimateOut])
async def get_project_estimates(
    project_id: int,
    _api_key: str = Depends(optional_api_key),
) -> list[EstimateOut]:
    """Get all saved estimates for a project."""
    return await project_service.get_estimates(project_id)


@router.post("/projects/{project_id}/estimates", response_model=EstimateOut, status_code=status.HTTP_201_CREATED)
async def save_project_estimate(
    project_id: int,
    estimate_type: str,
    estimate_data: dict,
    _api_key: str = Depends(optional_api_key),
) -> EstimateOut:
    """Save an estimate result to a project."""
    try:
        return await project_service.save_estimate(project_id, estimate_type, estimate_data)
    except Exception as exc:
        logger.error("Save estimate error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save estimate.") from exc
