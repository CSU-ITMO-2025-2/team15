from live.app.models.model import Model
from live.app.database.database import get_session


def get_model(modelid):
    with get_session() as session:
        return session.query(Model).query(modelid).one_or_none()


def save_model(path2model):
    with get_session() as session:
        model = Model(path2model=path2model)
        session.save(model)
        session.commit()
