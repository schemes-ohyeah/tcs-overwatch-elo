from TCS_Objects import Team, Match

a, b = Team.calculate_elo(4000, 3500, -1)
print(a, b)
c, d = Team.calculate_elo(a, b, 1)
print(c, d)
e, f = Team.calculate_elo(c, d, -1)
print(e, f)

win_chance = Match.calculate_win_chance(4000, 3800)
print(win_chance)

a, b = Team.calculate_elo(3981, 4077, 1)
print(a, b)
c, d = Team.calculate_elo(a, b, 1)
print(c, d)