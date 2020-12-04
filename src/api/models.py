from peewee import (
    Model,
    CharField,
    DateField,
    IntegerField,
    FloatField,
    TextField,
    ForeignKeyField,
    TimestampField
)
import datetime
from .db import get_db

class BaseModel(Model):
    class Meta:
        database = get_db()

class User(BaseModel):
    username = CharField(unique=True)
    password = CharField(unique=True)
    api_token = CharField(unique=True)

class Menu(BaseModel):
    start_date = DateField()
    end_date = DateField()

class Recipe(BaseModel):
    name = TextField(unique=True)
    price = IntegerField()
    cooking_time = IntegerField()
    cooking_difficulty = CharField()
    energy = FloatField()
    fat_total = FloatField()
    carbohydrate_total = FloatField()
    carbohydrate_sugars = FloatField()
    fiber = FloatField()
    protein = FloatField()
    cholesterol = FloatField()
    sodium = FloatField()

class MenuRecipe(BaseModel):
    ForeignKeyField(Menu, backref='recipes')
    ForeignKeyField(Recipe, backref='menus')
    amount = FloatField()
    unit = TextField()

class Ingredient(BaseModel):
    name = TextField()

class RecipeIngredient(BaseModel):
    ForeignKeyField(Recipe, backref='ingredients')
    ForeignKeyField(Ingredient, backref='recipes')

class Reviews(BaseModel):
    rating = IntegerField(null=False)
    comment = TextField(null=False)
    created = TimestampField(default=datetime.datetime.now)

