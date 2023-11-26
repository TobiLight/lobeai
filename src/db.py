from prisma import Prisma
db = Prisma(auto_register=True)


# MONGO_URI = getenv("MONGO_URI")

# client_mongo = MongoClient(
#     MONGO_URI if MONGO_URI else "mongodb+srv://0xTobi:EdmtTjWvlPNa2vnl@cluster0.ogakrxv.mongodb.net/?retryWrites=true&w=majority")

# mongo = client_mongo['sample_mflix']
