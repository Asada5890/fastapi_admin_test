from fastapi import FastAPI
from sqladmin import Admin
from database import engine, create_tables
from admin import (
    ProductCategoryAdmin,
    ProductTypeAdmin,
    QuarryAdmin,
    QuarryProductPriceAdmin,
    CustomerAdmin,
    OrderAdmin,
    TruckTypeAdmin  # Добавляем новую админку
)
from scipt import seed_data

# Создаем таблицы в БД
create_tables()

# Создаем и заполняем тестовыми данными
try:
    seed_data()
except Exception as e:
    print(f"⚠️ Ошибка при заполнении тестовыми данными: {e}")

app = FastAPI(title="Админка стройматериалов")

# Инициализация админки
admin = Admin(app, engine, title="Админка стройматериалов")

# Регистрация административных панелей
admin.add_view(ProductCategoryAdmin)
admin.add_view(ProductTypeAdmin)
admin.add_view(QuarryAdmin)
admin.add_view(QuarryProductPriceAdmin)
admin.add_view(CustomerAdmin)
admin.add_view(TruckTypeAdmin)  # Регистрируем админку для типов машин
admin.add_view(OrderAdmin)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
