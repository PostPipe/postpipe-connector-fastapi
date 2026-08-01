from fastapi import APIRouter

router = APIRouter()

# Placeholder for auth routes (porting authController.ts)
@router.post("/login")
async def login():
    return {"status": "ok"}
