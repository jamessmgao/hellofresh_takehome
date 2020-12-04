import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from peewee import SqliteDatabase


def get_db():
    if 'db' not in g:
        g.db = SqliteDatabase(
            current_app.config['DATABASE'],
            pragmas={
                'journal_mode': 'wal',
                'cache_size': -1 * 64000,  # 64MB
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0
            }
        )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    from . import models
    db = get_db()
    db.connect()
    db.create_tables([
        models.User,
        models.Menu,
        models.Recipe,
        models.MenuRecipe,
        models.Ingredient,
        models.RecipeIngredient,
        models.Reviews,
    ])

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
