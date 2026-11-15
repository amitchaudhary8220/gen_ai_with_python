def local_chai():
    yield "Masala Chai"
    yield "Ginger Chai"


def imported_chai():
    yield "Match"
    yield "Oolong"


def full_menu():
    yield from local_chai()
    yield from imported_chai()


# for chai in full_menu():
#     print(chai)


def chai_stall():
    try:
        while True:
            order = yield "Waiting for chai order"
    except:
        print("Stall closed, no more chai")
#During python auto clean up or using stall.close() function
#Cleaning up a paused generator means calling .close() on it, which raises GeneratorExit at the yield.
# which result in print of except statement

stall = chai_stall()
print(next(stall))


# stall.close() # cleaningup hangup memory