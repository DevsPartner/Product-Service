
Ich beginne mit `app/database.py`, dann `app/models.py`, `app/schemas.py`, `app/mapper.py`, `app/crud.py`, `app/main.py`, und am Ende noch `Dockerfile`, `docker-compose.yml`, `requirements.txt`.
Wenn du willst, kann ich danach noch tiefer auf einzelne Python-Konstrukte eingehen (z. B. `sessionmaker`, `yield`, `orm_mode`).

# 1) `app/database.py` — Zeile für Zeile

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
```

* `from sqlalchemy import create_engine`
  Importiert die Funktion, mit der wir eine **DB-Engine** (Verbindungsobjekt) erzeugen. Die Engine verwaltet Verbindungen, SQL-Rendering und die Kommunikation mit der DB.
* `from sqlalchemy.orm import sessionmaker, declarative_base`

  * `sessionmaker` ist eine Fabrik zum Erzeugen von `Session`-Objekten (ein `Session` ist ein DB-Kontext / Transaktionseinheit).
  * `declarative_base` erzeugt die Basis-Klasse, von der unsere ORM-Modelle erben.
* `import os`
  Importiert das `os`-Modul, damit wir Umgebungsvariablen (z. B. `DATABASE_URL`) lesen können.

```python
# DB URL aus Umgebungsvariable lesen, Standard fallback (postgres)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/products_db")
```

* Liest die Umgebungsvariable `DATABASE_URL`. Wenn sie nicht gesetzt ist, wird die angegebene Default-URL verwendet.
* Wichtig, weil in Docker / Prod die Konfiguration über Env-Variablen kommt.

```python
# Engine erstellen – verbindet uns mit der DB
engine = create_engine(DATABASE_URL, echo=True, future=True)
```

* `create_engine(DATABASE_URL, ...)` baut die Engine, die Verbindungen öffnen kann.
* `echo=True` aktiviert SQL-Logging (zeigt generierte SQL-Statements in der Konsole) — nützlich beim Entwickeln.
* `future=True` aktiviert einige neue SQLAlchemy-Verhaltensweisen (nicht zwingend nötig, empfiehlt sich bei modernem Code).

```python
# Session factory – erzeugt DB-Sessions (Transaktionen)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
```

* `SessionLocal` ist eine *konfigurierte* Session-Klasse.
* `bind=engine` heißt: Sessions nutzen diese Engine.
* `autoflush=False`: verhindert automatisches Flushen vor Leseoperationen (sämtliche Änderungen müssen explizit`commit()`/`flush()` auslösen) — hilft Vorhersehbarkeit.
* `autocommit=False` bedeutet, dass `commit()` explizit aufgerufen werden muss (Standard).
* `future=True` kompatibel mit `engine`-future-Modus.

```python
# Base-Klasse für Modelle (Models erben von Base)
Base = declarative_base()
```

* Erstellt die Basisklasse `Base`. Alle ORM-Klassen (z. B. `class Product(Base)`) erben davon; SQLAlchemy nutzt diese Base, um Tabellen-Informationen zu sammeln.

```python
# Dependency für FastAPI: liefert eine DB-Session pro Request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

* `def get_db()` definiert eine Funktion, die wir als **Dependency** in FastAPI benutzen.
* `db = SessionLocal()` erzeugt eine Session (eine Verbindung / Transaktions-Session).
* `yield db` gibt die Session an den aufrufenden FastAPI-Request-Handler zurück — nach der Request-Verarbeitung wird der Code nach `yield` ausgeführt.
* `finally: db.close()` stellt sicher, dass die Session/Connection immer wieder freigegeben wird (auch bei Exceptions).
* **Warum yield?** FastAPI erkennt Generatoren und sorgt dafür, dass die Aufräumlogik nach Nutzung ausgeführt wird — perfekte Lifecycle-Management.

---

# 2) `app/models.py` — Zeile für Zeile

```python
from sqlalchemy import Column, Integer, BigInteger, String, Numeric, Text
from sqlalchemy.orm import relationship
from .database import Base
```

* Importiert die SQLAlchemy-Datentypen (`Column`, `Integer`, `BigInteger`, `String`, `Numeric`, `Text`) die wir brauchen.
* `relationship` ist importiert, falls später Relationen gebraucht werden (nicht zwingend in unserem einfachen Produktbeispiel).
* `from .database import Base` importiert die `Base` Klasse (siehe `database.py`) für die Vererbung.

```python
class Product(Base):
    __tablename__ = "products"
```

* `class Product(Base)`: Definiert ein ORM-Model namens `Product`, das von `Base` erbt.
* `__tablename__ = "products"`: legt den Tabellen-Namen in der DB fest.

```python
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
```

* `id` ist eine Spalte vom Typ `BigInteger`.
* `primary_key=True`: bezeichnet die PK-Spalte.
* `index=True`: erzeugt einen DB-Index auf `id` (bei PK meist automatisch, aber explizit okay).
* `autoincrement=True`: DB generiert automatisch neue IDs beim Einfügen.

```python
    name = Column(String(255), nullable=False, index=True)
```

* `name` ist ein string-limitierter Wert (max 255 Zeichen).
* `nullable=False` bedeutet: Feld ist Pflicht (DB lässt keine NULL Werte zu).
* `index=True` weil wir wahrscheinlich nach Namen suchen oder filtern.

```python
    description = Column(Text, nullable=True)
```

* `description` ist längerer Text (`Text` Datentyp) und optional (`nullable=True`).

```python
    price = Column(Numeric(12, 2), nullable=False)  # Decimal-like storage
```

* `price` als `Numeric(12, 2)` speichert Dezimalwerte mit bis zu 12 Stellen insgesamt und 2 Nachkommastellen — ideal für Geldwerte.
* `nullable=False` heißt Pflichtfeld.

```python
    details = Column(Text, nullable=True)
    count = Column(Integer, nullable=False, default=0)
    image_link = Column(String(1024), nullable=True)
```

* `details`: weitere Informationen (optional).
* `count`: Anzahl verfügbarer Produkte, `Integer` mit `default=0`. `nullable=False` stellt sicher, dass ein Wert existiert.
* `image_link`: Link zum Bild; `String(1024)` erlaubt längere URLs; `nullable=True` erlaubt kein Bild.

---

# 3) `app/schemas.py` (Pydantic DTOs) — Zeile für Zeile

```python
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
```

* `BaseModel` ist die Pydantic-Basis für DTOs (Validierung, Serialisierung).
* `Field` erlaubt Metadaten (z. B. Beispiele, Beschränkungen).
* `Decimal` für exakte Dezimalrepräsentation.
* `Optional` für optionale Felder in Typenhinweisen.

```python
class ProductBase(BaseModel):
    name: str = Field(..., example="Kaffeemaschine")
    description: Optional[str] = None
    price: Decimal = Field(..., example="199.99")
    details: Optional[str] = None
    count: int = Field(..., ge=0, example=10)
    imageLink: Optional[str] = Field(None, alias="imageLink", max_length=1024)
```

* `class ProductBase(BaseModel)`: Basisschema mit gemeinsamen Feldern.
* `name: str = Field(..., example="Kaffeemaschine")`:

  * `...` bedeutet: Pflichtfeld (required).
  * `example` fügt OpenAPI-Dokumentation ein.
* `description: Optional[str] = None`: optional, Standard `None`.
* `price: Decimal = Field(..., example="199.99")`: Pflicht; `Decimal` sorgt für exakte Werte.
* `count: int = Field(..., ge=0, example=10)`: Pflicht; `ge=0` validiert `>= 0`.
* `imageLink: Optional[str] = Field(None, alias="imageLink", max_length=1024)`:

  * Der Attributname ist `imageLink` (CamelCase) — Pydantic kann Feldnamen via `alias` annehmen/ausgeben.
  * `max_length=1024` validiert Länge.

```python
    class Config:
        allow_population_by_field_name = True
```

* `Config` ist eine Pydantic-innere Klasse zur Konfiguration.
* `allow_population_by_field_name = True` erlaubt, sowohl `imageLink` (alias) als auch `image_link` (falls intern genutzt) zum Befüllen zu verwenden — nützlich für Flexibilität.

```python
class ProductCreate(ProductBase):
    pass
```

* `ProductCreate` erbt alles von `ProductBase`.
* `pass` bedeutet keine Änderung; dient der semantischen Trennung (Create-Intent).

```python
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    details: Optional[str] = None
    count: Optional[int] = None
    imageLink: Optional[str] = None
```

* `ProductUpdate` macht alle Felder optional — für Patch-/Update-Operationen.
* Durch optionale Felder kann `exclude_unset` genutzt werden, um nur geänderte Felder zu aktualisieren.

```python
class ProductRead(ProductBase):
    id: int

    class Config:
        orm_mode = True
```

* `ProductRead` ist das DTO für Responses (Ausgabe).
* `id: int` ergänzt das Basis-Schema.
* `orm_mode = True` erlaubt Pydantic, ORM-Objekte (`SQLAlchemy` Instanzen) direkt zu lesen (anstatt Dicts) — Pydantic liest Attribute aus dem Objekt.

---

# 4) `app/mapper.py` — Zeile für Zeile

```python
from .models import Product
from .schemas import ProductRead, ProductCreate
from decimal import Decimal
```

* Importiert das ORM-Modell und DTO-Klassen. `Decimal` um sicherzustellen, dass `price` als Decimal gehandhabt wird.

```python
def model_to_read(product: Product) -> ProductRead:
    """
    Konvertiert ein SQLAlchemy Product -> ProductRead DTO.
    """
    return ProductRead(
        id=product.id,
        name=product.name,
        description=product.description,
        price=Decimal(product.price),
        details=product.details,
        count=product.count,
        imageLink=product.image_link
    )
```

* `model_to_read` nimmt ein `Product` ORM-Objekt und erzeugt ein `ProductRead` DTO.
* `Decimal(product.price)`: stellt sicher, dass `price` als `Decimal` vorliegt (SQLAlchemy`s `Numeric`kann unterschiedlich zurückgeben — manchmal`Decimal`, manchmal `str`oder`Decimal`-ähnlich).
* `imageLink=product.image_link`: übersetzt DB-Feldname (`snake_case`) in API-Feldname (`camelCase`).

```python
def create_to_model(dto: ProductCreate) -> dict:
    """
    Mappt ProductCreate DTO zu einem dict, das in ein DB-Model passt.
    Wir geben ein dict zurück, weil SQLAlchemy-Model-Init bevorzugt kwargs verwendet.
    """
    return {
        "name": dto.name,
        "description": dto.description,
        "price": dto.price,
        "details": dto.details,
        "count": dto.count,
        "image_link": dto.imageLink
    }
```

* `create_to_model` konvertiert ein Create-DTO in ein Dict, das direkt in `models.Product(**dict)` verwendet werden kann.
* Wichtig: `image_link` (DB-Feld) ist anders benannt als `imageLink` (DTO) — Mapper behebt diese Diskrepanz.

**Warum Mapper?**

* Verhindert Kopplung zwischen internen DB-Feldern und externen API-Feldern.
* Zentralisiert Übersetzungslogik (z. B. Feldumbenennungen, Format-Konversionen).

---

# 5) `app/crud.py` — Zeile für Zeile

```python
from sqlalchemy.orm import Session
from . import models, schemas, mapper
from decimal import Decimal
```

* Importiert `Session` Typ für Typannotationen.
* Importiert lokale Module für Zugriff auf Models, Schemas, Mapper.
* `Decimal` falls in CRUD benötigt (z. B. für Rechenoperationen).

```python
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()
```

* `db.query(models.Product)`: baut eine Abfrage auf das `Product`-Model.
* `.filter(models.Product.id == product_id)`: fügt WHERE Bedingung hinzu.
* `.first()`: liefert das erste Ergebnis (oder `None`, wenn nicht vorhanden).
* Diese Funktion gibt das ORM-Objekt zurück.

```python
def list_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()
```

* `.offset(skip)`: überspringt `skip` viele Einträge (Pagination).
* `.limit(limit)`: begrenzt die Anzahl der zurückgegebenen Ergebnisse.
* `.all()`: liefert die Ergebnisliste.

```python
def create_product(db: Session, product_in: schemas.ProductCreate):
    payload = mapper.create_to_model(product_in)
    product = models.Product(**payload)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
```

* `payload = mapper.create_to_model(product_in)`: mappt DTO zu DB-Feldern.
* `product = models.Product(**payload)`: erstellt ein neues ORM-Objekt (noch nicht in DB).
* `db.add(product)`: markiert das Objekt für Einfügen.
* `db.commit()`: schreibt Änderung in die DB (INSERT).
* `db.refresh(product)`: lädt das frisch geschriebene Objekt erneut aus der DB (z. B. um `id` zu erhalten).
* `return product`: gibt das ORM-Objekt zurück.

```python
def update_product(db: Session, product: models.Product, updates: schemas.ProductUpdate):
    # Für jedes Feld, das nicht None ist, setzen wir das Model-Feld
    data = updates.dict(exclude_unset=True)
    if "imageLink" in data:
        data["image_link"] = data.pop("imageLink")
    for key, value in data.items():
        setattr(product, key, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
```

* `updates.dict(exclude_unset=True)`: erzeugt ein Dict nur mit Feldern, die tatsächlich in der Anfrage gesetzt wurden — wichtig damit wir keine Felder unabsichtlich auf `None` setzen.
* `if "imageLink" in data: data["image_link"] = data.pop("imageLink")`: mappt Feldname `imageLink` → `image_link` für DB.
* `setattr(product, key, value)`: setzt dynamisch Attribute am ORM-Objekt.
* `db.add(product)`: fügt Objekt zur Session hinzu (falls noch nicht persistent).
* `db.commit()` und `db.refresh(product)`: persistieren und laden aktualisierte Werte.
* `return product`: gibt das aktualisierte ORM-Objekt zurück.

```python
def delete_product(db: Session, product: models.Product):
    db.delete(product)
    db.commit()
    return
```

* `db.delete(product)`: markiert das Objekt zum Löschen.
* `db.commit()`: führt das DELETE in der DB aus.
* `return`: optional; hier nichts zurückgeben (bei HTTP 204 sinnvoll).

---

# 6) `app/main.py` — Zeile für Zeile

```python
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from . import models, schemas, crud, mapper
from .database import engine, Base, get_db
```

* Importiert FastAPI-Klassen (`FastAPI`, `Depends`, `HTTPException`, `status`).
* `List` für Typannotationen.
* `Session` Typ.
* Importiert eigene Module (`models`, `schemas`, `crud`, `mapper`).
* Holt `engine`, `Base`, `get_db` aus `database.py`.

```python
# Tabellen erstellen, falls noch nicht vorhanden (nur für Entwicklung; in Prod evtl. migrations verwenden)
Base.metadata.create_all(bind=engine)
```

* `Base.metadata.create_all(bind=engine)` erzeugt in der DB fehlende Tabellen basierend auf den ORM-Definitionen.
* **Nur für einfache Entwicklung**; in Produktionen benutzt man Migrations-Tools wie `alembic`.

```python
app = FastAPI(title="Product Service")
```

* Erzeugt die `FastAPI`-App-Instanz. `title` erscheint in der OpenAPI-Doku.

```python
@app.post("/products/", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Endpoint um ein Produkt zu erstellen.
    product_in wird durch Pydantic validiert.
    """
    product = crud.create_product(db=db, product_in=product_in)
    return mapper.model_to_read(product)
```

* `@app.post(...)` registriert eine POST-Route unter `/products/`.
* `response_model=schemas.ProductRead`: FastAPI validiert & serialisiert Rückgabe automatisch nach `ProductRead`.
* `status_code=201`: HTTP-Status 201 Created wird zurückgegeben.
* Funktionsparameter `product_in: schemas.ProductCreate`: FastAPI nutzt Pydantic, um Request-Body zu parsen/validieren.
* `db: Session = Depends(get_db)`: Abhängigkeit, die pro Anfrage eine DB-Session liefert.
* `product = crud.create_product(...)`: ruft CRUD-Schicht auf.
* `return mapper.model_to_read(product)`: wandelt ORM → DTO und gibt das Ergebnis zurück.

```python
@app.get("/products/{product_id}", response_model=schemas.ProductRead)
def get_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return mapper.model_to_read(product)
```

* GET-Route für Einzelprodukt.
* Pfad-Parameter `product_id: int` wird aus URL extrahiert und typ-geprüft.
* Wenn Produkt nicht gefunden: `HTTPException(404)` → FastAPI sendet passende Fehler-Antwort.

```python
@app.get("/products/", response_model=List[schemas.ProductRead])
def list_products_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.list_products(db, skip=skip, limit=limit)
    return [mapper.model_to_read(p) for p in products]
```

* GET Route für Liste von Produkten.
* Query-Parameter `skip` und `limit` (FastAPI extrahiert sie automatisch aus der URL, z. B. `/products?skip=10&limit=20`).
* Rückgabe ist eine Liste von `ProductRead`. Wir mappen jedes ORM-Objekt zu DTO.

```python
@app.patch("/products/{product_id}", response_model=schemas.ProductRead)
def update_product_endpoint(product_id: int, updates: schemas.ProductUpdate, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    updated = crud.update_product(db, product, updates)
    return mapper.model_to_read(updated)
```

* `PATCH` Route für partielle Updates.
* `updates: schemas.ProductUpdate` ist der Request-Body (alle Felder optional).
* Holt das Produkt, prüft Existenz, ruft `crud.update_product` auf und gibt das aktualisierte DTO zurück.

```python
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.delete_product(db, product)
    return None
```

* `DELETE` Route.
* Gibt `204 No Content` zurück (kein Body).
* Löscht das Produkt, wenn vorhanden, ansonsten `404`.

---

# 7) `Dockerfile` — Zeile für Zeile

```dockerfile
FROM python:3.11-slim
```

* Basis-Image: Python 3.11 in einer "slim" Variante (kleiner Footprint).

```dockerfile
WORKDIR /app
```

* Setzt Arbeitsverzeichnis im Container. Alle Commands laufen relativ zu `/app`.

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

* Kopiert `requirements.txt` in den Container und installiert Abhängigkeiten.
* `--no-cache-dir` reduziert Image-Größe.

```dockerfile
COPY . .
```

* Kopiert restlichen Code ins Image (`/app`).

```dockerfile
ENV PYTHONPATH=/app
```

* Setzt `PYTHONPATH` damit Module relativ zu `/app` importierbar sind.

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

* Startet Uvicorn-Server, lädt die App `app.main:app`.
* `--reload` aktiviert automatischen Reload bei Code-Änderungen (nur dev).

---

# 8) `docker-compose.yml` — Zeile für Zeile

```yaml
version: "3.8"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: products_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

* `db` Service nutzt das offizielle `postgres:15` Image.
* `environment`: setzt DB-Creds & DB-Name.
* `volumes`: persistente Daten (damit DB-Daten beim Neustart nicht verloren gehen).
* `ports`: mappt Container-Port 5432 auf Host-Port 5432 (nur für lokal dev).

```yaml
  product-service:
    build: .
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/products_db
    ports:
      - "8000:8000"
    volumes:
      - ./:/app
```

* `product-service` baut das lokale Dockerfile.
* `depends_on`: Startreihenfolge (db startet zuerst).
* Setzt `DATABASE_URL` so, dass der Service mit dem `db` Container kommunizieren kann.
* `ports` mappt 8000 (API) auf Host.
* `volumes` bind-mount für lokales Entwickeln (Code-Änderungen erscheinen sofort).

```yaml
volumes:
  pgdata:
```

* Definiert Persistenz-Volume `pgdata`.

---

# 9) `requirements.txt` — warum jede Zeile

```
fastapi
uvicorn[standard]
SQLAlchemy>=1.4
psycopg2-binary
pydantic
python-dotenv
```

* `fastapi` — Webframework.
* `uvicorn[standard]` — ASGI-Server mit empfohlenen Extras.
* `SQLAlchemy>=1.4` — ORM.
* `psycopg2-binary` — PostgreSQL DB-Treiber.
* `pydantic` — Datenvalidierung (FastAPI bringt es transitiv, aber explizit zu haben ist OK).
* `python-dotenv` — Umgebungsvariablen aus `.env` Datei laden (optional, praktisch).

---

# Zusätzliche Erklärungen zu häufigen Fragen / Fallstricke

* **Warum `Decimal` statt `float`?**
  `Decimal` ist exakt für Geldwerte. `float` führt zu Rundungsfehlern (siehe Beispiel mit 0.1 + 0.2).

* **Warum `orm_mode = True` in Pydantic?**
  Damit Pydantic Attribute von ORM-Objekten lesen kann (z. B. `product.name`) — sonst erwartet Pydantic Dicts.

* **Warum `yield` in `get_db()`?**
  So kann FastAPI Setup/Teardown (öffnen/close) sauber orchestrieren — ideal für Ressourcen-Management.

* **Warum Mapper statt direkte Zuweisung?**
  Mapper kapselt Namenskonversion und Formatkonversion. So änderst du nur eine Stelle, wenn du Feldnamen anpasst.

* **Warum `create_all()` nur für Entwicklung?**
  In Prod möchtest du kontrollierte Migrationen (Alembic), damit DB-Schemaänderungen nachvollziehbar/versioniert sind.

---

Wenn du willst, mache ich jetzt eins von diesen Schritten sofort (keine Wartezeiten, alles hier):

* A) **Generiere die vollständigen Dateien** (als Codeblöcke zum Kopieren) — ready-to-run.
* B) **Erkläre noch detaillierter einzelne präzise Zeilen**, z. B. wie `sessionmaker` intern funktioniert, oder wie `Decimal` intern serialisiert wird.
* C) **Erzeuge Tests** mit `pytest` + FastAPI `TestClient` für die Endpoints.

Welche Option willst du als Nächstes?
