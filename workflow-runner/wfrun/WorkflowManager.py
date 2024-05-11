import os
import importlib.util

class WorkflowManager:
    def __init__(self, workflows_dir):
        self.workflows_dir = workflows_dir
        if not os.path.exists(workflows_dir):
            os.makedirs(workflows_dir)

    def list_workflows(self, human_names=False):
        workflows = []
        for file in os.listdir(self.workflows_dir):
            if file.endswith(".py"):
                file_path = os.path.join(self.workflows_dir, file)
                file_name = os.path.splitext(file)[0]
                if human_names:
                    file_name = file_name.replace("_", " ").capitalize()
                workflows.append((file_path, file_name))
        return workflows

    def create_workflow(self, path):
        spec = importlib.util.spec_from_file_location("module.name", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in dir(module):
            obj = getattr(module, name)
            if hasattr(obj, "__name__") and obj.__name__ == "Workflow":
                return obj()
        return None
