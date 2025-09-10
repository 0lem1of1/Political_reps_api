from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Geography(Base):
    __tablename__ = "geography"
    
    zip_code = Column(String(5), primary_key=True, index=True)
    city = Column(String)
    state = Column(String)
    district = Column(String)

    representatives_map = relationship("RepGeographyMap", back_populates="geography")

class Representative(Base):
    __tablename__ = "representatives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    title = Column(String)
    branch = Column(String)

    geographies_map = relationship("RepGeographyMap", back_populates="representative")

class RepGeographyMap(Base):
    __tablename__ = "rep_geography_map"

    representative_id = Column(Integer, ForeignKey("representatives.id"), primary_key=True)
    geography_zip_code = Column(String(5), ForeignKey("geography.zip_code"), primary_key=True)

    representative = relationship("Representative", back_populates="geographies_map")
    geography = relationship("Geography", back_populates="representatives_map")
