from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import traceback
from oo import get_checkpoints, get_db

router = APIRouter(prefix="/db_funcs", tags=["funcs"])


@router.get("/get_function")
async def get_function(usecase_name: str = Header(...)):
    try:
        res = get_db(usecase_name=usecase_name)
        return JSONResponse(res)
    except Exception as e:
        traceback.print_exc()
        return HTTPException(str(e), status_code=500)


@router.get("/get_checkpoints")
async def get_op():
    try:
        res = await get_checkpoints()
        return JSONResponse(res, status_code=200)
    except Exception as e:
        return HTTPException(str(e), status_code=500)
