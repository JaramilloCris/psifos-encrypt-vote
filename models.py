


class Election:
    """
    Election class

    Attributes:
        name: Election name
        questions: Election questions
        public_key: Election public key

    """

    def __init__(self,name:str=None, questions={}, public_key=None, election_uuid="") -> None:
        self.name = name
        self.questions = questions
        self.public_key = public_key
        self.election_uuid = election_uuid


class EncryptedVote:

    """
    EncryptedVote class

    Attributes:
        answers: Answers
        election_uuid: Election uuid
    
    """

    def __init__(self, answers:list=[], election_uuid: str=None) -> None:
        self.answers = answers
        self.election_uuid = election_uuid

    def toJSONDict(self):
        value = {
            'answers': self.answers,
            'election_uuid': self.election_uuid,
        }

        return value
