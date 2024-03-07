import random

from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from components import Source, Sink, SourceSink, Bridge, Link, Vehicle
import pandas as pd
from collections import defaultdict


# ---------------------------------------------------------------
def set_lat_lon_bound(lat_min, lat_max, lon_min, lon_max, edge_ratio=0.02):
    """
    Set the HTML continuous space canvas bounding box (for visualization)
    give the min and max latitudes and Longitudes in Decimal Degrees (DD)

    Add white borders at edges (default 2%) of the bounding box
    """

    lat_edge = (lat_max - lat_min) * edge_ratio
    lon_edge = (lon_max - lon_min) * edge_ratio

    x_max = lon_max + lon_edge
    y_max = lat_min - lat_edge
    x_min = lon_min - lon_edge
    y_min = lat_max + lat_edge
    return y_min, y_max, x_min, x_max


# ---------------------------------------------------------------
class BangladeshModel(Model):
    """
    The main (top-level) simulation model

    One tick represents one minute; this can be changed
    but the distance calculation need to be adapted accordingly

    Class Attributes:
    -----------------
    step_time: int
        step_time = 1 # 1 step is 1 min

    path_ids_dict: defaultdict
        Key: (origin, destination)
        Value: the shortest path (Infra component IDs) from an origin to a destination

        Since there is only one road in the Demo, the paths are added with the road info;
        when there is a more complex network layout, the paths need to be managed differently

    sources: list
        all sources in the network

    sinks: list
        all sinks in the network

    """

    step_time = 1

    def __init__(self, seed=None, x_max=500, y_max=500, x_min=0, y_min=0, scen_dict = {'A': 0, 'B': 0, 'C': 0, 'D': 0}):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []
        self.bridges = []
        random.seed(seed)

        # Own data collector
        self.total_travel_time = []
        self.trucks_sink_counter = 0
        self.total_waiting_time = []

        self.total_delay_time = []
        self.amount_of_bridges = 0
        self.delay_per_bridge = {}

        self.generate_model()
        self.break_bridges(scen_dict)

        # # Data collector
        # bridge_metrics = {"delay_time": "delay_time"}
        # truck_metrics = {"travel_time": lambda agent: agent.travel_time
        #                 if type(agent) is Vehicle and agent.reached_end_flag == True
        #                     else None}
        #
        # self.datacollector_bridge = DataCollector(agent_reporters=bridge_metrics)
        # self.datacollector_trucks = DataCollector(agent_reporters=truck_metrics)


    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels
        """

        df = pd.read_csv('../data/N1_data_v2.csv')

        # a list of names of roads to be generated
        roads = ['N1']

        # roads = [
        #     'N1', 'N2', 'N3', 'N4',
        #     'N5', 'N6', 'N7', 'N8'
        # ]

        df_objects_all = []
        for road in roads:

            # be careful with the sorting
            # better remove sorting by id
            # Select all the objects on a particular road
            df_objects_on_road = df[df['road'] == road].sort_values(by=['id'])

            if not df_objects_on_road.empty:
                df_objects_all.append(df_objects_on_road)

                # the object IDs on a given road
                path_ids = df_objects_on_road['id']
                # add the path to the path_ids_dict
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                # put the path in reversed order and reindex
                path_ids = path_ids[::-1]
                path_ids.reset_index(inplace=True, drop=True)
                # add the path to the path_ids_dict so that the vehicles can drive backwards too
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids

        # put back to df with selected roads so that min and max and be easily calculated
        df = pd.concat(df_objects_all)
        y_min, y_max, x_min, x_max = set_lat_lon_bound(
            df['lat'].min(),
            df['lat'].max(),
            df['lon'].min(),
            df['lon'].max(),
            0.05
        )

        # ContinuousSpace from the Mesa package;
        # not to be confused with the SimpleContinuousModule visualization
        self.space = ContinuousSpace(x_max, y_max, True, x_min, y_min)

        for df in df_objects_all:
            for _, row in df.iterrows():    # index, row in ...

                # create agents according to model_type
                model_type = row['model_type']
                agent = None

                if model_type == 'source':
                    agent = Source(row['id'], self, row['length'], row['name'], row['road'])
                    self.sources.append(agent.unique_id)
                elif model_type == 'sink':
                    agent = Sink(row['id'], self, row['length'], row['name'], row['road'])
                    self.sinks.append(agent.unique_id)
                elif model_type == 'sourcesink':
                    agent = SourceSink(row['id'], self, row['length'], row['name'], row['road'])
                    self.sources.append(agent.unique_id)
                    self.sinks.append(agent.unique_id)
                elif model_type == 'bridge':
                    agent = Bridge(row['id'], self, row['length'], row['name'], row['road'], row['condition'])
                    self.bridges.append(agent)
                elif model_type == 'link':
                    agent = Link(row['id'], self, row['length'], row['name'], row['road'])

                if agent:
                    self.schedule.add(agent)
                    y = row['lat']
                    x = row['lon']
                    self.space.place_agent(agent, (x, y))
                    agent.pos = (x, y)


    def get_random_route(self, source):
        """
        pick up a random route given an origin
        """
        while True:
            # different source and sink
            sink = self.random.choice(self.sinks)
            if sink is not source:
                break
        return self.path_ids_dict[source, sink]

    def step(self):
        """
        Advance the simulation by one step.
        """
        # self.datacollector_bridge.collect(self)
        # self.datacollector_trucks.collect(self)
        self.schedule.step()

    def break_bridges(self, scenario_dict):
        for key in scenario_dict:
            print(key)
            bridges_condition_list = []
            for bridge in self.bridges:
                # print(bridge)
                # print(bridge.condition)
                if bridge.condition == key:
                    bridges_condition_list.append(bridge)
            # for bridge in bridges_condition_list:
            #     print(bridge.condition)

            amount_bridges = len(bridges_condition_list)
            amount_bridges_to_break = int((scenario_dict[key] / 100) * amount_bridges)
            for i in range(amount_bridges_to_break):
                bridge_to_break = random.choice(bridges_condition_list)
                #print(bridge_to_break)
                bridge_to_break.delay_time = bridge_to_break.get_delay_time()
                #print(bridge_to_break.delay_time)
                bridges_condition_list.remove(bridge_to_break)

    def get_data(self):
        data_dict = {}
        data_dict['avg_travel_time'] = sum(self.total_travel_time) / self.trucks_sink_counter
        data_dict['avg_waiting_time'] = sum(self.total_waiting_time) / self.trucks_sink_counter
        return data_dict


# EOF -----------------------------------------------------------
