from fastapi import HTTPException, status

from app.data.store import store
from app.services.base import CrudService


class ProjectService(CrudService):
    collection = "projects"

    def create(self, payload):
        data = payload.model_dump(mode="json")
        if data.get("phase") == "completed" and data.get("progress") != 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="项目标记为已完成时，进度必须达到100",
            )
        return store.add_item(self.collection, data)

    def update(self, item_id, payload):
        update_data = payload.model_dump(exclude_unset=True, mode="json")
        new_phase = update_data.get("phase")
        new_progress = update_data.get("progress")

        if new_phase == "completed" or (new_phase is None and new_progress is not None):
            current = store.find_item(self.collection, item_id)
            if current is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resource not found",
                )
            effective_progress = new_progress if new_progress is not None else current["progress"]
            effective_phase = new_phase if new_phase is not None else current["phase"]
            if effective_phase == "completed" and effective_progress != 100:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="项目标记为已完成时，进度必须达到100",
                )

        item = store.update_item(self.collection, item_id, update_data)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        return item


project_service = ProjectService()
