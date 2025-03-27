#011746951
import csv
import datetime
from hash import *
from package import *
from truck import *
from collections import deque
from itertools import permutations
from tabulate import tabulate
from colorama import Fore, Style
import random
import heapq

#Lookup with package using its ID. Time complexity = O(1)
def lookUp(id):
    return parsedPackages.search(id) 

#reverse address lookup using indexes
reverseAddressDict = {}

#Parse file, append data to initialized dictionary as key-val pairs. Time complexity O(N) where n is the number of rows
def loadAddresses():
    with open('WGUPS_Addresses.csv', encoding='utf-8-sig') as f:
        rida = csv.reader(f)
        for row in rida:
            index = int(row[0]) 
            address = row[2]  
            addressDict[address] = index 
            reverseAddressDict[index] = address
            
#Parse file, append data to initialized dictionary. Time complexity: O(N) where n is the number of rows
def loadpackage():
    try:
        with open('WGUPS_Package.csv', encoding='utf-8-sig') as f: 
            reader = csv.reader(f)
            for row in reader:
                address_index = addressDict.get(row[1].strip(), 0)
                
                newpackage = Package(
                    id=row[0].strip(),
                    address=address_index,
                    city=row[2].strip(),
                    state=row[3].strip(),
                    zip_code=row[4].strip(), 
                    delivery_time=row[5].strip(),
                    weight=row[6].strip(),
                    notes=row[7].strip(),
                    status= "at hub"
                    )
                parsedPackages.insert(newpackage.id, newpackage)
        return parsedPackages
    except Exception as e:
        print(f"Error parsing packages: {e}")
        return None

#parse data from the csv file. Time-complexity: O(N) where n is the number of rows
def readDistance():
    with open('distance_data.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            distanceData.append(row)
    return distanceData

#Init HashTable
parsedPackages = HashTable()

#distance arr
distanceData = []

#init dictionary 
addressDict = {}

loadAddresses()
parsedPackages = loadpackage()
distanceData = readDistance()


#Retrieve distance between two locations using distance matrix. Time complexity = O(1)
def getdistance(truckaddress, packageaddress):
    try:
        distance = distanceData[truckaddress][packageaddress]
        if distance == '' or distance is None:
            distance = distanceData[packageaddress][truckaddress]
        return float(distance)
    except Exception as e:
        print(f"Error: {e}")


POPULATION = 100
MUTATION = 0.01 
GENERATIONS = 100

#Generates an initial population of routes using random permutations. Time Complexity = O(P⋅n)
def populate(packages):
    #sort deadline packages by time, packages with deadlines remain unordered
    deadline_packages = sorted([p for p in packages if lookUp(p).delivery_time != 'EOD'], key=lambda pid: 
        datetime.datetime.strptime(lookUp(pid).delivery_time, "%I:%M %p")
    )
    eod_packages = [p for p in packages if lookUp(p).delivery_time == 'EOD']
    population = []
    for i in range(POPULATION):
        shuffled_eod = eod_packages.copy()
        random.shuffle(shuffled_eod)
        population.append(deadline_packages + shuffled_eod)
    return population

#Calculate total distance for a given truck route. Time Complexity = 0(n)
def weights(route, truck):
    totaldistance = 0
    currentAddress = truck.address
    for packageID in route:
        package = lookUp(packageID)
        if package:
            totaldistance += getdistance(currentAddress, package.address)
            currentAddress = package.address
    totaldistance += getdistance(currentAddress, addressDict["4001 South 700 East"])
    return totaldistance

#Create a child route where it would inherit contiguous segments from parent routes.
#Time-space complexity O(n^2)
def inheritance(parent1, parent2):
    size = len(parent2)
    #create child route w/ size of parent
    child = [None] * size
    #select starting & end points
    start, end = sorted([random.randint(0, size - 1) for i in range(2)])
    # assign sub-route to child from parent1 between start- end indices.
    child[start:end] = parent1[start:end]
    p2_pointer = 0
    for i in range(size):
        if child[i] is None:
            while parent2[p2_pointer] in child:
                p2_pointer += 1
            #add non-duplicate value from parent2.
            child[i] = parent2[p2_pointer]
    return child

#Apply random mutation by selecting two locations in a route and swapping them. Time complexity = O(1)
def mutation(route):
    if random.random() < MUTATION:
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
    return route

#Truncate top 3rd of routes by selection of shortest distances. Time complexity: O(nlogn)
def selection(population, truck):
    sort = sorted(population, key=lambda route: weights(route, truck))
    return sort[:POPULATION // 3]  

#Child route inherits attributes + mutations from parent routes 
#Select optimal route each successive generation. 
#Time-space complexity O(n^2)
def bestroute(truck):
    population = populate(truck.packages)
    for g in range(GENERATIONS):
        #select route
        selected = selection(population, truck)
        nextpopulation = []
        for p in range(POPULATION):
            #select two parents 
            parent1, parent2 = random.sample(selected, 2)
            #crossover
            child = inheritance(parent1, parent2)
            #swap locations
            child = mutation(child)
            nextpopulation.append(child)
        population = nextpopulation
    route = min(population, key=lambda route: weights(route, truck))
    return route

#Executes deliveries. Time complexity o(n)
def init(truck):
    route = bestroute(truck)
    currentAddress = truck.address
#20,16,14,13,15
    for packageID in route:  
        #obtain next package
        package = lookUp(packageID)
        if package:
            distance = getdistance(currentAddress, package.address)
            # Update address at 10:20 AM
            if truck.time >= datetime.timedelta(hours=10, minutes=20) and package.id == '9':
                package.address = addressDict["410 S State St"]
                new_route = bestroute(truck)
                route = route[:route.index(package.id)] + new_route
            truck.miles += distance
            truck.time += datetime.timedelta(minutes=(distance / 0.3))
            print(f"Truck {truck.truckID} delivered package {package.id} at {truck.time}")  
            currentAddress = package.address
            package.time_delivered = truck.time
            package.truckID = truck.truckID
    # Return to hub
    hub = addressDict["4001 South 700 East"] 
    distance_to_hub = getdistance(currentAddress, hub)
    truck.miles += distance_to_hub
    truck.time += datetime.timedelta(minutes=(distance_to_hub / 0.3))
    truck.miles = float(f"{truck.miles:.1f}")


#Instantiate new truck objects.
truck1 = Truck(packages=[str(a) for a in [15, 13, 14, 1, 16, 19, 20, 29, 30, 31, 34, 37, 40]], address=addressDict["4001 South 700 East"], miles=0, time=datetime.timedelta(hours=8), truckID=1)

truck2Packages = [str(b) for b in [6, 25, 18, 22, 23, 3, 27, 28, 32, 33, 35, 36, 38]]
truck2 = Truck(truck2Packages, addressDict["4001 South 700 East"], 0, datetime.timedelta(hours=9, minutes=5), 2)

truck3Packages = [str(c) for c in [2, 4, 5, 7, 8, 9, 10, 11, 12, 17, 21, 24, 26, 39]] 
truck3 = Truck(truck3Packages, addressDict["4001 South 700 East"], 0, datetime.timedelta(hours=10, minutes=10), 3)

#assign packages to trucks based on notes. Time complexity O(N^2)
def sortPackages(parsedPackages, trucks):
    try:
        for package in parsedPackages.values():
            assigned = False
            specialNotes = package.notes
            deliveryTime = package.deliveryTime
        
            #assign to trucks based on special conditions
            if "Can only be on truck 2" in specialNotes:
                trucks[1].packages.append(package)  
                assigned = True
            elif "Must be delivered with" in specialNotes:
                pairPackages = [id.strip() for id in specialNotes.split("Must be delivered with")[1].split(",")]
                for extractIDs in pairPackages:
                    related_package = parsedPackages.get(extractIDs.strip())
                    if related_package:                                                 
                        trucks[0].packages.append(related_package)  
                trucks[0].packages.append(package)  
                assigned = True
            elif "Delayed on flight---will not arrive to depot until 9:05 am" in specialNotes:
                trucks[1].packages.append(package) 
                assigned = True
            elif "Wrong address listed" in specialNotes:
                trucks[2].packages.append(package) 
                assigned = True
            elif "EOD" in deliveryTime:
                trucks[2].packages.append(package)  
                assigned = True
            if not assigned:
                trucks[2].packages.append(package) 
    except Exception as e:
        print(f"Exception: {e}")

trucks = [None, truck1, truck2, truck3]  

#print(truck1.lookUp(1))
#print(truck1.lookUp(2))
#print(truck1.lookUp(3))

#print each row in arr. time-space complexity: o(n)
#for a in distanceData:
#   print(a)
#sortPackages(parsedPackages, trucks)

def run():
    init(truck1)
    init(truck2)
    init(truck3)

#Convert timedelta to HH:MM format. Time complexity = O(1)
def timedelta(td):
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    am_pm = "AM" if hours < 12 else "PM"
    hours = hours % 12
    hours = 12 if hours == 0 else hours
    return f"{hours}:{minutes:02d} {am_pm}"


#Interface
def interface():
    print('Package Parcel Delivery Service')
    print('**********************')
    totalmiles = round(truck1.miles + truck2.miles + truck3.miles, 2)
    print(f"Route completed in: {totalmiles} miles")
    print(f"Truck 1 miles: {truck1.miles}")
    print(f"Truck 2 miles: {truck2.miles}")
    print(f"Truck 3 miles: {truck3.miles}")
    print('**********************')

    while True:
        print("\nEnter a command (1-3):")
        print("1. Display specific package")
        print("2. Display all package status")
        print("3. Exit")
        selectedNum = int(input())

        if selectedNum == 1:
            packageId = input('Enter a Package ID (1-40): ')
            timestamp = input('Enter a time in HH:MM format: ')
            h, m = map(int, timestamp.split(':'))
            user_time = datetime.timedelta(hours=h, minutes=m)

            #fetch package
            tempStorage = lookUp(packageId)

            address = reverseAddressDict.get(tempStorage.address, "Unknown")
            if tempStorage.id == '9':
                address = "410 S State St" if user_time >= datetime.timedelta(hours=10, minutes=20) else "300 State St"

            truck_departure = {
                1: datetime.timedelta(hours=8),
                2: datetime.timedelta(hours=9, minutes=5),
                3: datetime.timedelta(hours=10, minutes=10)
            }.get(tempStorage.truckID, datetime.timedelta(0))

            #determine status
            status = (
                "at hub" if user_time <= truck_departure else
                "en route" if not tempStorage.time_delivered or user_time < tempStorage.time_delivered else
                "delivered"
            )

            delivered_time = (
                timedelta(tempStorage.time_delivered) 
                if status == "delivered" 
                else "--"
            )

            print(tabulate([[tempStorage.id, timedelta(truck_departure), status, tempStorage.delivery_time, address, delivered_time, tempStorage.truckID]],
                headers=["Package ID", "Leaves Hub", "Status", "Deadline", "Delivery Address", "Time Delivered", "Truck"],tablefmt="grid"))

        elif selectedNum == 2:
            timestamp = input('Enter a time in HH:MM format: ')
            h, m = map(int, timestamp.split(':'))
            query_time = datetime.timedelta(hours=h, minutes=m)

            print(f"Status of packages at {timestamp}:")
            table_data = []

            #change address of pkg 9 at 10:20
            for Package in parsedPackages.values():
                address = reverseAddressDict.get(Package.address, "Unknown")
                if Package.id == '9':
                    address = "410 S State St" if query_time >= datetime.timedelta(hours=10, minutes=20) else "300 State St"

                truck_departure = {
                    1: datetime.timedelta(hours=8),
                    2: datetime.timedelta(hours=9, minutes=5),
                    3: datetime.timedelta(hours=10, minutes=10)
                }.get(Package.truckID, datetime.timedelta(0))

                # determine status
                status = (
                    "at hub" if query_time <= truck_departure else
                    "en route" if not Package.time_delivered or query_time < Package.time_delivered else
                    "delivered"
                )

                delivered_time = (
                    timedelta(Package.time_delivered) 
                    if status == "delivered" 
                    else "--"
                )

                table_data.append([
                Package.id,
                address,
                timedelta(truck_departure),
                status,
                Package.delivery_time,
                delivered_time,
                Package.truckID
            ])
            
            print(tabulate(table_data,headers=[f"{Fore.BLUE}Package ID{Style.RESET_ALL}", "Address", f"{Fore.LIGHTGREEN_EX}Leaves hub at{Style.RESET_ALL}",
                        "Status", f"{Fore.CYAN}Deadline{Style.RESET_ALL}", "Time delivered", "Truck ID"], tablefmt="pretty"))

        elif selectedNum == 3:
            print("Exiting program...")
            break

        else:
            print("Invalid command, please try again.")

#main
if "__main__":
    run()
    interface()


    