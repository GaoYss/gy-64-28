from pydantic import BaseModel


class DesignerWorkloadItem(BaseModel):
    designer: str
    measured: int
    quoted: int
    signed: int
    signed_budget: float
    avg_budget: float
    measurement_to_quote_rate: float
    quote_to_sign_rate: float
    measurement_to_sign_rate: float
    measured_customers: list[dict]
    quoted_customers: list[dict]
    signed_customers: list[dict]


class DesignerWorkloadSummary(BaseModel):
    total_designers: int
    total_measured: int
    total_quoted: int
    total_signed: int
    total_signed_budget: float
    overall_measurement_to_quote_rate: float
    overall_quote_to_sign_rate: float
    overall_measurement_to_sign_rate: float


class DesignerWorkload(BaseModel):
    generated_at: str
    workload: list[DesignerWorkloadItem]
    summary: DesignerWorkloadSummary
