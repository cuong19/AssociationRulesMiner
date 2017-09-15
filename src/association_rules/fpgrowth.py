from fim import fpgrowth


class FPGrowth:
    def __init__(self, transactions, support_threshold, min_set_size, max_set_size):
        self.transactions = transactions
        self.support_threshold = support_threshold
        self.min_set_size = min_set_size
        self.max_set_size = max_set_size
        self.results = None
        self.mine()

    def mine(self):
        self.results = fpgrowth(tracts=self.transactions, target="r", supp=self.support_threshold,
                                zmin=self.min_set_size+1, zmax=self.max_set_size+1,report='scl')
        return self.results

    def pretty_print(self):
        i = 0
        for result in self.results:
            i+=1
            print("Rule #" + str(i) + ":")
            print("\tAntecedents: " + str(result[1]))
            print("\tConsequents: " + str(result[0]))
            print("\tReport:")
            print("\t\tSupport: " + str(result[2]))
            print("\t\tConfidence: " + str(result[3]))
            print("\t\tLift: " + str(result[4]))

