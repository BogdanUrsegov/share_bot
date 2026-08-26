from aiogram.fsm.state import State, StatesGroup


class AgreeTerms(StatesGroup):
    agree = State()