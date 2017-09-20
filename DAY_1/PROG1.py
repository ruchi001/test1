def data_type():
    num_int = '12345'
    num_flot = 123.45
    str1 = "12345.23"
    list1 = [1, 2, 3, 4, 5]
    tuple1 = (1, 2, 3, 4, 5)
    dict1 = {'a': 1, 'b': 2, 'c': 3}

    print(num_int)
    print(num_flot)
    print(str1)
    print(list1)
    print(tuple1)
    print(dict1)
    print type(str1)
    print float(str1)
    print int(num_int)






def for_loop():
    list2 = [0, 2, 3, 4, 5, 6, 8, 9, 10]
    for i in range(len(list2)):
        print(i, list2[i])


def while_loop():
    count = 0
    while (count < 9):
       print 'The count is:', count
       count = count + 1

def nested_while():
    num1 = 2
    while(num1 < 10):
        num2 = 2
        while(num2 <= (num1/num2)):
            if not(num1 % num2):
                break
            num2 = num2 + 1
        if (num2 > num1/num2):
            print num1, " is prime"
        num1 = num1 + 1

def if_else():
    num = 85

    if num < 40:
        passed = False
        print ('fail')
    elif num < 60:
        passed = True
        print ('pass with less then 60')
    elif num < 80:
        print ('pass with less then 80')
        passed = True
    else:
        passed = True
        print('pass with more then 80')

    if passed is True:
        print ("pass")
    else:
        print ("fail")

def string_op():

    str1 = "Python is a general-purpose interpreted, interactive, object-oriented, and high-level programming language."
    print (str1)
    word = str1.find('and')
    print (word)
    str2 = str1.replace('and', '&')
    print (str2)
    words = str1.split()
    print(words)
    words.sort()
    for word in words:
            print(word)


def tuple_op():

    tup1 = (1,2,3,4)
    tup2 = (2,3,5,6)
    tup3 = tup1+tup2
    tup4 = tup1 * 4
    print (tup3)
    print (tup4)

def list_op():

    list1 = [1, 2, 3, 4, 5]
    list2 = [2, 4, 6, 8, 2]
    list1[2] = 9
    list1.append(0)
    print list1
    list2 = list2.append(list1)
    print list2
    
    
print("program succesful")



data_type()
for_loop()
while_loop()
nested_while()
if_else()
string_op()
tuple_op()
list_op()


