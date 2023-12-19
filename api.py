from config import BACKEND_URL, INFO_URL
from models import EncryptedVote
from utils import parse_questions

import json
import requests


def get_session(election_name: str) -> str:
    
    """
    Get a session cookie from the backend

    :param election_name: The name of the election
    :return: The session cookie
    
    """
    url = f"{BACKEND_URL}/{election_name}/vote?redirect=false"
    response = requests.get(url)
    return response.cookies["session"]


def send_vote_to_psifos(vote: EncryptedVote, session: str, election_name: str):
    """
    Send a vote to the backend

    :param vote: The vote to send
    :param session: The session cookie
    :param election_name: The name of the election
    :return: The response from the backend
    
    """

    url = f"{BACKEND_URL}/{election_name}/cast-vote"
    post_data = {"encrypted_vote": json.dumps(vote.toJSONDict())}
    headers = {"Content-Type": "application/json"}
    cookie_session = {'session': session}
    response = requests.post(url, json=post_data, headers=headers, cookies=cookie_session)
    return response

def get_info_election(election_name: str):
    """
    Get info about an election

    :param election_name: The name of the election
    :return: The response from the backend
    
    """
    url = f"{INFO_URL}/election/{election_name}"
    response = requests.get(url)
    election_json = response.json()
    return {
        "questions": parse_questions(json.loads(election_json["questions"])),
        "public_key": json.loads(election_json["public_key"]),
        "election_uuid": election_json["uuid"],
    }
