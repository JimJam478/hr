import datetime
import logging
from typing import List

from sqlalchemy import String, Integer, Date, create_engine, ForeignKey, UniqueConstraint, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

class HRDBBase(DeclarativeBase):
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class Employee(HRDBBase):
    __tablename__ = "hrms_employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(100))
    rank_id: Mapped[int] = mapped_column(ForeignKey("hrms_designation.id"))
    rank: Mapped['Designation'] = relationship(back_populates="employees") 

class Leaves(HRDBBase):
    __tablename__ = "hrms_leaves"
    __table_args__ = (
        UniqueConstraint("date","employee_id"),
        )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date())
    reason: Mapped[str] = mapped_column(String(50))
    employee_id: Mapped[int] = mapped_column(ForeignKey("hrms_employees.id"))

class Designation(HRDBBase):
    __tablename__ = "hrms_designation"
    id: Mapped[int] = mapped_column(primary_key=True)
    Designation: Mapped[str] = mapped_column(String(50))
    max_leaves: Mapped[int] = mapped_column(Integer)
    employees: Mapped["Employee"] = relationship(back_populates="rank")

def create_database_tables(db_uri):
    logger = logging.getLogger("HR")
    engine = create_engine(db_uri)
    HRDBBase.metadata.create_all(engine)
    logger.info("Created tables in database")

def get_session(db_uri):
    engine = create_engine(db_uri)
    Session = sessionmaker(bind = engine)
    session = Session()
    return session
