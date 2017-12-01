from flask_restful.reqparse import RequestParser, Argument

# Parser for Query
query_parser = RequestParser()
query_parser.add_argument(Argument(
    name='query',
    required=True,
    type=str,
    help="This argument is always required in order to get a response from the bot."
))
query_parser.add_argument(Argument(
    name='Authorization',
    required=False,
    type=str,
    location='headers',
    help="Authorization, currently only Waldur API token is supported."
))

# Parser for Teach
teach_parser = RequestParser()
teach_parser.add_argument(Argument(
    name='statement',
    required=True,
    type=str,
    help="Statement that is a possible response to 'previous_statement'."
))
teach_parser.add_argument(Argument(
    name='previous_statement',
    required=True,
    type=str,
    help="Statement to which 'statement' is a possible response."
))

# Parser for Authenticate
auth_parser = RequestParser()
auth_parser.add_argument(Argument(
    name='token',
    required=True,
    type=str,
    help="Waldur API token"
))
