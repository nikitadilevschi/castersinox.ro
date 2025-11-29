from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    main_image = models.ForeignKey(
        'ProductImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='category_main_image'
    )
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class SubCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    main_image = models.ForeignKey(
        'ProductImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategory_main_image'
    )
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Sub Categories"

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    features = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    # main_image = models.ImageField(upload_to='products/main/', null=True, blank=True)
    main_image = models.ForeignKey(
        'ProductImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='main_for'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Products"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/extra')

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name_plural = "Product Images"

class ContactSubmission(models.Model):
    fullname = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    features = models.ManyToManyField(Category, blank=True, related_name='contact_submissions')
    testimonial_consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fullname} — {self.email} ({self.created_at:%Y-%m-%d %H:%M})"