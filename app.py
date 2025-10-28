from flask import Flask
from flask_cors import CORS
from ariadne import MutationType, QueryType, make_executable_schema, graphql_sync, load_schema_from_path
from ariadne.explorer import ExplorerPlayground
from flask import request, jsonify
from logging.config import dictConfig
from log_conf import log_conf_dict

# App Configurations
dictConfig(log_conf_dict)
app = Flask(__name__)
CORS(app)

PLAYGROUND_HTML = ExplorerPlayground(title="Flask Graph API").html(None)

# Support GraphQL types
query = QueryType()
mutation = MutationType()

# in-memory items store
items = []

@app.route('/')
def hello():
  return 'GraphQL API is running!'

@query.field("hello")
def resolve_hello(_, info):
    app.logger.info(f"resolve_hello info=${info}")
    return "Hello, GraphQL!"

@query.field("goodbye")
def resolve_goodbye(_, info):
    app.logger.info(f"resolve_goodbye info=${info}")
    return "Bye, GraphQL!"

# Query resolver: Fetch all items
@query.field("items")
def resolve_items(*_):
    app.logger.info(f"resolve_items items=${items}")
    return items

# Mutation resolver: Add a new item
@mutation.field("addItem")
def resolve_add_item(_, info, name, quantity):
    app.logger.info(f"resolve_add_item info=${info}")
    new_item = {"name": name, "quantity": quantity}
    items.append(new_item)
    return new_item

schema = make_executable_schema(load_schema_from_path("schema.graphql"), query, mutation)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    app.logger.info("GET graphql_playground")
    return PLAYGROUND_HTML, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
   data = request.get_json()
   app.logger.info(f"graphql_server request JSON=${data}")
   success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
   app.logger.info(f"graphql_server result=${result}")
   return jsonify(result), 200 if success else 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
