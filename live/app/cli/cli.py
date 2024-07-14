from datetime import datetime

import click
from component.balance_component import add_balance, load_balance
from component.user_component import add_admin, add_client, get_user_by_login
from database.database import get_session
from ml.rabbitapi import send_message2rabbit
from models.model import Task
from component.data_component import get_by_path, upload_data
from component.model_component import get_model_by_name, save_model


# from ml.rabbitapi import send_message2rabbit


@click.group()
def cli():
    pass


@cli.command()
@click.option("-m", "--message")
def send_prediction_message(message: str):
    print("Message:", send_message2rabbit(message))


@cli.command()
@click.option("-l", "--login")
@click.option("-p", "--password")
@click.option("-e", "--email")
@click.option("-r", "--role")
def create_user(login: str, password: str, email: str, role: str):
    if role == "admin":
        add_admin(login, email, password)
    else:
        add_client(login, email, password)


@cli.command()
@click.option("-l", "--login")
@click.option("-a", "--amount", default=0)
def increase_balance(login: str, amount: float):
    user = get_user_by_login(login)
    add_balance(user.id, amount)


@cli.command()
@click.option("-l", "--login")
def check_balance(login: str):
    user = get_user_by_login(login)
    balance = load_balance(user.id)
    if balance:
        print(f"{user.login}:", balance.value)
    else:
        print(f"{user.login}: 0")


@cli.command()
@click.option("-l", "--login")
@click.option("-d", "--path2file", default="/data/demo-client/winequality-red.csv")
@click.option("-m", "--modelname", default="rfmodel")
@click.option("-m", "--modelpath", default="/models/rf_model.pkl")
def add_task(
        login: str,
        path2file: str,
        modelname: str,
        modelpath: str
):
    with get_session() as session:
        user = get_user_by_login(login);
        data = get_by_path(path2file)
        if data is None:
            upload_data(path2file, user.id)
            data = get_by_path(path2file)

        model = get_model_by_name(modelname)
        if model is None:
            save_model(modelpath, modelname)
            model = get_model_by_name(modelname)

        task = Task(
            task_type="wine-score",
            userid=user.id,
            dataid=data.id,
            modelid=model.id,
            status="init"
        )

        session.add(task)
        session.commit()


if __name__ == "__main__":
    cli()
