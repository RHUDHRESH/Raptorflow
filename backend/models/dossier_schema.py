from typing import List, Optional, Type

from pydantic import BaseModel, Field, create_model


class DossierField(BaseModel):
    name: str
    description: str
    required: bool = True
    query_hints: List[str] = Field(default_factory=list)
    field_type: Type = str

    model_config = {"arbitrary_types_allowed": True}


class DossierSchema(BaseModel):
    fields: List[DossierField]

    model_config = {"arbitrary_types_allowed": True}


DEFAULT_DOSSIER_SCHEMA = DossierSchema(
    fields=[
        DossierField(
            name="company_overview",
            description="Concise company overview and mission.",
            query_hints=["company overview", "mission statement", "about us"],
        ),
        DossierField(
            name="products_services",
            description="Primary products or services offered.",
            query_hints=["product suite", "services", "platform features"],
            field_type=List[str],
        ),
        DossierField(
            name="pricing_packaging",
            description="Pricing tiers, packaging, and monetization model.",
            query_hints=["pricing", "plans", "subscription tiers"],
        ),
        DossierField(
            name="target_segments",
            description="Core customer segments and ICP focus.",
            query_hints=["target customers", "ideal customer profile", "segments"],
            field_type=List[str],
        ),
        DossierField(
            name="positioning_messaging",
            description="Positioning, value proposition, and messaging themes.",
            query_hints=["positioning", "value proposition", "messaging"],
        ),
        DossierField(
            name="differentiators",
            description="Key differentiators or competitive advantages.",
            query_hints=["differentiators", "competitive advantage", "unique features"],
            field_type=List[str],
        ),
        DossierField(
            name="vulnerabilities",
            description="Weaknesses, risks, or gaps to exploit.",
            query_hints=["weaknesses", "limitations", "customer complaints"],
            field_type=List[str],
        ),
        DossierField(
            name="go_to_market",
            description="Go-to-market strategy and distribution channels.",
            query_hints=["go-to-market", "sales channels", "marketing strategy"],
        ),
        DossierField(
            name="recent_news",
            description="Recent announcements, launches, or notable news.",
            query_hints=["recent news", "press release", "announcement"],
            field_type=List[str],
        ),
        DossierField(
            name="customer_proof",
            description="Customer proof points, case studies, or testimonials.",
            query_hints=["case study", "testimonial", "customer story"],
            field_type=List[str],
        ),
        DossierField(
            name="leadership",
            description="Key leadership team members and roles.",
            query_hints=["leadership team", "executives", "founders"],
            field_type=List[str],
        ),
        DossierField(
            name="funding_financials",
            description="Funding history, financial signals, or revenue estimates.",
            query_hints=["funding", "investors", "revenue"],
        ),
        DossierField(
            name="tech_stack",
            description="Core technology stack and integrations.",
            query_hints=["tech stack", "integrations", "developer docs"],
            field_type=List[str],
        ),
        DossierField(
            name="partnerships",
            description="Strategic partnerships and ecosystem alliances.",
            query_hints=["partnerships", "alliances", "integrations partners"],
            field_type=List[str],
        ),
    ]
)


def build_dossier_model(schema: DossierSchema):
    field_definitions = {}
    for field in schema.fields:
        field_definitions[field.name] = (
            Optional[field.field_type],
            Field(default=None, description=field.description),
        )
    return create_model("DossierData", **field_definitions)
