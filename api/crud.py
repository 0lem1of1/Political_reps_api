from sqlalchemy.orm import Session, joinedload
from . import models

def get_representatives_by_zip(db: Session, zip_code: str):
    """
    Finds a geography by its ZIP code and returns all associated representatives.
    """
    mappings = (
        db.query(models.RepGeographyMap)
        .filter(models.RepGeographyMap.geography_zip_code == zip_code)
        .options(joinedload(models.RepGeographyMap.representative))
        .all()
    )

    if not mappings:
        return None

    #formatting
    representatives_list = []
    for mapping in mappings:
        rep = mapping.representative
        representatives_list.append({
            "name": rep.name,
            "title": rep.title,
            "branch": rep.branch,
        })
        
    return representatives_list
