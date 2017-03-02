import os
import json
import requests
import datetime as dt
import re
import random
import time



from flask import Flask, request, Response
from textblob import TextBlob

from fuzzywuzzy import fuzz
from collections import defaultdict
from collections import OrderedDict

application = Flask(__name__)

#SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')

slack_inbound_url = 'https://hooks.slack.com/services/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'

def post_to_bot_chat_slack_resp(answers, resp_obj):
	query_response = "\n"

	for item in answers:
		query_response += "Title: " + item[1] + "\n"
		query_response += "Link: " + "<"+item[2]+"|" + item[2]+">" + "\n"
		query_response += "Number of responses: " + str(item[3]) + "\n"
		query_response += "Date asked: " + dt.datetime.fromtimestamp(item[4]).strftime('%m-%d-%Y %H:%M:%S') + "\n\n"

	resp_obj["text"] = query_response
	r = requests.post(slack_inbound_url, json=resp_obj)

def get_answers_from_slack(text_que, que_tags = None):
	if(que_tags):
		stack_overflow_url = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&site=stackoverflow" + "&tagged=" + ";".join(que_tags)
	else:
		stack_overflow_url = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&site=stackoverflow"

	responses_to_question = requests.get(stack_overflow_url + "&q=" + text_que).json()["items"]

	list_of_responses = defaultdict(list)

	for thing in responses_to_question:
		list_of_responses[thing["question_id"]].append(thing["tags"])
		list_of_responses[thing["question_id"]].append(thing["title"])
		list_of_responses[thing["question_id"]].append(thing["link"])
		list_of_responses[thing["question_id"]].append(thing["answer_count"])
		list_of_responses[thing["question_id"]].append(thing["creation_date"])
		list_of_responses[thing["question_id"]].append(fuzz.ratio(text_que, thing["title"]))

	answers = []
	for k in list_of_responses:
		if  list_of_responses[k]:
			answers.append(list_of_responses[k])

	return answers


def post_to_bot_chat_slack_resp(answers, resp_obj):
	query_response = "\n"

	for item in answers:
		query_response += "Title: " + item[1] + "\n"
		query_response += "Link: " + "<"+item[2]+"|" + item[2]+">" + "\n"
		query_response += "Number of responses: " + str(item[3]) + "\n"
		query_response += "Date asked: " + dt.datetime.fromtimestamp(item[4]).strftime('%m-%d-%Y %H:%M:%S') + "\n\n"

	resp_obj["text"] = query_response
	r = requests.post(slack_inbound_url, json=resp_obj)

def get_weather(location_query, resp_obj):
	# Weather website: https://www.apixu.com

	API_KEY = "5c46eec5c2c14e3fa39150209172802"

	weather_api_url = "http://api.apixu.com/v1/forecast.json?days=2"

	full_url = weather_api_url + "&key=" + API_KEY + "&q=" + location_query

	rq = requests.get(full_url).json()
	
	resp_obj["image_url"] = rq["current"]["condition"]["icon"]
	
	resp_obj["text"] = print_pretty_forecast(rq)

        r = requests.post(slack_inbound_url, json=resp_obj)

def print_pretty_forecast(w_forecast):
	today_temp = w_forecast["current"]["temp_f"]
	tomorrow_temp = w_forecast["forecast"]["forecastday"][1]["day"]["avgtemp_f"]

	query_resp = w_forecast["location"]["name"] + ", " + w_forecast["location"]["region"] + "\n"

	query_resp += w_forecast["current"]["condition"]["text"] + "\n"
	query_resp += str(today_temp) + " degrees Fahrenheit" + "\n"
	query_resp += "*Feels like* " + str(w_forecast["current"]["feelslike_f"]) + " degrees Fahrenheit" + "\n"
	query_resp += "*Wind Speed:* " + str(w_forecast["current"]["wind_mph"]) + " mph\n"

	if abs(tomorrow_temp - today_temp) <= 4:
		query_resp += "Tomorrow's average forecast is to be nearly the same temp. as today\n"
	elif tomorrow_temp > today_temp:
		query_resp += "Tomorrow's average forecast is warmer than today\n"
	elif today_temp > tomorrow_temp:
		query_resp += "Tomorrow's average forecast is colder than today\n"

	query_resp += "Today\n"
	query_resp += "*High* " + str(w_forecast["forecast"]["forecastday"][0]["day"]["maxtemp_f"])
	query_resp += " | " + "*Low* " + str(w_forecast["forecast"]["forecastday"][0]["day"]["mintemp_f"]) + " degrees Fahrenheit\n"
	query_resp += "*Forecast for tomorrow:* " + w_forecast["forecast"]["forecastday"][1]["day"]["condition"]["text"] + "\n"

	return query_resp


@application.route('/slack', methods=['POST'])
def inbound():

	delay = random.uniform(0,10)
	time.sleep(delay)

	response = {'username': 'rush_robot', 'icon_emoji': ':robot_face:'}

	#if request.form.get('token') == SLACK_WEBHOOK_SECRET:
	channel = request.form.get('channel_name')
	username = request.form.get('user_name')
	text = request.form.get('text')
	inbound_message = username + " in " + channel + " says: " + text

	if username in ['zac.wentzell', 'rush']:
		if "&lt;BOTS_RESPOND&gt;" in text:
			response['text'] = "Hello, my name is rush_bot. I belong to Rush Kirubi. I live at 54.89.60.8"
			r = requests.post(slack_inbound_url, json=response)

		elif "&lt;I_NEED_HELP_WITH_CODING&gt;" in text:
			text_questions = [t.strip() for t in text.split(":")]
			answers = get_answers_from_slack(text_questions[1])

			post_to_bot_chat_slack_resp(answers, response)

		elif "&lt;I_NEED_HELP_WITH&gt;" in text:
			text_questions = [t.strip() for t in text.split(":")]

			user_tags = re.findall('\[(.*?)\]', text_questions[1])
			answers = get_answers_from_slack(text_questions[1], user_tags)

			post_to_bot_chat_slack_resp(answers, response)

		elif "&lt;WHAT'S_THE_WEATHER_LIKE_AT&gt;" in text:
			text_questions = [t.strip() for t in text.split(":")]
			get_weather(text_questions[1],response)
			
	return Response(), 200



@application.route('/', methods=['GET'])
def test():
    return Response('Your flask app is running!')


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=41953)
