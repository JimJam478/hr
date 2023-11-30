import datetime
import logging
from typing import List

from sqlalchemy import String, Integer, Date, create_engine, ForeignKey, UniqueConstraint, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker