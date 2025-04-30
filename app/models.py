from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

ticket_mechanic = db.Table(
    "ticket_mechanic",
    Base.metadata,
    db.Column("ticket_id", db.ForeignKey("service_tickets.id")),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id"))
)

ticket_service = db.Table(
    "ticket_service",
    Base.metadata,
    db.Column("ticket_id", db.ForeignKey("service_tickets.id")),
    db.Column("service_id", db.ForeignKey("services.id"))
)

class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(320), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(16), nullable=False)
    password: Mapped[str] = mapped_column(db.String(320), nullable=False)
    
    tickets: Mapped[List['ServiceTicket']] = db.relationship(back_populates='customer', cascade="all, delete")


class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(320), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(16), nullable=False)
    salary: Mapped[float] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(db.String(320), nullable=False)
    
    tickets: Mapped[List['ServiceTicket']] = db.relationship(secondary=ticket_mechanic, back_populates='mechanics')

class ServiceTicket(Base):
    __tablename__ = "service_tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    service_date: Mapped[date] = mapped_column(nullable=False)
    VIN: Mapped[str] = mapped_column(db.String(18), nullable=False)
    servic_desc: Mapped[str] = mapped_column(db.String(320), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"))
    
    customer: Mapped['Customer'] = db.relationship(back_populates='tickets')
    mechanics: Mapped[List['Mechanic']] = db.relationship(secondary=ticket_mechanic, back_populates='tickets')
    serialized_parts: Mapped[List['SerializedPart']] = db.relationship(back_populates='ticket')
    services: Mapped[List['Service']] = db.relationship(secondary=ticket_service, back_populates='tickets')
    
class PartDescription(Base):
    __tablename__ = "parts_descriptions"
    
    id: Mapped[int] = mapped_column(primary_key=True) 
    part_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    brand: Mapped[str] = mapped_column(db.String(255), nullable=False)
    
    serialized_parts: Mapped[List['SerializedPart']] = db.relationship(back_populates='part_description') 
    
class SerializedPart(Base):
    __tablename__ = "serialized_parts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"), nullable=True)
    part_id: Mapped[int] = mapped_column(db.ForeignKey("parts_descriptions.id"), nullable=False)
    
    part_description: Mapped['PartDescription'] = db.relationship(back_populates='serialized_parts')
    ticket: Mapped['ServiceTicket'] = db.relationship(back_populates='serialized_parts')
    
class Service(Base):
    __tablename__ = "services"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(320), nullable=False)
    labor_hours: Mapped[float] = mapped_column(nullable=False)
    labor_rate: Mapped[float] = mapped_column(nullable=False, default=100)
    
    tickets: Mapped[List['ServiceTicket']] = db.relationship(secondary=ticket_service, back_populates='services')
