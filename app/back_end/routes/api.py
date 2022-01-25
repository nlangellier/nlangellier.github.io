from fastapi import APIRouter

from .api_routes import game, leader_board

router = APIRouter(prefix='/api', tags=['API'])
router.include_router(router=game.router)
router.include_router(router=leader_board.router)
