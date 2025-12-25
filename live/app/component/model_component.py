from sqlmodel import Session

from models.model import Model


def get_model(modelid, session: Session) -> Model:
  return session.query(Model).where(Model.id == modelid).one_or_none()


def get_model_by_name(modelname, session: Session) -> Model:
  return session.query(Model).where(
      Model.modelname == modelname).one_or_none()


def save_model(path2model, name, session: Session) -> Model:
  model = Model(path2model=path2model, modelname=name)
  session.add(model)
  session.commit()
