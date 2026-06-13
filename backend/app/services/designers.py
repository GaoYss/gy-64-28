from app.data.store import store


class DesignerService:
    def get_workload(self) -> dict:
        return store.designer_workload()


designer_service = DesignerService()
