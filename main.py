import matplotlib.pyplot as plt
import math

ziarno = 12345

def losowa():
    global ziarno
    ziarno = (16807 * ziarno) % 2147483647
    return ziarno / 2147483647

def gen_poisson(A, n):
    wyniki = []
    q = math.exp(-A)
    for i in range(n):
        x = -1
        s = 1.0
        while s > q:
            s *= losowa()
            x += 1
        wyniki.append(x)
    return wyniki

def gen_gauss(mu, sigma, n):
    wyniki = []
    for i in range(n):
        u1 = losowa()
        u2 = losowa()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        wyniki.append(mu + sigma * z0)
    return wyniki

N = 10000
A_param = 5
mu_param = 10
sigma_param = 2

dane_poisson = gen_poisson(A_param, N)
dane_gauss = gen_gauss(mu_param, sigma_param, N)

plt.figure(figsize=(10, 8))

plt.subplot(2, 1, 1)
plt.hist(dane_poisson, bins=range(min(dane_poisson), max(dane_poisson) + 2), align='left', rwidth=0.8, color='blue', edgecolor='black')
plt.title(f"Rozklad Poissona (A={A_param})")

plt.subplot(2, 1, 2)
plt.hist(dane_gauss, bins=40, color='green', edgecolor='black')
plt.title(f"Rozklad Gaussa (mu={mu_param}, sigma={sigma_param})")

plt.tight_layout()
plt.show()