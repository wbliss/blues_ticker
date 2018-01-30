for temperature in [56, 56, 76, 87]:
    if temperature >= 0 and temperature <= 49:
        current_temp = temperature + 40
    elif temperature < 0:
        current_temp = temperature + 90
    elif temperature >= 50 and temperature <=99:
        current_temp = (temperature + 40) % 89 + 39
    else:
        current_temp = (temperature + 40) % 89 - (temperature % 89)



print("The temperature is", current_temp,)
