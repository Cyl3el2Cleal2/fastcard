from fastapi import APIRouter

router = APIRouter()

@router.get('/game')
def game():
  return 'Welcome to game api'