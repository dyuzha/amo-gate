from datetime import datetime
from pydantic import BaseModel, Field
from typing import ClassVar, Literal, Optional


class TextRenderMixin:
    icon: ClassVar[str] = ""

    def build_text(self, *parts: str | None) -> str:
        return "\n".join(filter(None, parts))

    def render_list(self, items: list) -> str:
        return "\n".join(i.to_text for i in items) if items else ""



class PayDataMixin(BaseModel):
    pay: bool | None = None
    price: int | None = None
    paid: bool | None = None

    def get_paid_price(self) -> int:
        return self.price if self.pay and self.paid and self.price else 0

    @property
    def text_payed_data(self) -> str | None:
        if self.pay is True:
            icon = "✅" if self.paid else "❌"
            return f"{icon} {self.price} ₽" if self.price else icon

        if self.pay is False:
            return "Бесплатно"

        return None


class VisitStatusMixin:
    status: Literal["set", "done", "cancel"]
    visit_date: datetime | None = None

    @property
    def text_visit_date(self) -> str | None:
        return (
            self.visit_date.strftime("%d.%m.%Y %H:%M")
            if self.visit_date else None
        )

    @property
    def text_status(self) -> str | None:
        return {
            "set": "⏳ Назначено",
            "done": "✔️ Выполнено",
            "cancel": "✖️ Отменено",
        }.get(self.status)


class Treatment(PayDataMixin, VisitStatusMixin, TextRenderMixin):
    id: int = Field(alias="item_id")
    action: str

    # icon: ClassVar[str] = "💉"

    @property
    def to_text(self) -> str:
        return self.build_text(
            f"{self.icon} {self.action}",
            self.text_payed_data,
            self.text_visit_date,
            self.text_status,
        )


class Lab(PayDataMixin, VisitStatusMixin, TextRenderMixin):
    id: int = Field(alias="lab_item_id")
    action: str = Field(alias="lab")
    treatment_item_id: Optional[int] = None

    # icon: ClassVar[str] = "🧪"

    @property
    def to_text(self) -> str:
        return self.build_text(
            f"{self.icon} {self.action}",
            self.text_payed_data,
            self.text_visit_date,
            self.text_status,
            # f"treatment_item_id: {self.treatment_item_id}",
        )
    # if self.treatment_item_id is not None:
            # parts.append(f'treatment_item_id: {self.treatment_item_id}')


class Packet(PayDataMixin, TextRenderMixin):
    id: int = Field(alias="packet_id")
    action: str = Field(alias="packet")
    treatments: list[Treatment] = Field(default_factory=list)

    # icon: ClassVar[str] = "📦"

    @property
    def to_text(self) -> str:
        return self.build_text(
            f"{self.icon} {self.action}",
            self.text_payed_data,
            self.render_list(self.treatments),
        )



class Complex(PayDataMixin, TextRenderMixin):
    id: int = Field(alias="complex_id")
    action: str = Field(alias="complex")
    treatments: list[Treatment] = Field(default_factory=list)
    labs: list[Lab] = Field(default_factory=list)

    # icon: ClassVar[str] = "🧩"

    @property
    def to_text(self) -> str:
        return self.build_text(
            f"{self.icon} {self.action}",
            self.text_payed_data,
            self.render_list(self.treatments),
            self.render_list(self.labs),
        )



class MC(BaseModel, TextRenderMixin):
    created_at: datetime = Field(alias='createdAt')
    id: int
    name: str
    birthday: datetime
    phone: Optional[str] = None
    email: Optional[str] = None
    lead_id: int
    treatments: list[Treatment] = Field(default_factory=list)
    labs: list[Lab] = Field(default_factory=list)
    packets: list[Packet] = Field(default_factory=list)
    complex: list[Complex] = Field(default_factory=list)


    @property
    def paid_price(self) -> int:
        total: int = 0
        for unit in self._paid_units:
            for p in unit:
                total += p.get_paid_price()
        return total


    @property
    def total_price(self) -> int:
        total: int = 0
        for paid in self._paid_units:
            for p in paid:
                total += p.price
        return total


    @property
    def tretments_text(self) -> str:
        return self.render_list(self.treatments)


    @property
    def labs_text(self) -> str:
        return self.render_list(self.labs)


    @property
    def packets_text(self) -> str:
        return self.render_list(self.packets)


    @property
    def complex_text(self) -> str:
        return self.render_list(self.complex)


    @property
    def _paid_units(self):
        return [self.treatments, self.labs, self.packets, self.complex]
