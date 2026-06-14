from copy import deepcopy
from datetime import date, datetime, timedelta
from itertools import count
from typing import Any


class InMemoryStore:
    def __init__(self) -> None:
        today = date.today()
        self._counters = {
            "customers": count(4),
            "appointments": count(4),
            "projects": count(4),
            "procurements": count(4),
            "inspections": count(4),
        }
        self.customers: list[dict[str, Any]] = [
            {
                "id": 1,
                "name": "Chen Wei",
                "phone": "13800010001",
                "community": "Riverside Garden",
                "house_type": "3 bed 2 bath",
                "source": "Referral",
                "budget": 280000,
                "status": "contacted",
                "reported_at": str(today - timedelta(days=16)),
                "owner": "Lina",
                "notes": "Prefers modern minimalist style.",
            },
            {
                "id": 2,
                "name": "Wang Min",
                "phone": "13800010002",
                "community": "Lakeview Mansion",
                "house_type": "Duplex",
                "source": "Online ad",
                "budget": 520000,
                "status": "measured",
                "reported_at": str(today - timedelta(days=9)),
                "owner": "Kai",
                "notes": "Needs full-house smart lighting quote.",
            },
            {
                "id": 3,
                "name": "Liu Fang",
                "phone": "13800010003",
                "community": "North Star Residence",
                "house_type": "2 bed 1 bath",
                "source": "Walk-in",
                "budget": 180000,
                "status": "signed",
                "reported_at": str(today - timedelta(days=4)),
                "owner": "Mia",
                "notes": "Contract signed, construction starts soon.",
            },
        ]
        self.appointments: list[dict[str, Any]] = [
            {
                "id": 1,
                "customer_id": 1,
                "customer_name": "Chen Wei",
                "address": "Riverside Garden B2-1201",
                "scheduled_at": f"{today + timedelta(days=1)}T10:00:00",
                "designer": "Qiao",
                "surveyor": "Hao",
                "status": "scheduled",
                "requirements": "Check load-bearing walls and balcony drainage.",
            },
            {
                "id": 2,
                "customer_id": 2,
                "customer_name": "Wang Min",
                "address": "Lakeview Mansion 8-302",
                "scheduled_at": f"{today + timedelta(days=2)}T14:30:00",
                "designer": "Yun",
                "surveyor": "Hao",
                "status": "scheduled",
                "requirements": "Bring laser measure and smart home checklist.",
            },
            {
                "id": 3,
                "customer_id": 3,
                "customer_name": "Liu Fang",
                "address": "North Star Residence 6-808",
                "scheduled_at": f"{today - timedelta(days=1)}T09:30:00",
                "designer": "Qiao",
                "surveyor": "Jun",
                "status": "completed",
                "requirements": "Dimensions confirmed.",
            },
        ]
        self.projects: list[dict[str, Any]] = [
            {
                "id": 1,
                "customer_name": "Liu Fang",
                "project_name": "North Star Residence Renovation",
                "manager": "Zhou",
                "phase": "demolition",
                "progress": 18,
                "start_date": str(today - timedelta(days=3)),
                "expected_finish": str(today + timedelta(days=57)),
                "risk_level": "low",
                "latest_update": "Demolition area protected, waste removal booked.",
            },
            {
                "id": 2,
                "customer_name": "Sun Jie",
                "project_name": "Central Park Apartment",
                "manager": "Tang",
                "phase": "waterproofing",
                "progress": 46,
                "start_date": str(today - timedelta(days=24)),
                "expected_finish": str(today + timedelta(days=36)),
                "risk_level": "medium",
                "latest_update": "Bathroom waterproofing needs second inspection.",
            },
            {
                "id": 3,
                "customer_name": "Zhao Lei",
                "project_name": "Harbor Loft",
                "manager": "Zhou",
                "phase": "finishing",
                "progress": 82,
                "start_date": str(today - timedelta(days=48)),
                "expected_finish": str(today + timedelta(days=12)),
                "risk_level": "low",
                "latest_update": "Cabinet installation completed.",
            },
        ]
        self.procurements: list[dict[str, Any]] = [
            {
                "id": 1,
                "project_id": 1,
                "project_name": "North Star Residence Renovation",
                "material": "Cement board",
                "supplier": "Jintai Building Materials",
                "quantity": 80,
                "unit": "sheets",
                "budget": 9600,
                "status": "ordered",
                "required_date": str(today + timedelta(days=5)),
            },
            {
                "id": 2,
                "project_id": 2,
                "project_name": "Central Park Apartment",
                "material": "Waterproof coating",
                "supplier": "Green Shield",
                "quantity": 24,
                "unit": "buckets",
                "budget": 7200,
                "status": "delivered",
                "required_date": str(today - timedelta(days=2)),
            },
            {
                "id": 3,
                "project_id": 3,
                "project_name": "Harbor Loft",
                "material": "Oak flooring",
                "supplier": "Nature Wood",
                "quantity": 110,
                "unit": "sqm",
                "budget": 38500,
                "status": "pending",
                "required_date": str(today + timedelta(days=8)),
            },
        ]
        self.inspections: list[dict[str, Any]] = [
            {
                "id": 1,
                "project_id": 1,
                "project_name": "North Star Residence Renovation",
                "inspection_type": "Site protection",
                "scheduled_date": str(today),
                "inspector": "An",
                "result": "passed",
                "issues": "Protection film installed correctly.",
            },
            {
                "id": 2,
                "project_id": 2,
                "project_name": "Central Park Apartment",
                "inspection_type": "Waterproofing",
                "scheduled_date": str(today + timedelta(days=1)),
                "inspector": "An",
                "result": "pending",
                "issues": "Awaiting 48-hour closed-water test.",
            },
            {
                "id": 3,
                "project_id": 3,
                "project_name": "Harbor Loft",
                "inspection_type": "Woodwork",
                "scheduled_date": str(today - timedelta(days=2)),
                "inspector": "Mo",
                "result": "整改",
                "issues": "One cabinet door gap exceeds tolerance.",
            },
        ]

    def list_items(self, collection: str) -> list[dict[str, Any]]:
        return deepcopy(getattr(self, collection))

    def find_item(self, collection: str, item_id: int) -> dict[str, Any] | None:
        for item in getattr(self, collection):
            if item["id"] == item_id:
                return deepcopy(item)
        return None

    def add_item(self, collection: str, payload: dict[str, Any]) -> dict[str, Any]:
        item = {"id": next(self._counters[collection]), **payload}
        getattr(self, collection).append(item)
        return deepcopy(item)

    def update_item(self, collection: str, item_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        items = getattr(self, collection)
        for index, item in enumerate(items):
            if item["id"] == item_id:
                updated = {**item, **payload, "id": item_id}
                items[index] = updated
                return deepcopy(updated)
        return None

    def designer_workload(self) -> dict[str, Any]:
        status_order = ["new", "contacted", "measured", "quoted", "signed", "lost"]

        designers: set[str] = set()
        for customer in self.customers:
            if customer.get("owner"):
                designers.add(customer["owner"])

        def status_index(status: str) -> int:
            try:
                return status_order.index(status)
            except ValueError:
                return -1

        workload = []
        for designer in sorted(designers):
            designer_customers = [
                c for c in self.customers
                if c.get("owner") == designer
            ]

            measured_customers = [
                c for c in designer_customers
                if status_index(c.get("status", "")) >= status_order.index("measured")
            ]
            quoted_customers = [
                c for c in designer_customers
                if status_index(c.get("status", "")) >= status_order.index("quoted")
            ]
            signed_customers = [
                c for c in designer_customers
                if c.get("status") == "signed"
            ]

            measured_count = len(measured_customers)
            quoted_count = len(quoted_customers)
            signed_count = len(signed_customers)

            total_budget = sum(c["budget"] for c in signed_customers)
            avg_budget = total_budget / signed_count if signed_count > 0 else 0

            measurement_to_quote_rate = (
                round((quoted_count / measured_count) * 100, 1)
                if measured_count > 0 else 0.0
            )
            quote_to_sign_rate = (
                round((signed_count / quoted_count) * 100, 1)
                if quoted_count > 0 else 0.0
            )
            measurement_to_sign_rate = (
                round((signed_count / measured_count) * 100, 1)
                if measured_count > 0 else 0.0
            )

            def customer_summary(c: dict) -> dict:
                return {
                    "id": c["id"],
                    "name": c["name"],
                    "community": c.get("community", ""),
                    "budget": c.get("budget", 0),
                    "status": c.get("status", ""),
                }

            workload.append({
                "designer": designer,
                "measured": measured_count,
                "quoted": quoted_count,
                "signed": signed_count,
                "signed_budget": total_budget,
                "avg_budget": round(avg_budget, 2),
                "measurement_to_quote_rate": measurement_to_quote_rate,
                "quote_to_sign_rate": quote_to_sign_rate,
                "measurement_to_sign_rate": measurement_to_sign_rate,
                "measured_customers": [customer_summary(c) for c in measured_customers],
                "quoted_customers": [customer_summary(c) for c in quoted_customers],
                "signed_customers": [customer_summary(c) for c in signed_customers],
            })

        total_measured = sum(item["measured"] for item in workload)
        total_quoted = sum(item["quoted"] for item in workload)
        total_signed = sum(item["signed"] for item in workload)
        total_signed_budget = sum(item["signed_budget"] for item in workload)

        overall_measurement_to_quote_rate = (
            round((total_quoted / total_measured) * 100, 1)
            if total_measured > 0 else 0.0
        )
        overall_quote_to_sign_rate = (
            round((total_signed / total_quoted) * 100, 1)
            if total_quoted > 0 else 0.0
        )
        overall_measurement_to_sign_rate = (
            round((total_signed / total_measured) * 100, 1)
            if total_measured > 0 else 0.0
        )

        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "workload": workload,
            "summary": {
                "total_designers": len(designers),
                "total_measured": total_measured,
                "total_quoted": total_quoted,
                "total_signed": total_signed,
                "total_signed_budget": total_signed_budget,
                "overall_measurement_to_quote_rate": overall_measurement_to_quote_rate,
                "overall_quote_to_sign_rate": overall_quote_to_sign_rate,
                "overall_measurement_to_sign_rate": overall_measurement_to_sign_rate,
            },
        }

    def summary(self) -> dict[str, Any]:
        active_projects = [project for project in self.projects if project["progress"] < 100]
        procurement_budget = sum(item["budget"] for item in self.procurements)
        pending_inspections = sum(1 for item in self.inspections if item["result"] == "pending")
        avg_progress = round(sum(project["progress"] for project in self.projects) / len(self.projects))

        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "metrics": [
                {"label": "Customer reports", "value": len(self.customers), "trend": "+3 this month"},
                {"label": "Measure bookings", "value": len(self.appointments), "trend": "2 upcoming"},
                {"label": "Active projects", "value": len(active_projects), "trend": f"{avg_progress}% avg progress"},
                {"label": "Pending inspections", "value": pending_inspections, "trend": "Quality follow-up"},
            ],
            "procurement_budget": procurement_budget,
            "phase_distribution": [
                {"phase": phase, "count": sum(1 for project in self.projects if project["phase"] == phase)}
                for phase in sorted({project["phase"] for project in self.projects})
            ],
            "recent_updates": [
                {
                    "project_name": project["project_name"],
                    "phase": project["phase"],
                    "progress": project["progress"],
                    "latest_update": project["latest_update"],
                }
                for project in sorted(self.projects, key=lambda item: item["progress"], reverse=True)
            ],
        }


store = InMemoryStore()
