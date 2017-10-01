from TCS_Objects import Team

a, b = Team.calculate_elo(4006.8333333333, 3987.3333333333, -1)
print(a, b)
c, d = Team.calculate_elo(a, b, 1)
print(c, d)
e, f = Team.calculate_elo(c, d, -1)
print(e, f)
