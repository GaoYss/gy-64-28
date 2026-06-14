from fastapi import HTTPException, status

from app.data.store import store
from app.services.base import CrudService

STATUS_ORDER = ["new", "contacted", "measured", "quoted", "signed"]
ALLOWED_TRANSITIONS = {
    "new": ["contacted", "lost"],
    "contacted": ["measured", "lost"],
    "measured": ["quoted", "lost"],
    "quoted": ["signed", "lost"],
    "signed": ["lost"],
    "lost": [],
}


class CustomerService(CrudService):
    collection = "customers"

    def update(self, item_id, payload):
        update_data = payload.model_dump(exclude_unset=True, mode="json")
        new_status = update_data.get("status")

        if new_status is not None:
            current = store.find_item(self.collection, item_id)
            if current is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resource not found",
                )
            current_status = current["status"]
            allowed = ALLOWED_TRANSITIONS.get(current_status, [])
            if new_status not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"当前状态不允许该操作，客户当前状态为「{current_status}」，不可直接变更为「{new_status}」",
                )

        item = store.update_item(self.collection, item_id, update_data)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        return item


customer_service = CustomerService()
