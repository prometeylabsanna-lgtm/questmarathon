from django.shortcuts import render


def home(request):
    """Landing page. Counter shows only paid participants; test value for now."""
    participants_count = 3057  # TODO: replace with UserProfile.objects.filter(payment_status="paid").count()
    context = {
        "counter_display": f"{participants_count:07d}",
    }
    return render(request, "pages/home.html", context)
