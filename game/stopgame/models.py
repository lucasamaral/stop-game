from django.db import models
from django.contrib.auth.models import User
import uuid
import datetime

class Player(models.Model):
    user = models.OneToOneField(User)
    score = models.IntegerField() #player score through history

    def __unicode__(self):
        return self.user.__unicode__()


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
    game_duration = models.PositiveIntegerField() #in rounds
    minimum_absolute_stop_time = models.PositiveIntegerField()
    selected_letters = models.ManyToManyField(Letter, through='Selection')
    is_protected = models.BooleanField(default=False)
    password = models.CharField(max_length=20, blank=True)
    hash_code = models.CharField(max_length=50, default='n')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.hash_code = uuid.uuid1().hex
        super(GameRoom, self).save(*args, **kwargs)

    def new_round(self):
        pass

    def __unicode__(self):
        return self.name


class GameRound(models.Model):
    cur_letter = models.CharField(max_length=1)
    room = models.ForeignKey(GameRoom)
    round_number = models.IntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    stopped = models.BooleanField(default=False)

    def __unicode__(self):
        return "Round {} of {}".format(self.round_number,self.room.name)


class Answer(models.Model):
    roundd = models.ForeignKey(GameRound)
    player = models.ForeignKey(Player)
    field = models.ForeignKey(Field)
    ans = models.CharField(max_length=50)
    valid = models.BooleanField()
    points = models.IntegerField()
    positive = models.IntegerField(default=0)
    negative = models.IntegerField(default=0)

    def __unicode__(self):
        return self.ans

    def expected_letter(self):
        return self.roundd.cur_letter


class PlayerGameRoom(models.Model):
    room = models.ForeignKey(GameRoom)
    player = models.ForeignKey(Player)
    current_score = models.IntegerField()

    class Meta:
        ordering = ('current_score',)


class Selection(models.Model):
    letter = models.ForeignKey(Letter)        
    game = models.ForeignKey(GameRoom)
    already_selected = models.BooleanField()
