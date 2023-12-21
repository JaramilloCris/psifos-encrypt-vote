from algs import EGPublicKey
from api import get_session, send_vote_to_psifos, get_info_election
from config import ELECTION_NAME, ELECTION_UUID, PUBLIC_KEY_JSON, QUESTIONS, ANSWERS
from encrypt import EncryptedAnswer
from models import Election, EncryptedVote
from multiprocessing import Process, Semaphore

import sys
import os

def random_answers():
    """
    Generate random answers

    :return: The random answers
    
    """

    import random

    return [
        [random.randint(0, question["total_answers"] - 1)]
        for question in QUESTIONS
    ]

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
    answers = random_answers()
    enc_ans = list(
        map(
            lambda idx_value: encrypt_answer(election, idx_value[0], idx_value[1]),
            enumerate(answers),
        )
    )
    vote = EncryptedVote(answers=enc_ans, election_uuid=election.election_uuid)
    result = vote.toJSONDict() if to_json else vote
    if to_json:
        print(result)

    return result

def handler_vote(election_name, **kwargs):
    """
    Handle a vote

    :param vote: The vote
    :param election_name: The election name
    
    """
    vote = encrypt_vote(to_json=False, **kwargs)
    cookie_session = get_session(election_name)
    send_vote_to_psifos(vote, cookie_session, election_name=election_name)


def send_vote(**kwargs):
    """
    Send a vote to the backend

    :param kwargs: The arguments
    
    """

    election_name = kwargs.get("name_election", None)
    election_name = ELECTION_NAME if election_name is None else election_name
    total_votes = int(kwargs.get("total_votes", 1))
    # Obtén el número de núcleos disponibles
    num_cores = os.cpu_count()
    
    # Limita la cantidad de procesos en paralelo usando un semáforo
    max_parallel_processes = min(num_cores, total_votes)
    semaphore = Semaphore(max_parallel_processes)
    
    def run_process():
        with semaphore:
            handler_vote(election_name, **kwargs)

    print(f"Sending {total_votes} votes... (this may take a while)")
    print(f"Using up to {max_parallel_processes} cores in parallel")

    processes = []

    for _ in range(total_votes):
        process = Process(target=run_process)
        processes.append(process)
        process.start()

    print("Waiting for all votes to be processed...")
    for process in processes:
        process.join()

    print("All votes have been processed")
        

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
