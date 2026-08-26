from src.models.grade import Grade
from src.models.query_request import QueryRequest
from src.models.route_identifier import RouteIdentifier


def test_query_request():
    request = QueryRequest(query="hello", session_id="test")
    assert request.query == "hello"


def test_route_identifier():
    route = RouteIdentifier(route="index")
    assert route.route == "index"


def test_grade():
    grade = Grade(binary_score="yes")
    assert grade.binary_score == "yes"
