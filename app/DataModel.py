from pydantic import BaseModel, ConfigDict, Field


class ReportedVersion(BaseModel):
    """A conflicting value copied from the intake note."""

    value: str
    evidence: str


class ExtractedField(BaseModel):
    """A mapped CNF value with the evidence needed for human review."""

    model_config = ConfigDict(extra="forbid")

    value: str | None = None
    evidence: str | None = None
    note: str | None = None
    reported_versions: list[ReportedVersion] = Field(default_factory=list)


class Claim(BaseModel):
    """The twelve-field CNF mapping returned by the extraction model."""

    model_config = ConfigDict(extra="forbid")

    claimant_full_name: ExtractedField
    date_of_birth: ExtractedField
    address: ExtractedField
    email: ExtractedField
    accident_date: ExtractedField
    accident_time: ExtractedField
    accident_location: ExtractedField
    claimant_role: ExtractedField
    claimant_vehicle_registration: ExtractedField
    other_vehicle_registration: ExtractedField
    injury_description: ExtractedField
    other_insurer_name: ExtractedField