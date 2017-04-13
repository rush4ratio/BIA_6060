import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import datetime as dt
import time
import unicodedata
import matplotlib.pyplot as plt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from dateutil.parser import parse
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from scipy.spatial.distance import euclidean

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def scrape_html(driver_copy, city_name):
    results = driver_copy.find_elements_by_class_name('LJTSM3-v-d')
    
    for result in results:
        if city_name.lower() in strip_accents(result.find_element_by_class_name('LJTSM3-v-c').text.lower()):
            test = result
            break
    
    bars = test.find_elements_by_class_name('LJTSM3-w-x')
    data = []
    for bar in bars:
        ActionChains(driver_copy).move_to_element(bar).perform()
        time.sleep(0.001)
        data.append((test.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[0].text, test.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[1].text))

    clean_data = [(parse(d[1].split('-')[0].strip()), float(d[0].replace('$', '').replace(',', '')))for d in data]

    return pd.DataFrame(clean_data, columns=['Start_Date', 'Price'])

def scroll_to_page_section(driver_, city_name_=None):
	action = ActionChains(driver_)
	e= driver_.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[2]')
	action.move_to_element(e)
	action.double_click(e)
	action.perform()

	if city_name_:
		return scrape_html(driver_, city_name_)

def scrape_data(start_date=None, from_place=None, to_place=None, city_name=None):
	url = "https://www.google.com/flights/explore/"
	driver = webdriver.Chrome(service_args = ['--ignore-ssl-errors=true'])
	driver.implicitly_wait(20)
	driver.get(url)

	scroll_to_page_section(driver)

	#from
	input_bx = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[2]/input')
	input_bx.send_keys(from_place)

	time.sleep(1)	
	# tab over to the next input field
	input_bx.send_keys(u'\ue004')

	#to
	input_bx2  = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[4]/input')
	input_bx2.send_keys(to_place)
	input_bx2.send_keys(u'\ue007')
	time.sleep(1)

	my_url = driver.current_url
	from_airports,to_airports = my_url.split(";")[1], my_url.split(";")[2]
	

	# format dates 
	start_d = start_date.strftime('%Y-%m-%d')

	# Fetch custom url
	user_url = url + "#explore;" + from_airports + ";li=3;lx=5;" + to_airports + ";d="+ start_d
	time.sleep(1)

	driver.get(user_url)
	time.sleep(1)
	fares = scroll_to_page_section(driver, city_name)

	return fares


	
def scrape_data_90(start_date=None, from_place=None, to_place=None, city_name=None):
	url = "https://www.google.com/flights/explore/"
	driver = webdriver.Chrome(service_args = ['--ignore-ssl-errors=true'])
	driver.implicitly_wait(20)
	driver.get(url)

	scroll_to_page_section(driver)

	#from
	input_bx = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[2]/input')
	input_bx.send_keys(from_place)

	time.sleep(1)	
	# tab over to the next input field
	input_bx.send_keys(u'\ue004')

	#to
	input_bx2  = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[4]/input')
	input_bx2.send_keys(to_place)
	input_bx2.send_keys(u'\ue007')
	time.sleep(1)

	my_url = driver.current_url
	from_airports,to_airports = my_url.split(";")[1], my_url.split(";")[2]
	

	# format dates 
	start_d = start_date.strftime('%Y-%m-%d')

	# Fetch custom url
	user_url = url + "#explore;" + from_airports + ";li=3;lx=5;" + to_airports + ";d="+ start_d
	time.sleep(1)

	driver.get(user_url)
	time.sleep(1)
	fares = scroll_to_page_section(driver, city_name)

	# We need 90-days, find out how many days we've got so far
	days_so_far = fares["Start_Date"][len(fares) - 1] - fares["Start_Date"][0]


	# days left to scrape for
	days_left = dt.timedelta(days = 90) - days_so_far
	new_start_d = (fares["Start_Date"][len(fares) - 1] + dt.timedelta(days = 1)).strftime('%Y-%m-%d')
	user_url = url + "#explore;" + from_airports + ";li=3;lx=5;" + to_airports + ";d=" + new_start_d

	driver.get(user_url)
	time.sleep(1)
	driver.implicitly_wait(20)
	
	# DOM is stale, got to do this again
	fares2 = scroll_to_page_section(driver, city_name)

	# We're only interested in a few days
	fares_left = fares2[:days_left.days]

	# Put the fares together
	fares = pd.concat([fares, fares_left], ignore_index = True)
	
	return fares


def task_3_dbscan(flight_data):
	# Mistake Price
	flight_data.Price[23] = 500


	time_stamps = np.arange(len(flight_data.Start_Date))
	data = np.array([[ts,dt] for ts,dt in zip(time_stamps, flight_data.Price)])	
	data_frame = pd.DataFrame(data, columns=["date","price"])
	
	
	# Change scaling for days
	days_mm = MinMaxScaler(feature_range=(-4,4)).fit_transform(data[:,0])

	# Normal scaling for Prices
	prices_normalized = StandardScaler().fit_transform(data[:,1])


	# Numpy's concat is not working for me
	dat = []
	for day, price in zip(days_mm, prices_normalized):
		dat.append([day, price])
		X = np.array(dat)

		db = DBSCAN(eps = .2, min_samples=2).fit(X)

		labels = db.labels_
		clusters = len(set(labels))
		unique_labels = set(labels)
		

	pf = pd.concat([data_frame, pd.DataFrame(db.labels_, columns=['cluster'])], axis = 1)

	# Mistake Price 
	mistake_price = X[23][1]

	"""
	## Plot Clusters
	colors = plt.cm.Spectral(np.linspace(0,1,len(unique_labels)))
	plt.subplots(figsize=(12,8))
	
	for k,c in zip(unique_labels, colors):	
		class_member_mask = (labels == k)
		xy = X[class_member_mask]
		plt.plot(xy[:,0], xy[:, 1],'o', markerfacecolor = c, markeredgecolor = 'k', markersize = 12)

	    # Label Mistake Price
		if any(mistake_price == xy[:, 1]):
			ix = np.in1d(xy.ravel(), mistake_price).reshape(xy.shape)
			coord = xy[int(np.where(ix)[0])]
			plt.plot(coord[0], coord[1],'xr', markerfacecolor = c, markeredgecolor = 'k', markersize = 18)

	# show cluster
	for x,y, clust in zip(days_mm,prices_normalized,labels.tolist()):
		plt.annotate('{}'.format(clust), xytext=(x+0.1,y), xy=(x,y),fontsize=10)


		plt.title("Total Clusters: {}".format(clusters), fontsize = 14, y = 1.01)
		
	## -- END of Plot
	"""


	# No noise cluster
	df = pf[pf.cluster != -1]

   # Our Mistake price is $500 stored in 23
	mistake_price_df = (pf[pf.price == pf.price[23]])

	# Calculate euclidean distance and add it to data frame as pd Series
	vals = df.drop("cluster", 1).as_matrix()
	euclidean_dist = [euclidean(mistake_price_df.drop("cluster", 1).as_matrix(), val_item) for val_item in vals]
	pf["eu_dist"] = pd.Series(euclidean_dist)

	# let's drop mistake price row to calculate nearest cluster
	df = pf[(pf.price != pf.price[23]) & (pf.cluster != -1)]

	# what's the nearest cluster
	nearest_clusters = df[df.eu_dist == df.eu_dist.min()].cluster.values

	mean_price_of_nearest_cluster = np.mean(pf[pf.cluster == int(nearest_clusters)].price)
	two_sd_from_mean = mean_price_of_nearest_cluster - 2 * np.std(pf.price)

	if all(mistake_price_df.price) < two_sd_from_mean and all(mistake_price_df.price < mean_price_of_nearest_cluster):
		print("Minimum Price: ", mistake_price_df.price)
		print("Date: ",flight_data.Start_Date[int(mistake_price_df.date)])
        
def task_3_IQR(flight_data):    
    Q1, Q3  = flight_data.Price.quantile(.25), flight_data.Price.quantile(.75)

    IQR = Q3 - Q1

    flight_iqr = flight_data[flight_data.Price < (Q1 - 1.5 * IQR)]

    print("Outlier via IQR 3 Method")
    print("=============================================")
    if not flight_iqr.empty:
        print(flight_iqr)
    else:
        print("'Mistake' prices haven't been found.")

def task_4_dbscan(flight_data):
	time_stamps = np.arange(len(flight_data.Start_Date))
	data = np.array([[ts,dt] for ts,dt in zip(time_stamps, flight_data.Price)])
	
	# Change scaling for days
	# Scaled deliberately as normal though the min max method is used in the sqrt(x^2 + y^2) method 
	days_mm = StandardScaler().fit_transform(data[:,0].reshape(-1, 1))

	# Normal scaling for Prices
	prices_normalized = StandardScaler().fit_transform(data[:,1].reshape(-1,1))

	# $20
	stand_norm_price_diff = (20)/np.std(data[:,1])

	# 1 day
	stand_norm_day_diff = (days_mm[1] - days_mm[0])

	epsilon = np.sqrt((stand_norm_price_diff**2) + (stand_norm_day_diff**2))

	# Numpy's concat not working for me
	dat = []
	for day, price in zip(days_mm, prices_normalized):
		dat.append([day, price])
	X = np.array(dat)

	db = DBSCAN(eps = epsilon, min_samples=5).fit(X.reshape(-1,2))



	data_frame = pd.DataFrame(data, columns=["date","price"])
	pf = pd.concat([data_frame, pd.DataFrame(db.labels_, columns=['cluster'])], axis = 1)
	contiguous_clusters = pf[pf.cluster != -1]
	lowest_period_price = int(contiguous_clusters.groupby(['cluster']).price.agg(['mean']).iloc[0])

	# return lowest priced period based on criteria
	return_df = pf[(pf.price == lowest_period_price) & (pf.cluster!=-1)]
	if return_df.empty:
		print("No prices that fit within the 5day max $20 threshold")
	else:
		print(return_df)

##### ==== TEST ===  ##### 
ex =dt.date(2017,5,28)
data= scrape_data(start_date=ex,from_place="new york",to_place="germany", city_name="berlin")


# task_3_dbscan(data)

task_3_IQR(data)

# task_4_dbscan(data)