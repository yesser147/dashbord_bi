# django_app/production/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Avg, F, FloatField
from django.db.models.functions import Coalesce
from django.views.decorators.http import require_GET
from .models import (
    ProductionCropsLivestock,
    ProducerPrices,
    FertilizersByProduct,
    LandUse,
    EmploymentAgriculture,
    ForeignDirectInvestmentAgriculture,
)

def dashboard(request):

    # options pour filtres initiaux (utiles dans templates)
    countries = list(ProductionCropsLivestock.objects.values_list('country', flat=True).distinct().order_by('country'))
    products = list(ProductionCropsLivestock.objects.values_list('product', flat=True).distinct().order_by('product'))
    years = list(ProductionCropsLivestock.objects.values_list('year', flat=True).distinct().order_by('year'))
    fertilizer_types = list(FertilizersByProduct.objects.values_list('fertilizer_type', flat=True).distinct().order_by('fertilizer_type'))
    context = {
        "countries": countries,
        "products": products,
        "years": years,
        "fertilizer_types": fertilizer_types,
    }
    # === DEFAULT VALUES ===
    default_country = "Tunisia"
    default_product = "Wheat"
    default_year = "2020"
    default_fertilizer = "Nitrogen"

    # === GLOBAL FILTERS WITH DEFAULTS ===
    country = request.GET.get("country", default_country)
    product = request.GET.get("product", default_product)
    year = request.GET.get("year", default_year)
    fertilizer = request.GET.get("fertilizer", default_fertilizer)

    return render(request, "dashboard.html", context)

def to_float_safe(v):
    try:
        return float(v) if v is not None else 0.0
    except:
        return 0.0

# --------------------------
# 1. Production & Rendement
# --------------------------

@require_GET
def api_production_timeseries(request):
    product = request.GET.get("product")
    country = request.GET.get("country")
    qs = ProductionCropsLivestock.objects.all()
    if product:
        qs = qs.filter(product=product)
    if country:
        qs = qs.filter(country=country)
    qs = qs.values('year').annotate(total=Coalesce(Sum('production_quantity'), 0.0)).order_by('year')
    data = [{"year": r['year'], "value": to_float_safe(r['total'])} for r in qs]
    return JsonResponse(data, safe=False)

@require_GET
def api_top_producers(request):
    product = request.GET.get("product")
    year = request.GET.get("year")
    n = int(request.GET.get("n", 10))
    if not product or not year:
        return JsonResponse({"error": "product and year required"}, status=400)
    qs = (ProductionCropsLivestock.objects
          .filter(product=product, year=year)
          .values('country')
          .annotate(total=Coalesce(Sum('production_quantity'), 0.0))
          .order_by('-total')[:n])
    data = [{"country": r['country'], "value": to_float_safe(r['total'])} for r in qs]
    return JsonResponse(data, safe=False)

@require_GET
def api_production_vs_price(request):
    product = request.GET.get("product")
    country = request.GET.get("country")
    year = request.GET.get("year")
    if not product:
        return JsonResponse({"error":"product required"}, status=400)

    prod_qs = ProductionCropsLivestock.objects.filter(product=product)
    if country:
        prod_qs = prod_qs.filter(country=country)
    if year:
        prod_qs = prod_qs.filter(year=year)
    prod_qs = prod_qs.values('country','year').annotate(prod_total=Coalesce(Sum('production_quantity'),0.0))

    price_qs = ProducerPrices.objects.filter(product=product)
    if country:
        price_qs = price_qs.filter(country=country)
    if year:
        price_qs = price_qs.filter(year=year)
    price_qs = price_qs.values('country','year').annotate(price_avg=Coalesce(Avg('price'),0.0))

    # join by (country,year)
    price_map = {(r['country'], r['year']): to_float_safe(r['price_avg']) for r in price_qs}
    out = []
    for r in prod_qs:
        key = (r['country'], r['year'])
        price = price_map.get(key)
        if price is not None:
            out.append({
                "country": r['country'],
                "year": r['year'],
                "production_quantity": to_float_safe(r['prod_total']),
                "price": price
            })
    return JsonResponse(out, safe=False)

@require_GET
def api_fertilizer_vs_production(request):
    product = request.GET.get("product")
    country = request.GET.get("country")
    fertilizer_type = request.GET.get("fertilizer_type")
    if not product:
        return JsonResponse({"error":"product required"}, status=400)
    prod_qs = ProductionCropsLivestock.objects.filter(product=product)
    fert_qs = FertilizersByProduct.objects.filter(country__isnull=False)
    if country:
        prod_qs = prod_qs.filter(country=country)
        fert_qs = fert_qs.filter(country=country)
    if fertilizer_type:
        fert_qs = fert_qs.filter(fertilizer_type=fertilizer_type)

    prod_agg = prod_qs.values('year').annotate(prod_total=Coalesce(Sum('production_quantity'),0.0)).order_by('year')
    fert_agg = fert_qs.values('year').annotate(fert_total=Coalesce(Sum('quantity'),0.0)).order_by('year')
    years = sorted({r['year'] for r in list(prod_agg) + list(fert_agg)})
    prod_map = {r['year']: to_float_safe(r['prod_total']) for r in prod_agg}
    fert_map = {r['year']: to_float_safe(r['fert_total']) for r in fert_agg}
    production = [prod_map.get(y,0.0) for y in years]
    fertilizer = [fert_map.get(y,0.0) for y in years]
    return JsonResponse({"years": years, "production": production, "fertilizer": fertilizer}, safe=False)

# --------------------------
# 2. Prix & Économie
# --------------------------
@require_GET
def api_price_timeseries(request):
    product = request.GET.get("product")
    country = request.GET.get("country")
    if not product:
        return JsonResponse({"error":"product required"}, status=400)
    qs = ProducerPrices.objects.filter(product=product)
    if country:
        qs = qs.filter(country=country)
    qs = qs.values('year').annotate(avg_price=Coalesce(Avg('price'),0.0)).order_by('year')
    data = [{"year": r['year'], "value": to_float_safe(r['avg_price'])} for r in qs]
    return JsonResponse(data, safe=False)

@require_GET
def api_price_by_country(request):
    product = request.GET.get("product")
    year = request.GET.get("year")
    if not product or not year:
        return JsonResponse({"error":"product and year required"}, status=400)
    qs = (ProducerPrices.objects
          .filter(product=product, year=year)
          .values('country')
          .annotate(avg_price=Coalesce(Avg('price'),0.0)))
    data = [{"country": r['country'], "value": to_float_safe(r['avg_price'])} for r in qs]
    return JsonResponse(data, safe=False)

@require_GET
def api_fdi_stacked(request):
    year = request.GET.get("year")
    if not year:
        return JsonResponse({"error":"year required"}, status=400)
    qs = (ForeignDirectInvestmentAgriculture.objects
          .filter(year=year)
          .values('receiving_country','investing_country')
          .annotate(total=Coalesce(Sum('investment_amount'),0.0)))
    receiving = sorted({r['receiving_country'] for r in qs})
    investing = sorted({r['investing_country'] for r in qs})
    recv_index = {c:i for i,c in enumerate(receiving)}
    matrix = {inv:[0.0 for _ in receiving] for inv in investing}
    for r in qs:
        i = recv_index[r['receiving_country']]
        matrix[r['investing_country']][i] = to_float_safe(r['total'])
    return JsonResponse({"receiving": receiving, "investing": investing, "matrix": matrix}, safe=False)

@require_GET
def api_price_boxplot(request):
    product = request.GET.get("product")
    country = request.GET.get("country")
    if not product:
        return JsonResponse({"error":"product required"}, status=400)
    qs = ProducerPrices.objects.filter(product=product)
    if country:
        qs = qs.filter(country=country)
    groups = {}
    for r in qs.values('country','price'):
        c = r['country'] or 'Unknown'
        groups.setdefault(c, []).append(to_float_safe(r['price']))
    out = [{"country": c, "values": vals} for c, vals in groups.items()]
    return JsonResponse(out, safe=False)

# --------------------------
# 3. Ressources & Main-d'oeuvre
# --------------------------
@require_GET
def api_land_share(request):
    country = request.GET.get("country")
    year = request.GET.get("year")
    if not country or not year:
        return JsonResponse({"error":"country and year required"}, status=400)
    qs = LandUse.objects.filter(country=country, year=year).values('land_area_agricultural','land_area_total')
    if not qs:
        return JsonResponse({"country":country,"year":year,"share_pct":0.0})
    r = qs[0]
    ag = to_float_safe(r.get('land_area_agricultural'))
    total = to_float_safe(r.get('land_area_total'))
    share = (ag/total*100.0) if total else 0.0
    return JsonResponse({"country":country,"year":int(year),"share_pct":share}, safe=False)

@require_GET
def api_employment_timeseries(request):
    country = request.GET.get("country")
    if not country:
        return JsonResponse({"error":"country required"}, status=400)
    qs = (EmploymentAgriculture.objects
          .filter(country=country)
          .values('year')
          .annotate(total=Coalesce(Sum('employment_agriculture'),0.0))
          .order_by('year'))
    data = [{"year": r['year'], "value": to_float_safe(r['total'])} for r in qs]
    return JsonResponse(data, safe=False)

@require_GET
def api_employment_vs_production(request):
    country = request.GET.get("country")
    year = request.GET.get("year")
    product = request.GET.get("product")
    if not country:
        return JsonResponse({"error":"country required"}, status=400)
    emp_qs = EmploymentAgriculture.objects.filter(country=country)
    if year:
        emp_qs = emp_qs.filter(year=year)
    emp_map = {r['year']: to_float_safe(r['employment_agriculture']) for r in emp_qs.values('year','employment_agriculture')}
    prod_qs = ProductionCropsLivestock.objects.filter(country=country)
    if product:
        prod_qs = prod_qs.filter(product=product)
    if year:
        prod_qs = prod_qs.filter(year=year)
    prod_map = {}
    for r in prod_qs.values('year').annotate(total=Coalesce(Sum('production_quantity'),0.0)):
        prod_map[r['year']] = to_float_safe(r['total'])
    years = sorted(set(list(emp_map.keys()) + list(prod_map.keys())))
    out = [{"year": y, "employment": emp_map.get(y,0.0), "production": prod_map.get(y,0.0)} for y in years]
    return JsonResponse(out, safe=False)
