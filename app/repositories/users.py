from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User, UserProfile


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, telegram_id: int, username: str | None, first_name: str | None) -> tuple[User, bool]:
        user = await self.session.scalar(
            select(User).where(User.telegram_id == telegram_id).options(selectinload(User.profile))
        )
        if user:
            user.username, user.first_name = username, first_name
            return user, False
        user = User(telegram_id=telegram_id, username=username, first_name=first_name)
        self.session.add(user)
        await self.session.flush()
        return user, True

    async def save_profile(self, user_id: int, **values: object) -> UserProfile:
        profile = await self.session.get(UserProfile, user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id, **values)
            self.session.add(profile)
        else:
            for key, value in values.items():
                setattr(profile, key, value)
        await self.session.flush()
        return profile

    async def delete_by_telegram_id(self, telegram_id: int) -> bool:
        result = await self.session.execute(delete(User).where(User.telegram_id == telegram_id))
        return bool(result.rowcount)
