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
    name='token',
    required=False,
    type=str,
    help="Waldur API token"
))

# Parser for Teach
teach_parser = RequestParser()
teach_parser.add_argument(Argument(
    name='statement',
    required=True,
    type=str,
    help="Required. Statement that is a possible response to 'previous_statement'."
))
teach_parser.add_argument(Argument(
    name='previous_statement',
    required=True,
    type=str,
    help="Required. Statement to which 'statement' is a possible response."
))