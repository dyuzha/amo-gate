from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional


STATUS_MAP = {
    "booked": "Забронировано",
    "checkin": "Проживает",
    "checkout": "Выехал",
    "cancel": "Отменено",
    "waiting": "В ожидании"
}


class BillData(BaseModel):
    billNum: Optional[str] = None
    billSum: Optional[str] = None
    billPaidSum: Optional[str] = None
    # billNum: str
    # billSum: str
    # billPaidSum: str


class Money(BaseModel):
    total: int
    paid: int


class Guest(BaseModel):
    fio: Optional[str] = None
    birthday: Optional[str] = None
    stayCount: Optional[int] = None
    roomCategory: Optional[str] = None
    ageGroup: Optional[str] = None
    cure: Optional[str] = None
    uid: Optional[str] = None
    billNum: Optional[int] = None

    @field_validator("billNum", mode="before")
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class ExtData(BaseModel):
    guests: list[Guest] = Field(default_factory=list)

    @property
    def guestsText(self) -> str:
        if self.guests is not None:
            return "\n".join(
                    f'{g.fio}\n'
                    f'Дата рождения: {g.birthday}\n'
                    f'Stay count: {g.stayCount}\n' #
                    f'Категория номера: {g.roomCategory}\n'
                    f'Возрастная группа: {g.ageGroup}\n'
                    f'Направление: {g.cure}\n'
                    f'UID: {g.uid}\n' #
                    f'Счет №: {g.billNum}\n' #
                for g in self.guests
            )
        return ''


class Booking(BaseModel):
    status: Literal[
            "Забронировано", "Проживает", "Выехал", "Отменено", "В ожидании"
            ]
    bookedAt: datetime
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    checkin: datetime
    checkout: datetime
    money: Money
    id: int
    lead_id: str
    docNum: int
    billData: List[BillData] = Field(default_factory=list)
    extData: ExtData

    @property
    def billDataText(self) -> str:
        if len(self.billData) != 0:
            return "\n".join(
                    f'Счет №: {b.billNum}\n'
                    f'Сумма: {b.billSum}\n'
                    f'Оплачено: {b.billPaidSum}\n'
                for b in self.billData
            )
        return ''

    @property
    def extDataText(self) -> str:
        return self.extData.guestsText

    @field_validator("status", mode="before")
    def map_status(cls, v):
        return STATUS_MAP.get(v, v)
