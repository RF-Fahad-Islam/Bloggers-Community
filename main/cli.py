import click
from flask.cli import with_appcontext
from . import db,app
@click.command(name="create")
@with_appcontext
def create():
    db.create_all()
    
app.cli.add_acommand(create)