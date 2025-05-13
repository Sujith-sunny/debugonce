def sample_function(x, y):
    return x / y

@debugonce
def buggy_function(a, b):
    return sample_function(a, b)

if __name__ == "__main__":
    try:
        result = buggy_function(10, 0)  # This will raise a ZeroDivisionError
    except ZeroDivisionError as e:
        print(f"Caught an exception: {e}")