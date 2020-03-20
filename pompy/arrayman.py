
self.array = [10, 170, 10, 250, 10, 350]
self.newArray = []
for i in range(len(self.array)-1):
    self.newArray.append(self.array[i])
    self.diff = self.array[i+1] - self.array[i]
    self.sign = np.sign(self.diff)
    self.magDiff = abs(self.diff)
    if self.magDiff > 180:
        self.magDiff = abs(self.magDiff - 360)
        self.sign = self.sign * -1
    self.diff = self.magDiff * self.sign
    self.diff = self.diff/600
    for j in range(1, 600):
        self.temp = self.array[i]+self.diff*j
        if self.temp < 0:
            self.temp += 360
        elif self.temp > 360:
            self.temp -= 360
        self.newArray.append(self.temp)
self.newArray.append(self.array[-1])
