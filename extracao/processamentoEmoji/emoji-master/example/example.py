# -*- coding: UTF-8 -*-
import emoji


print(emoji.emojize('Water! :water_wave:'))
print(emoji.demojize(u'🌊')) # for Python 2.x
print(emoji.demojize('🌊')) # for Python 3.x

print(emoji.emojize('Bola de futebol! :soccer_ball:�?'))
emo='ReageTuna ?�?�'
print(emoji.demojize(emo)) # for Python 3.x
