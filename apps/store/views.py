import  random
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

from apps.cart.cart import Cart
from .models import Product, Category, ProductReview


def search(request):
    query = request.GET.get('query')
    products = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(article__icontains=query))
    # Searchs for products which title or descripttion matches with query

    context = {
        'query': query,
        'products': products, 
    }

    return render(request, 'search.html', context)

def product_detail(request, category_slug, slug):
    product = get_object_or_404(Product, slug=slug)

    # Add review
    if request.method == 'POST':
        stars = request.POST.get('stars', 3)
        content = request.POST.get('content', '')
        review = ProductReview.objects.create(product=product, user=request.user, stars=stars, content=content) # Create review object
        return redirect('product_detail', category_slug=category_slug, slug=slug)

    # Get and Show related products
    related_products = list(product.category.products.filter(parent=None).exclude(id=product.id))
    # Testing 
    if len(related_products) >= 3:
        related_products = random.sample(related_products, 3)

    if product.parent:
        return redirect('product_detail', category_slug=category_slug, slug=product.parent.slug)
        # If product has parent (if product is variant) redirect to parent product

    imagesstring = "{'thumbnail': '%s', 'image': '%s'}," % (product.thumbnail.url, product.image.url)
    for image in product.images.all():
        imagesstring += ("{'thumbnail': '%s', 'image': '%s'}," % (image.thumbnail.url, image.image.url))

    cart = Cart(request)
    if cart.has_product(product.id):
        product.in_cart = True
    else:
        product.in_cart = False

    context = {
        'product': product,
        'imagesstring': imagesstring,
        'related_products': related_products
    }
    return render(request, 'product_detail.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(parent=None) # Show products which doesn't have parents (which is not variant of another product)
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'category_detail.html', context)
