from modeltranslation.translator import translator, TranslationOptions
from .models import Product, Category, SubCategory

class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'features',)

class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

class SubCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Product, ProductTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(SubCategory, SubCategoryTranslationOptions)