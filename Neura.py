import csv
import imageio
import numpy
import scipy.special


class train_neuralNetwork:
    def __init__(self, input_nodes, hidden_nodes, output_nodes, learning_rate, input_weight, output_weight, t=False):
        # Количество узлов в слоях
        self.in_nodes = input_nodes
        self.hid_nodes = hidden_nodes
        self.out_nodes = output_nodes

        self.learn = learning_rate  # Коэффицент обучения

        # Генерация весовых коэффицентов
        if not t:
            self.wih = numpy.random.normal(0.0, pow(self.hid_nodes, -0.5), (self.hid_nodes, self.in_nodes))
            self.who = numpy.random.normal(0.0, pow(self.out_nodes, -0.5), (self.out_nodes, self.hid_nodes))
        else:
            self.wih = input_weight
            self.who = output_weight

        self.activation_function = lambda x: scipy.special.expit(x)

    def train(self, inputs_list, targets_list):  # Тренировка сети
        targets = numpy.array(targets_list, ndmin=2).T

        inputs = numpy.array(inputs_list, ndmin=2).T
        hidden_inputs = numpy.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)

        final_inputs = numpy.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)

        output_errors = targets - final_outputs
        hidden_errors = numpy.dot(self.who.T, output_errors)

        self.who += self.learn * numpy.dot((output_errors * final_outputs * (1 - final_outputs)),
                                            numpy.transpose(hidden_outputs))
        self.wih += self.learn * numpy.dot((hidden_errors * hidden_outputs * (1 - hidden_outputs)),
                                            numpy.transpose(inputs))

    def query(self, inputs_list):  # Опрос сети
        inputs = numpy.array(inputs_list, ndmin=2).T

        hidden_inputs = numpy.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)

        final_inputs = numpy.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)

        return final_outputs

    def get_w(self, n):
        if n == 'wih':
            return self.wih
        elif n == 'who':
            return self.who


# Количество узлов и значение коэффицента обучения
inputnodes = 784
hiddennodes = 1000
outputnodes = 10
learningrate = 0.15

#  Первая нейросеть для определения весов
NeuraFirst = train_neuralNetwork(inputnodes, hiddennodes, outputnodes, learningrate, 0, 0, t=False)


# Тренировка сети
def Train(epochs, neural_network):
    # Цикл тренировки сети: epochs - количество итераций
    with open('mnist_train.csv', 'r') as file_train:
        train_data_list = file_train.readlines()

    for e in range(epochs):
        for record in train_data_list:
            all_values = record.split(',')
            image_array = numpy.asfarray(all_values[1:])
            inputs = (image_array / 255.0 * 0.99) + 0.01
            targets = numpy.zeros(outputnodes) + 0.01
            targets[int(all_values[0])] = 0.99
            neural_network.train(inputs, targets)
        SaveNeura(neural_network, n=e+1)
        print('Эпоха', e+1, 'завершена')

        # Проверка эффективности сети
        with open('mnist_test.csv', 'r') as file_test:
            test_data_list = file_test.readlines()

        scorecard = []
        for test_record in test_data_list:
            all_values = test_record.split(',')
            correct_label = int(all_values[0])

            inputs = (numpy.asfarray(all_values[1:]) / 255.0 * 0.99) + 0.01
            outputs = neural_network.query(inputs)
            label = numpy.argmax(outputs)

            if label == correct_label:
                scorecard.append(1)
            else:
                scorecard.append(0)
        # print(scorecard)
        scorecard_array = numpy.asarray(scorecard)
        print("эффективность = ", scorecard_array.sum() / scorecard_array.size)
    print('Обучение завершено')

    x = input('Сохранить результат?')
    if x == 'Да' or 'True' or '+':
        SaveNeura(neural_network)


# Сохранение результата тренировки
# TO DO:
# Сделать сравнение с прошлым результатом тренировки.
# Если эффективность больше - сохраняем результат, нет - не сохраняем и выводим ошибку
def SaveNeura(neural_network, n=None):
    input_weight = neural_network.get_w('wih')
    output_weight = neural_network.get_w('who')
    numpy.save('wih' + str(n) + '.npy', input_weight)
    numpy.save('who' + str(n) + '.npy', output_weight)


# Определение числа по изображению img.jpg (28x28 пикселей)
def Identify(neural_network, image):
    inputs = ((image / 255.0 * 0.99) + 0.01)
    inputs_list = []
    for i in inputs:
        for j in i:
            inputs_list.append(j)
    inputs = numpy.asfarray(inputs_list)
    outputs = neural_network.query(inputs)
    percent_dict = {}
    n = 0
    for i in outputs:
        percent = "%.2f" % (i[0] / outputs.sum() * 100)

        if float(percent) >= 10:
            percent_dict[n] = percent
        n += 1

    n = numpy.argmax(outputs)
    return n, percent_dict[n]


# Путь к изображению
img = (imageio.imread('img.jpg', as_gray=True))
# Создаем матрицу из изображения
img = numpy.array(img)


# Добавить тренировочные данные
def FalseAnswer(image, right_value):

    with open("mnist_train.csv", mode="a", newline='') as w_file:
        file_writer = csv.writer(w_file, delimiter=",")
        inpu = [int(right_value)]
        for i in image:
            for j in i:
                inpu.append(int(j))
        file_writer.writerow(inpu)
    print('Число', right_value, 'добавлено в тренировочный набор')


# Проверка эффективности сети
def Efficiency(neural_network):
    with open('mnist_test.csv', 'r') as file_test:
        test_data_list = file_test.readlines()

    scorecard = []
    for test_record in test_data_list:
        all_values = test_record.split(',')
        correct_label = int(all_values[0])

        inputs = (numpy.asfarray(all_values[1:]) / 255.0 * 0.99) + 0.01
        outputs = neural_network.query(inputs)
        label = numpy.argmax(outputs)

        if label == correct_label:
            scorecard.append(1)
        else:
            scorecard.append(0)
    # print(scorecard)
    scorecard_array = numpy.asarray(scorecard)
    print("эффективность = ", scorecard_array.sum() / scorecard_array.size)


class neuralNetwork:
    def __init__(self):
        self.wih = numpy.load('wih.npy')
        self.who = numpy.load('who.npy')

        self.activation_function = lambda x: scipy.special.expit(x)

    def query(self, inputs_list):  # Опрос сети
        inputs = numpy.array(inputs_list, ndmin=2).T

        hidden_inputs = numpy.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)

        final_inputs = numpy.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)

        return final_outputs
