# Class to store all the hub information
class Hubs:
    def __init__(self, address, zip, wgu_dist, distances):
        # Setting the address, zip code, and the distance to the wgu main hub
        self.address = address
        self.zip = zip
        self.wgu_dist = wgu_dist

        # dictionary with all hub distances
        self.distances = distances

