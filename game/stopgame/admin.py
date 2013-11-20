from django.contrib import admin
from models import Field, GameRoom, GameRound, Answer, Letter, Player

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','field', 'expected_letter', 'valid', 'points')

admin.site.register(Field)
admin.site.register(GameRoom)
admin.site.register(GameRound)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Letter)
admin.site.register(Player)