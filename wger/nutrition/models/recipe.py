from django.db import models
from django.conf import settings
from wger.nutrition.models.ingredient import Ingredient
from wger.nutrition.models.ingredient_weight_unit import IngredientWeightUnit
from wger.utils.models import AbstractHistoryMixin, AbstractLicenseModel
from wger.nutrition.helpers import NutritionalValues

class Recipe(AbstractLicenseModel, AbstractHistoryMixin, models.Model):
    """
    Model representing a custom recipe made of multiple ingredients.
    """
    name = models.CharField(max_length=200, verbose_name="Name")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creation date")
    
    def __str__(self):
        return self.name

    def get_nutritional_values(self):
        values = NutritionalValues()
        for item in self.ingredients.all():
            values += item.get_nutritional_values()
        return values

class RecipeIngredient(models.Model):
    """
    Model representing an ingredient in a recipe.
    """
    recipe = models.ForeignKey(Recipe, related_name='ingredients', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    unit = models.ForeignKey(IngredientWeightUnit, null=True, blank=True, on_delete=models.SET_NULL)
    
    def get_nutritional_values(self):
        item_weight = self.amount
        if self.unit:
            item_weight = self.amount * self.unit.gram

        values = NutritionalValues()

        if self.ingredient.energy:
            values.energy = self.ingredient.energy * item_weight / 100
        if self.ingredient.protein:
            values.protein = self.ingredient.protein * item_weight / 100
        if self.ingredient.carbohydrates:
            values.carbohydrates = self.ingredient.carbohydrates * item_weight / 100
        if self.ingredient.carbohydrates_sugar:
            values.carbohydrates_sugar = self.ingredient.carbohydrates_sugar * item_weight / 100
        if self.ingredient.fat:
            values.fat = self.ingredient.fat * item_weight / 100
        if self.ingredient.fat_saturated:
            values.fat_saturated = self.ingredient.fat_saturated * item_weight / 100
        if self.ingredient.fiber:
            values.fiber = self.ingredient.fiber * item_weight / 100
        if self.ingredient.sodium:
            values.sodium = self.ingredient.sodium * item_weight / 100

        return values
