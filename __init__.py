from .server import AbletonCopilotServer

def create_instance(c_instance):
    """
    This function is called by Ableton Live when the script is loaded.
    It must return an instance of your main script class.
    """
    return AbletonCopilotServer(c_instance)
