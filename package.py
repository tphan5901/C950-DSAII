#package class object
class Package:
    def __init__(self, id, address, city, state, zip_code, delivery_time, weight, notes, status):
        self.id = id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code  
        self.delivery_time = delivery_time
        self.weight = weight
        self.notes = notes
        self.status = status
        self.time_delivered = None
        self.truckID = None

    def __str__(self):
        return ("ID: %s, Address: %-20s, City: %s, State: %s, Zip: %s, "
                "Delivery Time: %s, Weight: %s, Notes: %s, "
                "Time Delivered: %s, Truck ID: %s") % (
            self.id, self.address, self.city, self.state, self.zip,
            self.deliveryTime, self.weight, self.notes, self.time_delivered, self.truckID
        )
        

