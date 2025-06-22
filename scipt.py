from database import get_db
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
from datetime import datetime, timedelta

def seed_data():
    with get_db() as db:
        # Очищаем базу данных перед заполнением
        db.query(OrderTruck).delete()
        db.query(Order).delete()
        db.query(TruckType).delete()
        db.query(Customer).delete()
        db.query(QuarryProductPrice).delete()
        db.query(Quarry).delete()
        db.query(ProductType).delete()
        db.query(ProductCategory).delete()
        
        # Создаем категории товаров
        categories = [
            ProductCategory(name="Щебень"),
            ProductCategory(name="Песок"),
            ProductCategory(name="Гравий"),
            ProductCategory(name="Бутовый камень"),
        ]
        db.add_all(categories)
        db.flush()
        
        # Создаем виды товаров
        product_types = [
            ProductType(name="Гранитный щебень 5-20", category=categories[0], base_unit="тонна"),
            ProductType(name="Гранитный щебень 20-40", category=categories[0], base_unit="тонна"),
            ProductType(name="Песок речной", category=categories[1], base_unit="м³"),
            ProductType(name="Песок карьерный", category=categories[1], base_unit="м³"),
            ProductType(name="Гравий 5-20", category=categories[2], base_unit="тонна"),
            ProductType(name="Бут 100-300", category=categories[3], base_unit="тонна"),
        ]
        db.add_all(product_types)
        db.flush()
        
        # Создаем карьеры
        quarries = [
            Quarry(name="Карьер 'Гранитный'", location="с. Гранитное", is_active=True),
            Quarry(name="Карьер 'Речной'", location="п. Речной", is_active=True),
            Quarry(name="Карьер 'Гравийный'", location="г. Гравийск", is_active=False),
        ]
        db.add_all(quarries)
        db.flush()
        
        # Устанавливаем цены на товары в карьерах
        prices = [
            QuarryProductPrice(quarry=quarries[0], product=product_types[0], price=1500.00),
            QuarryProductPrice(quarry=quarries[0], product=product_types[1], price=1400.00),
            QuarryProductPrice(quarry=quarries[0], product=product_types[5], price=1800.00),
            QuarryProductPrice(quarry=quarries[1], product=product_types[2], price=800.00),
            QuarryProductPrice(quarry=quarries[1], product=product_types[3], price=700.00),
            QuarryProductPrice(quarry=quarries[2], product=product_types[4], price=1200.00),
        ]
        db.add_all(prices)
        db.flush()
        
        # Создаем типы машин
        truck_types = [
    TruckType(name="Самосвал 10м³", volume=10.0, load_capacity=10.0, description="Малый самосвал"),
    TruckType(name="Самосвал 20м³", volume=20.0, load_capacity=20.0, description="Средний самосвал"),
    TruckType(name="Самосвал 30м³", volume=30.0, load_capacity=30.0, description="Крупный самосвал"),
    TruckType(name="Самосвал 40м³", volume=40.0, load_capacity=40.0, description="Очень крупный самосвал"),
    TruckType(name="Мегасамосвал 50м³", volume=50.0, load_capacity=50.0, description="Самый большой самосвал"),
]
        db.add_all(truck_types)
        db.flush()
        
        # Создаем клиентов
        customers = [
            Customer(
                full_name="Иванов Иван Иванович",
                phone="+79001234567",
                email="ivanov@example.com",
                address="г. Москва, ул. Ленина, д. 1"
            ),
            Customer(
                full_name="Петров Петр Петрович",
                phone="+79007654321",
                email="petrov@example.com",
                address="г. Санкт-Петербург, Невский пр., д. 100"
            ),
        ]
        db.add_all(customers)
        db.flush()
        
        # Создаем заказы
        orders = [
    Order(
        customer=customers[0],
        product=product_types[0],  # Гранитный щебень 5-20
        quarry=quarries[0],        # Карьер 'Гранитный'
        quantity=100.0,            # 100 тонн
        price_per_unit=1500.00,
        total_price=150000.00,
        delivery_address="г. Москва, ул. Строителей, д. 25",
        status="completed"
    ),
    Order(
        customer=customers[1],
        product=product_types[2],  # Песок речной
        quarry=quarries[1],        # Карьер 'Речной'
        quantity=150.0,            # 150 м³
        price_per_unit=800.00,
        total_price=120000.00,
        delivery_address="г. Санкт-Петербург, пр. Победы, д. 15",
        status="in_progress"
    ),
]
        db.add_all(orders)
        db.flush()
        
        # Добавляем машины в заказы
        order_trucks = [
    # Заказ 1 (100 тонн щебня)
    OrderTruck(order=orders[0], truck_type=truck_types[2], count=2),  # 2 × 30м³ = 60м³
    OrderTruck(order=orders[0], truck_type=truck_types[1], count=2),  # 2 × 20м³ = 40м³
    
    # Заказ 2 (150 м³ песка)
    OrderTruck(order=orders[1], truck_type=truck_types[4], count=2),  # 2 × 50м³ = 100м³
    OrderTruck(order=orders[1], truck_type=truck_types[3], count=1),  # 1 × 40м³ = 40м³
]

        db.add_all(order_trucks)
        
        db.commit()
        print("✅ Тестовые данные успешно добавлены в базу данных!")

if __name__ == "__main__":
    seed_data()