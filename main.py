from algs import EGPublicKey
from api import get_session, send_vote_to_psifos, get_info_election
from config import ELECTION_NAME, ELECTION_UUID, PUBLIC_KEY_JSON, QUESTIONS, ANSWERS
from encrypt import EncryptedAnswer
from models import Election, EncryptedVote

import sys

def get_info(info_psifos=False, election_name=None):

    """
    Get info about an election from the backend

    :param info_psifos: Whether to get info from the backend or from the psifos server
    :return: The election
    
    """

    public_key_json = PUBLIC_KEY_JSON
    questions = QUESTIONS
    election_uuid = ELECTION_UUID
    election_name = ELECTION_NAME if election_name is None else election_name
    if info_psifos:
        election_info = get_info_election(election_name)
        public_key_json = election_info["public_key"]
        questions = election_info["questions"]
        election_uuid = election_info["election_uuid"]

    public_key = EGPublicKey.fromJSONDict(public_key_json)
    election = Election(name=election_name, questions=questions, public_key=public_key, election_uuid=election_uuid)
    return election


def encrypt_answer(election, question_num, answer_indexed):
    """
    Given an election, a question number, and a list of answers to that question
    in the form of an array of 0-based indexes into the answer array,
    produce an EncryptedAnswer that works.

    :param election: The election
    :param question_num: The question number
    :param answer_indexed: The list of answers
    :return: The encrypted answer

    """

    encrypted_answer = EncryptedAnswer.fromElectionAndAnswer(
        election, question_num, answer_indexed
    )
    return encrypted_answer.toJSONDict()


def encrypt_vote(to_json=True, **kwargs):
    """
    Encrypt a vote

    :param to_json: Whether to return the vote as a JSON string
    :return: The encrypted vote

    """
    
    info_psifos = kwargs.get("info_psifos", False)
    election_name = kwargs.get("name_election", None)
    election = get_info(info_psifos=info_psifos, election_name=election_name)
    enc_ans = list(
        map(
            lambda idx_value: encrypt_answer(election, idx_value[0], idx_value[1]),
            enumerate(ANSWERS),
        )
    )
    vote = EncryptedVote(answers=enc_ans, election_uuid=election.election_uuid)
    result = vote.toJSONDict() if to_json else vote
    if to_json:
        print(result)

    return result


def send_vote(**kwargs):
    """
    Send a vote to the backend

    :param kwargs: The arguments
    
    """

    info_psifos = kwargs.get("info_psifos", False)
    election_name = kwargs.get("name_election", None)
    election = get_info(info_psifos=info_psifos, election_name=election_name)
    vote = encrypt_vote(to_json=False, **kwargs)
    total_votes = kwargs.get("total_votes", 1)
    for _ in range(int(total_votes)):
        cookie_session = get_session(election.name)
        send_vote_to_psifos(vote, cookie_session, election_name=election.name)


if __name__ == "__main__":
    action = sys.argv[1]
    info_psifos = sys.argv[2] == "-psifos" if len(sys.argv) > 2 else False
    name_election = sys.argv[3] if len(sys.argv) > 3 else None

    total_votes_position = 4 if info_psifos else 2
    total_votes = sys.argv[total_votes_position] if len(sys.argv) > total_votes_position else 1

    actions = {"send": send_vote, "encrypt": encrypt_vote}

    if action in actions:
        data = {
            "name_election": name_election,
            "info_psifos": info_psifos,
            "total_votes": total_votes,
        }
        actions[action](**data)
