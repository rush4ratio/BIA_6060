"""
Name: Rush Kirubi
==========================================================
USING PYTHON 3
==========================================================
"""


from collections import OrderedDict
from collections import defaultdict

import csv
import datetime as dt
import math
import statistics as st
import ast


class Series(list):
        def __eq__(self, other):
            ret_list = []

            for item in self:
                ret_list.append(item == other)

            return ret_list
        
        def __lt__(self, other):
            ret_list = []

            for item in self:
                ret_list.append(item < other)

            return ret_list
        
        def __le__(self, other):
            ret_list = []

            for item in self:
                ret_list.append(item <= other)

            return ret_list
        
        def __gt__(self, other):
            ret_list = []

            for item in self:
                ret_list.append(item > other)

            return ret_list
        
        def __ge__(self, other):
            ret_list = []

            for item in self:
                ret_list.append(item >= other)

            return ret_list

        def __ne__(self, other):
            ret_list = []

            for item in self:
                ret_list.append(item != other)

            return ret_list

def avg(a_list):
    return sum(a_list)/float(len(a_list))




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
            self.data =  list_of_lists[1:]
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

        # give proper data types
        self.data = [[self.convert(cell) for cell in line] for line in self.data]
           
            
        self.data = [OrderedDict(zip(self.header, row)) for row in self.data]

    #-----  Task 1 ------
    def is_cols_unique(self):
        return not (len(self.header) > len(set(self.header))) 
          

    def __getitem__(self, item):
        # rows only
        if isinstance(item, (int, slice)):
            for j in range(0, len(self.data)):
                    for key in self.data[j]:
                        if isinstance(self.data[j][key], dt.date):
                            self.data[j][key] = str(self.data[j][key])

            return self.data[item]

        # columns only
        elif isinstance(item, str):
            data_col = Series([row[item] for row in self.data])      
            
            for j in range(0, len(data_col)):
                if isinstance(data_col[j], dt.date):
                    data_col[j] = str(data_col[j])

            return data_col
            
            
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
            is_list_of_bools = all([isinstance(thing, bool) for thing in item])
            
            if is_list_of_bools:
                return_only_bools = []
                for counter in range(0,len(item)):
                    if item[counter]:
                        return_only_bools.append(self.data[counter])
                
                for j in range(0, len(return_only_bools)):
                    for key in return_only_bools[j]:
                        if isinstance(return_only_bools[j][key], dt.date):
                            return_only_bools[j][key] = str(return_only_bools[j][key])

                return return_only_bools
    
            else:
                
                return [[row[column_name] for column_name in item] for row in self.data]
            

            
    def get_rows_where_column_has_value(self, column_name, value, index_only = False):
        if index_only:
            return [index for index,row_value in enumerate(self[column_name]) if row_value == value]  
        else:
            return [row for row in self.data if row[column_name] == value]

    def min(self, column_name):
        try:
            num = min(self[column_name])
            return num
        except:
            print("could not get minimum")        

    def max(self, column_name):
        try:
            num = max(self[column_name])
            return num
        except:
            print("could not get maximum")       

    def sum(self, column_name):
        try:
            num = sum(self[column_name])
            return num
        except:
            print("could not get sum")
            
    def mean(self, column_name):
        try:
            num = sum(self[column_name]) / len(self[column_name])
            return num
        except:
            print("could not get mean") 

    def median(self, column_name):
        try:
            num = st.median(self[column_name])
            return num
        except:
            print("could not get median")       
    
    def std(self, column_name):
        try:
            mean = sum(self[column_name])/len(self[column_name])
            return math.sqrt(sum([(xi - mean)**2 for xi in self[column_name]])/len(self[column_name]))
        except:
            print("could not get standard deviation") 
        
    def convert(self,cell):
        if isinstance(cell,str):
            try:
                if isinstance(dt.datetime.strptime(cell, "%m/%d/%y %H:%M"), dt.date):
                    cell = dt.datetime.strptime(cell, "%m/%d/%y %H:%M")
                    return cell   
            except Exception:
                try:
                    if isinstance(ast.literal_eval(cell.replace(",","")), int):
                        return float(cell.replace(",",""))
                except Exception:
                    pass

            try:
                if isinstance(ast.literal_eval(cell), float) or isinstance(ast.literal_eval(cell), int):
                    return float(cell)    
            except Exception:
                    pass
                
        return cell

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
    
    def sort_by(self, column, reverseOrder = False):
        self.data.sort(key=lambda col: col[column], reverse = reverseOrder)

 
    def group_by(self,group_by_col, col_look_up, aggregate_func):
        dict_lookup = defaultdict(list)


        for ordered_dict_row in self.data:
            dict_lookup[ordered_dict_row[group_by_col]].append(
                ordered_dict_row[col_look_up]
                )

        aggregated_dict = {}

        aggregated_dict = { key: aggregate_func(dict_lookup[key]) for key in dict_lookup}

        return aggregated_dict


# lines = open("SalesJan2009.csv").readlines()
# lines = [line.strip() for line in lines]
# data = [l.split(',') for l in lines]

# mistake = lines[559].split('"')
# data[559] = mistake[0].split(",")[:-1]+[mistake[1]] + mistake[-1].split(',')[1:]   

df = DataFrame.from_csv('../SalesJan2009.csv')


"""

Tests

"""
# df.sort_by("Transaction_date")
# print(df[:5])




# Boolean indexing
#-------------------
# print(df[df["Payment_Type"] == "Visa"][:5])
# print(df[df["Price"] < 2000][:5])
# print(df[df["Price"] < 2000][:5])
# print(df[df["Price"] >= 3600][:5])



# print(df.group_by('Country', 'Price', avg))


# print(df.min("Transaction_date"))
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
