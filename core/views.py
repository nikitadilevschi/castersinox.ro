import os
from django.http import FileResponse
from django.shortcuts import get_object_or_404, reverse, render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, DetailView, FormView
from  django.template.response import TemplateResponse
from django.conf import settings
from .models import Product, Category, SubCategory, ProductImage, ContactSubmission
from django.db.models import Q
from .forms import ContactForm

class MainView(TemplateView):
    template_name = 'core/home_content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return TemplateResponse(request, self.template_name, context)


# Catalog view with filtering and search
class ProductPageView(TemplateView):
    template_name = 'core/catalog.html'

    FILTER_MAPPING = {
        'category': lambda queryset, value: queryset.filter(category__slug__iexact=value),
        'subcategory': lambda queryset, value: queryset.filter(subcategory__slug__iexact=value),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get('category_slug') or kwargs.get('slug')
        subcategory_slug = kwargs.get('subcategory_slug')

        categories = Category.objects.all()
        products = Product.objects.all().order_by('-created_at')

        current_category = None
        current_subcategory = None
        category_subcategories = SubCategory.objects.none()

        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            category_subcategories = SubCategory.objects.filter(category=current_category)

            # If a subcategory is selected, show products for it.
            if subcategory_slug:
                current_subcategory = get_object_or_404(
                    SubCategory,
                    slug=subcategory_slug,
                    category=current_category
                )
                products = products.filter(category=current_category, subcategory=current_subcategory)
            else:
                # If the category has subcategories and no subcategory selected,
                # hide category-level products so template shows subcategories first.
                if category_subcategories.exists():
                    products = None
                else:
                    products = products.filter(category=current_category)

            # Attach a small preview queryset to each subcategory
            for sub in category_subcategories:
                sub.products_preview = Product.objects.filter(
                    subcategory=sub
                ).order_by('-created_at')[:4]

        # Search only when products is not None
        query = self.request.GET.get('q')
        if query and products is not None:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query) | Q(features__icontains=query)
            )

        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value and products is not None:
                products = filter_func(products, value)
                filter_params[param] = value
            else:
                filter_params[param] = 'None'
        filter_params['q'] = query or ''

        context.update({
            'categories': categories,
            'subcategories': category_subcategories,
            'products': products,
            'current_category': current_category,
            'current_subcategory': current_subcategory,
            'filter_params': filter_params,
            'search_query': query or '',
        })

        if self.request.GET.get('show_search') == 'true':
            context['show_search'] = True
        elif self.request.GET.get('reset_search') == 'true':
            context['show_search'] = True

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return TemplateResponse(request, self.template_name, context)




class ProductDetailView(DetailView):
    model = Product
    template_name = 'core/product_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Determine the category the user is "on":
        # 1. Try a category slug passed in URL kwargs (common for nested routes)
        # 2. Try a `category` GET param
        # 3. Fall back to the product's own category
        category_slug = kwargs.get('category_slug') or self.kwargs.get('category_slug') or self.request.GET.get('category')
        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
        else:
            current_category = product.category

        # Related products come from the resolved current_category
        related_products = Product.objects.none()
        if current_category:
            related_products = Product.objects.filter(category=current_category).exclude(id=product.id)[:2]

        context.update({
            'product': product,
            'categories': Category.objects.all(),
            'related_products': related_products,
            'current_category': current_category,
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        return TemplateResponse(request, self.template_name, context)


class SuccessView(TemplateView):
    template_name = 'core/success.html'


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # save submission / send email (existing code)
            submission = ContactSubmission.objects.create(
                fullname=cd.get('fullname', ''),
                email=cd.get('email', ''),
                phone=cd.get('phone', ''),
                company=cd.get('company', ''),
                message=cd.get('message', ''),
                testimonial_consent=cd.get('testimonial_consent', False),
            )
            submission.features.set(cd.get('features_used', []))
            # optionally send email here
            messages.success(request, "Mulțumim! Cererea a fost trimisă.")
            return redirect('core:index')
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})

def PolicyView(request):
    return render(request, 'core/policy.html')

