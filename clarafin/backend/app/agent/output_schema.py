from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Citation(BaseModel):
    doc: str
    loc: str
    text: str

class MetricInsight(BaseModel):
    metric: str
    value: str
    interpretation: str
    citations: List[Citation]

class AnomalyInsight(BaseModel):
    title: str
    description: str
    citations: List[Citation]

class CurrentState(BaseModel):
    liquidity: MetricInsight
    margins: MetricInsight
    concentration: MetricInsight
    anomalies: List[AnomalyInsight]

class GapInsight(BaseModel):
    missing_item: str
    blocked_decision: str
    explanation: str

class FlagInsight(BaseModel):
    flag_type: str
    trajectory_observation: str
    severity: str

class StructuredAnalysisResult(BaseModel):
    current_state: CurrentState
    gap_detection: List[GapInsight]
    forward_flags: List[FlagInsight]
