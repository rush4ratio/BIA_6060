"""
Name: Rush Kirubi
==========================================================
USING PYTHON 3
==========================================================
"""


from collections import OrderedDict
import csv
import datetime as dt
import math
import statistics as st
import ast

class DataFrame():
    @classmethod
    def from_csv(cls, file_path, delim=',', quote_char='"'):
        with open(file_path,'rU')as infile:
            reader = csv.reader(infile, delimiter=delim, quotechar=quote_char)
            data = []
            
            for row in reader:
                data.append(row)

            return cls(list_of_lists = data)

    def __init__(self, list_of_lists, header = True):
        if header:
            self.data = list_of_lists[1:]
            self.header = list_of_lists[0]
        else:
            self.header = ['column' + str(index + 1) for index, column in enumerate(list_of_lists[0])]
            # get data as copy with slice
            self.data = list_of_lists[:]

        #----- Task 2 ------
        self.header = [header.strip() for header in self.header]
        self.data = [[entry.strip() for entry in entries]  for entries in self.data]

        #-----  Task 1 ------
        if not self.is_cols_unique():
            raise Exception("Duplicate columns are not allowed.")

        self.data = [OrderedDict(zip(self.header, row)) for row in self.data]

    #-----  Task 1 ------
    def is_cols_unique(self):
        return not (len(self.header) > len(set(self.header))) 
          

    def __getitem__(self, item):
        # rows only
        if isinstance(item, (int, slice)):
            return self.data[item]

        # columns only
        elif isinstance(item, str):
            return [row[item] for row in self.data]

        elif isinstance(item, tuple):
            if isinstance(item[0], list) or isinstance(item[1], list):
                if isinstance(item[0], list):
                    rows = [row for index,row in enumerate(self.data) if index in item[0]] 
                else:
                    rows = self.data[item[0]]

                if isinstance(item[1], list):
                    if all([isinstance(thing, int) for thing in item[1]]):
                        return [[column_value for index,column_value in enumerate([value for key, value in row.items()]) if index in item[1]] for row in rows]
                    elif all([isinstance(thing, str) for thing in item[1]]):
                        return [[row[column_name] for column_name in item[1]] for row in rows]
                    else:
                        raise TypeError("Sorry. Selection will not work.")
                else:
                    return [[value for key, value in row.items()][item[1]] for row in rows]
            else:
                if isinstance(item[1], (int, slice)):
                    return [[value for key, value in row.items()][item[1]] for row in self.data[item[0]]]
                elif isinstance(item[1], str):
                    return [row[item[1]] for row in self.data[item[0]]]
                else:
                    raise TypeError("Sorry! Can't handle this.")    
        # only for list of column names
        elif isinstance(item, list):
            return [[row[column_name] for column_name in item] for row in self.data]

    def get_rows_where_column_has_value(self, column_name, value, index_only = False):
        if index_only:
            return [index for index,row_value in enumerate(self[column_name]) if row_value == value]  
        else:
            return [row for row in self.data if row[column_name] == value]

    def min(self, column_name):
        calc_set = self.convert(self[column_name])
        if (calc_set):
            return min(calc_set)       

    def max(self, column_name):
        calc_set = self.convert(self[column_name])
        if (calc_set):
            return max(calc_set)      

    def sum(self, column_name):
        try:
           calc_set = self.convert(self[column_name])
           if (calc_set):
             return sum(calc_set)
        except TypeError:
            print("Could not sum data; format: {}".format(type(calc_set[1])))
    def mean(self, column_name):
        try:
           calc_set = self.convert(self[column_name])
           if (calc_set):
             return sum(calc_set)/len(calc_set)
        except TypeError:
            print("Could not sum data; format: {}".format(type(calc_set[1])))

    def median(self, column_name):
        try:
           calc_set = self.convert(self[column_name])
           return st.median(calc_set)
        except TypeError:
            print("Could not sum data; format: {}".format(type(calc_set[1])))          
    
    def std(self, column_name):
        try:
           calc_set = self.convert(self[column_name])
           if (calc_set):
              mean = sum(calc_set)/len(calc_set)

              return math.sqrt(sum([(xi - mean)**2 for xi in calc_set])/len(calc_set))
       
        except TypeError:
            print("Could not sum data; format: {}".format(type(calc_set[1])))

    def convert(self, calc_set):
        if isinstance(calc_set[1],str):
            try:
                if isinstance(dt.datetime.strptime(calc_set[1], "%m/%d/%y %H:%M"), dt.date):
                    calc_set = [dt.datetime.strptime(string, "%m/%d/%y %H:%M") for string in calc_set]
                    return calc_set   
            except ValueError:
                if isinstance(ast.literal_eval(calc_set[1].replace(",","")), int):
                    try:
                        calc_set = [float(num.replace(",","")) for num in calc_set]
                    except ValueError:
                        print("Could not do calculation on strings")
                    return calc_set

        if isinstance(calc_set[1],int):
            if all([int(num) for num in calc_set]):
                calc_set = [float(num) for num in calc_set]
                return calc_set

        else:
            raise ValueError("Could not do calculation on strings")
        
        return

    # Task 4
    def add_rows(self, a_list):   
        if len(a_list) == len(self.header):
            self.data.append(OrderedDict(zip(self.header, a_list)))
        else:
            raise ValueError("List entry could not be done. Incorrect number of columns.")
    
    # Task 5
    def add_column(self, list_of_values, column_name):
        
        if (len(self.data)) == len(list_of_values):
            self.header.append(column_name)

            for index, each_list in enumerate(self.data):
                self.data[index].update({column_name : list_of_values[index]})
        
        else:
            raise ValueError("The number of rows in the new column don't match those in the current data frame")
    
    def get_rows_where_column_has_value(self, column_name, value, index_only = False):
        if index_only:
            return [index for index,row_value in enumerate(self[column_name]) if row_value == value]  
        else:
            return [row for row in self.data if row[column_name] == value]

# lines = open("SalesJan2009.csv").readlines()
# lines = [line.strip() for line in lines]
# data = [l.split(',') for l in lines]

# mistake = lines[559].split('"')
# data[559] = mistake[0].split(",")[:-1]+[mistake[1]] + mistake[-1].split(',')[1:]   

df = DataFrame.from_csv('SalesJan2009.csv')


"""

Tests

"""
# print(df.max("Transaction_date"))
# print(df.median("Price"))

# ls = ["1/1/12 6:17","Product1","1000","Discoverer","carolina","Basildon","England","United Kingdom","1/1/12 6:00","1/2/09 6:08","51.5","-1.1166667"]

# df.add_rows(ls)

# print(df[998])

# import random
# ls = [random.randint(1,10) for r in range(0,len(df.data))]

# df.add_column(ls, "random_number")

# print(len(df.get_rows_where_column_has_value("random_number", 5)))
# print(df[:10])

# print(df.median("Price"))
