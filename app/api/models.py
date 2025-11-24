from app.database import Base
from sqlalchemy import (
    String,
    ForeignKey,
    BigInteger
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)


class Player(Base):
    __tablename__ = 'players'

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique = True)
    username: Mapped[str] = mapped_column(String(255), unique = True, nullable = True)
    prize_id: Mapped[int] = mapped_column(ForeignKey('prizes.id'), nullable = True)
    has_spun: Mapped[bool] = mapped_column(default = False)

    prize: Mapped["Prize"] = relationship(
        'Prize',
        back_populates = 'players'
    )

    def __repr__(self) -> str:
        return f'User: {self.username}'


class Prize(Base):
    __tablename__ = 'prizes'

    name: Mapped[str] = mapped_column(String(255), unique = True)
    quantity: Mapped[int] = mapped_column(default = 0)

    players: Mapped[list["Player"]] = relationship(
        'Player',
        back_populates = 'prize',
        cascade = 'all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f'Prize: {self.name}'
