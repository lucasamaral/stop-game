from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User)
    score = models.IntegerField() #player score through history


class Field(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=7)


class GameRound(models.Model):
    cur_letter = models.CharField(max_length=1)


class Letter(models.Model):
    letter = models.CharField(max_length=1)


class GameRoom(models.Model):
    name = models.CharField(max_length=30)
    players = models.ManyToManyField(Player, through='PlayerGameRoom')
    cur_round = models.ForeignKey(GameRound)
    fields = models.ManyToManyField(Field)
    round_duration = models.PositiveIntegerField() #time in seconds
    minimum_absolute_stop_time = models.PositiveIntegerField()
    selected_letters = models.ManyToManyField(Letter, through='Selection')


class Answer(models.Model):
    roundd = models.ForeignKey(GameRound)
    player = models.ForeignKey(Player)
    ans = models.CharField(max_length=50)


class PlayerGameRoom(models.Model):
    room = models.ForeignKey(GameRoom)
    player = models.ForeignKey(Player)
    current_score = models.IntegerField()


class Selection(models.Model):
    letter = models.ForeignKey(Letter)        
    game = models.ForeignKey(GameRoom)
    is_selected = models.BooleanField()
        