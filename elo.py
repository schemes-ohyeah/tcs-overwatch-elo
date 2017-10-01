r_1 = 4100
r_2 = 4000

R_1 = pow(10, r_1 / 400)
R_2 = pow(10, r_2 / 400)

E_1 = R_1 / (R_1 + R_2)
E_2 = R_2 / (R_1 + R_2)

S_1 = 0
S_2 = 1

K = 50

r_1prime = r_1 + K * (S_1 - E_1)
r_2prime = r_2 + K * (S_2 - E_2)

print(r_1prime)
print(r_2prime)