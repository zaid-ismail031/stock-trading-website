import json
import urllib.request

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.core.exceptions import ObjectDoesNotExist

from .models import Account, Stocks, Open, Closed


# __________________________________ACCOUNT FUNCTIONALITY______________________________________________
# Login functionality
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "shares/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "shares/login.html")


# Logout functionality
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Register functionality
def register(request):
    if request.method == "POST":

        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        if email is None or password is None or first_name is None or last_name is None:
            return render(request, "network/register.html", {
                "message": "Please fill in all fields."
            })

        if password != confirmation:
            return render(request, "shares/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = get_user_model().objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "shares/register.html")


# __________________________________HTML PAGES______________________________________________
# Home page
def index(request):
    return render(request, "shares/index.html")


# Stock page
@login_required
def stocks(request):
    stocks_queryset = Stocks.objects.all()
    return render(request, "shares/stocks.html", {
        "stocks": stocks_queryset
    })


# News page
@login_required
def news(request):
    return render(request, "shares/news.html")


# Stockinfo page
@login_required
def stockinfo(request, symbol):
    stock = Stocks.objects.get(stock_symbol=symbol.upper())
    return render(request, "shares/stockinfo.html", {
        "stock": stock
    })


# Open positions page
@login_required
def openPage(request):
    try:
        openPositions = Open.objects.filter(user=request.user)
        return render(request, "shares/open.html", {
            "hasOpen": True,
            "openPositions": openPositions
        })
    except ObjectDoesNotExist:
        return render(request, "shares/open.html", {
            "hasOpen": False
        })

# Closed positions page
@login_required
def closePage(request):
    try:
        closePositions = Closed.objects.filter(user=request.user)
        return render(request, "shares/close.html", {
            "hasClose": True,
            "closePositions": closePositions
        })
    except ObjectDoesNotExist:
        return render(request, "shares/close.html", {
            "hasClose": False
        })

# __________________________________API's______________________________________________

# Purchase shares API
@login_required
@csrf_exempt
def open(request):

    if request.method != 'POST':
        return JsonResponse({"error": "POST request required"})

    data = json.loads(request.body)
    symbol = data.get("symbol", "")
    numberShares = data.get("numberShares", "")

    try:
        Stocks.objects.get(stock_symbol=symbol)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Invalid stock"})

    with urllib.request.urlopen(f'https://sandbox.iexapis.com/stable/stock/{symbol}/batch?types=quote,news,chart&range=1m&last=10&token=Tsk_0a2e18ad710242d5acfb84a17190da50') as url:
        purchaser = Account.objects.get(id=request.user.id)
        data = json.loads(url.read().decode())
        price = float(data['quote']['latestPrice'])
        totalprice = price * float(numberShares)
        userMoney = float(purchaser.money)

        if totalprice > userMoney:
            return JsonResponse({"error": "You do not have the funds to complete this trade."})

        updatedUserMoney = userMoney - totalprice
        purchaser.money = updatedUserMoney
        purchaser.save()

        try:
            openPosition = Open.objects.get(user=request.user, stock_symbol=symbol)
            updatePrice = float(openPosition.position) + totalprice
            updateShares = float(openPosition.shares) + float(numberShares)
            openPosition.position = updatePrice
            openPosition.shares = updateShares

            openPosition.save()
        except ObjectDoesNotExist:
            userOpen = Open(
                user=request.user,
                stock_symbol=symbol,
                shares=numberShares,
                position=totalprice
            )

            userOpen.save()

    return JsonResponse({"success": "Purchase successful",
                         "paid": f"{totalprice}",
                         "updatedAccount": round(updatedUserMoney, 2)
                         })


# CLOSE POSITION API
@login_required
@csrf_exempt
def close(request):

    if request.method != 'POST':
        return JsonResponse({"error": "POST request required"})

    data = json.loads(request.body)
    symbol = data.get("symbol", "")

    try:
        Stocks.objects.get(stock_symbol=symbol)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Invalid stock"})

    try:
        openPosition = Open.objects.get(user=request.user, stock_symbol=symbol)
        with urllib.request.urlopen(f'https://cloud.iexapis.com/stable/stock/{symbol}/batch?types=quote,news,chart&range=1m&last=10&token=pk_c1b5f3ef041241d595d3b69659efcb5b') as url:
            purchaser = Account.objects.get(id=request.user.id)
            data = json.loads(url.read().decode())
            price = float(data['quote']['latestPrice'])
            print("This the value of one share: " + str(price))
            totalpriceAtClose = price * float(openPosition.shares)
            totalPriceAtOpen = float(openPosition.position)
            print("This is the total price at open: " + str(totalPriceAtOpen))
            print("This is the total price at close: " + str(totalpriceAtClose))
            gains = totalpriceAtClose - totalPriceAtOpen
            print("These are the gains" + str(gains))
            userMoney = float(purchaser.money)

            updatedUserMoney = userMoney + totalpriceAtClose + gains
            print("This is updated user money" + str(updatedUserMoney))
            purchaser.money = updatedUserMoney
            purchaser.save()

        try:
            checkClose = Closed.objects.get(user=request.user, stock_symbol=symbol)
            updateGains = float(checkClose.gains) + gains
            checkClose.gains = updateGains
            checkClose.save()
        except ObjectDoesNotExist:
            closedPosition = Closed(
                user=request.user,
                stock_symbol=symbol,
                shares=openPosition.shares,
                gains=gains
            )

            closedPosition.save()

    except ObjectDoesNotExist:
        return JsonResponse({"error": "You do not own any shares of this stock"})

    openPosition.delete()
    return JsonResponse({"success": "Position closed successfully",
                         "updatedAccount": round(updatedUserMoney, 2)})





