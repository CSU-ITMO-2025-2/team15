from models.model import Model
from database.database import get_session


def get_model(modelid):
    with get_session() as session:
        return session.query(Model).where(Model.id == modelid).one_or_none()

    
def get_model_by_name(modelname):
    with get_session() as session:
        return session.query(Model).where(Model.modelname == modelname).one_or_none()


def save_model(path2model, name):
    with get_session() as session:
        model = Model(path2model=path2model, modelname=name)
        session.add(model)
        session.commit()
