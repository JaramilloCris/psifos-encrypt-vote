from algs import EGPublicKey
from api import get_session, send_vote_to_psifos
from config import ELECTION_NAME, ELECTION_UUID, PUBLIC_KEY_JSON, QUESTIONS, ANSWERS
from encrypt import EncryptedAnswer
from models import Election, EncryptedVote

import sys

public_key = EGPublicKey.fromJSONDict(PUBLIC_KEY_JSON)
election = Election(name=ELECTION_NAME, questions=QUESTIONS, public_key=public_key)


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

    enc_ans = list(
        map(
            lambda idx_value: encrypt_answer(election, idx_value[0], idx_value[1]),
            enumerate(ANSWERS),
        )
    )
    vote = EncryptedVote(answers=enc_ans, election_uuid=ELECTION_UUID)
    result = vote.toJSONDict() if to_json else vote
    print(result)
    return result


def send_vote(**kwargs):
    vote = encrypt_vote(to_json=False)
    total_votes = kwargs.get("total_votes", 1)
    for _ in range(int(total_votes)):
        cookie_session = get_session(election.name)
        send_vote_to_psifos(vote, cookie_session, election_name=election.name)


if __name__ == "__main__":
    action = sys.argv[1]
    total_votes = sys.argv[2] if len(sys.argv) > 2 else 1

    actions = {"send": send_vote, "encrypt": encrypt_vote}

    if action in actions:
        data = {
            "total_votes": total_votes,
        }
        actions[action](**data)
