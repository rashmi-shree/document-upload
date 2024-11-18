from fastapi import APIRouter
from app.services.nlp_processing import process_query
router = APIRouter()

@router.get("/query/")
def query_document(query: str):
    result = process_query(query)
    return {"response": result}
