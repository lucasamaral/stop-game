from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User)
    score = models.IntegerField() #player score through history


class Field(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=7)

    def __unicode__(self):
        return self.name


class Letter(models.Model):
    letter = models.CharField(max_length=1)
    pre_selected = models.BooleanField()

    def __unicode__(self):
        return self.letter


class GameRoom(models.Model):
    name = models.CharField(max_length=30)
    players = models.ManyToManyField(Player, through='PlayerGameRoom')
    round_number = models.IntegerField()
    fields = models.ManyToManyField(Field)
    round_duration = models.PositiveIntegerField() #time in seconds
    minimum_absolute_stop_time = models.PositiveIntegerField()
    selected_letters = models.ManyToManyField(Letter, through='Selection')
    is_protected = models.BooleanField(default=False)

    def new_round(self):
        pass


class GameRound(models.Model):
    cur_letter = models.CharField(max_length=1)
    room = models.ForeignKey(GameRoom)
    round_number = models.IntegerField()


class Answer(models.Model):
    roundd = models.ForeignKey(GameRound)
    player = models.ForeignKey(Player)
    ans = models.CharField(max_length=50)
    valid = models.BooleanField()
    points = models.IntegerField()


class PlayerGameRoom(models.Model):
    room = models.ForeignKey(GameRoom)
    player = models.ForeignKey(Player)
    current_score = models.IntegerField()


class Selection(models.Model):
    letter = models.ForeignKey(Letter)        
    game = models.ForeignKey(GameRoom)
    already_selected = models.BooleanField()
        