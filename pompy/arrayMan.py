array = [90, 85, 80, 90, 95, 100, 105, 110]

newArray = []
for i in range(len(array)-1):
    newArray.append(array[i])
    diff = array[i+1] - array[i]
    diff = diff/600
    for j in range(1, 600):
        newArray.append(array[i]+diff*j)

newArray.append(array[-1])
