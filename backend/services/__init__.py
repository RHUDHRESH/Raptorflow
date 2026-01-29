"""
Services package for RaptorFlow
Business logic layer that coordinates between repositories and API endpoints
"""

# Only import services that actually exist and work
# from .billing import BillingService  # Commented out - broken dependencies
# from .campaign import CampaignService  # Commented out - broken dependencies
# from .content import ContentService  # Commented out - broken dependencies
# from .foundation import FoundationService  # Commented out - broken dependencies
# from .icp import ICPService  # Commented out - broken dependencies
# from .move import MoveService  # Commented out - broken dependencies
# from .onboarding import OnboardingService  # Commented out - broken dependencies

# Import payment and email services (these work)
from .email_service import EmailService
from .payment_service import PaymentService

__all__ = [
    "EmailService",
    "PaymentService",
]

# Vertex AI service - only import if available
try:
    from .vertex_ai_service import vertex_ai_service

    __all__.append("vertex_ai_service")
except ImportError:
    # Vertex AI dependencies not available
    pass
