import json
import logging
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.project import Project, Estimate, ChatSession, ChatMessage
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate, EstimateOut

logger = logging.getLogger(__name__)


class ProjectService:
    async def create_project(self, data: ProjectCreate) -> ProjectOut:
        async with async_session() as session:
            project = Project(
                project_name=data.project_name or data.project_idea[:50],
                project_idea=data.project_idea,
                currency=data.currency,
                status="Exploring",
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return ProjectOut(
                id=project.id,
                project_name=project.project_name,
                project_idea=project.project_idea,
                status=project.status,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )

    async def get_project(self, project_id: int) -> ProjectOut | None:
        async with async_session() as session:
            result = await session.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()
            if not project:
                return None
            return ProjectOut(
                id=project.id,
                project_name=project.project_name,
                project_idea=project.project_idea,
                status=project.status,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )

    async def list_projects(self) -> list[ProjectOut]:
        async with async_session() as session:
            result = await session.execute(select(Project).order_by(Project.updated_at.desc()))
            projects = result.scalars().all()
            return [
                ProjectOut(
                    id=p.id,
                    project_name=p.project_name,
                    project_idea=p.project_idea,
                    status=p.status,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
                for p in projects
            ]

    async def update_project(self, project_id: int, data: ProjectUpdate) -> ProjectOut | None:
        async with async_session() as session:
            project = await session.get(Project, project_id)
            if not project:
                return None
            if data.project_name is not None:
                project.project_name = data.project_name
            if data.status is not None:
                project.status = data.status
            project.updated_at = datetime.now()
            await session.commit()
            await session.refresh(project)
            return ProjectOut(
                id=project.id,
                project_name=project.project_name,
                project_idea=project.project_idea,
                status=project.status,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )

    async def delete_project(self, project_id: int) -> bool:
        async with async_session() as session:
            project = await session.get(Project, project_id)
            if not project:
                return False
            await session.delete(project)
            await session.commit()
            return True

    async def save_estimate(self, project_id: int, estimate_type: str, estimate_data: dict) -> EstimateOut:
        async with async_session() as session:
            estimate = Estimate(
                project_id=project_id,
                estimate_type=estimate_type,
                estimate_data=json.dumps(estimate_data),
            )
            session.add(estimate)
            await session.commit()
            await session.refresh(estimate)
            return EstimateOut(
                id=estimate.id,
                project_id=estimate.project_id,
                estimate_type=estimate.estimate_type,
                estimate_data=estimate.estimate_data,
                created_at=estimate.created_at,
            )

    async def get_estimates(self, project_id: int) -> list[EstimateOut]:
        async with async_session() as session:
            result = await session.execute(
                select(Estimate).where(Estimate.project_id == project_id).order_by(Estimate.created_at.desc())
            )
            estimates = result.scalars().all()
            return [
                EstimateOut(
                    id=e.id,
                    project_id=e.project_id,
                    estimate_type=e.estimate_type,
                    estimate_data=e.estimate_data,
                    created_at=e.created_at,
                )
                for e in estimates
            ]


project_service = ProjectService()
