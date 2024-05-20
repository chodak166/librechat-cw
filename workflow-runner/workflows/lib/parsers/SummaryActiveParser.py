from workflows.lib.ActiveParserAction import ActiveParserAction

class SummaryActiveParser:
  def parse(self, response, feedback_count):
    action = ActiveParserAction()
    if feedback_count == 0:
      action.info = "\n\n---\n\nAsking for summary\n\n---\n\n"
      action.feedback = "Please summarize your last response in three sentences."
    return action
