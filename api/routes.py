from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.tarot_engine import TarotEngine
from core.ai_interpreter import TarotInterpreter

router = APIRouter()
engine = TarotEngine()
interpreter = TarotInterpreter()


class InterpretRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=1000, description="使用者輸入的心情、煩惱、行程等")
    card_id: int = Field(..., ge=0, le=77, description="牌的 ID")
    is_reversed: bool = Field(..., description="是否逆位")


@router.post("/draw")
async def draw_card():
    """隨機抽取一張塔羅牌"""
    try:
        card = engine.draw_card()
        return {"success": True, "card": card}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"抽牌失敗: {str(e)}")


@router.post("/interpret")
async def interpret_card(request: InterpretRequest):
    """AI 解讀塔羅牌"""
    try:
        full_card = engine.get_full_card(request.card_id, request.is_reversed)
        if not full_card:
            raise HTTPException(status_code=404, detail="找不到這張牌")

        result = await interpreter.interpret(full_card, request.user_input)
        
        # 強制使用資料庫的內容，不使用 AI 隨機生成的，確保對應牌義並節省 token 依賴
        result["fortune"] = full_card["fortune"]
        result["lucky_task"] = full_card["lucky_task"]
        result["reminder"] = full_card["reminder"]
        
        return {"success": True, "interpretation": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解讀失敗: {str(e)}")
