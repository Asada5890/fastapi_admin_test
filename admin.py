from sqladmin import ModelView
from sqlalchemy import func
from models import (
    ProductCategory, 
    ProductType, 
    Quarry, 
    QuarryProductPrice,
    Customer, 
    Order,
    OrderTruck,
    TruckType
)


class ProductCategoryAdmin(ModelView, model=ProductCategory):
    name = "Категория товара"
    name_plural = "Категории товаров"
    column_list = ["id", "name"]
    column_searchable_list = ["name"]
    column_default_sort = [("name", False)]
    page_size = 20

class ProductTypeAdmin(ModelView, model=ProductType):
    name = "Вид товара"
    name_plural = "Виды товаров"
    column_list = ["id", "name", "category", "base_unit"]
    column_searchable_list = ["name"]
    column_sortable_list = ["category_id"]
    form_columns = ["name", "category_id", "base_unit"]
    page_size = 20
    
    # Добавляем автодополнение для категории
    form_ajax_refs = {
        'category': {
            'fields': (ProductCategory.name,),
            'order_by': ProductCategory.name,
        }
    }

class QuarryProductPriceAdmin(ModelView, model=QuarryProductPrice):
    name = "Цена товара"
    name_plural = "Цены товаров"
    column_list = ["quarry", "product", "price", "updated_at"]
    form_columns = ["quarry", "product", "price"]
    column_searchable_list = ["quarry.name", "product.name"]
    page_size = 20
    
    def after_model_change(self, data, model, is_created):
        """Обновляем дату обновления при изменении цены"""
        model.updated_at = func.now()

class QuarryAdmin(ModelView, model=Quarry):
    name = "Карьер"
    name_plural = "Карьеры"
    column_list = ["id", "name", "location", "is_active"]
    column_editable_list = ["is_active"]
    column_searchable_list = ["name"]
    form_columns = ["name", "location", "is_active"]
    page_size = 20

class CustomerAdmin(ModelView, model=Customer):
    name = "Клиент"
    name_plural = "Клиенты"
    column_list = ["id", "full_name", "phone", "email", "orders"]
    column_searchable_list = ["full_name", "phone", "email"]
    form_columns = ["full_name", "phone", "email", "address"]
    page_size = 20

class TruckTypeAdmin(ModelView, model=TruckType):
    name = "Тип машины"
    name_plural = "Типы машин"
    column_list = ["id", "name", "volume", "load_capacity"]
    form_columns = ["name", "volume", "load_capacity", "description"]
    column_searchable_list = ["name"]
    page_size = 20


class OrderTruckInline(ModelView, model=OrderTruck):
    name = "Машина для доставки"
    name_plural = "Машины для доставки"
    column_list = [
        "truck_type", 
        "count", 
        "total_volume",
        "total_capacity"
    ]
    form_columns = ["truck_type", "count"]
    column_sortable_list = ["count"]
    
    # Форматируем вычисляемые поля
    column_formatters = {
        "total_volume": lambda m, a: f"{m.truck_type.volume * m.count} м³",
        "total_capacity": lambda m, a: f"{m.truck_type.load_capacity * m.count} тонн"
    }
    
    def get_related_objects(self, obj: OrderTruck):
        if obj.truck_type is None:
            from .database import get_db
            with get_db() as db:
                db.refresh(obj, ['truck_type'])
        return obj

class OrderAdmin(ModelView, model=Order):
    name = "Заказ"
    name_plural = "Заказы"
    column_list = [
        "id", 
        "customer", 
        "product", 
        "quarry", 
        "quantity", 
        "price_per_unit",
        "total_price",
        "status",
        "created_at",
        "delivery_address",
        "trucks_summary"
    ]
    column_searchable_list = [
        "customer.full_name", 
        "customer.phone",
        "product.name",
        "quarry.name"
    ]
    column_sortable_list = ["created_at", "status", "quantity"]
    form_columns = [
        "customer", 
        "product", 
        "quarry", 
        "quantity", 
        "price_per_unit",
        "total_price",
        "status",
        "delivery_address"
    ]
    inline_models = [OrderTruckInline]  # Только машины
    page_size = 20
    
    # Форматирование даты
    column_formatters = {
        "created_at": lambda m, a: m.created_at.strftime("%d.%m.%Y %H:%M")
    }
    
    # Вычисляемое поле для общей стоимости товара
    column_formatters_detail = {
        "trucks_summary": lambda m, a: m.trucks_summary,
        "item_total": lambda m, a: m.quantity * m.price_per_unit
    }

    @property
    def trucks_summary(self):
        if not self.trucks:
            return "Машины не назначены"
        
        summary = []
        for truck in self.trucks:
            summary.append(f"{truck.truck_type.name} × {truck.count}")
        return ", ".join(summary)
    
    column_formatters = {
        "trucks_summary": lambda m, a: m.trucks_summary,
        "created_at": lambda m, a: m.created_at.strftime("%d.%m.%Y %H:%M")
    }

    inline_models = [OrderTruckInline]
