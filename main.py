from wtforms import SelectField
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select, Relationship
from sqladmin import Admin, ModelView
from sqlalchemy.orm import selectinload, joinedload
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import List, Optional

app = FastAPI()

# Настройка БД
DATABASE_URL = "sqlite:///test.db"
engine = create_engine(DATABASE_URL, echo=True)

# Инициализация админки с русским заголовком
admin = Admin(app, engine=engine, title="Админка")

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модели данных --------------------------------------------------------

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = True
    orders: List["Order"] = Relationship(back_populates="user")
    
    def __str__(self):
        return self.email

class Carrier(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    location: str
    contact_phone: str
    materials: List["Material"] = Relationship(back_populates="carrier")
    
    def __str__(self):
        return self.name

class MaterialType(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    
    def __str__(self):
        return self.name

class Material(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    price_per_ton: float
    carrier_id: int = Field(foreign_key="carrier.id")
    carrier: Carrier = Relationship(back_populates="materials")
    type_id: int = Field(foreign_key="materialtype.id")
    type: MaterialType = Relationship()
    orders: List["Order"] = Relationship(back_populates="material")
    
    def __str__(self):
        # Безопасный доступ к type.name
        return self.name

class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    quantity: float
    order_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending")
    
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="orders")
    material_id: int = Field(foreign_key="material.id")
    material: Material = Relationship(back_populates="orders")
    
    def __str__(self):
        return f"Заказ #{self.id}"

# Создаем таблицы
SQLModel.metadata.create_all(engine)

# Зависимость для сессии БД
def get_session():
    with Session(engine) as session:
        yield session

# Шаблоны
templates = Jinja2Templates(directory="templates")

# Админ-панель с улучшенным отображением данных --------------------------

class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    
    column_list = [User.id, User.email, User.is_active]
    column_labels = {
        User.id: "ID",
        User.email: "Email",
        User.is_active: "Активен"
    }
    form_excluded_columns = [User.hashed_password, User.orders]
    
    def is_accessible(self, request: Request) -> bool:
        return True

class CarrierAdmin(ModelView, model=Carrier):
    name = "Карьер"
    name_plural = "Карьеры"
    icon = "fa-solid fa-mountain"
    
    column_list = [Carrier.id, Carrier.name, Carrier.location, Carrier.contact_phone]
    column_labels = {
        Carrier.id: "ID",
        Carrier.name: "Название",
        Carrier.location: "Местоположение",
        Carrier.contact_phone: "Контактный телефон"
    }

class MaterialTypeAdmin(ModelView, model=MaterialType):
    name = "Тип материала"
    name_plural = "Типы материалов"
    icon = "fa-solid fa-cubes"
    
    column_list = [MaterialType.id, MaterialType.name]
    column_labels = {
        MaterialType.id: "ID",
        MaterialType.name: "Название"
    }

class MaterialAdmin(ModelView, model=Material):
    name = "Материал"
    name_plural = "Материалы"
    icon = "fa-solid fa-rock"
    
    column_list = [
        Material.id, 
        Material.name, 
        Material.price_per_ton,
        Material.carrier,
        Material.type
    ]
    column_labels = {
        Material.id: "ID",
        Material.name: "Название",
        Material.price_per_ton: "Цена за тонну (руб)",
        Material.carrier: "Карьер",
        Material.type: "Тип материала"
    }
    
    form_ajax_refs = {
        "carrier": {
            "fields": ["name"],
            "order_by": "name"
        },
        "type": {
            "fields": ["name"],
            "order_by": "name"
        }
    }
    
    # Жадная загрузка для Material
    def get_list_query(self, request: Request):
        return super().get_list_query(request).options(
            joinedload(Material.carrier),
            joinedload(Material.type)
        )

class OrderAdmin(ModelView, model=Order):
    name = "Заказ"
    name_plural = "Заказы"
    icon = "fa-solid fa-cart-shopping"
    
    column_list = [
        Order.id,
        Order.user,
        Order.material,
        Order.quantity,
        Order.order_date,
        Order.status
    ]
    column_labels = {
        Order.id: "ID",
        Order.user: "Пользователь",
        Order.material: "Материал",
        Order.quantity: "Количество (тонн)",
        Order.order_date: "Дата заказа",
        Order.status: "Статус"
    }
    
    column_formatters = {
        Order.order_date: lambda m, a: m.order_date.strftime("%d.%m.%Y %H:%M")
    }
    
    form_ajax_refs = {
        "user": {"fields": ["email"]},
        "material": {"fields": ["name"]}
    }
    form_overrides = {
        "status": SelectField
    }

    form_args = {
        "status": {
            "choices": [
                ("pending", "В обработке"),
                ("completed", "Выполнен"),
                ("cancelled", "Отменён")
            ],
            "label": "Статус"
        }
    }
    
    # Улучшенная жадная загрузка для Order
    def get_list_query(self, request: Request):
        return super().get_list_query(request).options(
            selectinload(Order.user),
            selectinload(Order.material).options(
                joinedload(Material.type),
                joinedload(Material.carrier)
            )
        )
    
    def get_detail_query(self, request: Request):
        return super().get_detail_query(request).options(
            selectinload(Order.user),
            selectinload(Order.material).options(
                joinedload(Material.type),
                joinedload(Material.carrier)
            )
        )

# Регистрация представлений админки
admin.add_view(UserAdmin)
admin.add_view(CarrierAdmin)
admin.add_view(MaterialTypeAdmin)
admin.add_view(MaterialAdmin)
admin.add_view(OrderAdmin)

# Роуты ----------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# API для работы с материалами
@app.get("/api/materials", response_class=HTMLResponse)
async def list_materials(
    request: Request,
    session: Session = Depends(get_session)
):
    materials = session.exec(
        select(Material)
        .options(
            joinedload(Material.carrier),
            joinedload(Material.type)
        )
    ).all()
    return templates.TemplateResponse(
        "materials.html",
        {"request": request, "materials": materials}
    )

# Регистрация пользователя
@app.post("/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    existing_user = session.exec(
        select(User).where(User.email == email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(password)
    user = User(email=email, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    return RedirectResponse("/", status_code=303)

# Создание заказа
@app.post("/orders/create")
async def create_order(
    user_id: int = Form(...),
    material_id: int = Form(...),
    quantity: float = Form(...),
    session: Session = Depends(get_session)
):
    material = session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    order = Order(
        user_id=user_id,
        material_id=material_id,
        quantity=quantity
    )
    session.add(order)
    session.commit()
    return {"message": "Order created successfully", "order_id": order.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)