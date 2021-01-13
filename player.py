import random
import uuid


class Player():
    def __init__(self, strategy, size, isPure = True, genes = None, parents = None):
        strategy_hashmap = {}
        strategy_hashmap['Cu'] = 'a'
        strategy_hashmap['Du'] = 'b'
        strategy_hashmap['Random'] = 'c'
        strategy_hashmap['Cp'] = 'd'
        strategy_hashmap['TFT'] = 'e'
        strategy_hashmap['TFTT'] = 'f'
        strategy_hashmap['Prober'] = 'g'

        def generate_bitstring(s, size):
            return strategy_hashmap[s] * size
        self.movehistory = []
        self.size = size
        self.id = str(uuid.uuid1())
        if isPure:
            self.strategy_bitstring = generate_bitstring(strategy, self.size)
            self.parents = None
            self.children = None
        else:
            self.strategy_bitstring = genes
            self.children = None
            self.parents = parents

    def crossover(self, mate):
        assert(self.size == mate.size)
        left = random.randint(0, self.size//2)
        right = random.randint(self.size//2, self.size)
        me_left = self.strategy_bitstring[0:left]
        mate_left = mate.strategy_bitstring[0:left]
        me_mid = self.strategy_bitstring[left:right]
        mate_mid = mate.strategy_bitstring[left:right]
        me_right = self.strategy_bitstring[right:]
        mate_right = mate.strategy_bitstring[right:]
        childA_bitstring = me_left + mate_mid + me_right
        childB_bitstring = mate_left + me_mid + mate_right
        childA = Player(None, self.size, False,
                        childA_bitstring, [self, mate])
        childB = Player(None, self.size, False,
                        childB_bitstring, [self, mate])
        self.children = [childA, childB]
        mate.children = [childA, childB]
        return childA, childB

    def move(self, opp, moveindex):
        strategy = self.strategy_bitstring[moveindex]
        previndex = moveindex - 1
        if strategy == "a":
            self.movehistory.append("c")
            return "c"

        if strategy == "b":
            self.movehistory.append("d")
            return "d"

        if strategy == "c":
            move = "c" if random.random() > 0.5 else "d"
            self.movehistory.append(move)
            return move

        if strategy == "d":
            coop_prob = 0.7
            move = "c" if random.random() > 1 - coop_prob else "d"
            self.movehistory.append(move)
            return move

        if strategy == "e":
            if moveindex == 0:
                self.movehistory.append("c")
                return "c"
            else:
                opp_prev = opp.movehistory[previndex]
                self.movehistory.append(opp_prev)
                return opp_prev

        if strategy == 'f':
            if moveindex == 0 or moveindex == 1:
                self.movehistory.append("c")
                return "c"
            else:
                opp_prev_1 = opp.movehistory[previndex]
                opp_prev_2 = opp.movehistory[previndex-1]
                if opp_prev_1 == "d" and opp_prev_2 == "d":
                    self.movehistory.append(opp_prev_1)
                    return opp_prev_1
                else:
                    self.movehistory.append("c")
                    return "c"
        if strategy == "g":
            moveset = ["d", "c", "c"]
            if moveindex in [0, 1, 2]:
                return moveset[moveindex]
            if moveindex >= 3:
                if opp.movehistory[2] == "c" and opp.movehistory[1] == "c":
                    self.movehistory.append("d")
                    return "d"
                else:
                    opp_prev = opp.movehistory[previndex]
                    self.movehistory.append(opp_prev)
                    return opp_prev
