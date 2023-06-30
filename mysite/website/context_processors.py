def favorites_count(request):
    if request.user.is_authenticated:
        favorites = request.user.usermenu.favorites.all().count()
    else:
        favorites = 0
    return {'favorites_count': favorites}


def cart_count(request):
    if request.user.is_authenticated:
        cart_num = request.user.usermenu.cart_items.all().count()
    else:
        cart_num = 0
    return {'cart_num': cart_num}
