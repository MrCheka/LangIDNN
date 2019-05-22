import abc


class IModel(object):
    def __init__(self, vocab_sizes):
        """interface for Models

        Args:
          vocab_sizes: list of two elements, input and output vocabulary size
        """
        self.vocab_sizes = vocab_sizes

    @abc.abstractmethod
    def eval(self, session, inputs):
        """Evaluate inputs and return computed outputs. It must have the same structure as the outputs."""
        return

