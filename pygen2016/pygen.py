#coding: utf8
import numpy as np 
from itertools import combinations 
import copy
import matplotlib.pyplot as plt

# функция для оптимизации
func = lambda x, y: (x-5) ** 2 + (y-1) ** 2
 
 
class GeneticEvolution:
    '''Генетическая оптимизация функции двух переменных'''
     
    def __init__(self, func, mut_prob=0.8, kill_portion=0.2, max_pairs=1000):
        self.func = func
        self.population = [] # Current symbolic expression
        self.mutation_probability = mut_prob
        self.portion = kill_portion
        self.max_pairs = max_pairs
     
    # начальная случайная популяция
    def generate_random_population(self, size=100):
        self.population = np.random.rand(100, 2).tolist()
     
    # инициализация поиска
    def initialize(self):
        self.generate_random_population()
     
    # основная функция "генетического" поиска
    def evolute(self, n_steps=40):
        n = 0
        while n < n_steps:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.scatter(np.array(self.population)[:,0], np.array(self.population)[:,1])
            ax.set_title('n=%s'%n)
            if n > 24:
                ax.set_xlim([4.95, 5.05])
                ax.set_ylim([0.98, 1.02])
            else:
                ax.set_xlim([0, 6])
                ax.set_ylim([0, 2])
            fig.savefig('{0:02}'.format(n)+'.png', dpi=100)
            print 'Шаг:', n
            n += 1
            ind = 0
            newpopulation = copy.copy(self.population) 
            for comb in combinations(range(len(self.population)), 2):
                ind += 1
                if ind > self.max_pairs:
                    break
                a = self.mutate(self.population[comb[0]])
                b = self.mutate(self.population[comb[1]])
                newitem = self.crossover(a, b)
                newpopulation.append(newitem)
            self.population = self.killing(newpopulation) 
        return np.min([func(x,y) for x, y in self.population])
 
    def killing(self, population):
        res = np.argsort([self.func(*item) for item in population])
        res = res[:np.random.poisson(int(len(population) * self.portion))]
        return np.array(population)[res].tolist()
                 
    # обмен значениями (кроссинговер), происходит с вероятностью 0.5 по умолчанию
    def crossover(self, a, b, prob=0.5):
        if np.random.rand() >  prob:
            return [a[0], b[1]]
        else:
            return [b[0], a[1]]
 
    # мутация значений происходит с определенной вероятностью (0.8 - по умолчанию) 
    def mutate(self, a):
        if np.random.rand() < self.mutation_probability:
            newa = a + (np.random.rand(2) - 0.5)*0.5
        else:
            newa = a
        return newa
         
g = GeneticEvolution(func=func)
g.initialize()
res = g.evolute()
print 'Результат оптимизации:', res
