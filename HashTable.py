class HashTable:

    def __init__(self):
        self.packages = []
        self.special_notes = []
        self.delivered_with = []
        self.delivery_deadlines = []

    # insert the packages using a linear probing hash function
    def insert_package_hash(self, id, address, city, state, zip, deadline, weight, notes, time, status, est_time):
        self.row_dictionary = {}

        # Find the item's index by using a hash function
        self.row_dictionary["id"] = id.strip()
        self.row_dictionary["address"] = address
        self.row_dictionary["city"] = city
        self.row_dictionary["state"] = state
        self.row_dictionary["zip"] = zip
        self.row_dictionary["deadline"] = deadline
        self.row_dictionary["weight"] = weight
        self.row_dictionary["notes"] = notes
        self.row_dictionary["time"] = time
        self.row_dictionary["status"] = status
        self.row_dictionary["est time"] = est_time
        self.packages.append(self.row_dictionary)

        # Add onto list of packages that has special notes
        if len(notes) != 0:
            if "delivered with" in notes:
                self.delivered_with.append(self.row_dictionary)
            else:
                self.special_notes.append(self.row_dictionary)
                if "Delayed" in notes:
                    self.row_dictionary["status"] = "Delayed"

        # Add onto list of packages that have a deadline, not include EOD
        if "EOD" not in deadline:
            self.delivery_deadlines.append(self.row_dictionary)

    # function to search for the given value within packages, if it exists return the dictionary for that package
    def search_hash_value(self, value):
        for package in self.packages:
            if value in package.values():
                return package

    # function to search for the given key within packages, if it exists return the dictionary for that package
    def search_hash_key(self, key):
        for package in self.packages:
            if key in package.row_dictionary.values():
                return package.row_dictionary
