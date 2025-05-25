import requests
from debugonce_packages import debugonce

# @debugonce
# def test_function_with_http_call(input):
#     """Function that makes an HTTP request."""
#     print(input)
#     response = requests.get("https://jsonplaceholder.typicode.com/posts/1 ")
#     data = response.json()
#     #print("HTTP Response:", data)
#     return cloud_data


# if __name__ == "__main__":
#     print("\nRunning test_function_with_http_call...")
#     test_function_with_http_call(5)


#write a buggy function
@debugonce
def divide(a,b):
    return a/b
if __name__ == "__main__":
    print("\nRunning divide...")
    divide(4,2)
    divide(4,0)