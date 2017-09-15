class AssociationRule:
    def __init__(self, antecedents, consequent, support, confidence, lift):
        self.antecedents = antecedents
        self.consequent = consequent
        self.support = support
        self.confidence = confidence
        self.lift = lift
