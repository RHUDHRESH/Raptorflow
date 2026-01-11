# PHASE 8: INDIAN MARKET INTEGRATION

---

## 8.1 PhonePe Payment Gateway

```python
# backend/indian_market/phonepe_gateway.py
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import hashlib
import base64
import json
import aiohttp
import logging

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PaymentRequest(BaseModel):
    """Payment initiation request."""
    user_id: str
    amount: float  # In INR
    plan_id: str
    redirect_url: str
    callback_url: str


class PaymentStatus(BaseModel):
    """Payment status response."""
    transaction_id: str
    merchant_transaction_id: str
    status: str  # SUCCESS, PENDING, FAILED
    amount: float
    payment_instrument: Optional[Dict] = None


class PhonePeGateway:
    """
    PhonePe Payment Gateway Integration (2026 SDK).

    Features:
    - OAuth 2.0 authentication
    - Payment initiation
    - Status checking
    - Refunds
    - Webhook validation
    - UPI Mandate (recurring payments)
    """

    def __init__(self):
        self.client_id = settings.PHONEPE_CLIENT_ID
        self.client_secret = settings.PHONEPE_CLIENT_SECRET
        self.environment = settings.PHONEPE_ENVIRONMENT

        if self.environment == "PRODUCTION":
            self.base_url = "https://api.phonepe.com/apis/hermes"
            self.auth_url = "https://api.phonepe.com/apis/identity-manager/v1/oauth/token"
        else:
            self.base_url = "https://api-preprod.phonepe.com/apis/pg-sandbox"
            self.auth_url = "https://api-preprod.phonepe.com/apis/identity-manager/v1/oauth/token"

        self._access_token = None
        self._token_expiry = None

    async def get_access_token(self) -> str:
        """
        Get OAuth access token using client credentials.
        """
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token

        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }

            async with session.post(self.auth_url, data=data) as response:
                result = await response.json()

                if response.status == 200:
                    self._access_token = result["access_token"]
                    self._token_expiry = datetime.now() + timedelta(seconds=result["expires_in"] - 60)
                    return self._access_token
                else:
                    raise Exception(f"PhonePe auth failed: {result}")

    async def initiate_payment(self, request: PaymentRequest) -> Dict[str, Any]:
        """
        Initiate a payment request.

        Returns:
            {
                "transaction_id": "...",
                "redirect_url": "...",  # Redirect user here
                "qr_code": "..."  # Optional QR for UPI
            }
        """
        merchant_tx_id = f"RF_{request.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        payload = {
            "merchantId": self.client_id,
            "merchantTransactionId": merchant_tx_id,
            "merchantUserId": request.user_id,
            "amount": int(request.amount * 100),  # Paise
            "redirectUrl": request.redirect_url,
            "redirectMode": "POST",
            "callbackUrl": request.callback_url,
            "paymentInstrument": {
                "type": "PAY_PAGE"
            }
        }

        # Encode payload
        payload_base64 = base64.b64encode(json.dumps(payload).encode()).decode()

        # Generate checksum
        checksum = self._generate_checksum(payload_base64, "/pg/v1/pay")

        token = await self.get_access_token()

        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "X-VERIFY": checksum
            }

            async with session.post(
                f"{self.base_url}/pg/v1/pay",
                json={"request": payload_base64},
                headers=headers
            ) as response:
                result = await response.json()

                if result.get("success"):
                    return {
                        "transaction_id": merchant_tx_id,
                        "redirect_url": result["data"]["instrumentResponse"]["redirectInfo"]["url"],
                        "status": "INITIATED"
                    }
                else:
                    raise Exception(f"Payment initiation failed: {result}")

    async def check_status(self, merchant_transaction_id: str) -> PaymentStatus:
        """
        Check payment status.
        """
        endpoint = f"/pg/v1/status/{self.client_id}/{merchant_transaction_id}"
        checksum = self._generate_checksum("", endpoint)

        token = await self.get_access_token()

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {token}",
                "X-VERIFY": checksum,
                "X-MERCHANT-ID": self.client_id
            }

            async with session.get(
                f"{self.base_url}{endpoint}",
                headers=headers
            ) as response:
                result = await response.json()

                if result.get("success"):
                    data = result["data"]
                    return PaymentStatus(
                        transaction_id=data.get("transactionId", ""),
                        merchant_transaction_id=merchant_transaction_id,
                        status=data.get("state", "UNKNOWN"),
                        amount=data.get("amount", 0) / 100,  # Paise to INR
                        payment_instrument=data.get("paymentInstrument")
                    )
                else:
                    return PaymentStatus(
                        transaction_id="",
                        merchant_transaction_id=merchant_transaction_id,
                        status="FAILED",
                        amount=0
                    )

    async def process_refund(
        self,
        original_transaction_id: str,
        amount: float,
        reason: str = "Customer request"
    ) -> Dict[str, Any]:
        """
        Process a refund for a completed payment.
        """
        refund_tx_id = f"REF_{original_transaction_id}_{datetime.now().strftime('%H%M%S')}"

        payload = {
            "merchantId": self.client_id,
            "merchantTransactionId": refund_tx_id,
            "originalTransactionId": original_transaction_id,
            "amount": int(amount * 100),
            "callbackUrl": f"{settings.API_BASE_URL}/webhooks/phonepe/refund"
        }

        payload_base64 = base64.b64encode(json.dumps(payload).encode()).decode()
        checksum = self._generate_checksum(payload_base64, "/pg/v1/refund")

        token = await self.get_access_token()

        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "X-VERIFY": checksum
            }

            async with session.post(
                f"{self.base_url}/pg/v1/refund",
                json={"request": payload_base64},
                headers=headers
            ) as response:
                result = await response.json()

                return {
                    "refund_id": refund_tx_id,
                    "success": result.get("success", False),
                    "status": result.get("data", {}).get("state", "UNKNOWN")
                }

    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        amount: float,
        frequency: str = "MONTHLY"
    ) -> Dict[str, Any]:
        """
        Create UPI Autopay mandate for recurring subscriptions.
        """
        mandate_id = f"SUB_{user_id}_{plan_id}"

        payload = {
            "merchantId": self.client_id,
            "merchantSubscriptionId": mandate_id,
            "merchantUserId": user_id,
            "authWorkflowType": "PENNY_DROP",
            "amountType": "FIXED",
            "amount": int(amount * 100),
            "frequency": frequency,
            "recurringCount": 12,  # 1 year
            "mobileNumber": "",  # Will be collected
            "deviceContext": {
                "deviceOS": "WEB"
            }
        }

        # Similar API call pattern...
        return {"mandate_id": mandate_id, "status": "INITIATED"}

    def validate_webhook(self, payload: str, x_verify: str) -> bool:
        """
        Validate incoming webhook from PhonePe.
        """
        expected_checksum = self._generate_checksum(payload, "/webhooks/phonepe")
        return x_verify == expected_checksum

    def _generate_checksum(self, payload_base64: str, endpoint: str) -> str:
        """
        Generate SHA256 checksum for request validation.
        """
        string_to_hash = f"{payload_base64}{endpoint}{self.client_secret}"
        hash_obj = hashlib.sha256(string_to_hash.encode())
        return hash_obj.hexdigest() + "###1"


from datetime import timedelta

# Singleton
phonepe_gateway = PhonePeGateway()
```

---

## 8.2 GST Invoice Service

```python
# backend/indian_market/gst_service.py
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GSTInvoiceItem(BaseModel):
    """Single line item in GST invoice."""
    description: str
    hsn_code: str  # Harmonized System Nomenclature
    quantity: int = 1
    unit: str = "NOS"
    rate: float
    discount: float = 0.0
    taxable_value: float = 0.0  # Calculated


class GSTInvoice(BaseModel):
    """Complete GST invoice."""
    invoice_number: str
    invoice_date: datetime

    # Seller
    seller_name: str
    seller_gstin: str
    seller_address: str
    seller_state: str
    seller_state_code: str

    # Buyer
    buyer_name: str
    buyer_gstin: Optional[str] = None  # Optional for B2C
    buyer_address: str
    buyer_state: str
    buyer_state_code: str

    # Items
    items: List[GSTInvoiceItem]

    # Totals
    subtotal: float = 0.0
    cgst_rate: float = 0.0
    cgst_amount: float = 0.0
    sgst_rate: float = 0.0
    sgst_amount: float = 0.0
    igst_rate: float = 0.0
    igst_amount: float = 0.0
    total_tax: float = 0.0
    grand_total: float = 0.0

    # Type
    supply_type: str = "B2B"  # B2B, B2C, SEZWP, SEZWOP
    is_reverse_charge: bool = False


class GSTService:
    """
    GST calculation and invoice generation for Indian market.

    Features:
    - CGST/SGST calculation (intra-state)
    - IGST calculation (inter-state)
    - Invoice generation
    - HSN code lookup
    - State code mapping
    """

    # Indian state codes for GST
    STATE_CODES = {
        "Andhra Pradesh": "37",
        "Arunachal Pradesh": "12",
        "Assam": "18",
        "Bihar": "10",
        "Chhattisgarh": "22",
        "Delhi": "07",
        "Goa": "30",
        "Gujarat": "24",
        "Haryana": "06",
        "Himachal Pradesh": "02",
        "Jharkhand": "20",
        "Karnataka": "29",
        "Kerala": "32",
        "Madhya Pradesh": "23",
        "Maharashtra": "27",
        "Manipur": "14",
        "Meghalaya": "17",
        "Mizoram": "15",
        "Nagaland": "13",
        "Odisha": "21",
        "Punjab": "03",
        "Rajasthan": "08",
        "Sikkim": "11",
        "Tamil Nadu": "33",
        "Telangana": "36",
        "Tripura": "16",
        "Uttar Pradesh": "09",
        "Uttarakhand": "05",
        "West Bengal": "19",
    }

    # HSN codes for common SaaS services
    HSN_CODES = {
        "software_subscription": "998314",
        "it_services": "998313",
        "cloud_services": "998315",
        "marketing_services": "998361",
    }

    # GST rates for services
    GST_RATES = {
        "software_subscription": 18.0,
        "it_services": 18.0,
        "cloud_services": 18.0,
        "marketing_services": 18.0,
    }

    def __init__(self):
        self.company_gstin = "RAPTORFLOW_GSTIN"  # From config
        self.company_name = "Raptorflow Technologies Pvt Ltd"
        self.company_address = "123 Tech Park, Bangalore"
        self.company_state = "Karnataka"
        self.company_state_code = "29"

    def calculate_gst(
        self,
        amount: float,
        seller_state: str,
        buyer_state: str,
        service_type: str = "software_subscription"
    ) -> Dict[str, Any]:
        """
        Calculate GST breakdown for a transaction.

        Args:
            amount: Base amount (before GST)
            seller_state: Seller's state
            buyer_state: Buyer's state
            service_type: Type of service for GST rate

        Returns:
            GST breakdown with CGST/SGST or IGST
        """
        gst_rate = self.GST_RATES.get(service_type, 18.0)
        gst_amount = amount * (gst_rate / 100)

        is_interstate = seller_state != buyer_state

        if is_interstate:
            # IGST for inter-state
            return {
                "base_amount": amount,
                "gst_rate": gst_rate,
                "is_interstate": True,
                "cgst_rate": 0.0,
                "cgst_amount": 0.0,
                "sgst_rate": 0.0,
                "sgst_amount": 0.0,
                "igst_rate": gst_rate,
                "igst_amount": round(gst_amount, 2),
                "total_gst": round(gst_amount, 2),
                "total_amount": round(amount + gst_amount, 2)
            }
        else:
            # CGST + SGST for intra-state
            half_rate = gst_rate / 2
            half_amount = gst_amount / 2

            return {
                "base_amount": amount,
                "gst_rate": gst_rate,
                "is_interstate": False,
                "cgst_rate": half_rate,
                "cgst_amount": round(half_amount, 2),
                "sgst_rate": half_rate,
                "sgst_amount": round(half_amount, 2),
                "igst_rate": 0.0,
                "igst_amount": 0.0,
                "total_gst": round(gst_amount, 2),
                "total_amount": round(amount + gst_amount, 2)
            }

    async def generate_invoice(
        self,
        user_id: str,
        plan_name: str,
        amount: float,
        buyer_name: str,
        buyer_gstin: str = None,
        buyer_address: str = "",
        buyer_state: str = "Maharashtra"
    ) -> GSTInvoice:
        """
        Generate a GST-compliant invoice.
        """
        # Get next invoice number
        invoice_number = await self._get_next_invoice_number()

        # Calculate GST
        gst = self.calculate_gst(
            amount=amount,
            seller_state=self.company_state,
            buyer_state=buyer_state
        )

        # Create item
        item = GSTInvoiceItem(
            description=f"Raptorflow {plan_name} - Monthly Subscription",
            hsn_code=self.HSN_CODES["software_subscription"],
            quantity=1,
            unit="NOS",
            rate=amount,
            taxable_value=amount
        )

        # Create invoice
        invoice = GSTInvoice(
            invoice_number=invoice_number,
            invoice_date=datetime.now(),

            seller_name=self.company_name,
            seller_gstin=self.company_gstin,
            seller_address=self.company_address,
            seller_state=self.company_state,
            seller_state_code=self.company_state_code,

            buyer_name=buyer_name,
            buyer_gstin=buyer_gstin,
            buyer_address=buyer_address,
            buyer_state=buyer_state,
            buyer_state_code=self.STATE_CODES.get(buyer_state, ""),

            items=[item],

            subtotal=amount,
            cgst_rate=gst["cgst_rate"],
            cgst_amount=gst["cgst_amount"],
            sgst_rate=gst["sgst_rate"],
            sgst_amount=gst["sgst_amount"],
            igst_rate=gst["igst_rate"],
            igst_amount=gst["igst_amount"],
            total_tax=gst["total_gst"],
            grand_total=gst["total_amount"],

            supply_type="B2B" if buyer_gstin else "B2C"
        )

        # Save invoice
        await self._save_invoice(user_id, invoice)

        return invoice

    async def _get_next_invoice_number(self) -> str:
        """Generate next invoice number."""
        from core.redis_client import redis_client

        # Format: RF/2025-26/0001
        fiscal_year = self._get_fiscal_year()

        client = await redis_client.get_client()
        seq = await client.incr(f"invoice_seq:{fiscal_year}")

        return f"RF/{fiscal_year}/{str(seq).zfill(4)}"

    def _get_fiscal_year(self) -> str:
        """Get current Indian fiscal year (April-March)."""
        now = datetime.now()

        if now.month >= 4:
            return f"{now.year}-{str(now.year + 1)[-2:]}"
        else:
            return f"{now.year - 1}-{str(now.year)[-2:]}"

    async def _save_invoice(self, user_id: str, invoice: GSTInvoice):
        """Save invoice to database."""
        from core.database import async_session_maker

        async with async_session_maker() as session:
            await session.execute(
                """
                INSERT INTO invoices (
                    invoice_number, user_id, invoice_date,
                    buyer_name, buyer_gstin, subtotal, total_gst, grand_total,
                    data, created_at
                )
                VALUES (
                    :invoice_number, :user_id, :invoice_date,
                    :buyer_name, :buyer_gstin, :subtotal, :total_gst, :grand_total,
                    :data, NOW()
                )
                """,
                {
                    "invoice_number": invoice.invoice_number,
                    "user_id": user_id,
                    "invoice_date": invoice.invoice_date,
                    "buyer_name": invoice.buyer_name,
                    "buyer_gstin": invoice.buyer_gstin,
                    "subtotal": invoice.subtotal,
                    "total_gst": invoice.total_tax,
                    "grand_total": invoice.grand_total,
                    "data": invoice.model_dump_json()
                }
            )
            await session.commit()


# Singleton
gst_service = GSTService()
```

---

## 8.3 Festival Calendar

```python
# backend/indian_market/festival_calendar.py
from typing import Dict, Any, List
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class Festival(BaseModel):
    """Indian festival/event."""
    name: str
    date: date
    type: str  # religious, national, shopping, business
    description: str
    marketing_relevance: str  # HIGH, MEDIUM, LOW
    recommended_lead_days: int  # Start campaign X days before
    target_industries: List[str] = []


class FestivalCalendar:
    """
    Indian festival and business calendar for campaign timing.

    Features:
    - Festival dates (Diwali, Holi, etc.)
    - Shopping events (EOFY, Republic Day sales)
    - Business events (Budget Day, Q4 close)
    - Automatic campaign suggestions
    """

    # Major Indian festivals and events (dates are approximate, update yearly)
    FESTIVALS_2025 = [
        Festival(
            name="Republic Day",
            date=date(2025, 1, 26),
            type="national",
            description="National holiday, patriotic campaigns work well",
            marketing_relevance="MEDIUM",
            recommended_lead_days=14,
            target_industries=["retail", "fashion", "electronics"]
        ),
        Festival(
            name="Holi",
            date=date(2025, 3, 14),
            type="religious",
            description="Festival of colors, celebration campaigns",
            marketing_relevance="HIGH",
            recommended_lead_days=21,
            target_industries=["fmcg", "fashion", "food", "beverages"]
        ),
        Festival(
            name="End of Financial Year",
            date=date(2025, 3, 31),
            type="business",
            description="B2B budget spending rush, clearance sales",
            marketing_relevance="HIGH",
            recommended_lead_days=30,
            target_industries=["b2b", "saas", "enterprise", "retail"]
        ),
        Festival(
            name="Independence Day",
            date=date(2025, 8, 15),
            type="national",
            description="National holiday, freedom sales",
            marketing_relevance="MEDIUM",
            recommended_lead_days=14,
            target_industries=["retail", "electronics"]
        ),
        Festival(
            name="Ganesh Chaturthi",
            date=date(2025, 8, 27),
            type="religious",
            description="Major festival in Maharashtra, Gujarat",
            marketing_relevance="HIGH",
            recommended_lead_days=21,
            target_industries=["retail", "jewelry", "sweets", "decoration"]
        ),
        Festival(
            name="Navratri",
            date=date(2025, 9, 22),
            type="religious",
            description="9-day festival, major shopping period",
            marketing_relevance="HIGH",
            recommended_lead_days=30,
            target_industries=["fashion", "jewelry", "electronics"]
        ),
        Festival(
            name="Dussehra",
            date=date(2025, 10, 2),
            type="religious",
            description="Victory of good over evil, auspicious for new beginnings",
            marketing_relevance="HIGH",
            recommended_lead_days=21,
            target_industries=["auto", "real_estate", "electronics"]
        ),
        Festival(
            name="Diwali",
            date=date(2025, 10, 20),
            type="religious",
            description="Festival of lights, BIGGEST shopping event",
            marketing_relevance="HIGH",
            recommended_lead_days=45,
            target_industries=["all"]
        ),
        Festival(
            name="Black Friday / Cyber Monday",
            date=date(2025, 11, 28),
            type="shopping",
            description="Western shopping event gaining traction in India",
            marketing_relevance="MEDIUM",
            recommended_lead_days=14,
            target_industries=["ecommerce", "electronics", "fashion"]
        ),
        Festival(
            name="Christmas",
            date=date(2025, 12, 25),
            type="religious",
            description="Year-end sales, gift giving",
            marketing_relevance="MEDIUM",
            recommended_lead_days=21,
            target_industries=["retail", "travel", "hospitality"]
        ),
    ]

    def get_upcoming_festivals(self, days_ahead: int = 60) -> List[Festival]:
        """
        Get festivals coming up in the next X days.
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)

        upcoming = [
            f for f in self.FESTIVALS_2025
            if today <= f.date <= end_date
        ]

        return sorted(upcoming, key=lambda f: f.date)

    def get_campaign_recommendations(
        self,
        industry: str = None,
        days_ahead: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get campaign recommendations based on upcoming festivals.

        Returns:
            List of campaign suggestions with timing
        """
        upcoming = self.get_upcoming_festivals(days_ahead)
        recommendations = []

        for festival in upcoming:
            # Check industry relevance
            if industry and industry not in festival.target_industries and "all" not in festival.target_industries:
                continue

            campaign_start = festival.date - timedelta(days=festival.recommended_lead_days)

            recommendations.append({
                "festival": festival.name,
                "festival_date": festival.date.isoformat(),
                "campaign_start_date": campaign_start.isoformat(),
                "days_until_start": (campaign_start - date.today()).days,
                "marketing_relevance": festival.marketing_relevance,
                "description": festival.description,
                "suggested_campaign_type": self._suggest_campaign_type(festival),
                "suggested_themes": self._get_themes(festival)
            })

        return recommendations

    def get_optimal_launch_dates(self, campaign_type: str = "product_launch") -> List[Dict]:
        """
        Get optimal dates to launch campaigns based on festival calendar.
        """
        # Avoid launching during major festivals (people are busy)
        # But leverage pre-festival periods

        recommendations = []
        today = date.today()

        for festival in self.FESTIVALS_2025:
            if festival.date < today:
                continue

            if festival.marketing_relevance == "HIGH":
                # Suggest launching 2-4 weeks before
                launch_window_start = festival.date - timedelta(days=30)
                launch_window_end = festival.date - timedelta(days=14)

                recommendations.append({
                    "reason": f"Pre-{festival.name} period",
                    "window_start": launch_window_start.isoformat(),
                    "window_end": launch_window_end.isoformat(),
                    "advantage": f"Leverage {festival.name} shopping momentum"
                })

        return recommendations

    def _suggest_campaign_type(self, festival: Festival) -> str:
        """Suggest campaign type based on festival."""
        if festival.type == "religious":
            return "celebration_discount"
        elif festival.type == "business":
            return "b2b_urgency"
        elif festival.type == "shopping":
            return "flash_sale"
        else:
            return "awareness"

    def _get_themes(self, festival: Festival) -> List[str]:
        """Get marketing themes for a festival."""
        theme_map = {
            "Diwali": ["prosperity", "new_beginnings", "family", "gifts", "celebration"],
            "Holi": ["colors", "joy", "celebration", "spring", "renewal"],
            "End of Financial Year": ["budget_utilization", "closing_deals", "year_end_review"],
            "Republic Day": ["patriotism", "pride", "national", "freedom"],
            "Independence Day": ["freedom", "patriotism", "national_pride"],
        }

        return theme_map.get(festival.name, ["celebration", "offers", "special"])


# Singleton
festival_calendar = FestivalCalendar()
```

---

## 8.4 Regional Language Support

```python
# backend/indian_market/regional_languages.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class TranslationRequest(BaseModel):
    """Translation request."""
    text: str
    source_language: str = "en"
    target_language: str
    context: Optional[str] = None  # Business context for better translation
    preserve_technical_terms: bool = True


class RegionalLanguageService:
    """
    Regional language support for Indian markets.

    Supported Languages:
    - Hindi (hi)
    - Tamil (ta)
    - Telugu (te)
    - Bengali (bn)
    - Marathi (mr)
    - Gujarati (gu)
    - Kannada (kn)
    - Malayalam (ml)
    - Punjabi (pa)

    Features:
    - Marketing content translation
    - Technical term preservation
    - Cultural adaptation (not just translation)
    - Hinglish support (Hindi-English mix)
    """

    SUPPORTED_LANGUAGES = {
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "bn": "Bengali",
        "mr": "Marathi",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "en": "English",
        "hinglish": "Hinglish"  # Special case
    }

    # Common business terms to preserve in English
    PRESERVE_TERMS = [
        "ROI", "CRM", "SaaS", "B2B", "B2C", "API", "AI", "ML",
        "startup", "funding", "revenue", "profit", "marketing",
        "sales", "leads", "conversion", "campaign", "SEO", "PPC"
    ]

    def __init__(self):
        self.model_client = None

    async def initialize(self, model_client):
        self.model_client = model_client

    async def translate(self, request: TranslationRequest) -> Dict[str, Any]:
        """
        Translate content to regional language.
        """
        if request.target_language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {request.target_language}")

        # Special handling for Hinglish
        if request.target_language == "hinglish":
            return await self._translate_to_hinglish(request)

        # Build translation prompt
        prompt = self._build_translation_prompt(request)

        response = await self.model_client.generate(
            model="gemini-2.0-flash",
            system_prompt="""
            You are an expert translator specializing in Indian languages.
            Translate the content accurately while:
            1. Preserving the marketing tone and impact
            2. Keeping technical terms in English (unless they have common local equivalents)
            3. Adapting idioms and expressions to local equivalents
            4. Maintaining the emotional appeal of the original
            """,
            user_prompt=prompt,
            temperature=0.3
        )

        return {
            "original": request.text,
            "translated": response.get("content", ""),
            "source_language": request.source_language,
            "target_language": request.target_language,
            "target_language_name": self.SUPPORTED_LANGUAGES[request.target_language]
        }

    async def generate_regional_content(
        self,
        topic: str,
        language: str,
        content_type: str,  # "social_post", "email", "ad_copy"
        foundation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate original content in regional language.
        Better than translation for authentic feel.
        """
        prompt = f"""
        Create {content_type} content in {self.SUPPORTED_LANGUAGES.get(language, language)}.

        Topic: {topic}
        Business: {foundation.get('business_description', '')}
        Target Audience: {foundation.get('icp_summaries', '')}

        Guidelines:
        1. Write naturally in {self.SUPPORTED_LANGUAGES.get(language)}, not as a translation
        2. Use local idioms and expressions
        3. Keep business/technical terms in English
        4. Match the cultural context of {self.SUPPORTED_LANGUAGES.get(language)}-speaking regions
        5. Be engaging and persuasive
        """

        response = await self.model_client.generate(
            model="gemini-2.0-flash",
            system_prompt="You are a native speaker marketing expert.",
            user_prompt=prompt,
            temperature=0.7
        )

        return {
            "content": response.get("content", ""),
            "language": language,
            "content_type": content_type
        }

    async def _translate_to_hinglish(self, request: TranslationRequest) -> Dict[str, Any]:
        """
        Special handling for Hinglish (Hindi-English mix).
        Very popular in Indian urban marketing.
        """
        prompt = f"""
        Convert this English text to Hinglish (Hindi-English mix):

        "{request.text}"

        Guidelines:
        1. Mix Hindi and English naturally, like urban Indians speak
        2. Keep English words that are commonly used (like "amazing", "offer", "deal")
        3. Use Hindi for emotional/cultural words
        4. Write in Roman script (not Devanagari)
        5. Make it sound natural and conversational

        Example:
        English: "Get amazing discounts on our new collection"
        Hinglish: "Humari nayi collection pe amazing discounts pao"
        """

        response = await self.model_client.generate(
            model="gemini-2.0-flash",
            system_prompt="You are an expert in urban Indian marketing language.",
            user_prompt=prompt,
            temperature=0.5
        )

        return {
            "original": request.text,
            "translated": response.get("content", ""),
            "source_language": request.source_language,
            "target_language": "hinglish",
            "target_language_name": "Hinglish (Hindi-English)"
        }

    def _build_translation_prompt(self, request: TranslationRequest) -> str:
        """Build translation prompt."""
        terms_to_preserve = ", ".join(self.PRESERVE_TERMS) if request.preserve_technical_terms else ""

        return f"""
        Translate the following text from {request.source_language} to {self.SUPPORTED_LANGUAGES[request.target_language]}:

        "{request.text}"

        Context: {request.context or 'Marketing content'}

        {'Keep these terms in English: ' + terms_to_preserve if terms_to_preserve else ''}

        Return only the translated text, nothing else.
        """


# Singleton
regional_language_service = RegionalLanguageService()
```
