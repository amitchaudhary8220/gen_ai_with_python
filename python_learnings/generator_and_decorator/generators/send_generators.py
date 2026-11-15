def chai_customer():
    print("Welcome! What chai would you like ?")
    order = yield
    print(f"Preparing: {order}")
    order = yield
    print(f" 1 Preparing: {order}")
    yield

    # while True:
    #     print(f"Preparing: {order}")
    #     order = yield


stall = chai_customer()
next(stall)  # start the generator

stall.send("Masala Chai")
stall.send("Lemon Chai")
next(stall)
