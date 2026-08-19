import logging
import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from src.accounts.models import UserProfile
from src.payments.models import Payment
from src.payments.services.liqpay import get_liqpay_service, liqpay_configured

logger = logging.getLogger(__name__)


def _get_profile(user) -> UserProfile:
    profile, _created = UserProfile.objects.get_or_create(
        user=user,
        defaults={"full_name": user.get_username(), "phone": ""},
    )
    return profile


@login_required
@require_http_methods(["GET", "POST"])
def payment_start(request):
    profile = _get_profile(request.user)
    if profile.is_paid:
        return redirect("quest:room", n=1)

    if request.method == "POST" and request.POST.get("action") == "dev_bypass":
        if settings.DEBUG and settings.PAYMENTS_DEV_BYPASS:
            with transaction.atomic():
                Payment.objects.create(
                    user=request.user,
                    order_id=f"dev-{uuid.uuid4().hex[:12]}",
                    amount=Decimal(str(settings.QUEST_PRICE)),
                    currency=settings.QUEST_CURRENCY,
                    status=Payment.Status.SANDBOX,
                    raw_payload={"source": "dev_bypass"},
                )
                profile.mark_paid()
            return redirect("quest:room", n=1)
        return redirect("accounts:cabinet")

    if not liqpay_configured():
        return render(
            request,
            "payments/start.html",
            {
                "page_title": _("Оплата"),
                "profile": profile,
                "not_configured": True,
                "dev_bypass": settings.DEBUG and settings.PAYMENTS_DEV_BYPASS,
            },
        )

    order_id = f"qm-{request.user.pk}-{uuid.uuid4().hex[:10]}"
    payment = Payment.objects.create(
        user=request.user,
        order_id=order_id,
        amount=Decimal(str(settings.QUEST_PRICE)),
        currency=settings.QUEST_CURRENCY,
        status=Payment.Status.PENDING,
    )
    profile.payment_status = UserProfile.PaymentStatus.PENDING
    profile.save(update_fields=["payment_status", "updated_at"])

    liqpay = get_liqpay_service()
    result_url = settings.LIQPAY_RESULT_URL or request.build_absolute_uri(
        reverse("payments:return")
    )
    server_url = settings.LIQPAY_SERVER_URL or request.build_absolute_uri(
        reverse("payments_api:webhook_liqpay")
    )
    form_data = liqpay.create_checkout_data(
        order_id=payment.order_id,
        amount=float(payment.amount),
        description="Квест-марафон — участь",
        result_url=result_url,
        server_url=server_url,
        currency=payment.currency,
    )
    return render(
        request,
        "payments/checkout.html",
        {
            "page_title": _("Оплата"),
            "profile": profile,
            "payment": payment,
            "liqpay_data": form_data["data"],
            "liqpay_signature": form_data["signature"],
            "liqpay_checkout_url": form_data["checkout_url"],
        },
    )


@login_required
def payment_return(request):
    profile = _get_profile(request.user)
    return render(
        request,
        "payments/return.html",
        {
            "page_title": _("Статус оплати"),
            "profile": profile,
        },
    )


@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook_liqpay(request):
    data_b64 = request.POST.get("data", "")
    signature = request.POST.get("signature", "")
    if not data_b64 or not signature:
        return HttpResponse("Bad request", status=400)

    liqpay = get_liqpay_service()
    if liqpay is None:
        logger.error("LiqPay webhook received but keys are not configured")
        return HttpResponse("Not configured", status=503)

    if not liqpay.verify_callback(data_b64, signature):
        return HttpResponse("Invalid signature", status=403)

    payload = liqpay.decode_data(data_b64)
    order_id = payload.get("order_id", "")
    status = payload.get("status", "")
    payment_id = str(payload.get("payment_id", "") or "")

    if not order_id:
        return HttpResponse("Missing order_id", status=400)

    success_statuses = {"success", "sandbox", "wait_accept"}
    idem_key = f"liqpay_{payment_id}_{status}" if payment_id else None

    try:
        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(order_id=order_id)
            if idem_key and Payment.objects.filter(idempotency_key=idem_key).exists():
                return HttpResponse("OK")
            if payment.status == Payment.Status.SUCCESS:
                return HttpResponse("OK")

            payment.raw_payload = payload
            payment.external_id = payment_id
            if idem_key:
                payment.idempotency_key = idem_key

            if status in success_statuses:
                payment.status = Payment.Status.SUCCESS
                payment.save()
                profile = UserProfile.objects.select_for_update().get(user=payment.user)
                profile.mark_paid()
            else:
                payment.status = Payment.Status.FAILURE
                payment.save()
    except Payment.DoesNotExist:
        logger.warning("LiqPay webhook unknown order_id=%s", order_id)
        return HttpResponse("Unknown order", status=404)

    return HttpResponse("OK")
