from datetime import date, datetime, timedelta

import pytest


class TestCustomerToMeasurement:

    def test_customer_status_transition_to_measured(self, client):
        customer_data = {
            "name": "Zhang San",
            "phone": "13900000001",
            "community": "Green Valley",
            "house_type": "3 bed 2 bath",
            "source": "Online ad",
            "budget": 300000,
            "status": "new",
            "reported_at": str(date.today() - timedelta(days=5)),
            "owner": "Lina",
            "notes": "Interested in modern style"
        }
        create_resp = client.post("/api/customers", json=customer_data)
        assert create_resp.status_code == 201
        customer_id = create_resp.json()["id"]

        client.patch(f"/api/customers/{customer_id}", json={"status": "contacted"})

        update_resp = client.patch(
            f"/api/customers/{customer_id}",
            json={"status": "measured"}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "measured"

        list_resp = client.get("/api/customers")
        assert list_resp.status_code == 200
        customers = list_resp.json()
        updated = next(c for c in customers if c["id"] == customer_id)
        assert updated["status"] == "measured"

    def test_create_measurement_appointment_for_customer(self, client):
        customer_data = {
            "name": "Li Si",
            "phone": "13900000002",
            "community": "Sunshine City",
            "house_type": "2 bed 1 bath",
            "source": "Referral",
            "budget": 200000,
            "status": "new",
            "reported_at": str(date.today() - timedelta(days=3)),
            "owner": "Kai",
            "notes": ""
        }
        customer_resp = client.post("/api/customers", json=customer_data)
        customer = customer_resp.json()
        customer_id = customer["id"]
        customer_name = customer["name"]

        client.patch(f"/api/customers/{customer_id}", json={"status": "contacted"})
        client.patch(f"/api/customers/{customer_id}", json={"status": "measured"})

        appointment_data = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "address": "Sunshine City A5-802",
            "scheduled_at": f"{date.today() + timedelta(days=3)}T10:00:00",
            "designer": "Qiao",
            "surveyor": "Hao",
            "status": "scheduled",
            "requirements": "Check load-bearing walls"
        }
        appt_resp = client.post("/api/appointments", json=appointment_data)
        assert appt_resp.status_code == 201
        appointment = appt_resp.json()
        assert appointment["customer_id"] == customer_id
        assert appointment["status"] == "scheduled"

        complete_resp = client.patch(
            f"/api/appointments/{appointment['id']}",
            json={"status": "completed", "requirements": "Measurement completed, dimensions recorded"}
        )
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "completed"

        customer_check = client.get("/api/customers")
        customers = customer_check.json()
        cust = next(c for c in customers if c["id"] == customer_id)
        assert cust["status"] == "measured"

    def test_invalid_customer_status_transition(self, client):
        resp = client.patch("/api/customers/1", json={"status": "invalid_status"})
        assert resp.status_code == 422

    def test_update_nonexistent_customer(self, client):
        resp = client.patch("/api/customers/9999", json={"status": "measured"})
        assert resp.status_code == 404

    def test_customer_skip_status_blocked(self, client):
        customer_data = {
            "name": "Skip Test",
            "phone": "13900000010",
            "community": "Skip Community",
            "house_type": "3 bed 2 bath",
            "source": "Online ad",
            "budget": 300000,
            "status": "new",
            "reported_at": str(date.today()),
            "owner": "Lina",
            "notes": ""
        }
        create_resp = client.post("/api/customers", json=customer_data)
        customer_id = create_resp.json()["id"]

        skip_resp = client.patch(
            f"/api/customers/{customer_id}",
            json={"status": "signed"}
        )
        assert skip_resp.status_code == 409
        detail = skip_resp.json()["detail"]
        assert "当前状态不允许该操作" in detail
        assert "new" in detail
        assert "signed" in detail

    def test_customer_new_to_contacted_allowed(self, client):
        customer_data = {
            "name": "Normal Flow",
            "phone": "13900000011",
            "community": "Normal Community",
            "house_type": "2 bed 1 bath",
            "source": "Referral",
            "budget": 200000,
            "status": "new",
            "reported_at": str(date.today()),
            "owner": "Kai",
            "notes": ""
        }
        create_resp = client.post("/api/customers", json=customer_data)
        customer_id = create_resp.json()["id"]

        resp = client.patch(f"/api/customers/{customer_id}", json={"status": "contacted"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "contacted"

    def test_customer_contacted_to_signed_blocked(self, client):
        customer_data = {
            "name": "Jump Test",
            "phone": "13900000012",
            "community": "Jump Community",
            "house_type": "2 bed 1 bath",
            "source": "Walk-in",
            "budget": 250000,
            "status": "contacted",
            "reported_at": str(date.today()),
            "owner": "Mia",
            "notes": ""
        }
        create_resp = client.post("/api/customers", json=customer_data)
        customer_id = create_resp.json()["id"]

        resp = client.patch(f"/api/customers/{customer_id}", json={"status": "signed"})
        assert resp.status_code == 409
        assert "当前状态不允许该操作" in resp.json()["detail"]

    def test_customer_to_lost_allowed_from_any_status(self, client):
        customer_data = {
            "name": "Lost Test",
            "phone": "13900000013",
            "community": "Lost Community",
            "house_type": "2 bed 1 bath",
            "source": "Online ad",
            "budget": 150000,
            "status": "measured",
            "reported_at": str(date.today()),
            "owner": "Lina",
            "notes": ""
        }
        create_resp = client.post("/api/customers", json=customer_data)
        customer_id = create_resp.json()["id"]

        resp = client.patch(f"/api/customers/{customer_id}", json={"status": "lost"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "lost"

    def test_customer_lost_cannot_transition(self, client):
        customer_data = {
            "name": "Stuck Test",
            "phone": "13900000014",
            "community": "Stuck Community",
            "house_type": "1 bed 1 bath",
            "source": "Online ad",
            "budget": 100000,
            "status": "lost",
            "reported_at": str(date.today()),
            "owner": "Kai",
            "notes": ""
        }
        create_resp = client.post("/api/customers", json=customer_data)
        customer_id = create_resp.json()["id"]

        resp = client.patch(f"/api/customers/{customer_id}", json={"status": "contacted"})
        assert resp.status_code == 409

    def test_customer_sequential_status_flow(self, client):
        customer_data = {
            "name": "Full Seq",
            "phone": "13900000015",
            "community": "Seq Community",
            "house_type": "3 bed 2 bath",
            "source": "Referral",
            "budget": 400000,
            "status": "new",
            "reported_at": str(date.today()),
            "owner": "Mia",
            "notes": ""
        }
        create_resp = client.post("/api/customers", json=customer_data)
        customer_id = create_resp.json()["id"]

        for next_status in ["contacted", "measured", "quoted", "signed"]:
            resp = client.patch(f"/api/customers/{customer_id}", json={"status": next_status})
            assert resp.status_code == 200
            assert resp.json()["status"] == next_status


class TestProjectProgressBoundary:

    def test_project_progress_zero_percent(self, client):
        project_data = {
            "customer_name": "Wang Wu",
            "project_name": "Test Project Zero",
            "manager": "Zhou",
            "phase": "design",
            "progress": 0,
            "start_date": str(date.today()),
            "expected_finish": str(date.today() + timedelta(days=60)),
            "risk_level": "low",
            "latest_update": "Project just started"
        }
        resp = client.post("/api/projects", json=project_data)
        assert resp.status_code == 201
        project = resp.json()
        assert project["progress"] == 0
        assert project["phase"] == "design"

    def test_project_progress_hundred_percent(self, client):
        project_data = {
            "customer_name": "Zhao Liu",
            "project_name": "Test Project Complete",
            "manager": "Tang",
            "phase": "completed",
            "progress": 100,
            "start_date": str(date.today() - timedelta(days=60)),
            "expected_finish": str(date.today()),
            "risk_level": "low",
            "latest_update": "Project fully completed"
        }
        resp = client.post("/api/projects", json=project_data)
        assert resp.status_code == 201
        project = resp.json()
        assert project["progress"] == 100
        assert project["phase"] == "completed"

    def test_project_progress_negative_rejected(self, client):
        project_data = {
            "customer_name": "Qian Qi",
            "project_name": "Test Negative Progress",
            "manager": "Zhou",
            "phase": "demolition",
            "progress": -1,
            "start_date": str(date.today()),
            "expected_finish": str(date.today() + timedelta(days=60)),
            "risk_level": "low"
        }
        resp = client.post("/api/projects", json=project_data)
        assert resp.status_code == 422

    def test_project_progress_over_100_rejected(self, client):
        project_data = {
            "customer_name": "Sun Ba",
            "project_name": "Test Over Progress",
            "manager": "Zhou",
            "phase": "finishing",
            "progress": 101,
            "start_date": str(date.today() - timedelta(days=50)),
            "expected_finish": str(date.today() + timedelta(days=10)),
            "risk_level": "low"
        }
        resp = client.post("/api/projects", json=project_data)
        assert resp.status_code == 422

    def test_update_progress_boundary_values(self, client):
        project_data = {
            "customer_name": "Zhou Jiu",
            "project_name": "Test Progress Update",
            "manager": "Zhou",
            "phase": "demolition",
            "progress": 50,
            "start_date": str(date.today() - timedelta(days=30)),
            "expected_finish": str(date.today() + timedelta(days=30)),
            "risk_level": "medium",
            "latest_update": "In progress"
        }
        create_resp = client.post("/api/projects", json=project_data)
        project_id = create_resp.json()["id"]

        update_resp = client.patch(
            f"/api/projects/{project_id}",
            json={"progress": 0}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["progress"] == 0

        update_resp = client.patch(
            f"/api/projects/{project_id}",
            json={"progress": 100, "phase": "completed"}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["progress"] == 100
        assert update_resp.json()["phase"] == "completed"

        invalid_resp = client.patch(
            f"/api/projects/{project_id}",
            json={"progress": 150}
        )
        assert invalid_resp.status_code == 422

    def test_project_phase_transitions(self, client):
        phases = ["design", "demolition", "plumbing", "waterproofing", "carpentry", "finishing", "completed"]
        progresses = [0, 15, 35, 50, 65, 85, 100]

        project_data = {
            "customer_name": "Wu Shi",
            "project_name": "Phase Transition Test",
            "manager": "Tang",
            "phase": phases[0],
            "progress": progresses[0],
            "start_date": str(date.today() - timedelta(days=10)),
            "expected_finish": str(date.today() + timedelta(days=50)),
            "risk_level": "low"
        }
        create_resp = client.post("/api/projects", json=project_data)
        project_id = create_resp.json()["id"]

        for phase, progress in zip(phases[1:], progresses[1:]):
            update_resp = client.patch(
                f"/api/projects/{project_id}",
                json={"phase": phase, "progress": progress, "latest_update": f"Entering {phase} phase"}
            )
            assert update_resp.status_code == 200
            updated = update_resp.json()
            assert updated["phase"] == phase
            assert updated["progress"] == progress

        list_resp = client.get("/api/projects")
        projects = list_resp.json()
        final = next(p for p in projects if p["id"] == project_id)
        assert final["phase"] == "completed"
        assert final["progress"] == 100

    def test_project_completed_without_progress_100_rejected_on_create(self, client):
        project_data = {
            "customer_name": "Invalid Complete",
            "project_name": "Invalid Complete Project",
            "manager": "Zhou",
            "phase": "completed",
            "progress": 80,
            "start_date": str(date.today() - timedelta(days=50)),
            "expected_finish": str(date.today()),
            "risk_level": "low"
        }
        resp = client.post("/api/projects", json=project_data)
        assert resp.status_code == 422
        assert "进度必须达到100" in resp.json()["detail"]

    def test_project_set_completed_without_progress_100_rejected_on_update(self, client):
        project_data = {
            "customer_name": "Update Complete",
            "project_name": "Update Complete Project",
            "manager": "Tang",
            "phase": "finishing",
            "progress": 85,
            "start_date": str(date.today() - timedelta(days=50)),
            "expected_finish": str(date.today() + timedelta(days=10)),
            "risk_level": "low"
        }
        create_resp = client.post("/api/projects", json=project_data)
        project_id = create_resp.json()["id"]

        resp = client.patch(
            f"/api/projects/{project_id}",
            json={"phase": "completed"}
        )
        assert resp.status_code == 422
        assert "进度必须达到100" in resp.json()["detail"]

    def test_project_set_completed_with_progress_100_allowed(self, client):
        project_data = {
            "customer_name": "Valid Complete",
            "project_name": "Valid Complete Project",
            "manager": "Zhou",
            "phase": "finishing",
            "progress": 95,
            "start_date": str(date.today() - timedelta(days=55)),
            "expected_finish": str(date.today() + timedelta(days=5)),
            "risk_level": "low"
        }
        create_resp = client.post("/api/projects", json=project_data)
        project_id = create_resp.json()["id"]

        resp = client.patch(
            f"/api/projects/{project_id}",
            json={"phase": "completed", "progress": 100}
        )
        assert resp.status_code == 200
        assert resp.json()["phase"] == "completed"
        assert resp.json()["progress"] == 100

    def test_project_progress_100_without_completed_phase_allowed(self, client):
        project_data = {
            "customer_name": "Progress 100",
            "project_name": "Progress 100 No Complete",
            "manager": "Tang",
            "phase": "finishing",
            "progress": 90,
            "start_date": str(date.today() - timedelta(days=55)),
            "expected_finish": str(date.today() + timedelta(days=5)),
            "risk_level": "low"
        }
        create_resp = client.post("/api/projects", json=project_data)
        project_id = create_resp.json()["id"]

        resp = client.patch(
            f"/api/projects/{project_id}",
            json={"progress": 100}
        )
        assert resp.status_code == 200
        assert resp.json()["progress"] == 100


class TestProcurementStatus:

    def test_procurement_full_status_flow(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Procurement Test",
            "project_name": "Procurement Flow Project",
            "manager": "Zhou",
            "phase": "demolition",
            "progress": 10,
            "start_date": str(date.today()),
            "expected_finish": str(date.today() + timedelta(days=60)),
            "risk_level": "low"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        procurement_data = {
            "project_id": project_id,
            "project_name": project_name,
            "material": "Cement",
            "supplier": "JianCai Co.",
            "quantity": 100,
            "unit": "bags",
            "budget": 5000,
            "status": "pending",
            "required_date": str(date.today() + timedelta(days=7))
        }
        create_resp = client.post("/api/procurements", json=procurement_data)
        assert create_resp.status_code == 201
        proc_id = create_resp.json()["id"]
        assert create_resp.json()["status"] == "pending"

        ordered_resp = client.patch(
            f"/api/procurements/{proc_id}",
            json={"status": "ordered"}
        )
        assert ordered_resp.status_code == 200
        assert ordered_resp.json()["status"] == "ordered"

        delivered_resp = client.patch(
            f"/api/procurements/{proc_id}",
            json={"status": "delivered"}
        )
        assert delivered_resp.status_code == 200
        assert delivered_resp.json()["status"] == "delivered"

        accepted_resp = client.patch(
            f"/api/procurements/{proc_id}",
            json={"status": "accepted"}
        )
        assert accepted_resp.status_code == 200
        assert accepted_resp.json()["status"] == "accepted"

    def test_procurement_return_flow(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Return Test",
            "project_name": "Return Flow Project",
            "manager": "Tang",
            "phase": "plumbing",
            "progress": 30,
            "start_date": str(date.today() - timedelta(days=20)),
            "expected_finish": str(date.today() + timedelta(days=40)),
            "risk_level": "medium"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        procurement_data = {
            "project_id": project_id,
            "project_name": project_name,
            "material": "Pipes",
            "supplier": "ShuiGuan Co.",
            "quantity": 50,
            "unit": "meters",
            "budget": 3000,
            "status": "pending",
            "required_date": str(date.today() + timedelta(days=5))
        }
        create_resp = client.post("/api/procurements", json=procurement_data)
        proc_id = create_resp.json()["id"]

        client.patch(f"/api/procurements/{proc_id}", json={"status": "ordered"})
        client.patch(f"/api/procurements/{proc_id}", json={"status": "delivered"})

        return_resp = client.patch(
            f"/api/procurements/{proc_id}",
            json={"status": "returned"}
        )
        assert return_resp.status_code == 200
        assert return_resp.json()["status"] == "returned"

    def test_procurement_invalid_status_rejected(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Invalid Status Test",
            "project_name": "Invalid Status Project",
            "manager": "Zhou",
            "phase": "design",
            "progress": 5,
            "start_date": str(date.today()),
            "expected_finish": str(date.today() + timedelta(days=60)),
            "risk_level": "low"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        invalid_data = {
            "project_id": project_id,
            "project_name": project_name,
            "material": "Test Material",
            "supplier": "Test Supplier",
            "quantity": 10,
            "unit": "units",
            "budget": 1000,
            "status": "invalid_status",
            "required_date": str(date.today() + timedelta(days=7))
        }
        resp = client.post("/api/procurements", json=invalid_data)
        assert resp.status_code == 422

    def test_procurement_quantity_must_be_positive(self, client):
        invalid_data = {
            "project_id": 1,
            "project_name": "Test",
            "material": "Test",
            "supplier": "Test",
            "quantity": 0,
            "unit": "units",
            "budget": 1000,
            "status": "pending",
            "required_date": str(date.today() + timedelta(days=7))
        }
        resp = client.post("/api/procurements", json=invalid_data)
        assert resp.status_code == 422

    def test_procurement_budget_non_negative(self, client):
        invalid_data = {
            "project_id": 1,
            "project_name": "Test",
            "material": "Test",
            "supplier": "Test",
            "quantity": 10,
            "unit": "units",
            "budget": -100,
            "status": "pending",
            "required_date": str(date.today() + timedelta(days=7))
        }
        resp = client.post("/api/procurements", json=invalid_data)
        assert resp.status_code == 422

    def test_procurement_nonexistent_project_rejected(self, client):
        procurement_data = {
            "project_id": 9999,
            "project_name": "Ghost Project",
            "material": "Phantom Cement",
            "supplier": "Nowhere Co.",
            "quantity": 50,
            "unit": "bags",
            "budget": 3000,
            "status": "pending",
            "required_date": str(date.today() + timedelta(days=7))
        }
        resp = client.post("/api/procurements", json=procurement_data)
        assert resp.status_code == 422
        assert "关联的项目不存在" in resp.json()["detail"]
        assert "9999" in resp.json()["detail"]

    def test_procurement_update_to_nonexistent_project_rejected(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Proc Update Test",
            "project_name": "Proc Update Project",
            "manager": "Zhou",
            "phase": "design",
            "progress": 5,
            "start_date": str(date.today()),
            "expected_finish": str(date.today() + timedelta(days=60)),
            "risk_level": "low"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        proc_data = {
            "project_id": project_id,
            "project_name": project_name,
            "material": "Test Material",
            "supplier": "Test Supplier",
            "quantity": 10,
            "unit": "units",
            "budget": 1000,
            "status": "pending",
            "required_date": str(date.today() + timedelta(days=7))
        }
        create_resp = client.post("/api/procurements", json=proc_data)
        proc_id = create_resp.json()["id"]

        update_resp = client.patch(
            f"/api/procurements/{proc_id}",
            json={"project_id": 9999}
        )
        assert update_resp.status_code == 422
        assert "关联的项目不存在" in update_resp.json()["detail"]

    def test_procurement_valid_project_allowed(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Valid Proc Test",
            "project_name": "Valid Proc Project",
            "manager": "Zhou",
            "phase": "demolition",
            "progress": 10,
            "start_date": str(date.today()),
            "expected_finish": str(date.today() + timedelta(days=60)),
            "risk_level": "low"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        procurement_data = {
            "project_id": project_id,
            "project_name": project_name,
            "material": "Valid Material",
            "supplier": "Valid Supplier",
            "quantity": 20,
            "unit": "units",
            "budget": 5000,
            "status": "pending",
            "required_date": str(date.today() + timedelta(days=7))
        }
        resp = client.post("/api/procurements", json=procurement_data)
        assert resp.status_code == 201
        assert resp.json()["project_id"] == project_id


class TestInspectionRectification:

    def test_inspection_pending_to_rectification(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Inspection Test",
            "project_name": "Inspection Flow Project",
            "manager": "Zhou",
            "phase": "waterproofing",
            "progress": 45,
            "start_date": str(date.today() - timedelta(days=25)),
            "expected_finish": str(date.today() + timedelta(days=35)),
            "risk_level": "medium"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        inspection_data = {
            "project_id": project_id,
            "project_name": project_name,
            "inspection_type": "Waterproofing",
            "scheduled_date": str(date.today()),
            "inspector": "An",
            "result": "pending",
            "issues": "Awaiting inspection"
        }
        create_resp = client.post("/api/inspections", json=inspection_data)
        assert create_resp.status_code == 201
        inspection_id = create_resp.json()["id"]
        assert create_resp.json()["result"] == "pending"

        rectify_resp = client.patch(
            f"/api/inspections/{inspection_id}",
            json={"result": "整改", "issues": "Waterproof layer thickness insufficient, needs rework"}
        )
        assert rectify_resp.status_code == 200
        assert rectify_resp.json()["result"] == "整改"
        assert "thickness insufficient" in rectify_resp.json()["issues"]

    def test_inspection_rectification_to_passed(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Rectification Test",
            "project_name": "Rectification Pass Project",
            "manager": "Tang",
            "phase": "carpentry",
            "progress": 60,
            "start_date": str(date.today() - timedelta(days=35)),
            "expected_finish": str(date.today() + timedelta(days=25)),
            "risk_level": "low"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        inspection_data = {
            "project_id": project_id,
            "project_name": project_name,
            "inspection_type": "Woodwork",
            "scheduled_date": str(date.today() - timedelta(days=2)),
            "inspector": "Mo",
            "result": "pending",
            "issues": ""
        }
        create_resp = client.post("/api/inspections", json=inspection_data)
        inspection_id = create_resp.json()["id"]

        client.patch(
            f"/api/inspections/{inspection_id}",
            json={"result": "整改", "issues": "Cabinet door gap exceeds tolerance by 2mm"}
        )

        pass_resp = client.patch(
            f"/api/inspections/{inspection_id}",
            json={"result": "passed", "issues": "Gap adjusted, now within tolerance. Inspection passed."}
        )
        assert pass_resp.status_code == 200
        assert pass_resp.json()["result"] == "passed"

        list_resp = client.get("/api/inspections")
        inspections = list_resp.json()
        final = next(i for i in inspections if i["id"] == inspection_id)
        assert final["result"] == "passed"

    def test_inspection_failed_result(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Failed Test",
            "project_name": "Failed Inspection Project",
            "manager": "Zhou",
            "phase": "finishing",
            "progress": 75,
            "start_date": str(date.today() - timedelta(days=45)),
            "expected_finish": str(date.today() + timedelta(days=15)),
            "risk_level": "high"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        inspection_data = {
            "project_id": project_id,
            "project_name": project_name,
            "inspection_type": "Electrical",
            "scheduled_date": str(date.today()),
            "inspector": "An",
            "result": "pending",
            "issues": ""
        }
        create_resp = client.post("/api/inspections", json=inspection_data)
        inspection_id = create_resp.json()["id"]

        fail_resp = client.patch(
            f"/api/inspections/{inspection_id}",
            json={"result": "failed", "issues": "Wiring does not meet safety standards, major rework required"}
        )
        assert fail_resp.status_code == 200
        assert fail_resp.json()["result"] == "failed"

    def test_inspection_invalid_result_rejected(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Invalid Test",
            "project_name": "Invalid Result Project",
            "manager": "Zhou",
            "phase": "demolition",
            "progress": 20,
            "start_date": str(date.today() - timedelta(days=10)),
            "expected_finish": str(date.today() + timedelta(days=50)),
            "risk_level": "low"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        invalid_data = {
            "project_id": project_id,
            "project_name": project_name,
            "inspection_type": "Site",
            "scheduled_date": str(date.today()),
            "inspector": "An",
            "result": "invalid_result",
            "issues": ""
        }
        resp = client.post("/api/inspections", json=invalid_data)
        assert resp.status_code == 422

    def test_update_nonexistent_inspection(self, client):
        resp = client.patch(
            "/api/inspections/9999",
            json={"result": "passed"}
        )
        assert resp.status_code == 404


class TestDashboardRefresh:

    def test_dashboard_initial_summary(self, client):
        resp = client.get("/api/dashboard/summary")
        assert resp.status_code == 200
        data = resp.json()

        assert "generated_at" in data
        assert "metrics" in data
        assert "procurement_budget" in data
        assert "phase_distribution" in data
        assert "recent_updates" in data

        assert len(data["metrics"]) == 4
        metric_labels = [m["label"] for m in data["metrics"]]
        assert "Customer reports" in metric_labels
        assert "Measure bookings" in metric_labels
        assert "Active projects" in metric_labels
        assert "Pending inspections" in metric_labels

    def test_dashboard_refresh_after_adding_customer(self, client):
        initial_resp = client.get("/api/dashboard/summary")
        initial_data = initial_resp.json()
        initial_customer_count = next(
            m["value"] for m in initial_data["metrics"] if m["label"] == "Customer reports"
        )

        new_customer = {
            "name": "Dashboard Test",
            "phone": "13800001234",
            "community": "Test Community",
            "house_type": "2 bed 1 bath",
            "source": "Online ad",
            "budget": 250000,
            "status": "new",
            "reported_at": str(date.today()),
            "owner": "Lina",
            "notes": ""
        }
        client.post("/api/customers", json=new_customer)

        refresh_resp = client.get("/api/dashboard/summary")
        refresh_data = refresh_resp.json()
        new_customer_count = next(
            m["value"] for m in refresh_data["metrics"] if m["label"] == "Customer reports"
        )

        assert new_customer_count == initial_customer_count + 1
        assert refresh_data["generated_at"] >= initial_data["generated_at"]

    def test_dashboard_refresh_after_adding_project(self, client):
        initial_resp = client.get("/api/dashboard/summary")
        initial_data = initial_resp.json()
        initial_active = next(
            m["value"] for m in initial_data["metrics"] if m["label"] == "Active projects"
        )

        new_project = {
            "customer_name": "Dashboard Project Test",
            "project_name": "Dashboard Test Project",
            "manager": "Zhou",
            "phase": "design",
            "progress": 10,
            "start_date": str(date.today()),
            "expected_finish": str(date.today() + timedelta(days=60)),
            "risk_level": "low",
            "latest_update": "New dashboard test project"
        }
        client.post("/api/projects", json=new_project)

        refresh_resp = client.get("/api/dashboard/summary")
        refresh_data = refresh_resp.json()
        new_active = next(
            m["value"] for m in refresh_data["metrics"] if m["label"] == "Active projects"
        )

        assert new_active == initial_active + 1

    def test_dashboard_refresh_after_adding_inspection(self, client):
        project_resp = client.post("/api/projects", json={
            "customer_name": "Dashboard Inspection Test",
            "project_name": "Dashboard Inspection Project",
            "manager": "Zhou",
            "phase": "waterproofing",
            "progress": 40,
            "start_date": str(date.today() - timedelta(days=20)),
            "expected_finish": str(date.today() + timedelta(days=40)),
            "risk_level": "medium"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        initial_resp = client.get("/api/dashboard/summary")
        initial_data = initial_resp.json()
        initial_pending = next(
            m["value"] for m in initial_data["metrics"] if m["label"] == "Pending inspections"
        )

        new_inspection = {
            "project_id": project_id,
            "project_name": project_name,
            "inspection_type": "Waterproofing",
            "scheduled_date": str(date.today() + timedelta(days=1)),
            "inspector": "An",
            "result": "pending",
            "issues": ""
        }
        client.post("/api/inspections", json=new_inspection)

        refresh_resp = client.get("/api/dashboard/summary")
        refresh_data = refresh_resp.json()
        new_pending = next(
            m["value"] for m in refresh_data["metrics"] if m["label"] == "Pending inspections"
        )

        assert new_pending == initial_pending + 1

    def test_dashboard_refresh_after_project_completion(self, client):
        initial_resp = client.get("/api/dashboard/summary")
        initial_data = initial_resp.json()
        initial_active = next(
            m["value"] for m in initial_data["metrics"] if m["label"] == "Active projects"
        )

        new_project = {
            "customer_name": "Completion Test",
            "project_name": "Completing Project",
            "manager": "Tang",
            "phase": "finishing",
            "progress": 95,
            "start_date": str(date.today() - timedelta(days=55)),
            "expected_finish": str(date.today() + timedelta(days=5)),
            "risk_level": "low",
            "latest_update": "Almost done"
        }
        create_resp = client.post("/api/projects", json=new_project)
        project_id = create_resp.json()["id"]

        after_add_resp = client.get("/api/dashboard/summary")
        after_add_data = after_add_resp.json()
        after_add_active = next(
            m["value"] for m in after_add_data["metrics"] if m["label"] == "Active projects"
        )
        assert after_add_active == initial_active + 1

        client.patch(
            f"/api/projects/{project_id}",
            json={"progress": 100, "phase": "completed"}
        )

        final_resp = client.get("/api/dashboard/summary")
        final_data = final_resp.json()
        final_active = next(
            m["value"] for m in final_data["metrics"] if m["label"] == "Active projects"
        )
        assert final_active == initial_active

    def test_dashboard_procurement_budget_refresh(self, client):
        initial_resp = client.get("/api/dashboard/summary")
        initial_budget = initial_resp.json()["procurement_budget"]

        project_resp = client.post("/api/projects", json={
            "customer_name": "Budget Test",
            "project_name": "Budget Test Project",
            "manager": "Zhou",
            "phase": "demolition",
            "progress": 5,
            "start_date": str(date.today()),
            "expected_finish": str(date.today() + timedelta(days=60)),
            "risk_level": "low"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        new_procurement = {
            "project_id": project_id,
            "project_name": project_name,
            "material": "Test Material",
            "supplier": "Test Supplier",
            "quantity": 10,
            "unit": "units",
            "budget": 15000,
            "status": "pending",
            "required_date": str(date.today() + timedelta(days=10))
        }
        client.post("/api/procurements", json=new_procurement)

        refresh_resp = client.get("/api/dashboard/summary")
        new_budget = refresh_resp.json()["procurement_budget"]

        assert new_budget == initial_budget + 15000

    def test_dashboard_recent_updates_sorted_by_progress(self, client):
        client.post("/api/projects", json={
            "customer_name": "Low Progress",
            "project_name": "Low Progress Project",
            "manager": "Zhou",
            "phase": "design",
            "progress": 10,
            "start_date": str(date.today()),
            "expected_finish": str(date.today() + timedelta(days=60)),
            "risk_level": "low",
            "latest_update": "Low progress update"
        })
        client.post("/api/projects", json={
            "customer_name": "High Progress",
            "project_name": "High Progress Project",
            "manager": "Tang",
            "phase": "finishing",
            "progress": 90,
            "start_date": str(date.today() - timedelta(days=50)),
            "expected_finish": str(date.today() + timedelta(days=10)),
            "risk_level": "low",
            "latest_update": "High progress update"
        })

        resp = client.get("/api/dashboard/summary")
        updates = resp.json()["recent_updates"]

        progresses = [u["progress"] for u in updates]
        assert progresses == sorted(progresses, reverse=True)


class TestEndToEndDecorationFlow:

    def test_complete_decoration_workflow(self, client):
        customer_resp = client.post("/api/customers", json={
            "name": "Full Flow Test",
            "phone": "13900009999",
            "community": "End-to-End Community",
            "house_type": "4 bed 3 bath",
            "source": "Referral",
            "budget": 800000,
            "status": "new",
            "reported_at": str(date.today() - timedelta(days=10)),
            "owner": "Lina",
            "notes": "Luxury renovation required"
        })
        customer_id = customer_resp.json()["id"]
        customer_name = customer_resp.json()["name"]

        client.patch(f"/api/customers/{customer_id}", json={"status": "contacted"})

        appointment_resp = client.post("/api/appointments", json={
            "customer_id": customer_id,
            "customer_name": customer_name,
            "address": "End-to-End Community B1-1201",
            "scheduled_at": f"{date.today() - timedelta(days=7)}T10:00:00",
            "designer": "Qiao",
            "surveyor": "Hao",
            "status": "completed",
            "requirements": "Measurement done, all dimensions recorded"
        })
        assert appointment_resp.status_code == 201

        client.patch(f"/api/customers/{customer_id}", json={"status": "measured"})

        client.patch(f"/api/customers/{customer_id}", json={"status": "quoted"})

        client.patch(f"/api/customers/{customer_id}", json={"status": "signed"})

        project_resp = client.post("/api/projects", json={
            "customer_name": customer_name,
            "project_name": "Full Flow Renovation",
            "manager": "Zhou",
            "phase": "demolition",
            "progress": 0,
            "start_date": str(date.today() - timedelta(days=5)),
            "expected_finish": str(date.today() + timedelta(days=55)),
            "risk_level": "medium",
            "latest_update": "Project kicked off"
        })
        project_id = project_resp.json()["id"]
        project_name = project_resp.json()["project_name"]

        procurement_resp = client.post("/api/procurements", json={
            "project_id": project_id,
            "project_name": project_name,
            "material": "Demolition tools and materials",
            "supplier": "Building Supplies Co.",
            "quantity": 1,
            "unit": "lot",
            "budget": 20000,
            "status": "ordered",
            "required_date": str(date.today() - timedelta(days=4))
        })
        proc_id = procurement_resp.json()["id"]
        client.patch(f"/api/procurements/{proc_id}", json={"status": "delivered"})
        client.patch(f"/api/procurements/{proc_id}", json={"status": "accepted"})

        inspection_resp = client.post("/api/inspections", json={
            "project_id": project_id,
            "project_name": project_name,
            "inspection_type": "Site Protection",
            "scheduled_date": str(date.today() - timedelta(days=3)),
            "inspector": "An",
            "result": "passed",
            "issues": "All protection measures in place"
        })
        assert inspection_resp.status_code == 201

        client.patch(f"/api/projects/{project_id}", json={
            "phase": "plumbing",
            "progress": 25,
            "latest_update": "Demolition complete, plumbing started"
        })

        client.patch(f"/api/projects/{project_id}", json={
            "phase": "waterproofing",
            "progress": 45,
            "latest_update": "Plumbing done, waterproofing in progress"
        })

        wp_inspection = client.post("/api/inspections", json={
            "project_id": project_id,
            "project_name": project_name,
            "inspection_type": "Waterproofing",
            "scheduled_date": str(date.today() - timedelta(days=1)),
            "inspector": "An",
            "result": "pending",
            "issues": ""
        })
        wp_id = wp_inspection.json()["id"]

        client.patch(f"/api/inspections/{wp_id}", json={
            "result": "整改",
            "issues": "Bathroom floor slope insufficient, needs adjustment"
        })

        client.patch(f"/api/inspections/{wp_id}", json={
            "result": "passed",
            "issues": "Slope corrected, 48-hour water test passed"
        })

        client.patch(f"/api/projects/{project_id}", json={
            "phase": "carpentry",
            "progress": 65,
            "latest_update": "Waterproofing passed, carpentry started"
        })

        client.patch(f"/api/projects/{project_id}", json={
            "phase": "finishing",
            "progress": 85,
            "latest_update": "Carpentry done, finishing works"
        })

        client.patch(f"/api/projects/{project_id}", json={
            "phase": "completed",
            "progress": 100,
            "latest_update": "Project completed and handed over to client"
        })

        dashboard_resp = client.get("/api/dashboard/summary")
        dashboard_data = dashboard_resp.json()

        customer_list = client.get("/api/customers")
        final_customer = next(c for c in customer_list.json() if c["id"] == customer_id)
        assert final_customer["status"] == "signed"

        project_list = client.get("/api/projects")
        final_project = next(p for p in project_list.json() if p["id"] == project_id)
        assert final_project["phase"] == "completed"
        assert final_project["progress"] == 100

        active_projects = next(
            m["value"] for m in dashboard_data["metrics"] if m["label"] == "Active projects"
        )
        completed_project = next(
            p for p in dashboard_data["recent_updates"] if p["project_name"] == project_name
        )
        assert completed_project["progress"] == 100

        assert final_customer["status"] == "signed"
        assert final_project["phase"] == "completed"
        assert final_project["progress"] == 100
