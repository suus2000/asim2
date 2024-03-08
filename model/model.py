import random

from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
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

    NEWLY ADDED:
    bridges: list
        all bridges in the network

    total_travel_time: list
        the travel time of each agent that has reached the end of the road

    truck_sink_counter: int
        the number of trucks that reach the end of the road

    total_waiting_time:
        the total waiting time of each agent that has reached the end of the road
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

        self.total_travel_time = []
        self.trucks_sink_counter = 0
        self.total_waiting_time = []

        self.amount_of_bridges = 0

        self.generate_model()
        # The method break_bridges is called to determine which
        # bridges should break with the scenario dictionary as input
        self.break_bridges(scen_dict)

        # Sets the seed of the model at initialization
        random.seed(seed)




    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels
        """

        # Cleaned data of N1 is used to run the model
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
                    # To check whether a bridge should break, its condition is needed
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
        self.schedule.step()

    def break_bridges(self, scenario_dict):
        """
        Determines which bridge should break and flags them
        """
        # Checks what bridges have a certain key (A,B,C,D) and adds them to a list
        for key in scenario_dict:
            bridges_condition_list = []
            for bridge in self.bridges:
                if bridge.condition == key:
                    bridges_condition_list.append(bridge)

            # Determines what amount of bridges of a certain condition should be broken with the scenario dictionary,
            # then makes random choices and flags them
            amount_bridges = len(bridges_condition_list)
            amount_bridges_to_break = int((scenario_dict[key] / 100) * amount_bridges)
            for i in range(amount_bridges_to_break):
                bridge_to_break = random.choice(bridges_condition_list)
                bridge_to_break.broken = True
                bridges_condition_list.remove(bridge_to_break)

    def get_data(self, seed):
        """
        Own data collector, more efficient as it generates data at end of model
        """
        data_dict = {}
        # Seed is being used as column name
        seed = str(seed)
        # Average travel time and average waiting time are being reported per run in one df per scenario
        data_dict['Average Travel Time'] = sum(self.total_travel_time) / self.trucks_sink_counter
        data_dict['Average Waiting Time'] = sum(self.total_waiting_time) / self.trucks_sink_counter
        df = pd.DataFrame.from_dict(data_dict, orient='index', columns=[seed])
        return df


# EOF -----------------------------------------------------------
