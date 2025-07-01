# basado en https://github.com/ArjanCodes/2023-fastapi/tree/main

from enum import Enum
from fastapi import FastAPI, HTTPException, Path, Query, Depends
from pydantic import BaseModel, Field

app = FastAPI(
    title="Basic FastAPI App",
    description="A simple FastAPI application with CRUD operations and query filtering.",
    version="0.1.0",
)


class Category(Enum):
    """Category for items in the inventory."""

    TOOLS = 'tools'
    CONSUMABLES = 'consumables'


class Item(BaseModel):
    """Representation of an item in the system."""

    name: str = Field(description="Name of the item.")
    price: float = Field(description="Price of the item in Euro.")
    count: int = Field(description="Amount of instances of this item in stock.")
    id: int = Field(description="Unique integer that specifies this item.")
    category: Category = Field(description="Category this item belongs to.")


# Sample data to simulate a database.
# In a real application, you would typically fetch this data from a database.
items = {
    0: Item(name="Hammer", price=9.99, count=20, id=0, category=Category.TOOLS),
    1: Item(name="Pliers", price=5.99, count=20, id=1, category=Category.TOOLS),
    2: Item(name="Nails", price=1.99, count=100, id=2, category=Category.CONSUMABLES),
}


# FastAPI handles JSON serialization and deserialization for us.
# We can simply use built-in python and Pydantic types, in this case dict[int, Item].
@app.get("/")
def index() -> dict[str, dict[int, Item]]:
    return {"items": items}


@app.get("/items/{item_id}")
def get_item(item_id: int) -> Item:
    if item_id not in items:
        raise HTTPException(status_code = 404, detail = f"Item with id {item_id} not found")
    return items[item_id]



from typing import Annotated

# ---------------------------------------------------------------------------
#  FILTRO DE CONSULTA (QUERY PARAMS) COMO MODELO Pydantic
# ---------------------------------------------------------------------------

class ItemFilter(BaseModel):
    """
    Define los parámetros de búsqueda como un único objeto.

    *  Cada campo es opcional (valor por defecto = None).
    *  Field(...) permite documentar y validar rangos (gt=0, ge=0, etc.).
    """
    name:     str      | None = Field(None, description="Nombre exacto")
    price:    float    | None = Field(None, gt=0, description="Precio exacto")
    count:    int      | None = Field(None, ge=0, description="Cantidad exacta")
    category: Category | None = None


# Alias de tipo opcional para la respuesta (solo para hacerla explícita)
Selection = dict[str, str | int | float | Category | None]

# ---------------------------------------------------------------------------
#  ENDPOINT: /items/
# ---------------------------------------------------------------------------

@app.get("/items/")
def query_items(
    # FastAPI “inyecta” la instancia ItemFilter usando Depends()
    # Los argumentos de la URL (?name=..., ?price=...) se parsean y validan aquí.
    filter: Annotated[ItemFilter, Depends()]
) -> dict[str, Selection | list[Item]]:
    """
    Busca artículos que cumplan TODOS los filtros proporcionados.
    Devuelve:
        - 'query'     → los parámetros recibidos (sin los que estén a None)
        - 'selection' → lista de Item coincidentes
    """

    # --- función interna de coincidencia ---
    def match(item: Item) -> bool:
        """
        Devuelve True si el item coincide con CADA campo que el
        usuario haya incluido en la consulta.
        Se usan solo los campos presentes en filter.model_fields_set.
        """
        return all(
            getattr(item, field) == getattr(filter, field)
            for field in filter.model_fields_set
        )

    # Filtrar la “base de datos”
    selection = [i for i in items.values() if match(i)]

    # Respuesta con metadatos
    return {
        "query":     filter.model_dump(exclude_none=True),  # parámetros reales
        "selection": selection,                             # coincidencias
    }

@app.post("/")
def add_item(item: Item) -> dict[str, Item]:

    if item.id in items:
        HTTPException(status_code=400, detail=f"Item with {item.id=} already exists.")

    items[item.id] = item
    return {"added": item}


@app.put("/items/{item_id}")
def update(
    item_id: int = Path(
        title="Item ID", description="Unique integer that specifies an item.", ge=0
    ),
    name: str
    | None = Query(
        title="Name",
        description="New name of the item.",
        default=None,
        min_length=1,
        max_length=8,
    ),
    price: float
    | None = Query(
        title="Price",
        description="New price of the item in Euro.",
        default=None,
        gt=0.0,
    ),
    count: int
    | None = Query(
        title="Count",
        description="New amount of instances of this item in stock.",
        default=None,
        ge=0,
    ),
):
    if item_id not in items:
        HTTPException(status_code=404, detail=f"Item with {item_id=} does not exist.")
    if all(info is None for info in (name, price, count)):
        raise HTTPException(
            status_code=400, detail="No parameters provided for update."
        )

    item = items[item_id]
    if name is not None:
        item.name = name
    if price is not None:
        item.price = price
    if count is not None:
        item.count = count

    return {"updated": item}


@app.delete("/items/{item_id}")
def delete_item(item_id: int) -> dict[str, Item]:

    if item_id not in items:
        raise HTTPException(
            status_code=404, detail=f"Item with {item_id=} does not exist."
        )

    item = items.pop(item_id)
    return {"deleted": item}