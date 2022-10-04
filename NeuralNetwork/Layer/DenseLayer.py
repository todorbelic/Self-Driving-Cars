from Base import *
import numpy as np
import random


class Dense(Layer):

    def __init__(self, input_size, output_size):
        super().__init__()
        self.weights = np.random.randn(output_size, input_size)
        self.bias = np.random.randn(output_size, 1)

    def forward(self, input):
        self.input = input
        return np.dot(self.weights, self.input) + self.bias

    def backward(self, output_gradient, learning_rate):
        weights_gradient = np.dot(output_gradient, self.input.T)
        self.weights -= learning_rate * weights_gradient
        self.bias -= learning_rate * output_gradient
        return np.dot(self.weights.T, output_gradient)

    def mutate(self, mutation_rate):
        mutation_rate_weights = np.random.randn(self.weights.shape[0], self.weights.shape[1])
        mutation_factor_temp = np.random.normal(loc=0, scale=1, size=self.weights.shape)
        mutation_factor_weights = np.where(mutation_rate_weights < mutation_rate, mutation_factor_temp, 0)
        self.weights += mutation_factor_weights

        mutation_rate_bias = np.random.randn(self.bias.shape[0], self.bias.shape[1])
        mutation_factor_temp = np.random.normal(loc=0, scale=1, size=self.bias.shape)
        mutation_factor_bias = np.where(mutation_rate_bias < mutation_rate, mutation_factor_temp, 0)
        self.bias += mutation_factor_bias

