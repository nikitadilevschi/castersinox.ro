from django.contrib import admin
from .models import Category, SubCategory, Product, ProductImage, ContactSubmission
from django import forms
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin


# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('thumbnail',)
    fields = ('thumbnail', 'image',)

    def thumbnail(self, instance):
        if instance.image:
            return format_html('<img src="{}" style="max-height:100px;"/>', instance.image.url)
        return ''
    thumbnail.short_description = 'Preview'

class ProductAdminForm(forms.ModelForm):
    main_image = forms.ModelChoiceField(
        queryset=ProductImage.objects.none(),
        required=False,
        label='Main image'
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['main_image'].queryset = ProductImage.objects.filter(
                product=self.instance
            )
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'category', 'subcategory']
    list_filter = ['category', 'subcategory']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]


class CategoryAdminForm(forms.ModelForm):
    main_image = forms.ModelChoiceField(
        queryset=ProductImage.objects.none(),
        required=False,
        label='Main image'
    )

    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['main_image'].queryset = ProductImage.objects.filter(
                product__category=self.instance
            )

class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ['name', 'slug', 'main_image', 'main_image_preview']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    readonly_fields = ('main_image_preview',)

    def main_image_preview(self, obj):
        if obj.main_image and obj.main_image.image:
            return format_html('<img src="{}" style="max-height:150px;"/>', obj.main_image.image.url)
        return ''
    main_image_preview.short_description = 'Main image preview'

class SubCategoryAdminForm(forms.ModelForm):
    main_image = forms.ModelChoiceField(
        queryset=ProductImage.objects.none(),
        required=False,
        label='Main image'
    )

    class Meta:
        model = SubCategory
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['main_image'].queryset = ProductImage.objects.filter(
                product__subcategory=self.instance
            )
class SubCategoryAdmin(admin.ModelAdmin):
    form = SubCategoryAdminForm
    list_display = ['name', 'category', 'slug', 'main_image']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['category']


class ContactSubmissionAdminForm(forms.ModelForm):
    testimonial_consent = forms.BooleanField(
        required=False,
        label='Acordul de prelucrare a datelor'
    )

    class Meta:
        model = ContactSubmission
        fields = '__all__'

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    form = ContactSubmissionAdminForm
    ContactSubmission._meta.verbose_name = "Email primit"
    ContactSubmission._meta.verbose_name_plural = "Emailuri primite"
    list_display = ('fullname', 'email', 'phone', 'company', 'testimonial_consent', 'created_at')
    list_filter = ('testimonial_consent', 'created_at')
    search_fields = ('fullname', 'email', 'company', 'message')

    readonly_fields = ('features_list',)
    fields = (
        'fullname', 'email', 'phone', 'company',
        'message', 'testimonial_consent', 'features_list'
    )

    def features_list(self, obj):
        return ", ".join([c.name for c in obj.features.all()]) if obj.pk else ""
    features_list.short_description = "Categorii"



admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
