from controllers.search_controller import SearchAPI , DownloadAPI

def initialize_routes(api):
    api.add_resource(SearchAPI, '/api/search/<query>')
    api.add_resource(DownloadAPI, '/api/download')