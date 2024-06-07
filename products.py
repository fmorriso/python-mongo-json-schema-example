from typing import ClassVar

from pyodmongo import DbModel


class Products(DbModel):
    name: str
    price: int
    category: str
    image: str
    id_visible: int
    _collection: ClassVar = 'Products'
