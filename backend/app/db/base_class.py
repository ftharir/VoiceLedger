from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    کلاس پایه برای تمام مدل‌های SQLAlchemy.
    به‌طور خودکار نام جدول را از اسم کلاس تولید می‌کند.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()