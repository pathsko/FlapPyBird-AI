class Perceptron:
    def __init__(self, activation, weights) -> None:
        self.weights = weights
        self.activation = activation

    def __copy__(self):
        return Perceptron(self.activation, self.weights)

    def predict(self, X):
        if len(X) != len(self.weights) - 1:
            raise Exception("Wrong input size")
        score = 0
        # print(self.weights[:len(self.weights)-1])
        for x, w in zip(X, self.weights[: len(self.weights) - 1]):
            score += x * w
        score += self.weights[len(self.weights) - 1]
        return self.activation(score)
