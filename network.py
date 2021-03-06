import numpy as np
from layer import FullyConnectedLayer
from utils import softmax
from utils import plot
import time

class NeuralNet:
    '''
    Neural Net class consists of l fully connected layers that classify a din dimensional data into one of 
    dout class labels

    din  : dimension of data
    dout : number of label class
    dhidden : number of neurons in hidden layers  
    '''
    def __init__(self, din, dout, dhidden):
        self.dim = []
        self.dim.append(din)
        self.dim.extend(dhidden)
        self.dim.append(dout)

        self.layer = []
        for i in range(len(self.dim) - 1):
            self.layer.append(FullyConnectedLayer(self.dim[i], self.dim[i + 1]))
        
        self.l = len(self.layer)
        self.w = [l.generateWeight() for l in self.layer]
        
    def __repr__(self):
        return 'NeuralNet with {0.din} to {0.dhidden} to {0.dout}'.format(self)

    def forward(self, x0, w):
        x = [None] * self.l
        x[0] = x0
        i = 0
        while i < self.l - 1:
            x[i + 1] = np.maximum(0, self.layer[i].forward(x[i], w[i]))
            i += 1
        p = self.layer[i].forward(x[i], w[i])
        return x, p

    def backward(self, x, w, dy):
        dw = [None] * self.l

        for i in reversed(range(self.l)):
            dx, dw[i] = self.layer[i].backward(x[i], w[i], dy)      
            dy  = dx * (1 * (x[i] > 0))
        return dw

    def loss(self, s, y):
        prob = softmax(s).reshape(1, -1)
        THRESHOLD = -10
        loss = -(THRESHOLD if prob[0][y] < np.exp(THRESHOLD) else np.log(prob[0][y]))
        prob[0][y] -= 1
        return loss, prob

    def train_iteration(self, data, label, stepSize, regularization=0.0):
        
        N = data.shape[0]

        loss     = [0] * N
        labelHat = [0] * N
        dwSum = None
        w = self.w

        for i in range(N):
            di = data[i]
            li = label[i]
            x, s = self.forward(di, w)
            
            loss[i], dy = self.loss(s, li)
            labelHat[i] = np.argmax(s)
            
            dw = self.backward(x, w, dy)
            if dwSum is None:
                dwSum = dw
            else:
                for j in range(self.l):
                    dwSum[j] += dw[j] 

        for i in range(self.l):
            g = (dwSum[i] / N) * stepSize + self.w[i] * regularization
            self.w[i] -= g

        return np.array(loss), np.array(labelHat)

    def train(self, trainData, trainLabel, stepSize, iter, regularization=0.0, testData=None, testLabel=None):
        start = time.time()
        for t in range(iter):
            trainLoss, trainLabelHat = self.train_iteration(trainData, trainLabel, stepSize, regularization)
            trainLoss = np.mean(trainLoss)
            trainErrRate = np.mean(1 * (trainLabelHat != trainLabel))

   
            now = time.time()
            timeRemain = (now - start) / (t + 1) * (iter - t - 1)
            
            if testData is not None:
                testLabelHat = self.predict(testData) 
                testErrRate = np.mean(1 * (testLabelHat != testLabel))
                s = 'Iter: {0:4d} | Loss: {1:2.2f} | Train ErrRate: {2:2.2f} | Test ErrRate:{3:2.2f} | Time Remain:{4:2.2f}'.format(t, trainLoss, trainErrRate, testErrRate, timeRemain)
            else:
                s = 'Iter: {0:4d} | Loss: {1:2.2f} | Train ErrRate: {2:2.2f} | Test ErrRate:N/A | Time Remain:{3:2.2f}'.format(t, trainLoss, trainLoss, timeRemain)
            
            print(s, end='')
            print('\r', end='')
            
        print('\nTime total : {0}'.format(time.time() - start))
        #print('\n')
        #plot(trainData[:,0], trainData[:,1], trainLabel, trainLabelHat)
        #plot(testData[:,0], testData[:,1], testLabel, testLabelHat)

    def predict(self, data):
        N = data.shape[0]
        label = [0] * N
        for i in range(N):
            di = data[i]
            _, s = self.forward(di, self.w)
            label[i] = np.argmax(s)
        return np.array(label)


    def show(self):
        x = np.linspace(-4, 4, 128)
        y = np.linspace(-4, 4, 128)
        data = []
        for xi in x:
            for yi in y:
                data.append([xi, yi])
        
        data = np.array(data)
        l = self.predict(data)
        plot(data[:,0], data[:,1], l)