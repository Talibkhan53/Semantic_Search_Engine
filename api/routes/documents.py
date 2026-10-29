from pathlib import Path
import logging
from fastapi import APIRouter, HTTPException, Query
from api.routes.dependencies import engine

logger = logging.getLogger(__name__)

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

@router.post("/load")
def load_document(path:str = Query(...,description="Path to a directory containing .txt files",min_length=1,),  ):
    document_path = Path(path).expanduser().resolve()

    if not document_path.exists():
        raise HTTPException(status_code=404,detail="Directory Does Not Exist")

    if not document_path.is_dir():
        raise HTTPException(status_code=400,detail="Path Must Be Directory")


    text_files = [
        file for file in document_path.iterdir()
        if file.is_file() and file.suffix.lower() == ".txt"
    ]

    if not  text_files:
        raise HTTPException(status_code=400,detail="The Directory Doesn't Contain Any .txt Files")


    try :
        embeddings = engine.prepare_data(document_path)

        return {
            "Message":"Document Indexing Completed",
            "directory":str(document_path),
            "index_files":len(embeddings),
            "files":list(embeddings.keys())
        }
    except (FileNotFoundError,ValueError) as exp:
        raise HTTPException(status_code=400,detail=str(exp)) from exp


    except Exception as exp:
          logger.exception("Unexpected failure during document indexing")
          raise HTTPException(
            status_code=500,
             detail="Document indexing failed due to an internal server error",
        ) from exp