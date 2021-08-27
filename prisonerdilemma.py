import player as p
import uuid
import random
import tree
import matplotlib.pyplot as plt
import sqlite3

# Standard Prisoner's Dilemma Payoff Matrix


def evaluation(moveA, moveB):
    if moveA == 'c' and moveB == 'c':
        return 3, 3
    if moveA == "c" and moveB == "d":
        return -1, 5
    if moveA == "d" and moveB == "c":
        return 5, -1
    if moveA == "d" and moveB == "d":
        return 0, 0

# Generate score for Agent A and B, respectively, for a single round of Iterated Prisoner's Dilemma of length gene_length


def generate_score(A, B, gene_length):
    ASum = 0
    BSum = 0
    for i in range(gene_length):
        moveA = A.move(B, i)
        moveB = B.move(A, i)
        AScore, BScore = evaluation(moveA, moveB)
        ASum += AScore
        BSum += BScore
    return ASum, BSum


''' 
Higher-level Simulation Class 

'''


class Simulation():
    def __init__(self, pool_size, gene_length, totalrounds, predetermined):
        self.poolsize = pool_size
        self.genesize = gene_length
        self.totalgenetic = 0
        self.totalrounds = totalrounds
        self.players = []
        self.strategies = ['Cu', 'Du', 'Random', 'Cp', 'TFT', 'TFTT', 'Prober']
        self.game_hashmap = {}
        self.tree_hashmap = {}
        self.genetic_instance = {}
        self.experimenttitle = ""
        self.geneticpercentage = {}
        self.geneticcount = {}
        self.reverse_lookup = {}
        strategy_hashmap = {}
        strategy_hashmap['Cu'] = 'a'
        strategy_hashmap['Du'] = 'b'
        strategy_hashmap['Random'] = 'c'
        strategy_hashmap['Cp'] = 'd'
        strategy_hashmap['TFT'] = 'e'
        strategy_hashmap['TFTT'] = 'f'
        strategy_hashmap['Prober'] = 'g'
        # Only these strategies will be included in the simulation
        implemented = ['Cu', 'Du', 'Random', 'Cp', 'TFT', 'TFTT', 'Prober']

        # Set up sqlite3 database
        conn = sqlite3.connect('players.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE players
             (strategy text, size real, bitstring text, id text, original text)''')
        # Initialization
        # Populating the reverse look up dictionary
        for i in strategy_hashmap:
            self.reverse_lookup[strategy_hashmap[i]] = i
        if predetermined:
            # Adding new players to the simulation
            for strategy in strategy_hashmap:
                if strategy in implemented:
                    for _ in range(self.poolsize):
                        new = p.Player(strategy,
                                       self.genesize)
                        self.players.append(new)
                        # Add to database
                        c.execute("INSERT INTO players VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                            strategy, self.genesize, new.strategy_bitstring, new.id, "True"))
                        conn.commit()
            # Creating tree object for each player
            for player in self.players:
                newnode = tree.TreeNode(player, player.id)
                self.tree_hashmap[player] = newnode
            # Populating initial genomic statistics
            for i in implemented:
                self.totalgenetic += self.poolsize * self.genesize
                self.genetic_instance[strategy_hashmap[i]
                                      ] = self.poolsize * self.genesize

    ''' 
    Simulation 1: 
        Initial Population is Predetermined
        Parameters:
            - Fixed Reproduction Rate: reprod_rate
        Evolution Schema:
            - Play iterated dilemma game in a round-robin format (every player plays against every other player)
            - Top reprod_rate fraction of total population mate in a random manner
                - Each reproduction event produces two offsprings
                - Reproduction uses 2-point crossover scheme
            - Species death is not taken into account
            - Overall simulation reflects a strictly-growth environment
    '''

    def sim_configuration_1(self, rp):
        # Open database connection
        conn = sqlite3.connect('players.db')
        c = conn.cursor()
        reprod_rate = rp
        self.experimenttitle = "Configuration 1 - Strictly-Growth (SG), Fixed Growth Rate (FGR) - SGFGR"
        for round in range(self.totalrounds):
            self.process_count()
            self.process_percentage()
            # Reset game hashmap
            self.game_hashmap = {}
            for player in self.players:
                self.game_hashmap[player] = 0
            for left in range(0, len(self.players)-1):
                for right in range(left+1, len(self.players)):
                    ARoundSum, BRoundSum = generate_score(
                        self.players[left],
                        self.players[right],
                        self.genesize)
                    playerA = self.players[left]
                    playerB = self.players[right]
                    print("Round: " + str(round))
                    print(playerA.strategy_bitstring +
                          " versus " + playerB.strategy_bitstring)
                    self.game_hashmap[playerA] += ARoundSum
                    self.game_hashmap[playerB] += BRoundSum
            self.game_hashmap = {k: v for k, v in sorted(
                self.game_hashmap.items(), key=lambda item: item[1], reverse=True)}
            n_opp = int(reprod_rate * len(self.players))
            matepool = []
            for i, j in enumerate(list(self.game_hashmap.keys())):
                if i > n_opp:
                    break
                else:
                    matepool.append(j)
            mate_times = len(matepool)
            for _ in range(mate_times):
                mates = random.sample(matepool, 2)
                A = mates[0]
                B = mates[1]
                print("Round: " + str(round))
                print("Mates: " + A.strategy_bitstring +
                      ", " + B.strategy_bitstring)
                child1, child2 = A.crossover(B)
                # Add to database
                c.execute("INSERT INTO players VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                    "N/A", child1.size, child1.strategy_bitstring, child1.id, "False"))
                c.execute("INSERT INTO players VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                    "N/A", child2.size, child2.strategy_bitstring, child2.id, "False"))
                conn.commit()
                for i in child1.strategy_bitstring:
                    self.genetic_instance[i] += 1
                    self.totalgenetic += 1
                for i in child2.strategy_bitstring:
                    self.genetic_instance[i] += 1
                    self.totalgenetic += 1
                child1node = tree.TreeNode(child1, child1.id)
                child2node = tree.TreeNode(child2, child2.id)
                self.tree_hashmap[child1] = child1node
                self.tree_hashmap[child2] = child2node
                ANode = self.tree_hashmap[A]
                BNode = self.tree_hashmap[B]
                ANode.left = child1node
                ANode.right = child2node
                BNode.left = child1node
                BNode.right = child2node
                self.players.append(child1)
                self.players.append(child2)
                self.game_hashmap[child1] = 0
                self.game_hashmap[child2] = 0
            for i in self.game_hashmap:
                print(i.strategy_bitstring, self.game_hashmap[i])
            self.print_players()
        conn.close()
        self.plot_percentage_count()

    def print_players(self):
        for player in self.players:
            print(player.id, player.strategy_bitstring)

    def traverse_players(self):
        for player in self.players:
            print("New Traversal")
            print("----------------")
            self.tree_hashmap[player].inorder()

    def process_percentage(self):
        for i in self.genetic_instance:
            percentage = float(self.genetic_instance[i]) / self.totalgenetic
            if i not in self.geneticpercentage:
                self.geneticpercentage[i] = [percentage]
            else:
                self.geneticpercentage[i].append(percentage)
            print(str(i) + ": " + str(percentage))

    def process_count(self):
        for i in self.genetic_instance:
            count = self.genetic_instance[i]
            if i not in self.geneticcount:
                self.geneticcount[i] = [count]
            else:
                self.geneticcount[i].append(count)
            print(str(i) + ": " + str(count))

    def generate_percentage_plot(self):
        time = list(range(0, self.totalrounds))
        for i in self.geneticpercentage:
            print(self.geneticpercentage[i])
            with plt.style.context('seaborn-darkgrid'):
                plt.plot(
                    time, self.geneticpercentage[i], '-o', label=self.reverse_lookup[i])

        plt.xlabel("Epoch")
        plt.ylabel("Percentage of Total Population")
        plt.suptitle("Percentage of Total Population vs Epoch")
        plt.legend()
        plt.show()

    def generate_number_plot(self):
        time = list(range(0, self.totalrounds))
        for i in self.geneticcount:
            print(self.geneticcount[i])
            with plt.style.context('seaborn-darkgrid'):
                plt.plot(time, self.geneticcount[i],
                         '-o', label=self.reverse_lookup[i],)
        plt.xlabel("Epoch")
        plt.ylabel("Agents")
        plt.legend("Agent Population vs Epoch")
        plt.show()

    def plot_percentage_count(self):
        with plt.style.context('dark_background'):
            fig, (ax1, ax2) = plt.subplots(2)
            fig.suptitle(self.experimenttitle)
        time = list(range(0, self.totalrounds))
        for i in self.geneticcount:
            print(self.geneticcount[i])
            ax1.plot(time, self.geneticcount[i],
                     '-o', label=self.reverse_lookup[i],)
        ax1.set(xlabel="Epoch", ylabel="Population")
        ax1.legend()
        for i in self.geneticpercentage:
            print(self.geneticpercentage[i])
            ax2.plot(
                time, self.geneticpercentage[i], '-o', label=self.reverse_lookup[i])
        ax2.set(xlabel="Epoch", ylabel="Population Percentage")
        ax2.legend()
        plt.show()
