class SymbolTable:
    def __init__(self, size):
        self.table_size = size
        self.table = [[] for _ in range(size)]

    def hash_function(self, name):
        return hash(name) % self.table_size

    def insert(self, name):
        hash_code = self.hash_function(name)
        bucket = self.table[hash_code]

        for item in bucket:
            if item[0] == name:
                return item[1]

        unique_code = f"{hash_code}.{len(bucket) + 1}"
        bucket.append((name, unique_code))
        return unique_code

    def display(self):
        with open("../ST.out", "w") as file:
            file.write("Symbol Table Contents:\n")
            for i, bucket in enumerate(self.table):
                if bucket:
                    file.write(f"Bucket {i}: {bucket}\n")
        print("Symbol table written to ST.out")
