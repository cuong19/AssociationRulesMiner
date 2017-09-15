from fim import fpgrowth
from src.association_rules.association_rule import AssociationRule

class FPGrowth:
    def __init__(self, transactions, support_threshold, min_set_size, max_set_size):
        self.transactions = transactions
        self.support_threshold = support_threshold
        self.min_set_size = min_set_size
        self.max_set_size = max_set_size
        self.rules = []
        self.mine()

    def mine(self):
        results = fpgrowth(tracts=self.transactions, target="r", supp=self.support_threshold,
                                zmin=self.min_set_size+1, zmax=self.max_set_size+1,report='scl')
        for result in results:
            rule = AssociationRule(result[1], result[0], result[2], result[3], result[4])
            self.rules.append(rule)

    def pretty_print(self):
        i = 0
        for rule in self.rules:
            i+=1
            print("Rule #" + str(i) + ":")
            print("\tAntecedents: " + str(rule.antecedents))
            print("\tConsequent: " + str(rule.consequent))
            print("\tReport:")
            print("\t\tSupport: " + str(rule.support))
            print("\t\tConfidence: " + str(rule.confidence))
            print("\t\tLift: " + str(rule.lift))

