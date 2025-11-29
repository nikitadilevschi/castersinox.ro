from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.types import TypeDecorator, TEXT
import json
from datetime import datetime
import re

# Define the base for declarative models
Base = declarative_base()

# Custom type for JSON data
class JSONEncodedDict(TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    subcategories = relationship("SubCategory", back_populates="category", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    def __init__(self, name):
        self.name = name
        self.slug = self._slugify(name)

    def _slugify(self, name):
        return re.sub(r'[^a-z0-9]+', '-', name.lower())

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

class SubCategory(Base):
    __tablename__ = 'subcategories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory", cascade="all, delete-orphan")

    def __init__(self, name, category):
        self.name = name
        self.slug = self._slugify(name)
        self.category = category

    def _slugify(self, name):
        return re.sub(r'[^a-z0-9]+', '-', name.lower())

    def __repr__(self):
        return f"<SubCategory(id={self.id}, name='{self.name}')>"

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    features = Column(JSONEncodedDict)  # Stored as JSON
    category_id = Column(Integer, ForeignKey('categories.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    category = relationship("Category", back_populates="products")
    subcategory = relationship("SubCategory", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

    def __init__(self, name, description, features, category, subcategory=None):
        self.name = name
        self.slug = self._slugify(name)
        self.description = description
        self.features = features
        self.category = category
        self.subcategory = subcategory

    def _slugify(self, name):
        return re.sub(r'[^a-z0-9]+', '-', name.lower())

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"

class ProductImage(Base):
    __tablename__ = 'product_images'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    image_path = Column(String(255), nullable=False)

    product = relationship("Product", back_populates="images")

    def __init__(self, product, image_path):
        self.product = product
        self.image_path = image_path

    def __repr__(self):
        return f"<ProductImage(id={self.id}, path='{self.image_path}')>"

DB_USER = "postgres"  # e.g., postgres
DB_PASSWORD = "asd2asd2A"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "castersinox" # The database you created

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)