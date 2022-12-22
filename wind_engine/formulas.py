def altitude_from_pressure(p):
    z = (1-(p/1013.25)**(1/5.255))*288.15/0.0065
    return z