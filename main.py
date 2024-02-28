import sys
import os
import json
from rich.traceback import Traceback
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, Static, TextArea

githubAPIKey = "foo"
commitMessage = ""


def create_default_config(config_path):
    with open(config_path, "w") as f:
        default_config = {"githubAPIKey": "foo"}
        json.dump(default_config, f)


class DOCodeTest(App):
    CSS_PATH = "main.tcss"
    BINDINGS = [
        ("ctrl+f", "toggle_files", "Toggle Files"),
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+s", "save", "Save"),
        ("ctrl+q", "show_key", "Show API Key"),
        ("ctrl+u", "edit_commit_message", "Edit Commit Message"),
        ("ctrl+l", "save_commit_message", "Save Commit Message"),
        ("ctrl+o", "push_commit", "Push Commit"),
    ]
    show_tree = var(True)

    def watch_show_tree(self, show_tree: bool) -> None:
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header()
        with Container():
            yield DirectoryTree(path, id="tree-view")
            yield TextArea.code_editor("", language="python", id="code", classes="code")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DirectoryTree).focus()
        self.load_config()

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

    def action_edit_commit_message(self) -> None:
        code_view = self.query_one("#code", TextArea)
        code_view.load_text(commitMessage)
        self.sub_title = "Editing Commit Message"

    def action_save_commit_message(self) -> None:
        global commitMessage
        code_view = self.query_one("#code", TextArea)
        commitMessage = code_view.text


if __name__ == "__main__":
    DOCodeTest().run()
