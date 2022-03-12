import math
import random
import requests
import re
from locust import HttpUser, TaskSet, task, constant
from locust import LoadTestShape
from bs4 import BeautifulSoup


class UserTasks(TaskSet):

    @staticmethod
    def get_random_word_from_dataset():
        with open('dataset.csv') as f:
            words = f.read().split()
            picked_word = random.choice(words)
            return picked_word

    
    @task
    def get_google_3rd_link(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0',
        }
        params = {
            'q': self.get_random_word_from_dataset(),
            'num': '10'
        }
        response = self.client.get("/search", params=params, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        result = soup.find_all('div', attrs = {'class': 'ZINbbc'})
        results=[re.search('\/url\?q\=(.*)\&sa',str(i.find('a', href = True)['href'])) for i in result if "url" in str(i)]
        links=[i.group(1) for i in results if i != None]
        third_result = requests.get(links[2])
        print(third_result.text)



class WebsiteUser(HttpUser):
    wait_time = constant(0)
    tasks = [UserTasks]



class StepLoadShape(LoadTestShape):
    """
    A step load shape
    Keyword arguments:
        step_time -- Time between steps
        step_load -- User increase amount at each step
        spawn_rate -- Users to stop/start per second at every step
        time_limit -- Time limit in seconds
    """

    step_time = 60
    step_load = 3
    spawn_rate = 0.05
    time_limit = 840

    def tick(self):
        run_time = self.get_run_time()
        if run_time > self.time_limit:
            return None

        current_step = math.floor(run_time / self.step_time) + 1
        if current_step > 10:
            current_step = 10
        return (current_step * self.step_load, self.spawn_rate)


# class StagesShape(LoadTestShape):       # This another way that we can define a loadtestshape for our test
#     """
#     A simply load test shape class that has different user and spawn_rate at
#     different stages.
#     Keyword arguments:
#         stages -- A list of dicts, each representing a stage with the following keys:
#             duration -- When this many seconds pass the test is advanced to the next stage
#             users -- Total user count
#             spawn_rate -- Number of users to start/stop per second
#             stop -- A boolean that can stop that test at a specific stage
#         stop_at_end -- Can be set to stop once all stages have run.
#     """

#     stages = [
#         {"duration": 60, "users": 3, "spawn_rate": 0.05},
#         {"duration": 60, "users": 6, "spawn_rate": 0.05},
#         {"duration": 60, "users": 9, "spawn_rate": 0.05},
#         {"duration": 60, "users": 12, "spawn_rate": 0.05},
#         {"duration": 60, "users": 15, "spawn_rate": 0.05},
#         {"duration": 60, "users": 18, "spawn_rate": 0.05},
#         {"duration": 60, "users": 21, "spawn_rate": 0.05},
#         {"duration": 60, "users": 24, "spawn_rate": 0.05},
#         {"duration": 60, "users": 27, "spawn_rate": 0.05},
#         {"duration": 300, "users": 30, "spawn_rate": 0.05},
#     ]

#     def tick(self):
#         run_time = self.get_run_time()

#         for stage in self.stages:
#             if run_time < stage["duration"]:
#                 tick_data = (stage["users"], stage["spawn_rate"])
#                 return tick_data
#         return None

