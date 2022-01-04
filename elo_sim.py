from random import gauss, shuffle
import matplotlib.pyplot as plt
from math import exp


# each 'rank' is a 100 mmr range

# actual elo represents a player's true rank
# current elo is a player's current rank

class Player:
    player_number = 0
    def __init__(self, elo, ideal_elo):
        self.elo = elo
        self.ideal_elo = ideal_elo
        self.number = Player.player_number
        Player.player_number += 1

    # performance in one game, modeled by a normal distribution around actual elo, assume a standard deviation in
    # performance of 1 rank (100 elo)
    def performance(self):
        return gauss(self.ideal_elo, 100)
    

# simple game, each team generates scores based on their skill and sums them up
# redistribute elo based on result + individual performance
# elo redistribution = -10 + 20 * (if team won) + (individual_score - match_average) / 10
def fight(team1, team2, league_average):
    assert(len(team1) == len(team2))
    scores1 = [player.performance() for player in team1]
    scores2 = [player.performance() for player in team2]

    t1_win = sum(scores1) > sum(scores2)
    match_average = (sum(scores1) + sum(scores2)) / (2 * len(team1))

    # redistribute elo    
    for i, player in enumerate(team1):
        player.elo += -10 + 20 * int(t1_win) + (scores1[i] - league_average) / 5

        # this is the step that should flatten out the distribution, we don't allow negative elo (don't know if any game does)
        if player.elo < 0:
            player.elo = 0

    for i, player in enumerate(team2):
        player.elo += -10 + 20 * int(not t1_win) + (scores2[i] - league_average) / 5
        if player.elo < 0:
           player.elo = 0

# generate a list of fair games from a population
def generate_teams(pop, league_size, team_size):
    assert(len(pop) % league_size == 0)
    assert(league_size % team_size == 0)
    
    population = list(sorted(pop, key=lambda p: p.elo))

    # sort people into leagues
    leagues = []
    for i in range(len(population)//league_size):
        league = population[:league_size]
        leagues.append(league)
        population = population[league_size:]
        
    # generate games for each league until we're empty

    games = []
    for league in leagues:
        shuffle(league)
        league_average = sum([p.elo for p in league]) / len(league)
        while len(league) > 0:
            team1 = league[:team_size]
            league = league[team_size:]
            team2 = league[:team_size]
            league = league[team_size:]
            games.append([team1, team2, league_average])
    return games
            


population_size = 10000
average_skill = 500
initial_elo = 250
generations = 1000
team_size = 5
league_size = 1000
population_cycling = True

skill_gain_function = lambda s: 10 / (1 + exp(s / (500/2)))

# player skill will be normally distributed around 500, with 0 being 3 standard deviations away
population = []
while len(population) < population_size:
    # done this way in case I want to modify how we make player distribution
    p = Player(initial_elo, gauss(500,500/4))
    population.append(p)

for generation in range(generations):
    
    
    if generation % 200 == 0:
        distribution = [p.elo for p in population]
        
        print("Generation %d" % generation)
        print("Total elo: %f" % sum(distribution))
        distribution = [p.elo for p in population if abs(p.elo) < 1500]
        
        plt.hist(distribution, bins = 2 * population_size // league_size)
        plt.show()

        plt.scatter([p.ideal_elo for p in population if abs(p.elo) < 1500], distribution)
        #plt.xlim(0,1500)
        #plt.ylim(0,1500)
        plt.show()


        if population_cycling:
            # phase out a random 10% of the population
            shuffle(population)
            population = population[population_size//10:]
            while len(population) < population_size:
                # done this way in case I want to modify how we make player distribution
                p = Player(initial_elo, gauss(500,500/4))
                population.append(p)

            

        
    games = generate_teams(population, league_size, team_size)
    for game in games:
        fight(game[0], game[1], game[2])

    for p in population:
        p.ideal_elo += skill_gain_function(p.ideal_elo) 

    
    
    




    
    
