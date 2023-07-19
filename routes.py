from controllers.search_controller import SearchAPI

def initialize_routes(api):
    api.add_resource(SearchAPI, '/api/search/<query>')