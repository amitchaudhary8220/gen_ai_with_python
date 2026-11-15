from functools import wraps


def require_admin(func):
    @wraps(func)
    def wrapper(user_role):
        if user_role != "admin":
            print("Access denied: Admins only")
            return None  # to avoid in error
        else:
            return func(user_role)

    return wrapper


# this @require_admin is shorthand for :
#  def access_tea_inventory(role):
#    ...
#access_tea_inventory = require_admin(access_tea_inventory)   # the name is REPLACED

@require_admin
def access_tea_inventory(role):
    print(f"Access to inventory to the tea granted {role}")


access_tea_inventory("user")
access_tea_inventory("admin")
