# Autumrose Stubbs 010698056
# Performance assessment for Data Structures and Algorithms II
import csv
from datetime import datetime, timedelta

from HashTable import HashTable
from Hubs import Hubs


#
#
# This section includes the methods used to read in the files and store the information
#
#


# Method to create all the call hubs and store the information
def read_hubs_file(filename, header_row):
    # Skip the first rows until the header starts
    i = 0
    with open(filename, 'r') as f:

        # Read the CSV file into a dictionary
        csv_reader = csv.reader(f)

        # Read in the first element
        next(csv_reader)
        row = next(csv_reader)
        address = row[0][29:len(row[0]) - 27].strip()
        zip_code = row[0][len(row[0]) - 7:len(row[0])].strip().replace("(", "").replace(")", "")
        hub = Hubs(address, zip_code, 0, {address: row[2]})
        hub_list.append(hub)
        count = 1
        # Iterate through the CSV dictionary and add them to the list using the insert_hash function
        for row in csv_reader:
            # Separate address and zip for easier comparison to package information
            address = row[1][:len(row[1]) - 7].strip()
            zip_code = row[1][len(row[1]) - 7:len(row[1])].strip().replace("(", "").replace(")", "")

            # Replace South with S for consistency
            if "South" in address:
                address = address.replace("South", "S")
            # initialize the dictionary to hold distances from current location
            distances_dict = {}

            # utilize count as each row increases the amount of cities by 1
            i = 0
            while i < count:
                distances_dict[hub_list[i].address] = row[i + 2]
                i += 1
            hub = Hubs(address, zip_code, row[2], distances_dict)
            hub_list.append(hub)
            count += 1


# Convert the package Excel to CSV, input variables are destination of excel and destination for the CSV
def read_package_file(filename, header_row):
    # Skip the first rows until the header starts
    i = 0
    with open(filename, 'r') as f:
        # Read the CSV file into a dictionary
        csv_reader = csv.DictReader(f)

        # Initiate the hash function list
        package_dict = HashTable()

        # Iterate through the CSV dictionary and add them to the list using the insert_hash function
        for row in csv_reader:
            address = row["Address"]
            # Replace South with S for consistency
            if "South" in address:
                address = address.replace("South", "S").strip()
            package_dict.insert_package_hash(row['Package\nID'].strip(), address, row["City "].strip(),
                                             row["State"].strip(), row["Zip"].strip(),
                                             row["Delivery\nDeadline"].strip(), row["Mass\nKILO"].strip(),
                                             row["page 1 of 1PageSpecial Notes"].strip(), None, "At the hub",
                                             datetime.strptime("23:59", '%H:%M'))
        return package_dict


#
#
# This section includes all helper methods
#
#


# Helper method for the sort_hubs() method insert_package() method
# This method will find and return the hub correlated with the given address
def find_location(address):
    for hub in hub_list:
        if address == hub.address:
            return hub


# This method first attempts to assign the package to truck 1 if there's room, if not will check truck 2 then truck 3
def standard_truck_assignment(truck1, truck2, truck3, package, max_size):
    # Keep truck 1 only full with a third of the packages. Truck 1 has the closest packages
    # Keep the truck light so it can finish fast and the driver can switch to truck 3

    if len(truck1) < round(len(package_hash.packages) / 3):
        truck1.append(package)
    # Then truck 2 if truck 3 was full
    elif len(truck2) < max_size:
        truck2.append(package)
    # And lastly add to truck 1 if both the other two were full
    elif len(truck3) < max_size:
        truck3.append(package)
    # Default to informing the user the trucks are all full if all 3 were denied
    else:
        print("You have too many packages, all your trucks are full!")


# When adding an item to a truck you must balance by removing an item from that truck and adding to the previous truck
# The list is already sorted so the closest locations are in truck 1 and the farthest are in truck 3
def balance_swap_packages(new_truck, old_truck, address, farther):
    # Don't move any items that have special notes, continue to the next item if they do
    # If farther is true assign 0 index i.e i.e truck 3 to truck 2
    if farther:
        i = 0
        while i < len(old_truck):
            package = old_truck[i]
            if package["notes"] == "" and package["address"] != address:
                insert_package(new_truck, package)
                old_truck.remove(package)
                break
            else:
                i += 1
    # else assign the last element index i.e truck 3 to 2
    else:
        i = len(old_truck) - 1
        while i > 0:
            package = old_truck[i]
            if package["notes"] == "" and package["address"] != address:
                insert_package(new_truck, package)
                old_truck.remove(package)
                break
            else:
                i -= 1


# When adding an item to a truck you must balance by removing an item from that truck and adding to the previous truck
# The list is already sorted so the closest locations are in truck 1 and the farthest are in truck 3
def balance_swap_packages_post_deadline(new_truck, old_truck, address, farther):
    # Don't move any items that have special notes, continue to the next item if they do
    # If farther is true assign 0 index i.e i.e truck 3 to truck 2
    if farther:
        i = 0
        while i < len(old_truck):
            package = old_truck[i]
            if package["notes"] == "" and package["address"] != address and package["deadline"] == "EOD":
                insert_package(new_truck, package)
                old_truck.remove(package)
                break
            else:
                i += 1
    # else assign the last element index i.e truck 3 to 2
    else:
        i = len(old_truck) - 1
        while i > 0:
            package = old_truck[i]
            if package["notes"] == "" and package["address"] != address and package["deadline"] == "EOD":
                insert_package(new_truck, package)
                old_truck.remove(package)
                break
            else:
                i -= 1


# Move all packages that match the given address to the given truck
def move_matching_packages(new_truck, old_truck, address, notes):
    matching_packages = []
    i = 0
    while i < len(old_truck):
        package = old_truck[i]
        if package["address"] == address:
            if package["notes"] == "" or package["notes"] == notes:
                matching_packages.append(package)

        i += 1
    for package in matching_packages:
        insert_package(new_truck, package)
        old_truck.remove(package)

    return len(matching_packages)


# Iterate through each truck and move deadline items up in the given truck until each item is meeting it's deadline
def move_packages_to_meet_deadline(truck, start_time):
    on_time = False

    # Set up initial estimated delivery times
    set_est_delivery_time(truck, start_time)

    # Iterate through each truck in the given truck
    for i in range(0, len(truck)):
        package = truck[i]
        # First check if the package even has a deadline
        if package in package_hash.delivery_deadlines:
            est_arrival = package["est time"]
            pkg_deadline = package["deadline"]
            pkg_deadline = datetime.strptime(pkg_deadline[:-3], '%H:%M')
            # Check if the package is already meeting it's deadline
            if pkg_deadline < est_arrival:
                on_time = False
                j = i - 1
                # Continue to move the package up in the truck until it's on time
                while not on_time and j >= 0:
                    prev = truck[j]
                    # Check if the package has no deadline or if it's already late
                    if prev["deadline"] == "EOD" or (prev["est time"] > datetime.strptime(prev["deadline"][:-3], '%H:%M')):
                        truck.remove(package)
                        truck.insert(j, package)
                        set_est_delivery_time(truck, start_time)
                        est_arrival = package["est time"]
                        # Check if the package will now make it by the deadline
                        if est_arrival <= pkg_deadline:
                            # Now that the package has it's new index, move matching address packages up
                            k = i - 1
                            while k > 0:
                                # Iterate through the items before the package's original index, until there's no match
                                prev = truck[k]
                                if prev is not package and prev["address"] == package["address"]:
                                    # If the address matches, move the package to the next index
                                    j += 1
                                    truck.remove(prev)
                                    truck.insert(j, prev)
                                    k -= 1
                                # Otherwise break as any matching addresses will be directly next to the package
                                else:
                                    break
                            # Reassign k to iterate the other direction
                            k = i + 1
                            while k < len(truck):
                                # Iterate through the items after the package's original index, until there's no match
                                prev = truck[k]
                                if prev is not package and prev["address"] == package["address"]:
                                    # If the address matches, move the package to the next index
                                    j += 1
                                    truck.remove(prev)
                                    truck.insert(j, prev)
                                    k += 1
                                # Otherwise break as any matching addresses will be directly next to the package
                                else:
                                    break
                            set_est_delivery_time(truck, start_time)
                            # Assign the boolean variable as True to break out of the loop
                            on_time = True
                    # If the previous package has a deadline and is already not on time
                    # Break as there is no way to be on time in this truck
                    else:
                        break
                    j -= 1
    return on_time


def set_est_delivery_time(truck, curr_time):
    previous_location = hub_list[0]
    total_miles = 0
    for curr_package in truck:
        # Assign the package's address and the hub for the package's address
        address = curr_package["address"]
        curr_hub = find_location(address)

        # If package address is in the previous locations listed distances
        if address == previous_location.address:
            curr_distance = 0
        elif address in previous_location.distances:
            # Assign that distance with rounding to one decimal for float
            curr_distance = round(float(previous_location.distances[address]), 1)
        # Else that means the previous_location distance must be listed under the curr_address
        else:
            # Find the previous location within current location's distances, round to the nearest 1, and assign
            curr_distance = round(float(curr_hub.distances[previous_location.address]), 1)
        # Calculate the current time and assign
        curr_time = calculate_time(curr_distance, curr_time)

        # Set the previous location and total miles
        previous_location = curr_hub

        # Set the estimated delivery time
        curr_package["est time"] = curr_time


# Set the status of a package to the given status and the time
def set_status(package, status, curr_time):
    package["status"] = status
    package["time"] = curr_time


# Set the starting status for the 3 trucks
def start_status(truck1, truck2, truck3):
    start_time = datetime.strptime("08:00", '%H:%M')
    for package in truck1:
        set_status(package, "En route", start_time)
    for package in truck2:
        set_status(package, "En route", start_time)
    for package in truck3:
        set_status(package, "At the hub", start_time)


# Helper method to calculate the time based on miles traveled, with the given speed of 18mph
def calculate_time(distance, curr_time):
    avg_speed = 18
    time = round(distance / avg_speed, 2)
    time_change = timedelta(hours=time)
    return curr_time + time_change


# Calculate the total miles traveled, with the given totals from each truck
def total_traveled_miles(truck1_miles, truck2_miles, truck3_miles):
    print("Current traveled miles: ", truck1_miles + truck1_miles + truck3_miles)


#
# This section includes processes used to sort the packages and assign packages to each truck
# First sort the hubs by closest to WGU, then sort the packages in the same order as the hub addresses are listed
# Assign to truck1, truck2, and truck3 respectively as they packages are already sorted
# Move any packages around based on special notes, use the insert function which will add it to the correct spot in the new truck
#


# Insert item into a truck and re-sort with the new item
def insert_package(truck, package):
    # Insert the package at the end to start
    truck.append(package)
    curr_hub = find_location(package["address"])
    smaller = True
    # Iterate through all the packages before the current one until there's none that are bigger
    i = len(truck) - 2
    while i >= 0 and smaller:
        prev_package = truck[i]
        prev_hub = find_location(prev_package["address"])
        # If the previous hub is closer to the WGU hub the hub's places
        if float(prev_hub.wgu_dist) > float(curr_hub.wgu_dist):
            truck[i] = package
            truck[i + 1] = prev_package
        else:
            # If no trade happened no need to continue for this item
            smaller = False
        i -= 1


# Sort the address from WGU starting hub from closest to farthest
def sort_hubs():
    i = 1
    # variable to tell the loop when it's done, if the item to the left is no longer greater
    smaller = True
    # Iterate through the list of hubs
    while i < len(hub_list):
        smaller = True
        j = i-1
        current = hub_list[i]
        # Iterate through all the hubs before the current one until there's none that are bigger
        while j >= 0 and smaller:
            previous = hub_list[j]
            # If the previous hub's distance from WGU is bigger swap the hub's places
            if float(previous.wgu_dist) > float(current.wgu_dist):
                hub_list[j] = current
                hub_list[j+1] = previous
            else:
                # If no trade happened no need to continue for this item
                smaller = False
            j -= 1
        i += 1


# Sort the packages in order of the closest to the primary hub to the farthest from the hub
# Using the already sorted list of hubs
def sort_packages():
    # Create a new list to temporarily store the sorted packages
    new_packages = []
    # access the global list for the packages
    global package_hash
    # Iterate through all of the sorted hubs
    for hub in hub_list:
        i = 0
        # Find all of the packages in the package hash that match the current hub
        while i < len(package_hash.packages):
            package = package_hash.packages[i]
            if hub.address == package["address"]:
                # If the package matches move it onto the end of the new list and remove it from the global
                new_packages.append(package)
                package_hash.packages.remove(package)
                i -= 1
            i += 1
    # Reassign the global list with the new list
    package_hash.packages = new_packages


#
# ALl pieces for ensuring all packages are going to make it on time by their delivery deadlines
# Call the method move_packages_to_meet_deadline within the same truck
# Move packages from different trucks if necessary
#
def deadline(truck1, truck2, truck3):
    # Move any packages with a deadline that aren't delayed to truck 2 as they are priority
    for package1 in truck3:
        if package1 in package_hash.delivery_deadlines and package1["notes"] == "":
            # Move the package and any packages that match its address to the same truck
            items_moved = move_matching_packages(truck2, truck3, package1["address"], package1["notes"])
            # Even out the trucks first, an item will be deleted from one so move all items over one
            for x in range(0, items_moved):
                # Take the first item from truck 3 add it to the end of truck 2
                balance_swap_packages_post_deadline(truck3, truck2, package1["address"], False)

    # Route truck 1, calculate the distance back to WGU and add it to truck 1 end time
    move_packages_to_meet_deadline(truck1, datetime.strptime("08:00", '%H:%M'))
    # Add the distance back to the WGU hub from the last stop of truck 1
    last_hub = find_location(truck1[len(truck1) - 1]["address"])
    truck1_end = round(float(last_hub.wgu_dist), 1)
    # Calculate the current time and assign
    truck1_end = calculate_time(truck1_end, truck1[len(truck1) - 1]["est time"])

    # Route truck 1, calculate the distance back to WGU and add it to truck 1 end time
    move_packages_to_meet_deadline(truck2, datetime.strptime("08:00", '%H:%M'))
    # Add the distance back to the WGU hub from the last stop of truck 1
    last_hub = find_location(truck2[len(truck1) - 1]["address"])
    truck2_end = round(float(last_hub.wgu_dist), 1)
    # Calculate the current time and assign
    truck2_end = calculate_time(truck2_end, truck2[len(truck2) - 1]["est time"])

    # Check which truck made it back first
    if truck1_end < truck2_end:
        start_time = truck1_end
    else:
        start_time = truck2_end
    # Truck 3 has all the delayed packages, must wait until 9:05 to depart
    if start_time < datetime.strptime("09:05", '%H:%M'):
        start_time = datetime.strptime("09:05", '%H:%M')
    on_time = move_packages_to_meet_deadline(truck3, start_time)

    # If there are still packages in truck 3 that are not on time
    # Take items from truck 1 and add them to truck 2, then pass to 3
    if not on_time:
        i = len(truck1) - 1
        while not on_time and i >= 0:
            package1 = truck1[i]
            # If the current package has no special notes or deadline, move to the end of truck 2 so truck 1 is faster
            # This way truck 1 driver can make it to truck 3 faster
            if package1["notes"] == "" and package1["deadline"] == "EOD" and len(truck3) < max_size:
                truck1.remove(package1)
                truck2.append(package1)
                j = len(truck2) - 1
                # From truck 2 then move the items at the end to truck 3 with the same specifications
                while not on_time and j >= 0:
                    package2 = truck2[i]
                    if package2["notes"] == "" and package2["deadline"] == "EOD" and len(truck3) < max_size:
                        truck2.remove(package2)
                        truck3.append(package2)
                        set_est_delivery_time(truck2, datetime.strptime("08:00", '%H:%M'))
                    j -= 1

                # Set truck 1's new delivery time, find
                set_est_delivery_time(truck1, datetime.strptime("08:00", '%H:%M'))
                # Add the distance back to the WGU hub from the last stop of truck 1
                last_hub = find_location(truck1[len(truck1) - 1]["address"])
                truck1_end = round(float(last_hub.wgu_dist), 1)
                # Calculate the current time and assign
                truck1_end = calculate_time(truck1_end, truck1[len(truck1) - 1]["est time"])

                # Check if all the packages in truck 3 are now on time
                set_est_delivery_time(truck3, truck1_end)
                for package3 in truck3:
                    if package3 not in package_hash.delivery_deadlines:
                        break
                    elif package3["est time"] > datetime.strptime(package3["deadline"][:-3], '%H:%M'):
                        on_time = False
                    else:
                        on_time = True
            i -= 1


def special_notes_delivered_with(truck1, truck2, truck3):
    deliver_with_packages = []
    for deliver_with_package in package_hash.delivered_with:
        # Find the additional package ID numbers
        special_notes = deliver_with_package["notes"]
        substring = special_notes[len(special_notes) - 7:]
        num1 = substring[:3].strip()
        num2 = substring[4:7].strip()

        # Find the packages associated with that ID
        num1_package = package_hash.search_hash_value(num1)
        num2_package = package_hash.search_hash_value(num2)
        num1_package["notes"] = "Must be delivered with ", deliver_with_package["id"], " ", num2_package["id"]
        num1_package["notes"] = "Must be delivered with ", deliver_with_package["id"], " ", num1_package["id"]

        # Keep track of all of the packages, only add if it's not already in the list
        if deliver_with_package not in deliver_with_packages:
            deliver_with_packages.append(deliver_with_package)
        if num1_package not in deliver_with_packages:
            deliver_with_packages.append(num1_package)
        if num2_package not in deliver_with_packages:
            deliver_with_packages.append(num2_package)

    # Sort the packages based on what trucks they're in
    deliver_with_truck1, deliver_with_truck2, deliver_with_truck3 = [], [], []
    for package in deliver_with_packages:
        if package in truck1:
            deliver_with_truck1.append(package)
        elif package in truck2:
            deliver_with_truck2.append(package)
        elif package in truck3:
            deliver_with_truck3.append(package)
    # Move the packages to the truck with the most already in it, if all equal will default to truck1
    # Check if truck 2 contains the most of the deliver together packages
    if len(deliver_with_truck2) > len(deliver_with_truck1) and len(deliver_with_truck2) > len(deliver_with_truck3):
        # Iterate through truck 1, remove the package first so it doesn't get swapped
        for package in deliver_with_truck1:
            # Move the package and any packages that match its address to the same truck
            items_moved = move_matching_packages(truck2, truck1, package["address"], package["notes"])

            # Even out the trucks first, an item will be deleted from one so move all items over one
            for x in range(0, items_moved):
                balance_swap_packages(truck1, truck2, package["address"], True)
        # Iterate through truck 3, remove the package first so it doesn't get swapped
        for package in deliver_with_truck3:
            # Move the package and any packages that match its address to the same truck
            items_moved = move_matching_packages(truck2, truck3, package["address"], package["notes"])
            # Even out the trucks first, an item will be deleted from one so move all items over one
            for x in range(0, items_moved):
                balance_swap_packages(truck3, truck2, package["address"], False)
    # Check if truck 3 contains the most of the deliver together packages
    elif len(deliver_with_truck3) > len(deliver_with_truck1) and len(deliver_with_truck3) > len(deliver_with_truck2):
        # Iterate through truck 1, remove the package first so it doesn't get swapped
        for package in deliver_with_truck2:
            # Move the package and any packages that match its address to the same truck
            items_moved = move_matching_packages(truck3, truck2, package["address"], package["notes"])

            # Even out the trucks first, an item will be deleted from one so move all items over one
            for x in range(0, items_moved):
                # Swap a package out from truck 3 to truck 2 then insert/sort the new package
                balance_swap_packages(truck2, truck3, package["address"], True)
        # Iterate through truck 3, remove the package first so it doesn't get swapped
        for package in deliver_with_truck1:
            # Move the package and any packages that match its address to the same truck
            items_moved = move_matching_packages(truck3, truck2, package["address"], package["notes"])
            # Even out the trucks first, an item will be deleted from one so move all items over one
            for x in range(0, items_moved):
                # Swap a package out from truck 3 to truck 2 then 2 to 1 then insert/sort the new package
                balance_swap_packages(truck2, truck3, package["address"], True)
                balance_swap_packages(truck1, truck2, package["address"], True)
    # If neither of the other trucks contained more packages or if they were equal then 1 is the default truck to add to
    else:
        # Iterate through truck 2, remove the package first so it doesn't get swapped
        for package in deliver_with_truck2:
            # Move the package and any packages that match its address to the same truck
            items_moved = move_matching_packages(truck1, truck2, package["address"], package["notes"])

            # Even out the trucks first, an item will be deleted from one so move all items over one
            for x in range(0, items_moved):
                # Swap a package out from truck 1 then insert/sort the new package
                balance_swap_packages(truck2, truck1, package["address"], False)
        # Iterate through truck 3, remove the package first so it doesn't get swapped
        for package in deliver_with_truck3:
            # Move the package and any packages that match its address to the same truck
            items_moved = move_matching_packages(truck1, truck3, package["address"], package["notes"])

            # Even out the trucks first, an item will be deleted from one so move all items over one
            for x in range(0, items_moved):
                # Swap a package out from truck 1 to truck 2 then 2 to 3 then insert/sort the new package
                balance_swap_packages(truck2, truck1, package["address"], False)
                balance_swap_packages(truck3, truck2, package["address"], False)


def special_notes_truck2(truck1, truck2, truck3, package):
    global max_size

    # If the package is incorrectly placed in truck 1
    if package in truck1:
        # Move the package and any packages that match its address to the same truck
        items_moved = move_matching_packages(truck2, truck1, package["address"], package["notes"])
        # Even out the trucks first, an item will be deleted from one so move all items over one
        for x in range(0, items_moved):
            balance_swap_packages(truck1, truck2, True)
    # If the package is incorrectly placed in truck 1
    elif package in truck3:
        # Move the package and any packages that match its address to the same truck
        items_moved = move_matching_packages(truck2, truck3, package["address"], package["notes"])
        # Even out the trucks first, an item will be deleted from one so move all items over one
        for x in range(0, items_moved):
            # Take the last item from truck 2 and add it to the front of truck 3 to make room for the new package
            balance_swap_packages(truck3, truck2, package["address"], False)


def special_notes_delayed(truck1, truck2, truck3, package):
    global max_size

    # If the package is incorrectly placed in truck 1
    if package in truck1:
        # Move the package and any packages that match its address to the same truck
        items_moved = move_matching_packages(truck3, truck1, package["address"], package["notes"])

        # Even out the trucks first, an item will be deleted from one so move all items over one
        for x in range (0, items_moved):
            # Take the first item from truck 3 add it to the end of truck 2
            balance_swap_packages(truck2, truck3, package["address"], True)
            # Then take the first item from truck 2 add it to the end of truck 1
            balance_swap_packages(truck1, truck2, package["address"], True)

    # If the package is incorrectly placed in truck 2
    elif package in truck2:
        # Move the package and any packages that match its address to the same truck
        items_moved = move_matching_packages(truck3, truck2, package["address"], package["notes"])

        # Take the first item from truck3 and add it to the end of truck2, iterate through how many packages were moved
        for x in range (0, items_moved):
            balance_swap_packages(truck2, truck3, package["address"], True)


def truck_assignment(truck1, truck2, truck3):
    global max_size
    # Sort the address from WGU starting hub from closest to farthest
    sort_hubs()

    # Sort the packages into the same order based on their delivery addresses
    sort_packages()

    i = 0
    # Iterate through the copy of the list of packages
    while i < len(package_hash.packages):
        # Assign the initial package and it's current address
        package = package_hash.packages[i]
        curr_address = package["address"]

        # Add each package to truck 1 first then truck 2 and 3
        standard_truck_assignment(truck1, truck2, truck3, package, max_size)
        i += 1

    # Check for special notes
    for package in package_hash.special_notes:
        # If truck 2 is in the notes use the method to assign the package to truck 2
        if "truck 2" in package["notes"]:
            special_notes_truck2(truck1, truck2, truck3, package)
        # If the notes contain delayed or wrong in the notes put it on truck 3 to wait to depart
        elif "Delayed" in package["notes"] or "Wrong" in package["notes"]:
            special_notes_delayed(truck1, truck2, truck3, package)
    # If the package needs to be delivered with other packages assign them all together in this one
    special_notes_delivered_with(truck1, truck2, truck3)
    # Check if packages are meeting their deadline and adjust if not
    deadline(truck1, truck2, truck3)


#
#
# This section includes main and the primary functions of the algorithm, with calling sort and routing the truck
#
#


#
# Trucks are in order of what route they will take
# This method calculates the time and distance between each stop and back to the WGU hub until the specified time
#
def route_truck(truck, start_time, end_time):
    # Total miles traveled
    total_miles = 0
    curr_time = start_time
    completion = True
    # Initialize the first location as the starting hub
    previous_location = hub_list[0]

    # Deliver packages in order as the truck's packages are already sorted
    # Iterate through each package in the first truck
    for package in truck:
        # For any package that had the wrong address make sure the time is after 10:20 to get the correct address
        if "Wrong" in package["notes"]:
            if curr_time < datetime.strptime("10:20", '%H:%M'):
                curr_time = datetime.strptime("10:20", '%H:%M')
            package["address"] = "410 S State St"
        # Assign the package's address and the hub for the package's address
        address = package["address"]
        curr_hub = find_location(address)
        # If package address is in the previous locations listed distances
        if address == previous_location.address:
            curr_distance = 0
        elif address in previous_location.distances:
            # Assign that distance with rounding to one decimal for float
            curr_distance = round(float(previous_location.distances[address]), 1)
        # Else that means the previous_location distance must be listed under the curr_address
        else:
            # Find the previous location within current location's distances, round to the nearest 1, and assign
            curr_distance = round(float(curr_hub.distances[previous_location.address]), 1)
        # Calculate the current time and assign
        curr_time = calculate_time(curr_distance, curr_time)
        # Check if it is passed the requested time
        if curr_time > end_time:
            completion = False
            break
        # If it's still within the time bounds, set the previous location and total miles
        else:
            total_miles = round(total_miles + curr_distance, 1)
            previous_location = curr_hub
            set_status(package, "Delivered", curr_time)

    # Add the distance back to the WGU hub from the last stop
    last_hub = find_location(truck[len(truck) - 1]["address"])
    curr_distance = round(float(last_hub.wgu_dist), 1)
    # Calculate the current time and assign
    curr_time = calculate_time(curr_distance, curr_time)
    total_miles += curr_distance

    # Return the total miles traveled, the ending time, and boolean for if the truck completed its route
    return {"miles_traveled": total_miles, "time_completed": curr_time, "truck_completed": completion}


# Greedy algorithm that first sorts by distance then considers special notes
def priorities(end_time):
    # Assign packages to their designated trucks
    truck1, truck2, truck3 = [], [], []
    truck_assignment(truck1, truck2, truck3)

    # Set the packages in truck 1 and 2 as en route at 8AM when they leave the hub and truck 3 as still at the hub
    start_status(truck1, truck2, truck3)
    # First route the first 2 trucks as there is only 1 driver
    truck3_results = {"miles_traveled": 0, "time_completed": end_time, "truck_completed": False}
    truck1_results = route_truck(truck1, datetime.strptime("08:00", '%H:%M'), end_time)
    truck2_results = route_truck(truck2, datetime.strptime("08:00", '%H:%M'), end_time)

    # Send truck 3 after truck 1 comes back as it has the closest locations and least packages
    # Check if the time is past 9:05 as truck 3 has all the delayed packages
    if truck1_results["time_completed"] > datetime.strptime("09:05", '%H:%M'):
        truck3_results = route_truck(truck3, truck1_results["time_completed"], end_time)
    else:
        truck3_results = route_truck(truck3, datetime.strptime("09:05", '%H:%M'), end_time)

    # Calculate and print total traveled miles if needed
    total_traveled_miles(truck1_results["miles_traveled"], truck2_results["miles_traveled"], truck3_results["miles_traveled"])


# Convert the files if still needed, read in all package and hub information
def initialize(id, end_time):
    # Create the hub list
    read_hubs_file("WGUPS Distance Table", 8)

    # Call the priorities method to assign and route the trucks until the specified time
    priorities(datetime.strptime(end_time, '%H:%M'))
    # If input is -1 print all packages
    if id == "-1":
        for package in package_hash.packages:
            print("id:", package['id'], "\tTime updated:", package["time"],
                  "\tDeadline:", package['deadline'], "\tWeight:", package["weight"], "\tAddress:", package["address"],
                  "\t City:", package["city"], "\t Zip Code:", package["zip"])
    # Otherwise print the specified package
    else:
        for package in package_hash.packages:
            if package["id"] == id:
                print("id: ", package['id'], "\tTime updated: ", package["time"],
                      "\tDeadline: ", package['deadline'], "\tWeight: ", package["weight"], "\tAddress: ",
                      package["address"],
                      "\t City: ", package["city"], "\t Zip Code: ", package["zip"])
                break


# Main program
if __name__ == '__main__':
    # Establish the global variables for packages, hubs, and the trucks
    # Read in the package file
    max_size = 16
    package_hash = read_package_file("WGUPS Package File", 8)
    hub_list = []

    # Read in user input
    user_selection = input("""
    Please enter the number of the option you would like from the list below:
        Option 1: Status update for all packages
        Option 2: Status update for specified package
        Option 3: Quit
    """)
    while user_selection != "3":
        # Print all of the packages at the given time
        if user_selection == "1":
            time = input("""
            Thank you for your selection, what time would you like to see the status for?
            "For the most accurate status, format your time with 2 digits for the hour/minutes and utilize the 24 hour clock":
                  Example: Input 15:30 for 3:30PM
            """)
            initialize("-1", time)
            break
        # Print the one package the user has selected at the given time
        elif user_selection == "2":
            time = input("""
            Thank you for your selection, what time would you like to see the status for?
            "For the most accurate status, format your time with 2 digits for the hour/minutes and utilize the 24 hour clock":
                  Example: Input 15:30 for 3:30PM
            """)
            input_id = input("Please enter in the package ID you would like to check from 1-40: ")
            initialize(input_id, time)
            break
        # Fallback if user has entered in an incorrect option
        else:
            print("Sorry your selection was invalid, please select an option from the menu below:")
            user_selection = input("""
                Please enter the number of the option you would like from the list below:
                    Option 1: Status update for all packages
                    Option 2: Status update for specified package
                    Option 3: Quit
                """)