from data import import_game, import_todays_game, get_current_date_time, get_update_time, is_game_today
 
def run():
    
    is_running = True #keeps app running
    last_import_attempted = get_current_date_time().split('.')[0] #initialized import attempted date
    update_date = ""
    update_time = "2401" #impossible for generate current_time to be higher, therefor will not trigger update
    
    if is_game_today(last_import_attempted): #if there is a game today, import
        import_todays_game() #imports todays game if there is one, otherwise returns false and does nothing
        update_datetime = get_update_time(last_import_attempted) #gets the time to update the score
        update_date = update_datetime.split('.')[0]
        update_time = update_datetime.split('.')[1]
   
    while is_running:
        current_datetime = get_current_date_time() #gets current datetime
        current_date = current_datetime.split('.')[0] 
        current_time = current_datetime.split('.')[1]
        
        if current_date != last_import_attempted: #if it is a new day
           
            if is_game_today(current_date): #attempts to import the game for that given day, if there is it imports and returns true, otherwise returns false and does nothing
                import_todays_game()
                update_datetime = get_update_time(current_datetime) #gets the time to update the score
                update_date = update_datetime.split('.')[0]
                update_time = update_datetime.split('.')[1]
                last_import_attempted = current_date #since game was imported, makes sure that it is not imported again
           
            else:
                last_import_attempted = current_date #if there is no game for given day, changes imported date
        
        elif current_date == update_date and int(current_time) > int(update_time): #if 
            #if previous game is marked as completed(use last_import_attempted to check):
                #Update the scores
                #update_date = ""
                #update_time = "2401"
            #else:
                #change add 30 minutes to update time (need function for that)

        
    #TODO - Check + update recent game function
    #While Loop - constantly checks date and time
    #If date is different - checks if import for today
    #True - grabs game time, waits until 3 hours after gametime, imports every x minute until game status is played
    #False - waits until date is different again
    return False
def main():
    return None

if __name__ == "__main__":
    main()
