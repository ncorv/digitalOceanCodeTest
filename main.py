import sys
import os
import json
from github import Github
from github import Auth
from rich.traceback import Traceback
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, TextArea

githubAPIKey = "foo"
repo_url = "https://github.com/ncorv/CodeTestEditRepo"


def create_default_config(config_path):
    with open(config_path, "w") as f:
        default_config = {"githubAPIKey": "foo"}
        json.dump(default_config, f)


class DOCodeTest(App):
    CSS_PATH = "main.tcss"
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+s", "save", "Save Open File"),
        ("ctrl+q", "show_key", "Show API Key"),
        ("ctrl+o", "push_commit", "Push File As Commit"),
    ]
    show_tree = var(True)

    def watch_show_tree(self, show_tree: bool) -> None:
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        global githubAPIKey
        global repo_url

        path = "./repo/" if len(sys.argv) < 2 else sys.argv[1]
        username, repo_name = repo_url.split('/')[-2:]
        self.load_config()
        auth = Auth.Token(githubAPIKey)
        g = Github(auth=auth)
        repo = g.get_user(username).get_repo(repo_name)
        contents = repo.get_contents("")

        for content in contents:
            if content.type == "file":
                file_path = os.path.join(path, content.path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as file:
                    file.write(content.decoded_content)
            else:  # is directory
                dir_path = os.path.join(path, content.path)
                os.makedirs(dir_path, exist_ok=True)

                sub_contents = repo.get_contents(content.path)
                for sub_content in sub_contents:
                    sub_file_path = os.path.join(dir_path, sub_content.path.split('/')[-1])
                    if sub_content.type == "file":
                        os.makedirs(os.path.dirname(sub_file_path), exist_ok=True)
                        with open(sub_file_path, "wb") as file:
                            file.write(sub_content.decoded_content)

        yield Header()
        with Container():
            yield DirectoryTree(path, id="tree-view")
            yield TextArea.code_editor("", language="python", id="code", classes="code")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DirectoryTree).focus()

    def load_config(self):
        global githubAPIKey
        config_path = "config.json"
        if not os.path.exists(config_path):
            create_default_config(config_path)
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                githubAPIKey = config.get("githubAPIKey")
        except Exception as e:
            self.load_code_view_and_set_sub_title(Traceback(theme="github-dark", width=None), "Config File ERROR")

    def load_code_view_and_set_sub_title(self, code_txt, sub_title):
        code_view = self.query_one("#code", TextArea)
        code_view.load_text(code_txt)
        self.sub_title = sub_title

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        event.stop()
        try:
            with open(str(event.path), 'r') as file:
                text = file.read()
                self.load_code_view_and_set_sub_title(text, str(event.path))
        except Exception:
            self.load_code_view_and_set_sub_title(Traceback(theme="github-dark", width=None), "ERROR")
        else:
            self.query_one("#code").scroll_home(animate=False)

    def save_current_file(self):
        current_path = self.sub_title
        if current_path and os.path.isfile(current_path):
            code_view = self.query_one("#code", TextArea)
            with open(current_path, 'w') as file:
                file.write(code_view.text)

    def action_toggle_files(self) -> None:
        self.show_tree = not self.show_tree

    def action_save(self) -> None:
        self.save_current_file()

    def action_show_key(self) -> None:
        code_view = self.query_one("#code", TextArea)
        code_view.load_text("API Key currently set to: " + githubAPIKey)
        self.sub_title = "Current API Key"

    def action_push_commit(self) -> None:
        code_view = self.query_one("#code", TextArea)
        code_view.load_text("API Key currently set to: " + githubAPIKey)
        self.sub_title = "Current API Key"

    def create_directory_structure(self, contents, path, repo=None):
        for content in contents:
            file_path = os.path.join(path, content.path)
            if content.type == "file":
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as file:
                    file.write(content.decoded_content)
            else:
                os.makedirs(file_path, exist_ok=True)
                self.create_directory_structure(repo.get_contents(content.path), file_path)

if __name__ == "__main__":
    DOCodeTest().run()
