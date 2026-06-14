from fastapi import HTTPException, status

from app.data.store import store
from app.services.base import CrudService


class ProcurementService(CrudService):
    collection = "procurements"

    def _validate_project(self, project_id: int):
        if store.find_item("projects", project_id) is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"关联的项目不存在（project_id={project_id}）",
            )

    def create(self, payload):
        data = payload.model_dump(mode="json")
        self._validate_project(data["project_id"])
        return store.add_item(self.collection, data)

    def update(self, item_id, payload):
        update_data = payload.model_dump(exclude_unset=True, mode="json")
        if "project_id" in update_data:
            self._validate_project(update_data["project_id"])
        item = store.update_item(self.collection, item_id, update_data)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        return item


procurement_service = ProcurementService()
