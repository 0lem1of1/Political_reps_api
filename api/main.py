from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import get_db, engine

#sqlalchemy checks for tables and create if not there
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Civic Tracker API",
    description="An API to find political representatives for a given U.S. ZIP code.",
    version="1.0.0",
)

@app.get("/representatives", response_model=schemas.APIResponse)
def read_representatives(
    zip: str = Query(..., min_length=5, max_length=5, regex="^[0-9]{5}$", description="A 5-digit U.S. ZIP code."),
    db: Session = Depends(get_db)
):
    
    representatives = crud.get_representatives_by_zip(db, zip_code=zip)
    
    if representatives is None:
        raise HTTPException(status_code=404, detail=f"ZIP code '{zip}' not found.")
        
    return {"zip": zip, "representatives": representatives}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Civic Tracker API."}
