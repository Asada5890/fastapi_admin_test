from sqlalchemy import Column, Float, Integer, String, ForeignKey, Boolean, DateTime, DECIMAL, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class ProductCategory(Base):
    __tablename__ = 'productcategory'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, comment="Категория")
    
    def __repr__(self):
        return self.name

class ProductType(Base):
    __tablename__ = 'producttype'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, comment="Вид товара")
    category_id = Column(Integer, ForeignKey('productcategory.id', ondelete='SET NULL'), nullable=True)
    base_unit = Column(String(20), default="тонна", comment="Единица измерения")
    
    category = relationship("ProductCategory", backref="product_types")
    
    def __repr__(self):
        return f"{self.name} ({self.base_unit})"

class Quarry(Base):
    __tablename__ = 'quarry'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, comment="Название карьера")
    location = Column(String(255), nullable=True, comment="Местоположение")
    is_active = Column(Boolean, default=True, comment="Активен")
    
    prices = relationship("QuarryProductPrice", back_populates="quarry")
    
    def __repr__(self):
        return self.name

class QuarryProductPrice(Base):
    __tablename__ = 'quarryproductprice'
    
    id = Column(Integer, primary_key=True)
    quarry_id = Column(Integer, ForeignKey('quarry.id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('producttype.id', ondelete='CASCADE'))
    price = Column(DECIMAL(10, 2), nullable=False, comment="Цена")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="Обновлено")
    
    quarry = relationship("Quarry", back_populates="prices", lazy="joined")
    product = relationship("ProductType", lazy="joined")
    
    __table_args__ = (UniqueConstraint('quarry_id', 'product_id', name='unique_quarry_product'),)
    
    def __repr__(self):
        return f"{self.quarry.name} - {self.product.name}: {self.price}"

class Customer(Base):
    __tablename__ = 'customer'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False, comment="ФИО")
    phone = Column(String(20), nullable=False, comment="Телефон")
    email = Column(String(255), nullable=True, comment="Email")
    address = Column(Text, nullable=False, comment="Адрес доставки")
    
    orders = relationship("Order", back_populates="customer")
    
    def __repr__(self):
        return f"{self.full_name} ({self.phone})"



class TruckType(Base):
    __tablename__ = 'trucktype'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, comment="Название типа машины")
    volume = Column(Float, nullable=False, comment="Объем кузова (м³)")
    load_capacity = Column(Float, nullable=False, comment="Грузоподъемность (тонн)")
    description = Column(Text, nullable=True, comment="Описание")
    
    def __repr__(self):
        return f"{self.name} ({self.volume} м³)"

class Order(Base):
    __tablename__ = 'order'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="new", comment="Статус заказа")
    total_price = Column(DECIMAL(10, 2), nullable=False, comment="Итоговая стоимость")
    delivery_address = Column(Text, nullable=False, comment="Адрес доставки")
    
    # Поля товара (ранее были в OrderItem)
    product_id = Column(Integer, ForeignKey('producttype.id'), nullable=False)
    quarry_id = Column(Integer, ForeignKey('quarry.id'), nullable=False)
    quantity = Column(Float, nullable=False, comment="Количество товара")
    price_per_unit = Column(DECIMAL(10, 2), nullable=False, comment="Цена за единицу")
    
    # Связи
    customer = relationship("Customer", back_populates="orders", lazy="joined")
    product = relationship("ProductType", lazy="joined")
    quarry = relationship("Quarry", lazy="joined")
    trucks = relationship("OrderTruck", back_populates="order", cascade="all, delete-orphan")
    
    # Вычисляемое свойство для проверки
    @property
    def item_total(self):
        return self.quantity * self.price_per_unit
    

    @property
    def trucks_summary(self):
        """Сводная информация о машинах для доставки"""
        if not self.trucks:
            return "Машины не назначены"
        
        summary = []
        for truck in self.trucks:
            summary.append(f"{truck.truck_type.name} × {truck.count}")
        return ", ".join(summary)
    
    def __repr__(self):
        return f"Заказ #{self.id}: {self.product.name} x {self.quantity}"


class OrderTruck(Base):
    __tablename__ = 'ordertruck'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id', ondelete='CASCADE'))
    truck_type_id = Column(Integer, ForeignKey('trucktype.id'), nullable=False)
    count = Column(Integer, nullable=False, default=1, comment="Количество машин")
    
    order = relationship("Order", back_populates="trucks")
    truck_type = relationship("TruckType", lazy="joined")
    
    # Вычисляемые свойства для удобства
    @property
    def total_volume(self):
        return self.truck_type.volume * self.count
    
    @property
    def total_capacity(self):
        return self.truck_type.load_capacity * self.count
    
    def __repr__(self):
        return f"{self.truck_type.name} x {self.count}"
