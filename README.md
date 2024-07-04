# FlapPyBird with AI

This project is an enhanced version of the original [FlapPyBird](https://github.com/sourabhv/FlapPyBird) game, which now includes an AI that plays the game automatically. The main objective of this project is to apply the knowledge obtained about AI and metaheuristics to solve a problem, not to improve the initial version of the game. Obviously, adding an option where the game is played by an AI does not make it more fun; in fact, it makes it lose all its enjoyment.

## Original Project

This implementation is based on the [FlapPyBird](https://github.com/sourabhv/FlapPyBird) project created by Sourabh Verma. The original code is available [here](https://github.com/sourabhv/FlapPyBird) and is licensed under the MIT License.

## AI Implementation

The AI in this project uses a simple perceptron whose parameters are optimized using a genetic algorithm. The genetic algorithm aims to maximize the score obtained by the perceptron, which takes the distance to the next and the second next pipes as input and outputs actions to control the bird

### Methodology

1. **Data Collection:** Data collection is not explicitly required for this project since the genetic algorithm evolves the perceptron parameters based on the performance during the game.
2. **Training:** The training process involves the following steps:
   - **InitAIlization:** A population of random perceptron parameters is generated.
   - **Evaluation:** Each individual's performance is evaluated by running the game and recording the score.
   - **Selection:** The best-performing individuals are selected to create the next generation.
   - **Crossover:** Selected individuals are combined to produce offspring.
   - **Mutation:** Random changes are introduced to some offspring to maintain genetic diversity.
3. **Evaluation:** The AI's performance is evaluated based on the score achieved during gameplay. Higher scores indicate better performance.

### Solution Encoding

The perceptron's parameters, which include weights and bAIses, are encoded as chromosomes in the genetic algorithm. Each chromosome is a vector of floating-point numbers representing these parameters.

### Fitness Function

The fitness function measures how well a given set of perceptron parameters performs in the game. It is defined as the score achieved by the bird using those parameters. Higher scores result in higher fitness values.

### Perceptron

The perceptron used in this project is a simple neural network with a single layer. It takes the distances to the next and the second next pipes as inputs and outputs whether the bird should flap or not.

## Installation

To run this project on your local machine, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/pathsko/FlapPyBird-AI.git
    cd FlapPyBird-AI
    ```

2. **Install the required dependencies:**

    ```bash
    make init
    ```

3. **"Train" the AI:**

    Use `make train` to start the training process. A black window will open; ignore it, as it is necessary for the training process.

    Alternatively, you can use `make train-verbose` which performs the same task, but in this case, the window will display each evaluation of each solution in each generation. Due to this, the training process will be slower than with the previous command.

> **Disclaimer:** As the generations advance, the evaluation of each solution becomes slower because each solution improves, survives longer, and achieves higher scores.
After completing the training process, you will find the best solution of each generation in the "results" folder, and the best overall solution in "finalsol.txt".

## Usage

To start the game with the AI, simply run:
```bash
make ai
```
This command reads the best parameters from "finalsol.txt". After this, press the space bar or any arrow key and enjoy watching how the AI masters the game.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- The original [FlapPyBird](https://github.com/sourabhv/FlapPyBird) project by Sourabh Verma.
