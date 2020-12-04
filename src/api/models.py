from peewee import (
    Model,
    CharField,
    DateField,
    IntegerField,
    FloatField,
    TextField,
    ForeignKeyField,
    TimestampField,
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
    name = TextField(unique=True)


class Recipe(BaseModel):
    name = TextField(unique=True)
    price = IntegerField()
    cooking_time = IntegerField()
    cooking_difficulty = CharField()
    energy = FloatField()
    fat_total = FloatField()
    fat_saturates = FloatField()
    carbohydrate_total = FloatField()
    carbohydrate_sugars = FloatField()
    fiber = FloatField()
    protein = FloatField()
    cholesterol = FloatField()
    sodium = FloatField()


class MenuRecipe(BaseModel):
    menu = ForeignKeyField(Menu, backref="recipes")
    recipe = ForeignKeyField(Recipe, backref="menus")


class Ingredient(BaseModel):
    name = TextField()


class RecipeIngredient(BaseModel):
    recipe = ForeignKeyField(Recipe, backref="ingredients")
    ingredient = ForeignKeyField(Ingredient, backref="recipes")
    amount = FloatField()
    unit = TextField()


class MenuReviews(BaseModel):
    rating = IntegerField(null=False)
    comment = TextField(null=False)
    created = TimestampField(default=datetime.datetime.now)
    menu = ForeignKeyField(Menu, backref="reviews")
    user = ForeignKeyField(User, backref="menu_reviews")


class RecipeReviews(BaseModel):
    rating = IntegerField(null=False)
    comment = TextField(null=False)
    created = TimestampField(default=datetime.datetime.now)
    recipe = ForeignKeyField(Recipe, backref="reviews")
    user = ForeignKeyField(User, backref="recipe_reviews")
