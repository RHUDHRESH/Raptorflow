# PAYMENTS INTEGRATION

> PhonePe Payment Gateway + GST Compliance

---

## 1. PAYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PAYMENT FLOW                                      │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   FRONTEND  │───▶│   BACKEND   │───▶│   PHONEPE   │───▶│   WEBHOOK   │  │
│  │             │    │             │    │             │    │             │  │
│  │ 1. Select   │    │ 2. Create   │    │ 3. Process  │    │ 4. Confirm  │  │
│  │    plan     │    │    payment  │    │    payment  │    │    status   │  │
│  │             │    │             │    │             │    │             │  │
│  │ 5. Redirect │◀───│ 6. Update   │◀───│             │◀───│             │  │
│  │    to app   │    │    status   │    │             │    │             │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PHONEPE SETUP (2025/2026 API)

### 2.1 Environment Configuration

```env
# PhonePe Credentials (Production)
PHONEPE_CLIENT_ID=your_client_id
PHONEPE_CLIENT_SECRET=your_client_secret
PHONEPE_MERCHANT_ID=MERCHANTXXXXXX
PHONEPE_ENVIRONMENT=production  # or 'sandbox'

# Webhook
PHONEPE_WEBHOOK_SECRET=your_webhook_secret

# Callback URLs
PHONEPE_REDIRECT_URL=https://app.raptorflow.com/billing/callback
PHONEPE_WEBHOOK_URL=https://api.raptorflow.com/api/v1/webhooks/phonepe
```

### 2.2 PhonePe Client

```python
# backend/payments/phonepe_client.py
import os
import httpx
import hashlib
import base64
import json
from datetime import datetime
from typing import Literal
import uuid

class PhonePeClient:
    """PhonePe Payment Gateway Client (2025/2026 API)."""

    def __init__(self):
        self.client_id = os.getenv("PHONEPE_CLIENT_ID")
        self.client_secret = os.getenv("PHONEPE_CLIENT_SECRET")
        self.merchant_id = os.getenv("PHONEPE_MERCHANT_ID")
        self.environment = os.getenv("PHONEPE_ENVIRONMENT", "sandbox")

        # API URLs
        if self.environment == "production":
            self.base_url = "https://api.phonepe.com/apis/hermes"
            self.auth_url = "https://api.phonepe.com/apis/identity-manager/v1/oauth/token"
        else:
            self.base_url = "https://api-preprod.phonepe.com/apis/pg-sandbox"
            self.auth_url = "https://api-preprod.phonepe.com/apis/identity-manager/v1/oauth/token"

        self._access_token = None
        self._token_expires_at = None

    async def _get_access_token(self) -> str:
        """Get OAuth access token."""
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.auth_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )

            if response.status_code != 200:
                raise Exception(f"Failed to get access token: {response.text}")

            data = response.json()
            self._access_token = data["access_token"]
            # Token usually valid for 1 hour, refresh 5 min before
            self._token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 300)

            return self._access_token

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict = None
    ) -> dict:
        """Make authenticated request to PhonePe."""
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{endpoint}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "X-MERCHANT-ID": self.merchant_id
                },
                json=data
            )

            return response.json()

    # ═══════════════════════════════════════════════════════════════════
    # PAYMENT INITIATION
    # ═══════════════════════════════════════════════════════════════════

    async def initiate_payment(
        self,
        amount_inr: float,
        user_id: str,
        order_type: str,  # subscription, top_up
        redirect_url: str,
        webhook_url: str,
        metadata: dict = None
    ) -> dict:
        """Initiate a payment."""

        # Generate unique transaction ID
        merchant_transaction_id = f"RF_{order_type}_{user_id[:8]}_{int(datetime.now().timestamp())}"

        # Amount in paise (INR * 100)
        amount_paise = int(amount_inr * 100)

        payload = {
            "merchantId": self.merchant_id,
            "merchantTransactionId": merchant_transaction_id,
            "amount": amount_paise,
            "redirectUrl": redirect_url,
            "redirectMode": "REDIRECT",
            "callbackUrl": webhook_url,
            "merchantUserId": user_id,
            "paymentInstrument": {
                "type": "PAY_PAGE"
            }
        }

        if metadata:
            payload["merchantOrderId"] = metadata.get("order_id", merchant_transaction_id)

        result = await self._make_request("POST", "/pg/v1/pay", payload)

        if result.get("success"):
            return {
                "success": True,
                "merchant_transaction_id": merchant_transaction_id,
                "payment_url": result["data"]["instrumentResponse"]["redirectInfo"]["url"],
                "phonepe_transaction_id": result.get("data", {}).get("transactionId")
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "Payment initiation failed"),
                "code": result.get("code")
            }

    # ═══════════════════════════════════════════════════════════════════
    # PAYMENT STATUS
    # ═══════════════════════════════════════════════════════════════════

    async def check_payment_status(
        self,
        merchant_transaction_id: str
    ) -> dict:
        """Check payment status."""

        result = await self._make_request(
            "GET",
            f"/pg/v1/status/{self.merchant_id}/{merchant_transaction_id}"
        )

        if result.get("success"):
            data = result.get("data", {})
            return {
                "success": True,
                "status": data.get("state"),  # COMPLETED, PENDING, FAILED
                "transaction_id": data.get("transactionId"),
                "amount": data.get("amount", 0) / 100,  # Convert from paise
                "payment_instrument": data.get("paymentInstrument", {})
            }
        else:
            return {
                "success": False,
                "status": "UNKNOWN",
                "error": result.get("message")
            }

    # ═══════════════════════════════════════════════════════════════════
    # REFUNDS
    # ═══════════════════════════════════════════════════════════════════

    async def initiate_refund(
        self,
        original_transaction_id: str,
        amount_inr: float,
        reason: str = "Customer request"
    ) -> dict:
        """Initiate a refund."""

        refund_id = f"REFUND_{int(datetime.now().timestamp())}"
        amount_paise = int(amount_inr * 100)

        payload = {
            "merchantId": self.merchant_id,
            "merchantTransactionId": refund_id,
            "originalTransactionId": original_transaction_id,
            "amount": amount_paise,
            "callbackUrl": os.getenv("PHONEPE_WEBHOOK_URL")
        }

        result = await self._make_request("POST", "/pg/v1/refund", payload)

        return {
            "success": result.get("success", False),
            "refund_id": refund_id,
            "status": result.get("data", {}).get("state"),
            "error": result.get("message") if not result.get("success") else None
        }

    # ═══════════════════════════════════════════════════════════════════
    # SUBSCRIPTION (UPI Mandate)
    # ═══════════════════════════════════════════════════════════════════

    async def create_subscription(
        self,
        user_id: str,
        plan: str,
        amount_inr: float,
        frequency: Literal["MONTHLY", "YEARLY"],
        redirect_url: str
    ) -> dict:
        """Create recurring subscription via UPI Mandate."""

        subscription_id = f"SUB_{user_id[:8]}_{int(datetime.now().timestamp())}"
        amount_paise = int(amount_inr * 100)

        # Calculate dates
        start_date = datetime.now()
        if frequency == "MONTHLY":
            end_date = start_date.replace(year=start_date.year + 1)
        else:
            end_date = start_date.replace(year=start_date.year + 5)

        payload = {
            "merchantId": self.merchant_id,
            "merchantSubscriptionId": subscription_id,
            "merchantUserId": user_id,
            "authWorkflowType": "PENNY_DROP",
            "amountType": "FIXED",
            "amount": amount_paise,
            "frequency": frequency,
            "recurringCount": 12 if frequency == "MONTHLY" else 5,
            "subscriptionStart": int(start_date.timestamp() * 1000),
            "subscriptionExpiry": int(end_date.timestamp() * 1000),
            "redirectUrl": redirect_url,
            "redirectMode": "REDIRECT"
        }

        result = await self._make_request("POST", "/pg/v1/subscription/create", payload)

        if result.get("success"):
            return {
                "success": True,
                "subscription_id": subscription_id,
                "mandate_url": result["data"]["instrumentResponse"]["redirectInfo"]["url"]
            }
        else:
            return {
                "success": False,
                "error": result.get("message")
            }

    # ═══════════════════════════════════════════════════════════════════
    # WEBHOOK VERIFICATION
    # ═══════════════════════════════════════════════════════════════════

    def verify_webhook(
        self,
        x_verify_header: str,
        response_body: str
    ) -> bool:
        """Verify webhook signature."""

        # PhonePe webhook verification
        # X-VERIFY = SHA256(response + "/pg/v1/status" + salt_key) + "###" + salt_index

        webhook_secret = os.getenv("PHONEPE_WEBHOOK_SECRET")

        # Extract salt index from header
        parts = x_verify_header.split("###")
        if len(parts) != 2:
            return False

        expected_hash, salt_index = parts

        # Compute hash
        string_to_hash = response_body + "/pg/v1/status" + webhook_secret
        computed_hash = hashlib.sha256(string_to_hash.encode()).hexdigest()

        return computed_hash == expected_hash


# Singleton
_phonepe_client: PhonePeClient | None = None

def get_phonepe_client() -> PhonePeClient:
    global _phonepe_client
    if _phonepe_client is None:
        _phonepe_client = PhonePeClient()
    return _phonepe_client
```

---

## 3. PAYMENT SERVICE

```python
# backend/payments/payment_service.py
from core.database import get_supabase_client
from payments.phonepe_client import get_phonepe_client
from datetime import datetime, timedelta
import os

# Subscription plans
PLANS = {
    "free": {
        "name": "Free",
        "price_inr": 0,
        "budget_usd": 1.00,
        "features": ["Basic features", "1 ICP", "10 moves/month"]
    },
    "starter": {
        "name": "Starter",
        "price_inr": 799,
        "budget_usd": 10.00,
        "features": ["All features", "3 ICPs", "Unlimited moves", "Priority support"]
    },
    "growth": {
        "name": "Growth",
        "price_inr": 2999,
        "budget_usd": 50.00,
        "features": ["All features", "Unlimited ICPs", "Advanced analytics", "API access"]
    },
    "enterprise": {
        "name": "Enterprise",
        "price_inr": 9999,
        "budget_usd": 200.00,
        "features": ["Everything", "Custom integrations", "Dedicated support", "SLA"]
    }
}

class PaymentService:
    """Payment and subscription management."""

    def __init__(self):
        self.phonepe = get_phonepe_client()
        self.supabase = get_supabase_client()

    # ═══════════════════════════════════════════════════════════════════
    # SUBSCRIPTION MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════

    async def get_plans(self) -> list[dict]:
        """Get available subscription plans."""
        return [
            {"id": plan_id, **plan_data}
            for plan_id, plan_data in PLANS.items()
        ]

    async def get_user_subscription(self, user_id: str) -> dict | None:
        """Get user's current subscription."""
        result = self.supabase.table("subscriptions").select("*").eq(
            "user_id", user_id
        ).single().execute()

        return result.data

    async def initiate_subscription(
        self,
        user_id: str,
        plan_id: str,
        billing_cycle: str = "monthly"
    ) -> dict:
        """Initiate subscription payment."""

        if plan_id not in PLANS:
            return {"success": False, "error": "Invalid plan"}

        plan = PLANS[plan_id]

        if plan["price_inr"] == 0:
            # Free plan - activate immediately
            return await self._activate_free_plan(user_id)

        # Calculate amount with GST
        base_amount = plan["price_inr"]
        if billing_cycle == "annual":
            base_amount = base_amount * 10  # 2 months free

        gst_amount = base_amount * 0.18
        total_amount = base_amount + gst_amount

        # Create payment record
        payment_id = self._create_payment_record(
            user_id=user_id,
            amount_inr=base_amount,
            gst_amount=gst_amount,
            total_amount=total_amount,
            payment_type="subscription",
            metadata={"plan": plan_id, "billing_cycle": billing_cycle}
        )

        # Initiate PhonePe payment
        result = await self.phonepe.initiate_payment(
            amount_inr=total_amount,
            user_id=user_id,
            order_type="subscription",
            redirect_url=f"{os.getenv('FRONTEND_URL')}/billing/callback?payment_id={payment_id}",
            webhook_url=f"{os.getenv('API_URL')}/api/v1/webhooks/phonepe",
            metadata={"payment_id": payment_id, "plan": plan_id}
        )

        if result["success"]:
            # Update payment record with PhonePe transaction ID
            self.supabase.table("payments").update({
                "phonepe_merchant_transaction_id": result["merchant_transaction_id"],
                "status": "processing"
            }).eq("id", payment_id).execute()

            return {
                "success": True,
                "payment_url": result["payment_url"],
                "payment_id": payment_id
            }
        else:
            # Mark payment as failed
            self.supabase.table("payments").update({
                "status": "failed"
            }).eq("id", payment_id).execute()

            return {"success": False, "error": result["error"]}

    async def _activate_free_plan(self, user_id: str) -> dict:
        """Activate free plan immediately."""

        # Check if user already has subscription
        existing = await self.get_user_subscription(user_id)

        if existing:
            # Update existing
            self.supabase.table("subscriptions").update({
                "plan": "free",
                "status": "active",
                "price_inr": 0,
                "current_period_start": datetime.now().isoformat(),
                "current_period_end": (datetime.now() + timedelta(days=365)).isoformat()
            }).eq("user_id", user_id).execute()
        else:
            # Create new
            self.supabase.table("subscriptions").insert({
                "user_id": user_id,
                "plan": "free",
                "status": "active",
                "price_inr": 0,
                "current_period_start": datetime.now().isoformat(),
                "current_period_end": (datetime.now() + timedelta(days=365)).isoformat()
            }).execute()

        # Update user budget
        self.supabase.table("users").update({
            "subscription_tier": "free",
            "budget_limit_monthly": PLANS["free"]["budget_usd"]
        }).eq("id", user_id).execute()

        return {"success": True, "plan": "free"}

    def _create_payment_record(
        self,
        user_id: str,
        amount_inr: float,
        gst_amount: float,
        total_amount: float,
        payment_type: str,
        metadata: dict
    ) -> str:
        """Create payment record in database."""
        import uuid

        payment_id = str(uuid.uuid4())

        self.supabase.table("payments").insert({
            "id": payment_id,
            "user_id": user_id,
            "amount_inr": amount_inr,
            "gst_amount": gst_amount,
            "total_amount": total_amount,
            "status": "pending",
            "metadata": metadata
        }).execute()

        return payment_id

    # ═══════════════════════════════════════════════════════════════════
    # WEBHOOK HANDLING
    # ═══════════════════════════════════════════════════════════════════

    async def handle_payment_webhook(
        self,
        merchant_transaction_id: str,
        status: str,
        transaction_id: str,
        amount: float,
        payment_instrument: dict
    ):
        """Handle PhonePe payment webhook."""

        # Find payment record
        result = self.supabase.table("payments").select("*").eq(
            "phonepe_merchant_transaction_id", merchant_transaction_id
        ).single().execute()

        if not result.data:
            raise ValueError(f"Payment not found: {merchant_transaction_id}")

        payment = result.data
        user_id = payment["user_id"]
        metadata = payment.get("metadata", {})

        if status == "COMPLETED":
            # Update payment status
            self.supabase.table("payments").update({
                "status": "completed",
                "phonepe_transaction_id": transaction_id,
                "payment_method": payment_instrument.get("type"),
                "payment_instrument": payment_instrument,
                "completed_at": datetime.now().isoformat()
            }).eq("id", payment["id"]).execute()

            # Activate subscription
            plan_id = metadata.get("plan", "starter")
            billing_cycle = metadata.get("billing_cycle", "monthly")

            await self._activate_paid_subscription(
                user_id=user_id,
                plan_id=plan_id,
                billing_cycle=billing_cycle,
                payment_id=payment["id"]
            )

        elif status == "FAILED":
            self.supabase.table("payments").update({
                "status": "failed"
            }).eq("id", payment["id"]).execute()

    async def _activate_paid_subscription(
        self,
        user_id: str,
        plan_id: str,
        billing_cycle: str,
        payment_id: str
    ):
        """Activate paid subscription after successful payment."""

        plan = PLANS[plan_id]

        # Calculate period
        now = datetime.now()
        if billing_cycle == "monthly":
            period_end = now + timedelta(days=30)
        else:
            period_end = now + timedelta(days=365)

        # Update or create subscription
        existing = await self.get_user_subscription(user_id)

        subscription_data = {
            "plan": plan_id,
            "status": "active",
            "price_inr": plan["price_inr"],
            "billing_cycle": billing_cycle,
            "current_period_start": now.isoformat(),
            "current_period_end": period_end.isoformat()
        }

        if existing:
            self.supabase.table("subscriptions").update(
                subscription_data
            ).eq("user_id", user_id).execute()
        else:
            self.supabase.table("subscriptions").insert({
                "user_id": user_id,
                **subscription_data
            }).execute()

        # Update user budget
        self.supabase.table("users").update({
            "subscription_tier": plan_id,
            "budget_limit_monthly": plan["budget_usd"]
        }).eq("id", user_id).execute()

        # Link payment to subscription
        self.supabase.table("payments").update({
            "subscription_id": existing["id"] if existing else None
        }).eq("id", payment_id).execute()
```

---

## 4. GST INVOICE SERVICE

```python
# backend/payments/gst_service.py
from datetime import datetime
from decimal import Decimal

class GSTService:
    """GST calculation and invoice generation."""

    GST_RATE = Decimal("0.18")  # 18% GST

    # State codes for GST
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
        "Jammu and Kashmir": "01",
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
        "West Bengal": "19"
    }

    # Company details (seller)
    COMPANY_GSTIN = os.getenv("COMPANY_GSTIN", "29AABCU9603R1ZM")
    COMPANY_NAME = "Raptorflow Technologies Pvt Ltd"
    COMPANY_ADDRESS = "123 Tech Park, Bangalore, Karnataka 560001"
    COMPANY_STATE = "Karnataka"

    def calculate_gst(
        self,
        base_amount: Decimal,
        buyer_state: str
    ) -> dict:
        """Calculate GST based on buyer location."""

        seller_state = self.COMPANY_STATE

        if buyer_state == seller_state:
            # Intra-state: CGST + SGST (9% each)
            cgst = base_amount * (self.GST_RATE / 2)
            sgst = base_amount * (self.GST_RATE / 2)
            igst = Decimal("0")
            gst_type = "INTRA"
        else:
            # Inter-state: IGST (18%)
            cgst = Decimal("0")
            sgst = Decimal("0")
            igst = base_amount * self.GST_RATE
            gst_type = "INTER"

        total_gst = cgst + sgst + igst
        total_amount = base_amount + total_gst

        return {
            "base_amount": float(base_amount),
            "cgst": float(cgst),
            "sgst": float(sgst),
            "igst": float(igst),
            "total_gst": float(total_gst),
            "total_amount": float(total_amount),
            "gst_type": gst_type,
            "gst_rate": float(self.GST_RATE * 100)
        }

    def generate_invoice(
        self,
        payment: dict,
        user: dict,
        buyer_details: dict
    ) -> dict:
        """Generate GST-compliant invoice."""

        invoice_number = self._generate_invoice_number()
        invoice_date = datetime.now()

        # Calculate GST
        base_amount = Decimal(str(payment["amount_inr"]))
        buyer_state = buyer_details.get("state", "Karnataka")
        gst_calc = self.calculate_gst(base_amount, buyer_state)

        invoice = {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date.isoformat(),

            # Seller details
            "seller": {
                "name": self.COMPANY_NAME,
                "gstin": self.COMPANY_GSTIN,
                "address": self.COMPANY_ADDRESS,
                "state": self.COMPANY_STATE,
                "state_code": self.STATE_CODES.get(self.COMPANY_STATE, "29")
            },

            # Buyer details
            "buyer": {
                "name": buyer_details.get("name", user.get("full_name", "")),
                "gstin": buyer_details.get("gstin"),  # Optional for B2C
                "address": buyer_details.get("address", ""),
                "state": buyer_state,
                "state_code": self.STATE_CODES.get(buyer_state, ""),
                "email": user.get("email")
            },

            # Line items
            "items": [
                {
                    "description": payment.get("metadata", {}).get("plan", "Subscription"),
                    "hsn_code": "998431",  # Software services
                    "quantity": 1,
                    "unit_price": float(base_amount),
                    "amount": float(base_amount)
                }
            ],

            # Totals
            "subtotal": float(base_amount),
            **gst_calc,

            # Payment details
            "payment_id": payment.get("id"),
            "transaction_id": payment.get("phonepe_transaction_id"),
            "payment_method": payment.get("payment_method", "UPI"),

            # Status
            "status": "paid"
        }

        return invoice

    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number."""
        now = datetime.now()
        # Format: RF/2025-26/0001
        fiscal_year = self._get_fiscal_year(now)

        # Get next sequence from database
        # This should be a proper sequence in production
        import uuid
        seq = str(uuid.uuid4())[:8].upper()

        return f"RF/{fiscal_year}/{seq}"

    def _get_fiscal_year(self, date: datetime) -> str:
        """Get Indian fiscal year (Apr-Mar)."""
        if date.month >= 4:
            return f"{date.year}-{str(date.year + 1)[-2:]}"
        else:
            return f"{date.year - 1}-{str(date.year)[-2:]}"
```

---

## 5. API ENDPOINTS

```python
# backend/api/v1/billing.py
from fastapi import APIRouter, Depends, HTTPException, Request
from core.auth import get_current_user, AuthenticatedUser
from payments.payment_service import PaymentService
from payments.phonepe_client import get_phonepe_client
from pydantic import BaseModel

router = APIRouter()

class SubscriptionRequest(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"

class TopUpRequest(BaseModel):
    amount_usd: float

# ═══════════════════════════════════════════════════════════════════
# PLANS
# ═══════════════════════════════════════════════════════════════════

@router.get("/plans")
async def get_plans():
    """Get available subscription plans."""
    service = PaymentService()
    return {"plans": await service.get_plans()}

# ═══════════════════════════════════════════════════════════════════
# SUBSCRIPTION
# ═══════════════════════════════════════════════════════════════════

@router.get("/subscription")
async def get_subscription(user: AuthenticatedUser = Depends(get_current_user)):
    """Get user's current subscription."""
    service = PaymentService()
    subscription = await service.get_user_subscription(user.id)

    if not subscription:
        return {"subscription": None, "plan": "free"}

    return {"subscription": subscription}

@router.post("/subscription")
async def create_subscription(
    request: SubscriptionRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Initiate subscription payment."""
    service = PaymentService()
    result = await service.initiate_subscription(
        user_id=user.id,
        plan_id=request.plan_id,
        billing_cycle=request.billing_cycle
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@router.post("/subscription/cancel")
async def cancel_subscription(user: AuthenticatedUser = Depends(get_current_user)):
    """Cancel subscription."""
    service = PaymentService()
    # Implement cancellation logic
    pass

# ═══════════════════════════════════════════════════════════════════
# USAGE
# ═══════════════════════════════════════════════════════════════════

@router.get("/usage")
async def get_usage(user: AuthenticatedUser = Depends(get_current_user)):
    """Get usage summary."""
    from services.usage_tracker import UsageTracker

    tracker = UsageTracker()
    daily = await tracker.get_daily_usage(user.id)
    monthly = await tracker.get_monthly_usage(user.id)
    budget = await tracker.check_budget(user.id, 0)

    return {
        "daily": daily,
        "monthly": monthly,
        "budget": {
            "limit": budget["budget_limit"],
            "used": budget["current_usage"],
            "remaining": budget["remaining"]
        }
    }

# ═══════════════════════════════════════════════════════════════════
# INVOICES
# ═══════════════════════════════════════════════════════════════════

@router.get("/invoices")
async def get_invoices(user: AuthenticatedUser = Depends(get_current_user)):
    """Get user's invoices."""
    from core.database import get_supabase_client

    supabase = get_supabase_client()
    result = supabase.table("payments").select("*").eq(
        "user_id", user.id
    ).eq("status", "completed").order("created_at", desc=True).execute()

    return {"invoices": result.data}

@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Get specific invoice."""
    from core.database import get_supabase_client
    from payments.gst_service import GSTService

    supabase = get_supabase_client()

    # Get payment
    payment = supabase.table("payments").select("*").eq(
        "id", invoice_id
    ).eq("user_id", user.id).single().execute()

    if not payment.data:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Get user details
    user_data = supabase.table("users").select("*").eq(
        "id", user.id
    ).single().execute()

    # Generate invoice
    gst_service = GSTService()
    invoice = gst_service.generate_invoice(
        payment=payment.data,
        user=user_data.data,
        buyer_details={}  # Would come from user profile
    )

    return {"invoice": invoice}

# ═══════════════════════════════════════════════════════════════════
# WEBHOOK
# ═══════════════════════════════════════════════════════════════════

@router.post("/webhooks/phonepe")
async def phonepe_webhook(request: Request):
    """Handle PhonePe webhook."""

    # Get headers
    x_verify = request.headers.get("X-VERIFY")

    # Get body
    body = await request.body()
    body_str = body.decode()

    # Verify signature
    phonepe = get_phonepe_client()
    if not phonepe.verify_webhook(x_verify, body_str):
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Parse payload
    import json
    import base64

    payload = json.loads(body_str)
    response_data = json.loads(base64.b64decode(payload["response"]).decode())

    # Handle payment
    service = PaymentService()
    await service.handle_payment_webhook(
        merchant_transaction_id=response_data["merchantTransactionId"],
        status=response_data["code"],  # PAYMENT_SUCCESS, PAYMENT_ERROR, etc.
        transaction_id=response_data.get("transactionId"),
        amount=response_data.get("amount", 0) / 100,
        payment_instrument=response_data.get("paymentInstrument", {})
    )

    return {"status": "ok"}
```

---

## 6. FRONTEND INTEGRATION

```typescript
// frontend/src/lib/billing.ts
import { api } from './api'

export interface Plan {
  id: string
  name: string
  price_inr: number
  budget_usd: number
  features: string[]
}

export interface Subscription {
  id: string
  plan: string
  status: string
  price_inr: number
  billing_cycle: string
  current_period_end: string
}

export const billing = {
  async getPlans(): Promise<Plan[]> {
    const { plans } = await api.get<{ plans: Plan[] }>('/api/v1/billing/plans')
    return plans
  },

  async getSubscription(): Promise<Subscription | null> {
    const { subscription } = await api.get<{ subscription: Subscription | null }>(
      '/api/v1/billing/subscription'
    )
    return subscription
  },

  async subscribe(planId: string, billingCycle: 'monthly' | 'annual' = 'monthly') {
    const result = await api.post<{ success: boolean; payment_url?: string }>(
      '/api/v1/billing/subscription',
      { plan_id: planId, billing_cycle: billingCycle }
    )

    if (result.success && result.payment_url) {
      // Redirect to PhonePe
      window.location.href = result.payment_url
    }

    return result
  },

  async getUsage() {
    return api.get('/api/v1/billing/usage')
  },

  async getInvoices() {
    const { invoices } = await api.get<{ invoices: any[] }>('/api/v1/billing/invoices')
    return invoices
  }
}
```
