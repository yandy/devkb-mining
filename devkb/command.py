class BaseCommand(object):

    def name(self):
        """
        Command name
        """
        return self.__class__.__module__.split('.')[-1]

    def help(self):
        """
        Command help text
        """
        return ""

    def add_arguments(self, parser):
        pass

    def run(self, args):
        """
        Entry point for running commands
        """
        raise NotImplementedError
