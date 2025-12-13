from functools import wraps


def transaction(func):
  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Ищем сессию в аргументах (FastAPI передает её как kwargs)
    session = kwargs.get('session')
    if not session:
      # Если сессия не в kwargs, пробуем найти среди позиционных (редко нужно)
      return await func(*args, **kwargs)

    try:
      result = await func(*args, **kwargs)
      session.commit()  # Авто-коммит
      return result
    except Exception as e:
      session.rollback()  # Авто-откат
      raise e  # Пробрасываем ошибку дальше (чтобы её поймал Exception Handler)

  return wrapper
