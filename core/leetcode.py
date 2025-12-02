import requests
import logging


QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
    recentAcSubmissionList(username: $username, limit: $limit) {
        id
        title
        titleSlug
        timestamp
    }
}
"""


def fetch_last_ac(username, limit=50):
    url = "https://leetcode.com/graphql"
    payload = {
        "query": QUERY,
        "variables": {"username": username, "limit": limit},
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return []
    
    logging.info(f"Fetched recent AC submissions for user {username}: {response.json()}")

    data = response.json()["data"]["recentAcSubmissionList"]
    return data or []
