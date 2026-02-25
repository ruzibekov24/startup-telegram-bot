from aiogram.fsm.state import State, StatesGroup

class SubmitState(StatesGroup):
    waiting_video = State()

class AnnounceState(StatesGroup):
    waiting_text = State()
    waiting_button_text = State()
    waiting_button_url = State()
    waiting_confirm = State()
