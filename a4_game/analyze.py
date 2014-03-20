def destroy_prob(attacker, defender, current_tile, turns):
    """
    This function finds out the probability of destroying a defender sitting on
    current_tile, given an attacker and number of turns.

    It returns a list turns+1 in length containing at each index the probability of
    destroying that unit on that turn.

    phony_damage is used here as well as in the gui to prevent the actual damage from
    being shown for units that have a chance at missing (just stormtroopers for now).
    """
    prob_list = list()
    memo = {}

    if attacker.phony_damage == True:
        d = attacker.get_false_damage(defender, current_tile) # get falsified attacker damage
    else:
        d = attacker.get_damage(defender, current_tile) # get attacker damage
    for turn in range(turns + 1):
        prob_list.append(memo_prob(d, defender.health, turn, memo)) # append probability at that turn to prob
        
    return prob_list

def memo_prob(damage, health, turn, memo = {}):
    """
    Our program implements a top-down approach where it will constantly
    look at what the probability is when there are turn-1 turns left, up
    until there are zero turns left.

    We've memoized and made it recursive to reduce the runtime as much as
    possible. Even the order in which it checks if the modifier is -1,0,1,2
    is ordered in such a way that it has to got through a minimal number of
    checks.

    Our dictionary memoizes the health left and the turn number to prevent
    unecessary recalling, and stores the probability of destroying the unit.
    """

    # prevent pointless calling for calculations already done
    if (health, turn) in memo:
        return memo[(health, turn)]
    
    total_prob = 0
    
    # if a branch depletes health before turns left is zero, immediately return False
    if turn == 0 or health <= 0:
        return health <= 0

    for modifier in range(-1, 3):
        if modifier is -1 or modifier is 1:
            percent = 0.2
        elif modifier is 0:
            percent = 0.5
        elif modifier is 2:
            percent = 0.1

        # total_prob is the probability of killing a unit multiplied by a simple
        # 'True or False: is the unit dead?'
        total_prob += percent * memo_prob(damage, health - (damage + modifier), turn-1, memo)

    memo[(health, turn)] = total_prob
    return memo[(health, turn)]
