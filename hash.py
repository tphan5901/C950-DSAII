#Code for the HashTable obtained from: https://wgu.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=f08d7871-d57a-496e-a6a1-ac7601308c71
class HashTable:
    #Intialize hashtable and predefine capacity
    def __init__(self, initial_capacity=41):
        self.table = [[] for _ in range(initial_capacity)]

    def insert(self, key, item):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]
        # update key if it is already in the bucket
        for kv in bucket_list:
            if kv[0] == key:
                kv[1] = item
                return
        bucket_list.append([key, item])

    # Searches for an item with matching key in the hash table.
    # Returns the item if found, or None if not found.
    def search(self, key):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]
        for kv in bucket_list:
            if kv[0] == key:
                return kv[1]
        return None
    
    def values(self):
        #Return all package objects in the HashTable
        all_values = []
        for bucket in self.table:
            for key_value in bucket:
                all_values.append(key_value[1])
        return all_values
    
