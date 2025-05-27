import requests
from debugonce_packages import debugonce

@debugonce
def fetch_and_save_post(post_id, filename):
    """Fetch a post from an API and save its title to a file."""
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    response = requests.get(url)
    data = response.json()
    # This will raise KeyError if 'title' is missing, which is useful for testing exception capture
    title = data["title"]
    with open(filename, "w") as f:
        f.write(title)
    return title

if __name__ == "__main__":
    print("\nRunning fetch_and_save_post...")
    try:
        result = fetch_and_save_post(1, "post_title.txt")
        print("Result:", result)
    except Exception as e:
        print("Exception captured:", e)